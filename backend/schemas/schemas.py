# backend/schemas/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ==================== AUTH SCHEMAS ====================

class UserRegister(BaseModel):
    """
    What we expect when someone registers.
    If the frontend sends data in a different shape, FastAPI auto-rejects it.
    """
    name: str           # Required: must be a string
    email: EmailStr     # Required: must be a valid email format
    password: str       # Required: must be a string

class UserLogin(BaseModel):
    """What we expect when someone logs in."""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """What we send back after successful login."""
    access_token: str   # The JWT token
    token_type: str     # Always "bearer"
    user_name: str      # So frontend can display "Welcome, Ali!"

class UserResponse(BaseModel):
    """Safe user data to send to frontend (no password!)."""
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # Allows converting SQLAlchemy model to this schema

# ==================== DOCUMENT SCHEMAS ====================

class DocumentResponse(BaseModel):
    """What we send back after a file is uploaded."""
    id: int
    filename: str
    upload_date: datetime

    class Config:
        from_attributes = True

# ==================== CHAT SCHEMAS ====================

class AskQuestion(BaseModel):
    """What we expect when a student asks a question."""
    question: str       # The actual question

class ChatResponse(BaseModel):
    """What we send back with the AI's answer."""
    question: str
    answer: str

# ==================== QUIZ SCHEMAS ====================

class GenerateQuizRequest(BaseModel):
    """Request to generate a quiz."""
    topic: Optional[str] = "general"  # Optional topic, defaults to "general"
    num_questions: Optional[int] = 5  # How many questions to generate

class QuizQuestion(BaseModel):
    """A single quiz question."""
    question: str
    options: List[str]      # List of 4 choices: ["A) ...", "B) ...", ...]
    correct_answer: str     # Which option is correct

class QuizResponse(BaseModel):
    """The full quiz sent to the frontend."""
    topic: str
    questions: List[QuizQuestion]

class SubmitQuizRequest(BaseModel):
    """What the frontend sends when student submits answers."""
    topic: str
    answers: List[str]          # Student's selected answers
    correct_answers: List[str]  # The correct answers (for scoring)

class QuizScoreResponse(BaseModel):
    """What we send back after grading the quiz."""
    score: int
    correct: int
    total: int
    message: str

# ==================== DASHBOARD SCHEMAS ====================

class DashboardResponse(BaseModel):
    """All the data for the dashboard page."""
    total_quizzes: int
    average_score: float
    recent_scores: List[dict]
    weak_topics: List[str]
    uploaded_documents: int

# ==================== PREDICTION SCHEMAS ====================

class PredictRequest(BaseModel):
    """Input features for the ML prediction model."""
    study_hours: float      # Hours studied per day
    quiz_score: float       # Average quiz score
    practice_count: int     # Number of quizzes/practice tests taken

class PredictResponse(BaseModel):
    """Prediction result."""
    prediction: str         # "PASS" or "FAIL"
    confidence: float       # How confident the model is (0-1)
    message: str            # Human-readable explanation