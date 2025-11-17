"""Redis-based rate limiting"""
import redis
import time
from typing import Optional
from backend.core.config import settings
# Metrics recording handled by metrics middleware

# Initialize Redis client for rate limiting
try:
    rate_limit_redis = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=False,  # Use bytes for rate limiting
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    rate_limit_redis.ping()
except Exception as e:
    print(f"Warning: Redis connection for rate limiting failed: {e}. Using in-memory fallback.")
    rate_limit_redis = None
    # Fallback to in-memory storage
    rate_limit_store = {}


def check_rate_limit(
    client_id: str,
    max_requests: int = 100,
    window: int = 60
) -> bool:
    """
    Check if client has exceeded rate limit using Redis
    
    Args:
        client_id: Unique identifier for the client (e.g., user email, IP address)
        max_requests: Maximum number of requests allowed in the window
        window: Time window in seconds
    
    Returns:
        True if request is allowed, False if rate limit exceeded
    """
    if rate_limit_redis is None:
        # Fallback to in-memory rate limiting
        return _check_rate_limit_memory(client_id, max_requests, window)
    
    try:
        key = f"rate_limit:{client_id}"
        now = int(time.time())
        
        # Use Redis pipeline for atomic operations
        pipe = rate_limit_redis.pipeline()
        
        # Remove old entries (outside window)
        pipe.zremrangebyscore(key, 0, now - window)
        
        # Count current requests in window
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(now): now})
        
        # Set expiration
        pipe.expire(key, window)
        
        # Execute pipeline
        results = pipe.execute()
        current_count = results[1]
        
        allowed = current_count < max_requests
        # Metrics recording handled by metrics middleware
        return allowed
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Rate limit check error: {e}")
        
        # SECURITY: Fail closed in production, fail open in development
        from backend.core.config import settings
        if settings.ENVIRONMENT == "production":
            # In production, fail closed to prevent DoS if Redis is down
            logger.critical("Rate limiting failed in production - rejecting request for safety")
            return False  # Fail closed
        else:
            # In development, fail open to allow testing
            logger.warning("Rate limiting failed in development - allowing request")
        return True  # Fail open


def _check_rate_limit_memory(client_id: str, max_requests: int, window: int) -> bool:
    """In-memory fallback for rate limiting"""
    now = time.time()
    
    if client_id not in rate_limit_store:
        rate_limit_store[client_id] = []
    
    # Remove old entries
    rate_limit_store[client_id] = [
        req_time for req_time in rate_limit_store[client_id]
        if now - req_time < window
    ]
    
    # Check limit
    if len(rate_limit_store[client_id]) >= max_requests:
        return False
    
    # Add current request
    rate_limit_store[client_id].append(now)
    return True


def get_rate_limit_status(client_id: str, window: int = 60) -> dict:
    """
    Get current rate limit status for a client
    
    Returns:
        Dictionary with current request count and remaining requests
    """
    if rate_limit_redis is None:
        return {"current": 0, "remaining": 100, "reset_in": window}
    
    try:
        key = f"rate_limit:{client_id}"
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
            "remaining": max(0, 100 - current),
            "reset_in": reset_in
        }
    except Exception as e:
        print(f"Rate limit status error: {e}")
        return {"current": 0, "remaining": 100, "reset_in": window}

