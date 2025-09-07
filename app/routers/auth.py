"""
Async authentication router for user registration, login, and profile management
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_db
from app.core.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.models.models import User
from app.models.schemas import Token, UserRegister, User as UserResponse, UserSimple
from app.core.logging_config import SecurityLogger, AuditLogger, get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/register", response_model=UserSimple, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserRegister, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Register a new user (async)

    - **username**: Unique username
    - **email**: User email address
    - **password**: User password (will be hashed)
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    try:
        # Check if username already exists
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            # Log failed registration attempt
            SecurityLogger.log_registration(
                username=user_data.username,
                email=user_data.email,
                success=False,
                ip_address=client_ip,
                user_agent=user_agent,
                failure_reason="Username already exists",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        # Check if email already exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_email = result.scalar_one_or_none()

        if existing_email:
            # Log failed registration attempt
            SecurityLogger.log_registration(
                username=user_data.username,
                email=user_data.email,
                success=False,
                ip_address=client_ip,
                user_agent=user_agent,
                failure_reason="Email already exists",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        # Log successful registration
        SecurityLogger.log_registration(
            username=user_data.username,
            email=user_data.email,
            success=True,
            ip_address=client_ip,
            user_agent=user_agent,
        )

        # Log audit event
        AuditLogger.log_user_action(
            user_id=str(db_user.id),
            action="user_registered",
            resource="user",
            resource_id=str(db_user.id),
            ip_address=client_ip,
            user_agent=user_agent,
        )

        logger.info(f"New user registered: {user_data.username}")
        return db_user

    except HTTPException:
        # Re-raise HTTP exceptions (they're already logged above)
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(
            f"Unexpected error during user registration for {user_data.username}: {str(e)}",
            extra={
                "username": user_data.username,
                "email": user_data.email,
                "ip_address": client_ip,
                "user_agent": user_agent,
            },
            exc_info=True,
        )

        # Log failed registration
        SecurityLogger.log_registration(
            username=user_data.username,
            email=user_data.email,
            success=False,
            ip_address=client_ip,
            user_agent=user_agent,
            failure_reason=f"Internal error: {type(e).__name__}",
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration",
        )


@router.post("/login", response_model=Token)
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Login user and return JWT token (async)

    - **username**: User's username
    - **password**: User's password
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    try:
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            # Log failed login attempt
            SecurityLogger.log_login_attempt(
                username=form_data.username,
                success=False,
                ip_address=client_ip,
                user_agent=user_agent,
                failure_reason="Invalid credentials",
            )

            logger.warning(f"Failed login attempt for user: {form_data.username}")

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )

        # Log successful login
        SecurityLogger.log_login_attempt(
            username=form_data.username,
            success=True,
            ip_address=client_ip,
            user_agent=user_agent,
        )

        # Log audit event
        AuditLogger.log_user_action(
            user_id=str(user.id),
            action="user_login",
            resource="auth",
            ip_address=client_ip,
            user_agent=user_agent,
        )

        logger.info(f"User logged in successfully: {form_data.username}")

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        # Re-raise HTTP exceptions (they're already logged above)
        raise
    except Exception as e:
        # Log unexpected errors during login
        logger.error(
            f"Unexpected error during login for {form_data.username}: {str(e)}",
            extra={
                "username": form_data.username,
                "ip_address": client_ip,
                "user_agent": user_agent,
            },
            exc_info=True,
        )

        # Log failed login attempt
        SecurityLogger.log_login_attempt(
            username=form_data.username,
            success=False,
            ip_address=client_ip,
            user_agent=user_agent,
            failure_reason=f"Internal error: {type(e).__name__}",
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login",
        )


@router.get("/me", response_model=UserSimple)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user profile (async)

    Requires authentication token
    """
    return current_user


@router.get("/me/tasks")
async def read_user_tasks(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's tasks (async)

    Requires authentication token
    """
    from app.models.schemas import Task as TaskResponse
    from app.models.models import Task
    from typing import List

    result = await db.execute(select(Task).where(Task.user_id == current_user.id))
    tasks = result.scalars().all()
    return tasks
