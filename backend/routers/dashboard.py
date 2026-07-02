# backend/routers/dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.models import User, QuizScore, Document
from backend.auth_utils import get_current_user

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all data needed for the dashboard:
    - Total quizzes taken
    - Average score
    - Recent quiz scores
    - Weak topics (topics where score < 60)
    - Number of uploaded documents
    """
    
    # Get all quiz scores for this user
    all_scores = db.query(QuizScore).filter(
        QuizScore.user_id == current_user.id
    ).all()
    
    # Calculate statistics
    total_quizzes = len(all_scores)
    
    if total_quizzes > 0:
        average_score = sum(s.score for s in all_scores) / total_quizzes
        # "sum(s.score for s in all_scores)" = generator expression
        # It's like a loop: total = 0; for s in all_scores: total += s.score
    else:
        average_score = 0
    
    # Get recent 5 scores for the chart
    recent_scores = db.query(QuizScore).filter(
        QuizScore.user_id == current_user.id
    ).order_by(QuizScore.date.desc()).limit(5).all()
    
    # Find weak topics: topics where average score is below 60
    # Group scores by topic and calculate average per topic
    weak_topics = []
    topic_scores = {}  # Dictionary: {"Photosynthesis": [60, 40, 55]}
    
    for score_record in all_scores:
        topic = score_record.topic or "General"
        if topic not in topic_scores:
            topic_scores[topic] = []
        topic_scores[topic].append(score_record.score)
    
    for topic, scores in topic_scores.items():
        avg = sum(scores) / len(scores)
        if avg < 60:  # Below 60% is considered weak
            weak_topics.append(topic)
    
    # Count uploaded documents
    doc_count = db.query(Document).filter(
        Document.user_id == current_user.id
    ).count()
    
    return {
        "total_quizzes": total_quizzes,
        "average_score": round(average_score, 1),
        "recent_scores": [
            {
                "topic": s.topic or "General",
                "score": s.score,
                "date": s.date.strftime("%b %d")  # Format: "Jan 15"
            }
            for s in recent_scores
        ],
        "weak_topics": weak_topics,
        "uploaded_documents": doc_count,
        "student_name": current_user.name
    }