"""
Logging middleware for request/response tracking and performance monitoring
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging_config import AccessLogger, get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses"""

    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        # Paths to exclude from logging (e.g., health checks)
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/favicon.ico"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Extract request information
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        url = str(request.url)

        # Start timing
        start_time = time.time()

        # Log request start
        logger.info(
            f"Request started: {method} {url}",
            extra={
                "request_id": request_id,
                "method": method,
                "url": url,
                "ip_address": client_ip,
                "user_agent": user_agent,
                "event": "request_start",
            },
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate response time
            response_time = time.time() - start_time

            # Get user ID if available (from auth)
            user_id = getattr(request.state, "user_id", None)

            # Try to extract user ID from token if not already set
            if not user_id:
                auth_header = request.headers.get("authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    try:
                        from app.core.auth import verify_token
                        from fastapi import HTTPException, status

                        token = auth_header.split(" ")[1]
                        credentials_exception = HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",
                        )
                        username = verify_token(token, credentials_exception)
                        if username:
                            # We have the username, could get user_id from DB but
                            # that would be expensive in middleware
                            user_id = username  # Use username as identifier for now
                    except Exception:
                        pass  # Invalid token, continue without user_id

            # Log successful response
            AccessLogger.log_request(
                method=method,
                url=url,
                status_code=response.status_code,
                response_time=response_time,
                ip_address=client_ip,
                user_agent=user_agent,
                user_id=user_id,
                request_id=request_id,
            )

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{response_time:.4f}"

            return response

        except Exception as e:
            # Calculate response time even for errors
            response_time = time.time() - start_time

            # Log error
            logger.error(
                f"Request failed: {method} {url} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "ip_address": client_ip,
                    "user_agent": user_agent,
                    "response_time": response_time,
                    "event": "request_error",
                    "exception_type": type(e).__name__,
                },
                exc_info=True,
            )

            # Re-raise the exception to be handled by exception handlers
            raise

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request headers"""
        # Check for forwarded headers (common in load balancers/proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        if request.client:
            return request.client.host

        return "unknown"


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and slow query detection"""

    def __init__(self, app, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold  # seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        response_time = time.time() - start_time

        # Log slow requests
        if response_time > self.slow_request_threshold:
            logger.warning(
                f"Slow request detected: {request.method} {request.url} took {response_time:.4f}s",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "event": "slow_request",
                    "threshold": self.slow_request_threshold,
                },
            )

        return response
