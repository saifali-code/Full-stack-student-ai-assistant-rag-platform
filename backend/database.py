# backend/database.py

# SQLAlchemy is a Python library that talks to databases
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load our secret settings from the .env file
load_dotenv()

# DATABASE_URL tells SQLAlchemy how to connect to PostgreSQL
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/study_assistant")

# "engine" is the actual connection to the database
# It's like starting a car engine before you can drive
engine = create_engine(DATABASE_URL)

# SessionLocal creates "sessions" — each session is one conversation with the DB
# A session lets you do multiple queries in one go
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for all our database models (tables)
# Every table class will inherit from Base
Base = declarative_base()

# This function gives each API request its own database session
# It's like giving each customer their own shopping cart
def get_db():
    db = SessionLocal()  # Open a new session
    try:
        yield db          # Give it to whoever asked for it
    finally:
        db.close()        # Always close it when done (prevent memory leaks)