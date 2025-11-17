"""
Response Utilities
Provides utilities for creating standardized API responses.
"""
from typing import Optional, Dict, Any, List
from fastapi.responses import JSONResponse
from datetime import datetime
import json


def create_success_response(
    data: Any,
    message: Optional[str] = None,
    status_code: int = 200,
    metadata: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create a standardized success response.

    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code
        metadata: Optional metadata dictionary

    Returns:
        JSONResponse with success format

    Example:
        ```python
        return create_success_response(
            data={"user_id": 123},
            message="User created successfully",
            status_code=201
        )
        ```
    """
    response_data = {
        "success": True,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }

    if message:
        response_data["message"] = message

    if metadata:
        response_data["metadata"] = metadata

    return JSONResponse(status_code=status_code, content=response_data)


def create_paginated_response(
    items: List[Any],
    total: int,
    limit: int,
    offset: int,
    metadata: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create a standardized paginated response.

    Args:
        items: List of items
        total: Total number of items
        limit: Items per page
        offset: Offset for pagination
        metadata: Optional metadata dictionary

    Returns:
        JSONResponse with paginated format

    Example:
        ```python
        return create_paginated_response(
            items=signals,
            total=100,
            limit=10,
            offset=0
        )
        ```
    """
    has_more = (offset + limit) < total

    response_data = {
        "success": True,
        "data": {
            "items": items,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": has_more,
                "page": (offset // limit) + 1 if limit > 0 else 1,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 1
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    if metadata:
        response_data["metadata"] = metadata

    return JSONResponse(status_code=200, content=response_data)


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        error_code: Error code (e.g., "VALIDATION_ERROR")
        message: Error message
        status_code: HTTP status code
        details: Optional error details
        request_id: Optional request ID for tracking

    Returns:
        JSONResponse with error format

    Example:
        ```python
        return create_error_response(
            error_code="VALIDATION_ERROR",
            message="Invalid email format",
            status_code=400,
            details={"field": "email"}
        )
        ```
    """
    response_data = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    }

    if details:
        response_data["error"]["details"] = details

    if request_id:
        response_data["error"]["request_id"] = request_id

    return JSONResponse(status_code=status_code, content=response_data)


def create_validation_error_response(
    errors: List[Dict[str, str]],
    status_code: int = 400
) -> JSONResponse:
    """
    Create a standardized validation error response.

    Args:
        errors: List of validation errors with 'field' and 'message'
        status_code: HTTP status code

    Returns:
        JSONResponse with validation error format

    Example:
        ```python
        return create_validation_error_response([
            {"field": "email", "message": "Invalid email format"},
            {"field": "password", "message": "Password too short"}
        ])
        ```
    """
    return create_error_response(
        error_code="VALIDATION_ERROR",
        message="Validation failed",
        status_code=status_code,
        details={"errors": errors}
    )


def add_response_headers(
    response: JSONResponse,
    headers: Dict[str, str]
) -> JSONResponse:
    """
    Add custom headers to response.

    Args:
        response: JSONResponse object
        headers: Dictionary of headers to add

    Returns:
        Response with added headers
    """
    for key, value in headers.items():
        response.headers[key] = value

    return response


def format_datetime_for_response(dt: datetime) -> str:
    """
    Format datetime for API response (ISO 8601).

    Args:
        dt: Datetime object

    Returns:
        ISO 8601 formatted string
    """
    return dt.isoformat() if dt else None


def serialize_response_data(data: Any) -> Any:
    """
    Serialize response data (handle datetime, etc.).

    Args:
        data: Data to serialize

    Returns:
        Serialized data
    """
    if isinstance(data, datetime):
        return format_datetime_for_response(data)
    elif isinstance(data, dict):
        return {k: serialize_response_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_response_data(item) for item in data]
    elif hasattr(data, '__dict__'):
        # Handle SQLAlchemy models
        return serialize_response_data(data.__dict__)
    else:
        return data
