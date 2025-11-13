"""Security event logging"""
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request
import traceback

# Create security logger
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Create file handler for security logs
    # Ensure logs directory exists
    import os
    os.makedirs("logs", exist_ok=True)
    handler = logging.FileHandler("logs/security.log")
handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
security_logger.addHandler(handler)


class SecurityEvent:
    """Security event types"""
    FAILED_LOGIN = "failed_login"
    SUCCESSFUL_LOGIN = "successful_login"
    ACCOUNT_LOCKED = "account_locked"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    TOKEN_BLACKLISTED = "token_blacklisted"
    ADMIN_ACTION = "admin_action"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    CSRF_VIOLATION = "csrf_violation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_DELETED = "account_deleted"


def log_security_event(
    event_type: str,
    user_id: Optional[int] = None,
    email: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
):
    """
    Log a security event
    
    Args:
        event_type: Type of security event
        user_id: User ID (if applicable)
        email: User email (if applicable)
        ip_address: Client IP address
        user_agent: User agent string
        details: Additional event details
        request: FastAPI request object (for extracting IP, user agent)
    """
    if request:
        ip_address = ip_address or request.client.host if request.client else None
        user_agent = user_agent or request.headers.get("User-Agent")
    
    event_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "email": email,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "details": details or {}
    }
    
    security_logger.info(json.dumps(event_data))


def log_failed_login(email: str, ip_address: Optional[str] = None, request: Optional[Request] = None):
    """Log failed login attempt"""
    log_security_event(
        SecurityEvent.FAILED_LOGIN,
        email=email,
        ip_address=ip_address,
        request=request,
        details={"reason": "invalid_credentials"}
    )


def log_successful_login(user_id: int, email: str, ip_address: Optional[str] = None, request: Optional[Request] = None):
    """Log successful login"""
    log_security_event(
        SecurityEvent.SUCCESSFUL_LOGIN,
        user_id=user_id,
        email=email,
        ip_address=ip_address,
        request=request
    )


def log_account_locked(email: str, ip_address: Optional[str] = None, request: Optional[Request] = None):
    """Log account lockout"""
    log_security_event(
        SecurityEvent.ACCOUNT_LOCKED,
        email=email,
        ip_address=ip_address,
        request=request,
        details={"reason": "too_many_failed_attempts"}
    )


def log_rate_limit_exceeded(client_id: str, endpoint: str, ip_address: Optional[str] = None, request: Optional[Request] = None):
    """Log rate limit violation"""
    log_security_event(
        SecurityEvent.RATE_LIMIT_EXCEEDED,
        email=client_id if "@" in client_id else None,
        ip_address=ip_address,
        request=request,
        details={"endpoint": endpoint, "client_id": client_id}
    )


def log_admin_action(admin_id: int, admin_email: str, action: str, target: Optional[str] = None, request: Optional[Request] = None):
    """Log admin action"""
    log_security_event(
        SecurityEvent.ADMIN_ACTION,
        user_id=admin_id,
        email=admin_email,
        request=request,
        details={"action": action, "target": target}
    )


def log_csrf_violation(ip_address: Optional[str] = None, request: Optional[Request] = None):
    """Log CSRF violation"""
    log_security_event(
        SecurityEvent.CSRF_VIOLATION,
        ip_address=ip_address,
        request=request,
        details={"reason": "token_mismatch_or_missing"}
    )


def log_unauthorized_access(user_id: Optional[int], email: Optional[str], resource: str, request: Optional[Request] = None):
    """Log unauthorized access attempt"""
    log_security_event(
        SecurityEvent.UNAUTHORIZED_ACCESS,
        user_id=user_id,
        email=email,
        request=request,
        details={"resource": resource, "reason": "insufficient_permissions"}
    )

