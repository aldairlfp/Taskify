"""
Async authentication utilities for JWT token handling and password management
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from dotenv import load_dotenv

from app.core.database import get_db
from app.models.models import User
from app.core.logging_config import SecurityLogger, get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

# JWT Configuration from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token verification failed: no username in token")
            raise credentials_exception
        return username
    except JWTError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        raise credentials_exception


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user from JWT token (async)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username = verify_token(token, credentials_exception)

    try:
        # Use async database query
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning(f"User not found in database: {username}")
            raise credentials_exception

        return user

    except Exception as e:
        logger.error(f"Error getting user from database: {str(e)}", exc_info=True)
        raise credentials_exception


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active user (async version)"""
    # Store user ID in request state for logging middleware
    # Note: This will be available in the request context
    return current_user


async def authenticate_user(db: AsyncSession, username: str, password: str):
    """Authenticate user with username and password (async)"""
    try:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            logger.debug(f"Authentication failed: user not found: {username}")
            return False
        if not verify_password(password, user.hashed_password):
            logger.warning(
                f"Authentication failed: invalid password for user: {username}"
            )
            return False

        logger.debug(f"User authenticated successfully: {username}")
        return user

    except Exception as e:
        logger.error(
            f"Error during authentication for user {username}: {str(e)}", exc_info=True
        )
        return False
