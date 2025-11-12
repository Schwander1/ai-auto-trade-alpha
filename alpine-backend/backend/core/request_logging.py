"""Request/response logging with PII redaction"""
import logging
import json
import re
from typing import Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from backend.core.request_tracking import get_request_id

logger = logging.getLogger(__name__)

# PII patterns to redact
PII_PATTERNS = [
    (r'password["\']?\s*[:=]\s*["\']?([^"\',}\s]+)', r'password": "[REDACTED]"'),
    (r'token["\']?\s*[:=]\s*["\']?([^"\',}\s]+)', r'token": "[REDACTED]"'),
    (r'authorization["\']?\s*[:=]\s*["\']?([^"\',}\s]+)', r'authorization": "[REDACTED]"'),
    (r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\',}\s]+)', r'api_key": "[REDACTED]"'),
    (r'secret["\']?\s*[:=]\s*["\']?([^"\',}\s]+)', r'secret": "[REDACTED]"'),
    (r'email["\']?\s*[:=]\s*["\']?([^"\',}\s@]+@[^"\',}\s]+)', r'email": "[REDACTED_EMAIL]"'),
    (r'credit[_-]?card["\']?\s*[:=]\s*["\']?(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})', r'credit_card": "[REDACTED]"'),
    (r'card[_-]?number["\']?\s*[:=]\s*["\']?(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})', r'card_number": "[REDACTED]"'),
]


def redact_pii(text: str) -> str:
    """Redact PII from text"""
    redacted = text
    for pattern, replacement in PII_PATTERNS:
        redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)
    return redacted


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log requests and responses with PII redaction"""
    
    async def dispatch(self, request: Request, call_next: ASGIApp):
        request_id = get_request_id(request)
        
        # Log request
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        
        # Redact PII from query params
        request_info_str = json.dumps(request_info, default=str)
        request_info_str = redact_pii(request_info_str)
        
        logger.info(f"Request: {request_info_str}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        response_info = {
            "request_id": request_id,
            "status_code": response.status_code,
            "path": request.url.path,
        }
        
        # Only log response body for errors (and redact PII)
        if response.status_code >= 400:
            try:
                # Try to get response body (may not always be available)
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                
                if body:
                    body_str = body.decode('utf-8', errors='ignore')
                    body_str = redact_pii(body_str)
                    response_info["body"] = body_str[:500]  # Limit length
                
                # Recreate response with body
                from starlette.responses import Response as StarletteResponse
                response = StarletteResponse(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
            except Exception as e:
                logger.warning(f"Could not log response body: {e}")
        
        response_info_str = json.dumps(response_info, default=str)
        logger.info(f"Response: {response_info_str}")
        
        return response

