"""CSRF protection middleware"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import secrets
import hmac
import hashlib
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF protection using double-submit cookie pattern"""
    
    CSRF_TOKEN_HEADER = "X-CSRF-Token"
    CSRF_COOKIE_NAME = "csrf_token"
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
    
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF check for safe methods
        if request.method in self.SAFE_METHODS:
            response = await call_next(request)
            # Set CSRF cookie for safe methods
            if not request.cookies.get(self.CSRF_COOKIE_NAME):
                csrf_token = secrets.token_urlsafe(32)
                response.set_cookie(
                    self.CSRF_COOKIE_NAME,
                    csrf_token,
                    httponly=False,  # Must be accessible to JavaScript
                    samesite="strict",
                    secure=True,  # HTTPS only
                    max_age=3600 * 24  # 24 hours
                )
            return response
        
        # For state-changing methods, verify CSRF token
        csrf_token_header = request.headers.get(self.CSRF_TOKEN_HEADER)
        csrf_token_cookie = request.cookies.get(self.CSRF_COOKIE_NAME)
        
        if not csrf_token_header or not csrf_token_cookie:
            logger.warning(f"CSRF token missing: header={bool(csrf_token_header)}, cookie={bool(csrf_token_cookie)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing"
            )
        
        # Verify tokens match (constant-time comparison)
        if not hmac.compare_digest(csrf_token_header, csrf_token_cookie):
            logger.warning("CSRF token mismatch")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token mismatch"
            )
        
        # Verify origin header
        origin = request.headers.get("Origin")
        referer = request.headers.get("Referer")
        
        if origin:
            # Validate origin matches expected domain
            # In production, check against allowed origins
            pass
        
        response = await call_next(request)
        return response


def generate_csrf_token() -> str:
    """Generate a new CSRF token"""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, cookie_token: str) -> bool:
    """Verify CSRF token using constant-time comparison"""
    return hmac.compare_digest(token, cookie_token)

