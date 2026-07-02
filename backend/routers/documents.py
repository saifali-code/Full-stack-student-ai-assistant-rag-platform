# backend/routers/documents.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime

from backend.database import get_db
from backend.models.models import User, Document
from backend.auth_utils import get_current_user

router = APIRouter(tags=["Documents"])

# Where to save uploaded files on our server
UPLOAD_DIR = "uploads"

# Create the uploads folder if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),              # "..." means this is REQUIRED
    current_user: User = Depends(get_current_user),  # Must be logged in
    db: Session = Depends(get_db)
):
    """
    Uploads a PDF or text file.
    
    Steps:
    1. Check the file type is allowed
    2. Create a unique filename (to avoid conflicts)
    3. Save the file to the uploads/ folder
    4. Save file info to the database
    5. Trigger the RAG system to process the file
    6. Return success
    """
    
    # STEP 1: Validate file type
    allowed_types = ["application/pdf", "text/plain"]
    allowed_extensions = [".pdf", ".txt"]
    
    # Get the file extension (.pdf, .txt, etc.)
    _, ext = os.path.splitext(file.filename)
    
    if ext.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Please upload PDF or TXT files only."
        )
    
    # STEP 2: Create a unique filename to avoid overwriting existing files
    # We add timestamp to make it unique
    # Example: "biology_notes_20240115_143022.pdf"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{current_user.id}_{timestamp}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, safe_filename)
    
    # STEP 3: Save the file to disk
    # "wb" = write binary mode (for PDFs and other binary files)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        # shutil.copyfileobj efficiently copies the uploaded file to disk
    
    # STEP 4: Save record to database
    new_doc = Document(
        user_id=current_user.id,
        filename=file.filename,  # Original name (to show user)
        filepath=filepath         # Full path (to read later)
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    # STEP 5: Process with RAG system
    # Import here to avoid circular imports
    from backend.services.rag_service import process_document
    try:
        process_document(filepath, current_user.id)
        rag_status = "File processed and ready for questions!"
    except Exception as e:
        # If RAG processing fails, we still saved the file — just warn the user
        rag_status = f"File saved but RAG processing failed: {str(e)}"
    
    # STEP 6: Return response
    return {
        "message": "File uploaded successfully!",
        "document_id": new_doc.id,
        "filename": file.filename,
        "rag_status": rag_status
    }


@router.get("/documents")
def get_user_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns a list of all files uploaded by the current user.
    Used on the Upload page to show "Your uploaded files".
    """
    
    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).all()
    
    return {
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "upload_date": doc.upload_date.strftime("%Y-%m-%d %H:%M")
            }
            for doc in documents
            # This is a "list comprehension" — a compact way to build a list
            # For each doc in documents, create a dictionary with these fields
        ]
    }