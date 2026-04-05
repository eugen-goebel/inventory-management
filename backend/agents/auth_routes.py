"""Authentication API routes — register, login, user info."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from models.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from agents.auth_service import register_user, authenticate_user, create_access_token
from agents.auth_deps import get_current_user
from models.orm import User

auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@auth_router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account.

    The first user registered bootstraps as admin. All subsequent users
    are created as viewer regardless of any client-supplied role — role
    escalation must happen out-of-band (direct DB or by an existing admin).
    """
    forced_role = "admin" if db.query(User).count() == 0 else "viewer"
    try:
        user = register_user(db, data.username, data.email, data.password, forced_role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    token = create_access_token(user.id, user.username, user.role)
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@auth_router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate and receive a JWT token."""
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(user.id, user.username, user.role)
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@auth_router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return UserResponse.model_validate(user)
