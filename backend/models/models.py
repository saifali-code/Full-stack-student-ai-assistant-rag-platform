# backend/models/models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

# Each class = one table in the database
# Each variable inside = one column in that table

class User(Base):
    """
    This class represents the 'users' table.
    Every student who registers gets a row here.
    """
    __tablename__ = "users"  # This must match the table name in schema.sql

    id = Column(Integer, primary_key=True, index=True)
    # primary_key=True means this is the unique identifier
    # index=True makes searches faster
    
    name = Column(String(100), nullable=False)
    # nullable=False means this field is REQUIRED
    
    email = Column(String(255), unique=True, nullable=False)
    # unique=True means no two users can have the same email
    
    password = Column(String(255), nullable=False)
    # We will HASH the password before storing (never store plain text!)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # server_default=func.now() means: automatically set to current time

    # Relationships — tell SQLAlchemy how tables connect
    # "If I have a User, I can get all their documents with user.documents"
    documents = relationship("Document", back_populates="owner", cascade="all, delete")
    quiz_scores = relationship("QuizScore", back_populates="student", cascade="all, delete")
    chat_history = relationship("ChatHistory", back_populates="student", cascade="all, delete")


class Document(Base):
    """
    Represents the 'documents' table.
    Each uploaded PDF/note is one row here.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    # ForeignKey("users.id") means: this must match an id in the users table
    
    filename = Column(String(255), nullable=False)  # Original file name
    filepath = Column(String(500), nullable=False)  # Where it's saved on disk
    upload_date = Column(DateTime(timezone=True), server_default=func.now())

    # This lets us do: document.owner to get the User who uploaded it
    owner = relationship("User", back_populates="documents")


class QuizScore(Base):
    """
    Represents the 'quiz_scores' table.
    Each quiz attempt is saved here.
    """
    __tablename__ = "quiz_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Integer, nullable=False)       # Score percentage (0-100)
    topic = Column(String(255))                   # Topic of the quiz
    total_questions = Column(Integer, default=5)
    correct_answers = Column(Integer, default=0)
    date = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User", back_populates="quiz_scores")


class ChatHistory(Base):
    """
    Represents the 'chat_history' table.
    Every question asked and AI answer is saved here.
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text, nullable=False)  # Text = very long string (no limit)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User", back_populates="chat_history")