"""Standardized error response format"""
from fastapi import HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.core.request_tracking import get_request_id
from fastapi import Request


class ErrorDetail(BaseModel):
    """Error detail model"""
    code: str
    message: str
    type: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standardized error response"""
    error: ErrorDetail
    request_id: Optional[str] = None


# Error code registry
class ErrorCodes:
    """Standard error codes"""
    # Authentication errors (AUTH_xxx)
    AUTH_001 = "AUTH_001"  # Invalid or expired token
    AUTH_002 = "AUTH_002"  # Token blacklisted
    AUTH_003 = "AUTH_003"  # Invalid credentials
    AUTH_004 = "AUTH_004"  # Account locked
    AUTH_005 = "AUTH_005"  # Account inactive
    AUTH_006 = "AUTH_006"  # 2FA required
    AUTH_007 = "AUTH_007"  # 2FA verification failed
    
    # Authorization errors (AUTHZ_xxx)
    AUTHZ_001 = "AUTHZ_001"  # Insufficient permissions
    AUTHZ_002 = "AUTHZ_002"  # Admin access required
    AUTHZ_003 = "AUTHZ_003"  # Resource ownership required
    AUTHZ_004 = "AUTHZ_004"  # Role not found
    
    # Validation errors (VALIDATION_xxx)
    VALIDATION_001 = "VALIDATION_001"  # Invalid input format
    VALIDATION_002 = "VALIDATION_002"  # Missing required field
    VALIDATION_003 = "VALIDATION_003"  # Value out of range
    VALIDATION_004 = "VALIDATION_004"  # Invalid email format
    VALIDATION_005 = "VALIDATION_005"  # Invalid symbol format
    VALIDATION_006 = "VALIDATION_006"  # Password too weak
    
    # Rate limiting (RATE_xxx)
    RATE_001 = "RATE_001"  # Rate limit exceeded
    
    # CSRF errors (CSRF_xxx)
    CSRF_001 = "CSRF_001"  # CSRF token missing
    CSRF_002 = "CSRF_002"  # CSRF token mismatch
    CSRF_003 = "CSRF_003"  # Origin not allowed
    
    # Resource errors (RESOURCE_xxx)
    RESOURCE_001 = "RESOURCE_001"  # Resource not found
    RESOURCE_002 = "RESOURCE_002"  # Resource already exists
    RESOURCE_003 = "RESOURCE_003"  # Resource conflict
    
    # Server errors (SERVER_xxx)
    SERVER_001 = "SERVER_001"  # Internal server error
    SERVER_002 = "SERVER_002"  # Service unavailable
    SERVER_003 = "SERVER_003"  # Database error
    SERVER_004 = "SERVER_004"  # External service error
    
    # Request errors (REQUEST_xxx)
    REQUEST_001 = "REQUEST_001"  # Request body too large
    REQUEST_002 = "REQUEST_002"  # Invalid content type
    REQUEST_003 = "REQUEST_003"  # Malformed request


# Error type mapping
ERROR_TYPES = {
    "AUTH": "authentication_error",
    "AUTHZ": "authorization_error",
    "VALIDATION": "validation_error",
    "RATE": "rate_limit_error",
    "CSRF": "csrf_error",
    "RESOURCE": "resource_error",
    "SERVER": "server_error",
    "REQUEST": "request_error",
}


def get_error_type(code: str) -> str:
    """Get error type from error code"""
    prefix = code.split("_")[0]
    return ERROR_TYPES.get(prefix, "unknown_error")


def create_error_response(
    code: str,
    message: str,
    status_code: int = 400,
    field: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> HTTPException:
    """Create standardized error response"""
    request_id = get_request_id(request) if request else None
    
    error_detail = ErrorDetail(
        code=code,
        message=message,
        type=get_error_type(code),
        field=field,
        details=details
    )
    
    error_response = ErrorResponse(
        error=error_detail,
        request_id=request_id
    )
    
    return HTTPException(
        status_code=status_code,
        detail=error_response.model_dump()
    )


def format_error_response(
    code: str,
    message: str,
    status_code: int = 400,
    field: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> Dict[str, Any]:
    """Format error response as dictionary"""
    request_id = get_request_id(request) if request else None
    
    return {
        "error": {
            "code": code,
            "message": message,
            "type": get_error_type(code),
            "field": field,
            "details": details
        },
        "request_id": request_id
    }


def create_rate_limit_error(request: Optional[Request] = None, max_requests: int = 100) -> HTTPException:
    """Create standardized rate limit error"""
    return create_error_response(
        ErrorCodes.RATE_001,
        f"Rate limit exceeded. Maximum {max_requests} requests per minute.",
        status_code=429,
        request=request
    )

