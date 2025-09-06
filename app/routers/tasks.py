from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
import uuid

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.models import Task, User
from app.models.schemas import TaskCreate, TaskUpdate, Task as TaskResponse

# Create router for task endpoints
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new task (async).

    - **title**: Task title (required)
    - **description**: Task description (optional)

    Requires authentication.
    """
    db_task = Task(
        title=task.title, description=task.description, user_id=current_user.id
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


@router.get("/", response_model=List[TaskResponse])
async def read_tasks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve current user's tasks with optional filtering (async).

    - **skip**: Number of tasks to skip (for pagination)
    - **limit**: Maximum number of tasks to return (max 1000 for performance)
    - **state**: Optional filter by state ("done" or "pending")

    Requires authentication. Only returns tasks belonging to the authenticated user.
    """
    # Limit maximum results for performance
    if limit > 1000:
        limit = 1000

    # Build query with user filter
    statement = select(Task).where(Task.user_id == current_user.id)

    # Add ordering for consistent pagination
    statement = statement.order_by(Task.created_at.desc())

    # Apply pagination
    statement = statement.offset(skip).limit(limit)

    # Execute async query
    result = await db.execute(statement)
    tasks = result.scalars().all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def read_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific task by ID (async).

    Requires authentication. Only returns task if it belongs to the authenticated user.
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a task (async).

    - **title**: New task title (optional)
    - **description**: New task description (optional)
    - **state**: Task completion status - "done" or "pending" (optional)

    Requires authentication. Only allows updating tasks that belong to the authenticated user.
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    # Update only the fields that are provided
    task_data = task_update.model_dump(exclude_unset=True)
    for field, value in task_data.items():
        if field == "state" and isinstance(value, str):
            # Convert "done"/"pending" string to boolean
            setattr(task, field, value == "done")
        else:
            setattr(task, field, value)

    # Update the updated_at timestamp
    from datetime import datetime

    task.updated_at = datetime.utcnow()

    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a task (async).

    Requires authentication. Only allows deleting tasks that belong to the authenticated user.
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    await db.delete(task)
    await db.commit()
    return None
