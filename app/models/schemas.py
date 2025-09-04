from pydantic import BaseModel, field_serializer, field_validator
from datetime import datetime
from typing import Optional
import uuid


# Base schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class UserBase(BaseModel):
    username: str
    email: str  # Changed from EmailStr to str temporarily


# Request schemas (what we receive from the client)
class TaskCreate(TaskBase):
    """Schema for creating a new task"""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task"""

    title: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None  # Accept "done" or "pending"

    @field_validator("state")
    @classmethod
    def validate_state(cls, v):
        """Convert string state to boolean and validate"""
        if v is None:
            return None
        if v not in ["done", "pending"]:
            raise ValueError('State must be either "done" or "pending"')
        return v == "done"  # Convert to boolean: "done" -> True, "pending" -> False


class UserCreate(UserBase):
    """Schema for creating a new user"""

    password: str


# Response schemas (what we send back to the client)
class Task(TaskBase):
    """Schema for task responses"""

    id: uuid.UUID
    state: bool  # Internal field (boolean from database)
    created_at: datetime
    updated_at: datetime
    user_id: uuid.UUID

    class Config:
        from_attributes = True  # This allows Pydantic to work with SQLAlchemy models

    @field_serializer("state")
    def serialize_state(self, state: bool) -> str:
        """Convert boolean state to user-friendly string"""
        return "done" if state else "pending"


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
