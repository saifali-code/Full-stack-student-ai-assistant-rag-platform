# backend/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import our own files
from backend.database import get_db
from backend.models.models import User
from backend.schemas.schemas import UserRegister, UserLogin, TokenResponse
from backend.auth_utils import hash_password, verify_password, create_access_token

# APIRouter groups related routes together
# prefix="/auth" means all routes here start with /auth (optional)
router = APIRouter(tags=["Authentication"])

# ============================================================
# REGISTER ENDPOINT
# POST /register
# ============================================================

@router.post("/register", status_code=201)
def register(
    user_data: UserRegister,   # FastAPI validates this automatically using our schema
    db: Session = Depends(get_db)  # Gets a database session
):
    """
    Creates a new user account.
    
    What happens step by step:
    1. Frontend sends: {"name": "Ali", "email": "ali@test.com", "password": "pass123"}
    2. We check if email already exists in database
    3. If not, we hash the password
    4. We save the new user to database
    5. We return a success message
    """
    
    # STEP 1: Check if email is already taken
    # db.query(User) = SELECT * FROM users
    # .filter(User.email == user_data.email) = WHERE email = 'ali@test.com'
    # .first() = LIMIT 1 (get just the first result, or None)
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    
    if existing_user:
        # HTTP 400 = Bad Request (the user made an error — email already taken)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )
    
    # STEP 2: Hash the password BEFORE saving
    # NEVER save plain text passwords!
    hashed = hash_password(user_data.password)
    
    # STEP 3: Create the User object (but don't save yet)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed   # Store the HASH not the original password
    )
    
    # STEP 4: Add to session and commit (this actually saves to database)
    db.add(new_user)      # Stage the INSERT
    db.commit()           # Execute the INSERT
    db.refresh(new_user)  # Get the auto-generated id from database
    
    # STEP 5: Return success
    return {
        "message": f"Account created successfully! Welcome, {new_user.name}!",
        "user_id": new_user.id
    }


# ============================================================
# LOGIN ENDPOINT
# POST /login
# ============================================================

@router.post("/login", response_model=TokenResponse)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Logs in a user and returns a JWT token.
    
    Steps:
    1. Frontend sends: {"email": "ali@test.com", "password": "pass123"}
    2. We find the user by email
    3. We verify the password matches the hash
    4. We create a JWT token
    5. We return the token to frontend
    """
    
    # STEP 1: Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # STEP 2: Check if user exists AND password is correct
    if not user or not verify_password(credentials.password, user.password):
        # We give the same error for both cases — for security
        # (Don't tell hackers "email doesn't exist" or "wrong password" separately)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # STEP 3: Create JWT token
    token = create_access_token(user_id=user.id)
    
    # STEP 4: Return token
    # Frontend will store this and send it with every future request
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_name=user.name
    )