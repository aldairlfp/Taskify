"""
Centralized logging configuration for Taskify application
Provides error logging, audit logging, and request/response logging
"""

import logging
import logging.handlers
import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to console output"""

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        if hasattr(record, "levelname"):
            color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs JSON for structured logging"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "ip_address"):
            log_entry["ip_address"] = record.ip_address
        if hasattr(record, "method"):
            log_entry["method"] = record.method
        if hasattr(record, "url"):
            log_entry["url"] = record.url
        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code
        if hasattr(record, "response_time"):
            log_entry["response_time"] = record.response_time
        if hasattr(record, "action"):
            log_entry["action"] = record.action
        if hasattr(record, "resource"):
            log_entry["resource"] = record.resource
        if hasattr(record, "resource_id"):
            log_entry["resource_id"] = record.resource_id

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging():
    """Set up logging configuration for the application"""

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Changed to DEBUG to capture all levels

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler with colors (INFO and above for console)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Keep console at INFO to avoid noise
    console_formatter = ColoredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler for general application logs (includes DEBUG)
    file_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "app.log", maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    file_handler.setLevel(logging.DEBUG)  # Changed to DEBUG to capture all logs
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Separate DEBUG file handler for detailed debugging
    debug_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "debug.log", maxBytes=10 * 1024 * 1024, backupCount=3  # 10MB
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(funcName)s:%(lineno)d]",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    debug_handler.setFormatter(debug_formatter)
    root_logger.addHandler(debug_handler)

    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "errors.log", maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]\n%(exc_text)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)


def setup_audit_logger():
    """Set up audit logger for user actions"""
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False  # Don't propagate to root logger

    # Clear existing handlers
    audit_logger.handlers.clear()

    # Audit file handler with JSON formatting
    audit_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "audit.log", maxBytes=10 * 1024 * 1024, backupCount=10  # 10MB
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(JsonFormatter())
    audit_logger.addHandler(audit_handler)

    return audit_logger


def setup_security_logger():
    """Set up security logger for authentication and authorization events"""
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = False  # Don't propagate to root logger

    # Clear existing handlers
    security_logger.handlers.clear()

    # Security file handler with JSON formatting
    security_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "security.log", maxBytes=10 * 1024 * 1024, backupCount=10  # 10MB
    )
    security_handler.setLevel(logging.INFO)
    security_handler.setFormatter(JsonFormatter())
    security_logger.addHandler(security_handler)

    return security_logger


def setup_access_logger():
    """Set up access logger for HTTP requests"""
    access_logger = logging.getLogger("access")
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False  # Don't propagate to root logger

    # Clear existing handlers
    access_logger.handlers.clear()

    # Access file handler with JSON formatting
    access_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "access.log", maxBytes=10 * 1024 * 1024, backupCount=10  # 10MB
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(JsonFormatter())
    access_logger.addHandler(access_handler)

    return access_logger


# Initialize loggers
audit_logger = setup_audit_logger()
security_logger = setup_security_logger()
access_logger = setup_access_logger()


class AuditLogger:
    """Helper class for audit logging"""

    @staticmethod
    def log_user_action(
        user_id: str,
        action: str,
        resource: str = None,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        user_agent: str = None,
    ):
        """Log user actions for audit purposes"""
        extra = {
            "user_id": user_id,
            "action": action,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        if resource:
            extra["resource"] = resource
        if resource_id:
            extra["resource_id"] = resource_id
        if details:
            extra.update(details)

        audit_logger.info(f"User {user_id} performed action: {action}", extra=extra)


class SecurityLogger:
    """Helper class for security logging"""

    @staticmethod
    def log_login_attempt(
        username: str,
        success: bool,
        ip_address: str = None,
        user_agent: str = None,
        failure_reason: str = None,
    ):
        """Log login attempts"""
        extra = {
            "action": "login_attempt",
            "username": username,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        if failure_reason and not success:
            extra["failure_reason"] = failure_reason

        message = f"Login {'successful' if success else 'failed'} for user: {username}"
        if not success and failure_reason:
            message += f" - Reason: {failure_reason}"

        security_logger.info(message, extra=extra)

    @staticmethod
    def log_registration(
        username: str,
        email: str,
        success: bool,
        ip_address: str = None,
        user_agent: str = None,
        failure_reason: str = None,
    ):
        """Log user registration attempts"""
        extra = {
            "action": "user_registration",
            "username": username,
            "email": email,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        if failure_reason and not success:
            extra["failure_reason"] = failure_reason

        message = (
            f"User registration {'successful' if success else 'failed'} for: {username}"
        )
        if not success and failure_reason:
            message += f" - Reason: {failure_reason}"

        security_logger.info(message, extra=extra)

    @staticmethod
    def log_unauthorized_access(
        path: str, ip_address: str = None, user_agent: str = None, user_id: str = None
    ):
        """Log unauthorized access attempts"""
        extra = {
            "action": "unauthorized_access",
            "path": path,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        if user_id:
            extra["user_id"] = user_id

        security_logger.warning(f"Unauthorized access attempt to: {path}", extra=extra)


class AccessLogger:
    """Helper class for access logging"""

    @staticmethod
    def log_request(
        method: str,
        url: str,
        status_code: int,
        response_time: float,
        ip_address: str = None,
        user_agent: str = None,
        user_id: str = None,
        request_id: str = None,
    ):
        """Log HTTP requests"""
        extra = {
            "method": method,
            "url": url,
            "status_code": status_code,
            "response_time": response_time,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        if user_id:
            extra["user_id"] = user_id
        if request_id:
            extra["request_id"] = request_id

        access_logger.info(
            f"{method} {url} - {status_code} - {response_time:.4f}s", extra=extra
        )
