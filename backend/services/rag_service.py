# backend/services/rag_service.py

import os
import pickle  # For saving/loading Python objects to disk
from typing import Optional
import PyPDF2  # For reading PDF files
from sentence_transformers import SentenceTransformer  # For creating embeddings
import faiss  # Facebook's vector similarity search library
import numpy as np  # For numerical operations
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ============================================================
# GLOBAL SETUP
# ============================================================

# Load the embedding model once (it takes a few seconds to load)
# 'all-MiniLM-L6-v2' is a small but powerful model
# It converts text to 384-dimensional vectors (arrays of 384 numbers)
print("Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Embedding model loaded!")

# Folder to store FAISS indexes
FAISS_DIR = "faiss_indexes"
os.makedirs(FAISS_DIR, exist_ok=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_faiss_paths(user_id: int):
    """
    Each user gets their own FAISS index (so students don't see each other's notes).
    Returns paths to the two files we need:
    - index file: the FAISS vector database
    - texts file: the original text chunks (so we can return them)
    """
    index_path = os.path.join(FAISS_DIR, f"user_{user_id}.index")
    texts_path = os.path.join(FAISS_DIR, f"user_{user_id}_texts.pkl")
    return index_path, texts_path


def load_or_create_index(user_id: int):
    """
    Loads the user's FAISS index from disk, or creates a new empty one.
    
    FAISS needs to know the dimension of vectors upfront.
    all-MiniLM-L6-v2 creates 384-dimensional vectors.
    """
    index_path, texts_path = get_faiss_paths(user_id)
    
    if os.path.exists(index_path):
        # Load existing index
        index = faiss.read_index(index_path)
        
        # Load the text chunks
        with open(texts_path, 'rb') as f:
            texts = pickle.load(f)
        
        return index, texts
    else:
        # Create new empty index
        # faiss.IndexFlatL2 = simple index using L2 (Euclidean) distance
        # 384 = dimension of our embeddings
        dimension = 384
        index = faiss.IndexFlatL2(dimension)
        texts = []  # Empty list — will store text chunks
        return index, texts


def save_index(user_id: int, index, texts: list):
    """Saves the FAISS index and text chunks to disk."""
    index_path, texts_path = get_faiss_paths(user_id)
    
    faiss.write_index(index, index_path)
    
    with open(texts_path, 'wb') as f:
        pickle.dump(texts, f)


# ============================================================
# DOCUMENT PROCESSING (called when PDF is uploaded)
# ============================================================

def read_pdf(filepath: str) -> str:
    """
    Reads a PDF file and extracts all the text.
    
    Returns a single string with all the text from the PDF.
    """
    text = ""
    
    if filepath.endswith('.pdf'):
        # Open the PDF file
        with open(filepath, 'rb') as file:  # 'rb' = read binary
            reader = PyPDF2.PdfReader(file)
            
            # Loop through each page and extract text
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n"
    else:
        # For .txt files, just read directly
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    
    return text


def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Splits a long text into smaller chunks.
    
    WHY CHUNKING?
    - AI models have a limit on how much text they can read at once
    - Smaller chunks make searching more precise
    - We only send RELEVANT chunks (not entire notes) to the AI
    
    HOW IT WORKS:
    - chunk_size = 500 characters per chunk
    - overlap = 50 characters overlap between chunks
    
    Example with chunk_size=20, overlap=5:
    Text: "Hello World This Is A Test Of Chunking System"
    Chunk 1: "Hello World This Is A"
    Chunk 2: "Is A Test Of Chunking"  ← overlaps with chunk 1
    Chunk 3: "Chunking System"
    
    Overlap helps because important sentences might span chunk boundaries.
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # Try to break at a sentence or paragraph boundary
        if end < text_length:
            # Look for a good break point (period, newline) within last 100 chars
            break_point = text.rfind('.', start, end)
            if break_point == -1:
                break_point = text.rfind('\n', start, end)
            if break_point != -1 and break_point > start:
                end = break_point + 1
        
        chunk = text[start:end].strip()
        if chunk:  # Don't add empty chunks
            chunks.append(chunk)
        
        # Move start forward, but go back by 'overlap' characters
        start = end - overlap
    
    return chunks


def process_document(filepath: str, user_id: int):
    """
    Main function called when a student uploads a document.
    
    COMPLETE FLOW:
    1. Read the text from PDF/TXT
    2. Split into chunks
    3. Create embeddings for each chunk
    4. Add to FAISS index
    5. Save to disk
    """
    
    print(f"Processing document: {filepath}")
    
    # STEP 1: Read text
    text = read_pdf(filepath)
    
    if not text.strip():
        raise ValueError("Could not extract any text from the document")
    
    # STEP 2: Split into chunks
    chunks = split_into_chunks(text)
    print(f"Created {len(chunks)} chunks")
    
    # STEP 3: Create embeddings
    # embedding_model.encode() converts list of strings to numpy array of vectors
    # Shape: (num_chunks, 384)
    # Example: 10 chunks → array of shape (10, 384)
    print("Creating embeddings...")
    embeddings = embedding_model.encode(chunks)
    
    # FAISS needs float32 format
    embeddings = np.array(embeddings, dtype=np.float32)
    
    # STEP 4: Load or create index and add embeddings
    index, existing_texts = load_or_create_index(user_id)
    
    # Add new embeddings to the index
    index.add(embeddings)
    
    # Keep track of the text chunks (in same order as embeddings)
    existing_texts.extend(chunks)
    
    # STEP 5: Save to disk
    save_index(user_id, index, existing_texts)
    
    print(f"Document processed! Total chunks in index: {len(existing_texts)}")


# ============================================================
# RETRIEVAL (called when student asks a question)
# ============================================================

def get_relevant_context(query: str, user_id: int, top_k: int = 3) -> str:
    """
    Searches the student's notes for text relevant to the query.
    
    Steps:
    1. Convert the query to an embedding
    2. Search FAISS for the most similar chunks
    3. Return those chunks as context
    
    Returns empty string if no notes uploaded.
    """
    
    index_path, texts_path = get_faiss_paths(user_id)
    
    # If user has no notes uploaded yet
    if not os.path.exists(index_path):
        return ""
    
    # Load the index
    index, texts = load_or_create_index(user_id)
    
    if index.ntotal == 0:  # No embeddings stored
        return ""
    
    # STEP 1: Embed the query
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding, dtype=np.float32)
    
    # STEP 2: Search for top_k most similar chunks
    # index.search() returns:
    # - distances: how similar each result is (lower = more similar)
    # - indices: the positions of matching chunks in our texts list
    k = min(top_k, index.ntotal)  # Can't return more than we have
    distances, indices = index.search(query_embedding, k)
    
    # STEP 3: Get the actual text for those indices
    relevant_chunks = []
    for idx in indices[0]:  # indices[0] because we searched 1 query
        if idx != -1:  # -1 means no result found
            relevant_chunks.append(texts[idx])
    
    # Join chunks with separators
    context = "\n\n---\n\n".join(relevant_chunks)
    return context


def get_answer(question: str, user_id: int) -> str:
    """
    Complete RAG pipeline: takes a question, finds relevant notes, gets AI answer.
    
    This is called when a student asks a question on the Chat page.
    """
    
    # STEP 1: Get relevant context from notes
    context = get_relevant_context(question, user_id)
    
    # STEP 2: Build prompt
    if context:
        prompt = f"""You are a helpful study assistant. Answer the student's question 
based on their study notes provided below.

If the answer is in the notes, explain it clearly.
If the answer is not in the notes, say so and provide a general answer.

STUDENT'S NOTES:
{context}

STUDENT'S QUESTION: {question}

ANSWER:"""
    else:
        # No notes uploaded yet — answer from general knowledge
        prompt = f"""You are a helpful study assistant. The student hasn't uploaded any notes yet.
Answer this question from your general knowledge and remind them they can upload notes for more specific help.

QUESTION: {question}

ANSWER:"""
    
    # STEP 3: Call AI API
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful, patient tutor helping students understand their study material."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        return answer
        
    except Exception as e:
        return f"Sorry, I couldn't get an answer right now. Error: {str(e)}"