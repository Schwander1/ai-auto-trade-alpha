"""Rate limiting for Argo API"""
import redis
import time
from typing import Optional
from functools import wraps
from fastapi import HTTPException, Request, Response
import logging

# Import settings with fallback for import path
try:
    from argo.core.config import settings
except ImportError:
    from core.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis client for rate limiting
try:
    rate_limit_redis = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=False,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    rate_limit_redis.ping()
    logger.info(f"Redis connected for rate limiting: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
except Exception as e:
    logger.warning(f"Redis connection for rate limiting failed: {e}. Using in-memory fallback.")
    rate_limit_redis = None
    rate_limit_store = {}


def check_rate_limit(
    client_id: str,
    max_requests: int = 100,
    window: int = 60
) -> bool:
    """
    Check if client has exceeded rate limit
    
    Args:
        client_id: Unique identifier (IP address or API key)
        max_requests: Maximum requests per window
        window: Time window in seconds
    
    Returns:
        True if allowed, False if rate limit exceeded
    """
    if rate_limit_redis is None:
        return _check_rate_limit_memory(client_id, max_requests, window)
    
    try:
        key = f"argo_rate_limit:{client_id}"
        now = int(time.time())
        
        pipe = rate_limit_redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, window)
        
        results = pipe.execute()
        current_count = results[1]
        
        return current_count < max_requests
    
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return True  # Fail open


def _check_rate_limit_memory(client_id: str, max_requests: int, window: int) -> bool:
    """In-memory fallback for rate limiting"""
    now = time.time()
    
    if client_id not in rate_limit_store:
        rate_limit_store[client_id] = []
    
    rate_limit_store[client_id] = [
        req_time for req_time in rate_limit_store[client_id]
        if now - req_time < window
    ]
    
    if len(rate_limit_store[client_id]) >= max_requests:
        return False
    
    rate_limit_store[client_id].append(now)
    return True


def get_rate_limit_status(client_id: str, max_requests: int = 100, window: int = 60) -> dict:
    """
    Get current rate limit status for a client
    
    Returns:
        Dictionary with current request count and remaining requests
    """
    if rate_limit_redis is None:
        return {"current": 0, "remaining": max_requests, "reset_in": window}
    
    try:
        key = f"argo_rate_limit:{client_id}"
        now = int(time.time())
        
        # Remove old entries
        rate_limit_redis.zremrangebyscore(key, 0, now - window)
        
        # Get current count
        current = rate_limit_redis.zcard(key)
        
        # Get TTL
        ttl = rate_limit_redis.ttl(key)
        reset_in = ttl if ttl > 0 else window
        
        return {
            "current": current,
            "remaining": max(0, max_requests - current),
            "reset_in": reset_in
        }
    except Exception as e:
        logger.error(f"Rate limit status error: {e}")
        return {"current": 0, "remaining": max_requests, "reset_in": window}


def add_rate_limit_headers(
    response: Response,
    client_id: str,
    max_requests: int = 100,
    window: int = 60
) -> Response:
    """Add rate limit headers to response"""
    status = get_rate_limit_status(client_id, max_requests, window)
    response.headers["X-RateLimit-Limit"] = str(max_requests)
    response.headers["X-RateLimit-Remaining"] = str(status["remaining"])
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + status["reset_in"])
    return response


def rate_limit(max_requests: int = 100, window: int = 60):
    """Decorator for rate limiting endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request") or (args[0] if args and hasattr(args[0], "client") else None)
            response = kwargs.get("response") or None
            
            if request:
                client_id = request.client.host if request.client else "unknown"
            else:
                client_id = "unknown"
            
            if not check_rate_limit(client_id, max_requests, window):
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window} seconds."
                )
            
            result = await func(*args, **kwargs)
            
            # Add rate limit headers if response object is available
            if response and isinstance(response, Response):
                add_rate_limit_headers(response, client_id, max_requests, window)
            
            return result
        return wrapper
    return decorator

