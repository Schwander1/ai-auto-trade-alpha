"""Metrics middleware for Prometheus"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Request
from backend.core.metrics import record_request
import time


class MetricsMiddleware(BaseHTTPMiddleware):
    """Record metrics for all requests"""
    
    async def dispatch(self, request: Request, call_next: ASGIApp):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        method = request.method
        endpoint = request.url.path
        status_code = response.status_code
        
        record_request(method, endpoint, status_code, duration)
        
        return response

