from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
import uuid

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.models import Task, User
from app.models.schemas import TaskCreate, TaskUpdate, Task as TaskResponse
from app.core.logging_config import AuditLogger, get_logger

logger = get_logger(__name__)

# Create router for task endpoints
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new task (async).

    - **title**: Task title (required)
    - **description**: Task description (optional)

    Requires authentication.
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    try:
        db_task = Task(
            title=task.title, description=task.description, user_id=current_user.id
        )
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)

        # Log audit event
        AuditLogger.log_user_action(
            user_id=str(current_user.id),
            action="task_created",
            resource="task",
            resource_id=str(db_task.id),
            details={"title": task.title, "description": task.description},
            ip_address=client_ip,
            user_agent=user_agent,
        )

        logger.info(f"Task created by user {current_user.username}: {db_task.title}")
        return db_task

    except Exception as e:
        logger.error(
            f"Error creating task for user {current_user.username}: {str(e)}",
            extra={
                "user_id": str(current_user.id),
                "task_title": task.title,
                "ip_address": client_ip,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating task",
        )


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

    Requires authentication. Only returns tasks belonging to the authenticated user.
    """
    # Limit maximum results for performance
    if limit > 1000:
        limit = 1000

    try:
        # Build query with user filter
        statement = select(Task).where(Task.user_id == current_user.id)

        # Add ordering for consistent pagination
        statement = statement.order_by(Task.created_at.desc())

        # Apply pagination
        statement = statement.offset(skip).limit(limit)

        # Execute async query
        result = await db.execute(statement)
        tasks = result.scalars().all()

        logger.debug(f"Retrieved {len(tasks)} tasks for user {current_user.username}")
        return tasks

    except Exception as e:
        logger.error(
            f"Error retrieving tasks for user {current_user.username}: {str(e)}",
            extra={"user_id": str(current_user.id)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving tasks",
        )


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
    try:
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        )
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(
                f"User {current_user.username} tried to access non-existent task: {task_id}",
                extra={"user_id": str(current_user.id), "task_id": str(task_id)},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving task {task_id} for user {current_user.username}: {str(e)}",
            extra={"user_id": str(current_user.id), "task_id": str(task_id)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving task",
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    task_update: TaskUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a task (async).

    - **title**: New task title (optional)
    - **description**: New task description (optional)
    - **is_done**: New completion status (optional)

    Requires authentication. Only updates task if it belongs to the authenticated user.
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    try:
        # Find task
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        )
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(
                f"User {current_user.username} tried to update non-existent task: {task_id}",
                extra={
                    "user_id": str(current_user.id),
                    "task_id": str(task_id),
                    "ip_address": client_ip,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        # Store original values for audit
        original_values = {
            "title": task.title,
            "description": task.description,
            "is_done": task.is_done,
        }

        # Update task fields
        if task_update.title is not None:
            task.title = task_update.title
        if task_update.description is not None:
            task.description = task_update.description
        if task_update.is_done is not None:
            task.is_done = task_update.is_done

        await db.commit()
        await db.refresh(task)

        # Prepare change details for audit
        changes = {}
        if (
            task_update.title is not None
            and task_update.title != original_values["title"]
        ):
            changes["title"] = {
                "from": original_values["title"],
                "to": task_update.title,
            }
        if (
            task_update.description is not None
            and task_update.description != original_values["description"]
        ):
            changes["description"] = {
                "from": original_values["description"],
                "to": task_update.description,
            }
        if (
            task_update.is_done is not None
            and task_update.is_done != original_values["is_done"]
        ):
            changes["is_done"] = {
                "from": original_values["is_done"],
                "to": task_update.is_done,
            }

        # Log audit event
        AuditLogger.log_user_action(
            user_id=str(current_user.id),
            action="task_updated",
            resource="task",
            resource_id=str(task.id),
            details={"changes": changes, "task_title": task.title},
            ip_address=client_ip,
            user_agent=user_agent,
        )

        logger.info(
            f"Task updated by user {current_user.username}: {task.title}",
            extra={"changes": changes},
        )
        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating task {task_id} for user {current_user.username}: {str(e)}",
            extra={
                "user_id": str(current_user.id),
                "task_id": str(task_id),
                "ip_address": client_ip,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating task",
        )


@router.delete("/{task_id}")
async def delete_task(
    task_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a task (async).

    Requires authentication. Only allows deleting tasks that belong to the authenticated user.
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    try:
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        )
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(
                f"User {current_user.username} tried to delete non-existent task: {task_id}",
                extra={
                    "user_id": str(current_user.id),
                    "task_id": str(task_id),
                    "ip_address": client_ip,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        # Store task info for audit before deletion
        task_info = {
            "title": task.title,
            "description": task.description,
            "is_done": task.is_done,
        }

        await db.delete(task)
        await db.commit()

        # Log audit event
        AuditLogger.log_user_action(
            user_id=str(current_user.id),
            action="task_deleted",
            resource="task",
            resource_id=str(task_id),
            details=task_info,
            ip_address=client_ip,
            user_agent=user_agent,
        )

        logger.info(
            f"Task deleted by user {current_user.username}: {task_info['title']}"
        )
        return {"message": "Task deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting task {task_id} for user {current_user.username}: {str(e)}",
            extra={
                "user_id": str(current_user.id),
                "task_id": str(task_id),
                "ip_address": client_ip,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting task",
        )
