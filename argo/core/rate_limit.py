"""Rate limiting for Argo API"""
import redis
import time
from typing import Optional
from functools import wraps
from fastapi import HTTPException, Request
import logging

logger = logging.getLogger(__name__)

# Initialize Redis client for rate limiting
try:
    rate_limit_redis = redis.Redis(
        host="localhost",
        port=6379,
        password=None,
        db=0,
        decode_responses=False,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    rate_limit_redis.ping()
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


def rate_limit(max_requests: int = 100, window: int = 60):
    """Decorator for rate limiting endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request") or (args[0] if args and hasattr(args[0], "client") else None)
            
            if request:
                client_id = request.client.host if request.client else "unknown"
            else:
                client_id = "unknown"
            
            if not check_rate_limit(client_id, max_requests, window):
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window} seconds."
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

