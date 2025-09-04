from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
import uuid

from app.core.database import get_db
from app.models.models import Task, User
from app.models.schemas import TaskCreate, TaskUpdate, Task as TaskResponse

# Create router for task endpoints
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)

# Temporary user ID for testing (until we add authentication)
TEMP_USER_ID = uuid.uuid4()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task.

    - **title**: Task title (required)
    - **description**: Task description (optional)
    """
    # For now, we'll create a temporary user if it doesn't exist
    # In a real app, this would come from authentication
    user = db.exec(select(User).where(User.id == TEMP_USER_ID)).first()
    if not user:
        temp_user = User(
            id=TEMP_USER_ID,
            username="testuser",
            email="test@example.com",
            hashed_password="temp_password",
        )
        db.add(temp_user)
        db.commit()
        db.refresh(temp_user)
        user = temp_user

    db_task = Task(title=task.title, description=task.description, user_id=user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/", response_model=List[TaskResponse])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve tasks.

    - **skip**: Number of tasks to skip (for pagination)
    - **limit**: Maximum number of tasks to return
    """
    statement = select(Task).offset(skip).limit(limit)
    tasks = db.exec(statement).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Get a specific task by ID.
    """
    task = db.exec(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: uuid.UUID, task_update: TaskUpdate, db: Session = Depends(get_db)
):
    """
    Update a task.

    - **title**: New task title (optional)
    - **description**: New task description (optional)
    - **state**: Task completion status (optional)
    """
    task = db.exec(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    # Update only the fields that are provided
    task_data = task_update.model_dump(exclude_unset=True)
    for field, value in task_data.items():
        setattr(task, field, value)

    # Update the updated_at timestamp
    from datetime import datetime

    task.updated_at = datetime.utcnow()

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Delete a task.
    """
    task = db.exec(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    db.delete(task)
    db.commit()
    return None
