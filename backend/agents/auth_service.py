"""
Authentication service — JWT token management, password hashing, user CRUD.
"""

import os
from datetime import datetime, timezone, timedelta

import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from models.orm import User

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Returns:
        dict with 'sub', 'username', 'role' keys

    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is invalid
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def register_user(db: Session, username: str, email: str, password: str, role: str = "viewer") -> User:
    """
    Create a new user account.

    Raises:
        ValueError: If username or email already exists
    """
    if db.query(User).filter(User.username == username).first():
        raise ValueError(f"Username '{username}' is already taken")
    if db.query(User).filter(User.email == email).first():
        raise ValueError(f"Email '{email}' is already registered")

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Verify credentials and return the user, or None if invalid."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()
