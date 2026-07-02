-- This creates the database tables for our Smart Study Assistant
-- Run this file in PostgreSQL to set up the database

-- Drop tables if they exist (useful for resetting during development)
DROP TABLE IF EXISTS chat_history;
DROP TABLE IF EXISTS quiz_scores;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS users;

-- USERS TABLE
-- Stores every registered student's account information
CREATE TABLE users (
    id SERIAL PRIMARY KEY,          -- Auto-incrementing unique ID for each user
    name VARCHAR(100) NOT NULL,     -- Student's full name (max 100 characters)
    email VARCHAR(255) UNIQUE NOT NULL, -- Email must be unique (no duplicate accounts)
    password VARCHAR(255) NOT NULL, -- We store a HASHED password (never plain text!)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- When the account was created
);

-- DOCUMENTS TABLE
-- Keeps track of every PDF/note a student uploads
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, -- Links to the user who uploaded
    filename VARCHAR(255) NOT NULL,      -- Original name of the file
    filepath VARCHAR(500) NOT NULL,      -- Where the file is saved on our server
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- "REFERENCES users(id)" means: this user_id must exist in the users table
-- "ON DELETE CASCADE" means: if a user is deleted, their documents are too

-- QUIZ_SCORES TABLE
-- Saves quiz results so students can track their progress
CREATE TABLE quiz_scores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,             -- Score out of 100
    topic VARCHAR(255),                 -- What subject/topic the quiz was about
    total_questions INTEGER DEFAULT 5,  -- How many questions were in the quiz
    correct_answers INTEGER DEFAULT 0,  -- How many they got right
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CHAT_HISTORY TABLE
-- Saves every question a student asked and the AI's answer
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,   -- The student's question (TEXT = unlimited length)
    answer TEXT NOT NULL,     -- The AI's answer
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add some test data to verify everything works
INSERT INTO users (name, email, password) 
VALUES ('Test Student', 'test@test.com', 'not_a_real_password');

-- Verify tables were created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';