"""Standardized response formatting"""
from fastapi import Response
from typing import Optional, Dict, Any
from datetime import datetime
from backend.core.request_tracking import get_request_id
from fastapi import Request


def format_error_response(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> Dict[str, Any]:
    """
    Format standardized error response
    
    Args:
        status_code: HTTP status code
        message: Error message
        details: Additional error details
        request: FastAPI request object
    
    Returns:
        Formatted error response
    """
    response = {
        "error": {
            "code": status_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    if request:
        request_id = get_request_id(request)
        response["error"]["request_id"] = request_id
    
    return response


def add_rate_limit_headers(
    response: Response,
    remaining: int,
    reset_at: Optional[int] = None
) -> Response:
    """
    Add rate limit headers to response
    
    Args:
        response: FastAPI response object
        remaining: Remaining requests in window
        reset_at: Unix timestamp when rate limit resets
    
    Returns:
        Response with rate limit headers
    """
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    if reset_at:
        response.headers["X-RateLimit-Reset"] = str(reset_at)
    return response


def format_paginated_response(
    items: list,
    total: int,
    limit: int,
    offset: int,
    request: Optional[Request] = None
) -> Dict[str, Any]:
    """
    Format standardized paginated response
    
    Args:
        items: List of items
        total: Total number of items
        limit: Items per page
        offset: Offset for pagination
        request: FastAPI request object
    
    Returns:
        Formatted paginated response
    """
    response = {
        "items": items,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
            "page": (offset // limit) + 1 if limit > 0 else 1,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 1
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    if request:
        request_id = get_request_id(request)
        response["request_id"] = request_id
    
    return response

