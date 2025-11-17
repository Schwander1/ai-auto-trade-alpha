"""Rate limiting middleware for FastAPI"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import HTTPException
import time
import logging
from typing import Callable

try:
    from argo.core.rate_limit import check_rate_limit, get_rate_limit_status, add_rate_limit_headers
except ImportError:
    from core.rate_limit import check_rate_limit, get_rate_limit_status, add_rate_limit_headers

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests"""
    
    def __init__(
        self,
        app,
        max_requests: int = 100,
        window: int = 60,
        exempt_paths: list = None
    ):
        """
        Initialize rate limiting middleware
        
        Args:
            app: FastAPI application
            max_requests: Maximum requests per window
            window: Time window in seconds
            exempt_paths: List of paths to exempt from rate limiting
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.exempt_paths = exempt_paths or ["/health", "/metrics", "/docs", "/openapi.json", "/redoc"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting"""
        # Skip rate limiting for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Get client identifier (IP address)
        client_id = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not check_rate_limit(client_id, self.max_requests, self.window):
            status = get_rate_limit_status(client_id, self.max_requests, self.window)
            logger.warning(f"Rate limit exceeded for {client_id}: {status}")
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {self.max_requests} requests per {self.window} seconds",
                    "retry_after": status.get("reset_in", self.window)
                },
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + status.get("reset_in", self.window)),
                    "Retry-After": str(status.get("reset_in", self.window))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        status = get_rate_limit_status(client_id, self.max_requests, self.window)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(status.get("remaining", 0))
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + status.get("reset_in", self.window))
        
        return response

