from pydantic import BaseModel, field_serializer, field_validator, model_validator
from datetime import datetime
from typing import Optional, Any, Dict
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

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        """Validate title field"""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("Title must be a string")
            if len(v.strip()) == 0:
                raise ValueError("Title cannot be empty")
            if len(v) > 200:
                raise ValueError("Title cannot exceed 200 characters")
        return v.strip() if v else None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """Validate description field"""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("Description must be a string")
            if len(v) > 1000:
                raise ValueError("Description cannot exceed 1000 characters")
        return v.strip() if v else None

    @field_validator("state")
    @classmethod
    def validate_state(cls, v):
        """Validate state field"""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("State must be a string")
            if v not in ["done", "pending"]:
                raise ValueError('State must be either "done" or "pending"')
        return v

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data: Any) -> Any:
        """Validate that only allowed fields are present"""
        if isinstance(data, dict):
            allowed_fields = {"title", "description", "state"}
            provided_fields = set(data.keys())
            invalid_fields = provided_fields - allowed_fields

            if invalid_fields:
                raise ValueError(
                    f"Invalid field(s): {', '.join(invalid_fields)}. "
                    f"Allowed fields are: {', '.join(allowed_fields)}"
                )
        return data

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "TaskUpdate":
        """Ensure at least one field is provided for update"""
        if all(
            getattr(self, field) is None for field in ["title", "description", "state"]
        ):
            raise ValueError(
                "At least one field (title, description, or state) must be provided for update"
            )
        return self

    class Config:
        """Pydantic configuration"""

        extra = "forbid"  # Forbid extra fields not defined in the model


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
    """JWT Token response"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data"""

    username: Optional[str] = None


class UserLogin(BaseModel):
    """User login credentials"""

    username: str
    password: str


class UserRegister(BaseModel):
    """User registration data"""

    username: str
    email: str
    password: str
