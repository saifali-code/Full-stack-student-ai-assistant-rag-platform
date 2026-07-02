# backend/routers/chat.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.models import User, ChatHistory
from backend.schemas.schemas import AskQuestion, ChatResponse
from backend.auth_utils import get_current_user
from backend.services.rag_service import get_answer

router = APIRouter(tags=["Chat"])


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: AskQuestion,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Answers a student's question using their uploaded notes.
    
    Flow:
    Student asks "What is photosynthesis?"
         ↓
    RAG system searches notes for relevant chunks
         ↓
    Relevant text is sent to AI along with the question
         ↓
    AI generates an answer based on the notes
         ↓
    Answer is saved to history and returned
    """
    
    # Get the question from the request
    question = request.question.strip()
    
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Call the RAG service to get an answer
    # This is where the magic happens — see rag_service.py for details
    answer = get_answer(
        question=question,
        user_id=current_user.id
    )
    
    # Save to chat history database
    chat_record = ChatHistory(
        user_id=current_user.id,
        question=question,
        answer=answer
    )
    db.add(chat_record)
    db.commit()
    
    return ChatResponse(question=question, answer=answer)


@router.get("/chat-history")
def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the last 20 questions and answers for this user."""
    
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.desc()).limit(20).all()
    # .order_by(ChatHistory.created_at.desc()) = newest first
    # .limit(20) = only get last 20
    
    return {
        "history": [
            {
                "question": chat.question,
                "answer": chat.answer,
                "date": chat.created_at.strftime("%Y-%m-%d %H:%M")
            }
            for chat in history
        ]
    }