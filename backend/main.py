# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import Base, engine

# Import all routers
from backend.routers import auth, documents, chat, quiz, dashboard, prediction

# ============================================================
# CREATE DATABASE TABLES
# ============================================================
# This creates all tables from our model definitions
# It's safe to call multiple times — it won't recreate existing tables
Base.metadata.create_all(bind=engine)

# ============================================================
# CREATE FASTAPI APP
# ============================================================
app = FastAPI(
    title="Smart Study Assistant API",
    description="Backend for the Smart Study Assistant web application",
    version="1.0.0"
)

# ============================================================
# CORS MIDDLEWARE
# ============================================================
# CORS = Cross-Origin Resource Sharing
# 
# PROBLEM: Browsers block requests from one origin to another by default
# Our frontend runs on: http://localhost:5173
# Our backend runs on:  http://localhost:8000
# These are DIFFERENT origins → browser blocks requests!
#
# SOLUTION: Tell the backend to allow requests from our frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,    # Allow cookies/auth headers
    allow_methods=["*"],       # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],       # Allow all headers (including Authorization)
)

# ============================================================
# REGISTER ROUTERS
# ============================================================
# Each router handles a group of related endpoints
# prefix="" means no prefix — routes are available at root level

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(quiz.router)
app.include_router(dashboard.router)
app.include_router(prediction.router)


# ============================================================
# ROOT ENDPOINT
# ============================================================
@app.get("/")
def root():
    """
    Simple health check endpoint.
    Visit http://localhost:8000 to verify the server is running.
    """
    return {
        "message": "Smart Study Assistant API is running!",
        "docs": "Visit http://localhost:8000/docs for API documentation",
        "status": "healthy"
    }