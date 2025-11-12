"""Caching headers middleware"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Request
from typing import Callable


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Add Cache-Control headers to responses"""
    
    # Cache rules for different paths
    CACHE_RULES = {
        "/api/v1/signals": "public, max-age=60",  # 1 minute for signals
        "/api/v1/stats": "public, max-age=300",  # 5 minutes for stats
        "/health": "no-cache, no-store, must-revalidate",  # No cache for health
        "/metrics": "no-cache, no-store, must-revalidate",  # No cache for metrics
    }
    
    DEFAULT_CACHE = "no-cache, no-store, must-revalidate"  # Default: no cache
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Determine cache control header
        cache_control = self.DEFAULT_CACHE
        for path, cache_value in self.CACHE_RULES.items():
            if request.url.path.startswith(path):
                cache_control = cache_value
                break
        
        # Add cache control header
        response.headers["Cache-Control"] = cache_control
        
        # Add ETag support for cache validation
        if "public" in cache_control:
            response.headers["ETag"] = f'"{hash(str(response.body))}"'
        
        return response

