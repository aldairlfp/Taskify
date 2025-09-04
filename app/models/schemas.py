from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
import uuid


# Base schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class UserBase(BaseModel):
    username: str
    email: EmailStr


# Request schemas (what we receive from the client)
class TaskCreate(TaskBase):
    """Schema for creating a new task"""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task"""

    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""

    password: str


# Response schemas (what we send back to the client)
class Task(TaskBase):
    """Schema for task responses"""

    id: uuid.UUID
    state: bool
    created_at: datetime
    updated_at: datetime
    user_id: uuid.UUID

    class Config:
        from_attributes = True  # This allows Pydantic to work with SQLAlchemy models


class User(UserBase):
    """Schema for user responses"""

    id: uuid.UUID
    created_at: datetime
    tasks: list[Task] = []

    class Config:
        from_attributes = True


class TaskResponse(Task):
    """Extended task response with owner information"""

    owner: Optional[User] = None


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
