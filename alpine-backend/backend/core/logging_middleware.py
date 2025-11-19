"""
Logging Middleware
Provides request/response logging, performance tracking, and error logging.
"""
import time
import logging
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    Logs:
    - Request method, path, query parameters
    - Response status code
    - Request duration
    - Error details (if any)
    """

    def __init__(self, app: ASGIApp, log_request_body: bool = False, log_response_body: bool = False):
        """
        Initialize logging middleware.

        Args:
            app: ASGI application
            log_request_body: Whether to log request body (default: False for security)
            log_response_body: Whether to log response body (default: False for performance)
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details"""
        start_time = time.time()

        # Extract request details
        method = request.method
        path = str(request.url.path)
        query_params = dict(request.query_params)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Log request
        logger.info(
            f"Request: {method} {path} | "
            f"IP: {client_ip} | "
            f"Query: {query_params if query_params else 'none'}"
        )

        # Log request body if enabled (be careful with sensitive data)
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8')[:500]  # Limit length
                    logger.debug(f"Request body: {body_str}")
            except Exception as e:
                logger.warning(f"Could not log request body: {e}")

        # Process request
        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Log response
            status_code = response.status_code
            logger.info(
                f"Response: {method} {path} | "
                f"Status: {status_code} | "
                f"Duration: {duration:.3f}s | "
                f"IP: {client_ip}"
            )

            # Log slow requests
            if duration > 1.0:
                logger.warning(
                    f"Slow request: {method} {path} took {duration:.3f}s | "
                    f"Status: {status_code}"
                )

            # Add performance header
            response.headers["X-Response-Time"] = f"{duration:.3f}"

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request error: {method} {path} | "
                f"Error: {str(e)} | "
                f"Duration: {duration:.3f}s | "
                f"IP: {client_ip}",
                exc_info=True
            )
            raise


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging errors with detailed context.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log errors"""
        try:
            response = await call_next(request)

            # Log error responses
            if response.status_code >= 400:
                from backend.core.request_tracking import get_request_id
                request_id = get_request_id(request)
                logger.warning(
                    f"Error response: {request.method} {request.url.path} | "
                    f"Status: {response.status_code} | "
                    f"IP: {request.client.host if request.client else 'unknown'}",
                    extra={
                        "path": request.url.path,
                        "method": request.method,
                        "status_code": response.status_code,
                        "client_ip": request.client.host if request.client else "unknown",
                        "request_id": request_id,
                    }
                )

            return response

        except Exception as e:
            from backend.core.request_tracking import get_request_id
            request_id = get_request_id(request)
            logger.error(
                f"Unhandled exception: {request.method} {request.url.path} | "
                f"Error: {type(e).__name__}: {str(e)} | "
                f"IP: {request.client.host if request.client else 'unknown'}",
                exc_info=True,
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "client_ip": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "request_id": request_id,
                    "exception_type": type(e).__name__,
                }
            )
            raise


def setup_logging_middleware(app: ASGIApp, log_request_body: bool = False) -> ASGIApp:
    """
    Setup logging middleware for FastAPI application.

    Args:
        app: FastAPI application
        log_request_body: Whether to log request bodies

    Returns:
        Application with middleware added
    """
    app.add_middleware(
        RequestLoggingMiddleware,
        log_request_body=log_request_body,
        log_response_body=False  # Don't log response bodies for performance
    )
    app.add_middleware(ErrorLoggingMiddleware)

    return app


def log_api_call(
    endpoint: str,
    method: str,
    user_id: Optional[int] = None,
    duration: Optional[float] = None,
    status_code: Optional[int] = None,
    error: Optional[str] = None
):
    """
    Log API call with structured information.

    Args:
        endpoint: API endpoint path
        method: HTTP method
        user_id: User ID (if authenticated)
        duration: Request duration in seconds
        status_code: HTTP status code
        error: Error message (if any)
    """
    log_data = {
        "endpoint": endpoint,
        "method": method,
        "user_id": user_id,
        "duration": duration,
        "status_code": status_code,
        "error": error
    }

    if error:
        logger.error(f"API call failed: {json.dumps(log_data)}")
    elif status_code and status_code >= 400:
        logger.warning(f"API call error: {json.dumps(log_data)}")
    else:
        logger.info(f"API call: {json.dumps(log_data)}")
