"""
Enhanced Error Handling Utilities
Provides structured error handling, error responses, and error recovery.
"""
from typing import Optional, Dict, Any, List, Callable
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
import logging
import traceback
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error exception"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(APIError):
    """Resource not found error exception"""
    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier}
        )


class UnauthorizedError(APIError):
    """Unauthorized access error exception"""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED"
        )


class ForbiddenError(APIError):
    """Forbidden access error exception"""
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN"
        )


class RateLimitError(APIError):
    """Rate limit exceeded error exception"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


def create_error_response(
    error: Exception,
    include_traceback: bool = False,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Create standardized error response.

    Args:
        error: Exception that occurred
        include_traceback: Whether to include traceback (development only)
        request_id: Optional request ID for tracking

    Returns:
        JSONResponse with error details
    """
    if isinstance(error, APIError):
        status_code = error.status_code
        error_code = error.error_code
        message = error.message
        details = error.details
    elif isinstance(error, HTTPException):
        status_code = error.status_code
        error_code = "HTTP_ERROR"
        message = error.detail
        details = {}
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_code = "INTERNAL_ERROR"
        message = "An internal error occurred"
        details = {}

    response_data = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id
        }
    }

    if details:
        response_data["error"]["details"] = details

    # Include traceback in development
    if include_traceback and status_code >= 500:
        response_data["error"]["traceback"] = traceback.format_exc()

    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


def handle_exception(error: Exception, include_traceback: bool = False) -> JSONResponse:
    """
    Handle exception and return appropriate error response.

    Args:
        error: Exception to handle
        include_traceback: Whether to include traceback

    Returns:
        JSONResponse with error details
    """
    # Log error
    logger.error(f"Exception occurred: {type(error).__name__}: {str(error)}", exc_info=True)

    # Create error response
    return create_error_response(error, include_traceback=include_traceback)


def safe_execute(func: Callable, *args, default: Any = None, **kwargs) -> Any:
    """
    Safely execute a function and return default value on error.

    Args:
        func: Function to execute
        *args: Positional arguments
        default: Default value to return on error
        **kwargs: Keyword arguments

    Returns:
        Function result or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Error in safe_execute: {e}")
        return default


async def safe_execute_async(func: Callable, *args, default: Any = None, **kwargs) -> Any:
    """
    Safely execute an async function and return default value on error.

    Args:
        func: Async function to execute
        *args: Positional arguments
        default: Default value to return on error
        **kwargs: Keyword arguments

    Returns:
        Function result or default value
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Error in safe_execute_async: {e}")
        return default
