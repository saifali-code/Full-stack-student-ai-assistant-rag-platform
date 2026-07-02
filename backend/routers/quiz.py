# backend/routers/quiz.py

import json
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.models import User, QuizScore
from backend.schemas.schemas import (
    GenerateQuizRequest, QuizResponse, 
    SubmitQuizRequest, QuizScoreResponse
)
from backend.auth_utils import get_current_user
from backend.services.rag_service import get_relevant_context
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter(tags=["Quiz"])


@router.post("/generate-quiz")
async def generate_quiz(
    request: GenerateQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a multiple-choice quiz from the student's uploaded notes.
    
    Steps:
    1. Get relevant context from notes (using RAG)
    2. Ask AI to create quiz questions based on context
    3. Parse the AI response into structured questions
    4. Return questions to frontend
    """
    
    # STEP 1: Get relevant content from notes
    # If a topic is specified, search for that topic in notes
    context = get_relevant_context(
        query=request.topic,
        user_id=current_user.id
    )
    
    if not context:
        # No notes uploaded yet
        context = "General knowledge quiz"
    
    num_q = request.num_questions or 5
    
    # STEP 2: Ask AI to create questions
    # We give it a very specific format so we can parse the response
    prompt = f"""
    You are a teacher creating a quiz. Based on the following study material, 
    create exactly {num_q} multiple choice questions.
    
    STUDY MATERIAL:
    {context}
    
    TOPIC: {request.topic}
    
    Return ONLY valid JSON in this exact format (no other text):
    {{
        "questions": [
            {{
                "question": "What is...?",
                "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
                "correct_answer": "A) option1"
            }}
        ]
    }}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful teacher. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7  # Some creativity but mostly factual
        )
        
        # Extract the text response
        ai_response = response.choices[0].message.content
        
        # STEP 3: Parse JSON response
        # Remove any markdown code blocks if present
        ai_response = ai_response.strip()
        if ai_response.startswith("```"):
            ai_response = ai_response.split("```")[1]
            if ai_response.startswith("json"):
                ai_response = ai_response[4:]
        
        quiz_data = json.loads(ai_response)
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="AI returned invalid format. Please try again."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating quiz: {str(e)}"
        )
    
    return {
        "topic": request.topic,
        "questions": quiz_data["questions"]
    }


@router.post("/submit-quiz")
def submit_quiz(
    submission: SubmitQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Grades the submitted quiz and saves the score.
    
    Steps:
    1. Compare student's answers with correct answers
    2. Calculate score percentage
    3. Save score to database
    4. Return results
    """
    
    # STEP 1: Grade the quiz
    correct_count = 0
    total = len(submission.correct_answers)
    
    for student_answer, correct_answer in zip(submission.answers, submission.correct_answers):
        # zip() pairs up corresponding items from two lists
        # Example: zip(["A","B","C"], ["A","C","C"]) → [("A","A"), ("B","C"), ("C","C")]
        if student_answer.strip() == correct_answer.strip():
            correct_count += 1
    
    # STEP 2: Calculate percentage
    score = int((correct_count / total) * 100) if total > 0 else 0
    
    # STEP 3: Save to database
    quiz_record = QuizScore(
        user_id=current_user.id,
        score=score,
        topic=submission.topic,
        total_questions=total,
        correct_answers=correct_count
    )
    db.add(quiz_record)
    db.commit()
    
    # STEP 4: Create a message based on score
    if score >= 80:
        message = "Excellent! You know this topic very well! 🌟"
    elif score >= 60:
        message = "Good job! Keep studying to improve further. 📚"
    elif score >= 40:
        message = "You need more practice on this topic. 💪"
    else:
        message = "Don't worry! Review this topic and try again. 🔄"
    
    return QuizScoreResponse(
        score=score,
        correct=correct_count,
        total=total,
        message=message
    )