"""
API Utilities
Common utilities for API route handlers to reduce duplication
"""
from fastapi import Request, Response
from typing import Optional
import time
import logging

from backend.core.rate_limit import check_rate_limit, get_rate_limit_status
from backend.core.response_formatter import add_rate_limit_headers
from backend.core.error_responses import create_rate_limit_error

logger = logging.getLogger(__name__)


def apply_rate_limiting(request: Request, response: Response, client_id: str):
    """
    Apply rate limiting and add headers to response
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
        client_id: Client identifier (usually user email or IP)
    
    Raises:
        HTTPException: If rate limit exceeded
    """
    if not check_rate_limit(client_id):
        raise create_rate_limit_error(request=request)
    
    rate_limit_status = get_rate_limit_status(client_id)
    add_rate_limit_headers(
        response,
        remaining=rate_limit_status["remaining"],
        reset_at=int(time.time()) + rate_limit_status["reset_in"]
    )


def get_client_id(request: Request, user_email: Optional[str] = None) -> str:
    """
    Get client ID for rate limiting
    
    Args:
        request: FastAPI request object
        user_email: Optional user email (preferred over IP)
    
    Returns:
        Client identifier string
    """
    if user_email:
        return user_email
    
    if request.client:
        return request.client.host
    
    return "anonymous"

