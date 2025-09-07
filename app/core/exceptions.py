"""
Custom exception handlers for production error handling
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
from typing import Union
import uuid

from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with detailed logging"""
    error_id = str(uuid.uuid4())
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Log with contextual information
    logger.warning(
        f"HTTP {exc.status_code} error at {request.url}: {exc.detail}",
        extra={
            "error_id": error_id,
            "status_code": exc.status_code,
            "method": request.method,
            "url": str(request.url),
            "ip_address": client_ip,
            "user_agent": user_agent,
            "error_detail": exc.detail,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_id": error_id,
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": time.time(),
            "path": str(request.url),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with user-friendly messages"""
    error_id = str(uuid.uuid4())
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Log validation errors with context
    logger.warning(
        f"Validation error at {request.url}: {exc.errors()}",
        extra={
            "error_id": error_id,
            "method": request.method,
            "url": str(request.url),
            "ip_address": client_ip,
            "user_agent": user_agent,
            "validation_errors": exc.errors(),
        },
    )

    # Format validation errors in a user-friendly way
    errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        errors.append(
            {"field": field_path, "message": error["msg"], "type": error["type"]}
        )

    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "error_id": error_id,
            "status_code": 422,
            "message": "Validation failed",
            "details": errors,
            "timestamp": time.time(),
            "path": str(request.url),
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors with logging"""
    error_id = str(uuid.uuid4())
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Log critical errors with full context
    logger.error(
        f"Unexpected error at {request.url}: {str(exc)}",
        extra={
            "error_id": error_id,
            "method": request.method,
            "url": str(request.url),
            "ip_address": client_ip,
            "user_agent": user_agent,
            "exception_type": type(exc).__name__,
        },
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "error_id": error_id,
            "status_code": 500,
            "message": "Internal server error",
            "timestamp": time.time(),
            "path": str(request.url),
        },
    )


async def starlette_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle Starlette HTTP exceptions"""
    error_id = str(uuid.uuid4())
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    logger.warning(
        f"Starlette HTTP {exc.status_code} error at {request.url}",
        extra={
            "error_id": error_id,
            "status_code": exc.status_code,
            "method": request.method,
            "url": str(request.url),
            "ip_address": client_ip,
            "user_agent": user_agent,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_id": error_id,
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": time.time(),
            "path": str(request.url),
        },
    )
