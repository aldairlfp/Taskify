from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid


class User(SQLModel, table=True):
    """
    User model - represents users in our system
    Each user can have multiple tasks
    """

    __tablename__ = "users"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    email: str = Field(max_length=100, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with tasks
    tasks: List["Task"] = Relationship(back_populates="owner")


class Task(SQLModel, table=True):
    """
    Task model - represents a TODO item
    Each task belongs to a user
    Optimized for large data volumes with proper indexing
    """

    __tablename__ = "tasks"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=200, index=True)  # Index for search performance
    description: Optional[str] = Field(default=None, max_length=1000)
    state: bool = Field(default=False, index=True)  # Index for filtering by state
    created_at: datetime = Field(
        default_factory=datetime.utcnow, index=True
    )  # Index for ordering
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign key to users table with index for performance
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    # Relationship with user
    owner: Optional[User] = Relationship(back_populates="tasks")
