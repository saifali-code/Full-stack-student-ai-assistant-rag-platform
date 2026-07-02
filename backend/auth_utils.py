# backend/auth_utils.py

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import User
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# PASSWORD HASHING
# ============================================================

# CryptContext handles password hashing using bcrypt algorithm
# bcrypt is VERY secure — it's designed to be slow so hackers can't brute-force it
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """
    Converts a plain password into a secure hash.
    
    Example:
    Input:  "mypassword123"
    Output: "$2b$12$eW5FHjIq4t8uXbEiGDfjaeK..." (looks random)
    
    The same password ALWAYS produces a DIFFERENT hash (due to "salt")
    but verify_password can still check them.
    """
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain password matches a stored hash.
    
    Example:
    verify_password("mypassword123", "$2b$12$eW5FH...") → True
    verify_password("wrongpassword", "$2b$12$eW5FH...") → False
    """
    return pwd_context.verify(plain_password, hashed_password)

# ============================================================
# JWT TOKEN SYSTEM
# ============================================================

# SECRET_KEY is like a password used to sign tokens
# If someone doesn't have this key, they can't fake tokens
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = "HS256"          # The encryption algorithm
TOKEN_EXPIRE_HOURS = 24      # Tokens expire after 24 hours

def create_access_token(user_id: int) -> str:
    """
    Creates a JWT token for a logged-in user.
    
    The token contains:
    - user_id: so we know WHO this token belongs to
    - exp: when this token expires
    
    Returns a string token that looks like: "eyJ..."
    """
    # Data to put inside the token
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
        # exp = expiration time (24 hours from now)
    }
    
    # jwt.encode() creates the token using our SECRET_KEY
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str) -> dict:
    """
    Reads a JWT token and returns what's inside.
    Raises an error if the token is invalid or expired.
    
    Returns: {"user_id": 1} or similar
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again."
        )

# ============================================================
# CURRENT USER DEPENDENCY
# ============================================================

# OAuth2PasswordBearer tells FastAPI where to look for the token
# "tokenUrl" is just for documentation — it points to our login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),   # FastAPI automatically extracts token from request header
    db: Session = Depends(get_db)          # FastAPI automatically provides a database session
) -> User:
    """
    This function is used to PROTECT routes.
    Any route that uses this as a dependency will require authentication.
    
    How it works:
    1. FastAPI extracts the token from "Authorization: Bearer <token>" header
    2. We decode the token to get user_id
    3. We look up the user in the database
    4. We return the User object
    
    If anything fails → 401 Unauthorized error
    
    Usage example:
    @router.get("/protected")
    def protected_route(current_user: User = Depends(get_current_user)):
        return {"message": f"Hello {current_user.name}!"}
    """
    # Decode the token
    payload = verify_token(token)
    user_id = payload.get("user_id")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token doesn't contain user ID"
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found — account may have been deleted"
        )
    
    return user  # This User object is passed to the route function