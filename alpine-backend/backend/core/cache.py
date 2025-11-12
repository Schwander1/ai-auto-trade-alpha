"""Redis caching utilities"""
import redis
import json
import hashlib
from functools import wraps
from typing import Optional, Callable, Any
from backend.core.config import settings
from backend.core.metrics import (
    record_cache_hit, record_cache_miss, record_cache_operation,
    update_redis_status
)

# Initialize Redis client
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    # Test connection
    redis_client.ping()
    update_redis_status(True)
except Exception as e:
    print(f"Warning: Redis connection failed: {e}. Caching disabled.")
    redis_client = None
    update_redis_status(False)


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()


def cache_response(ttl: int = 300, prefix: str = "cache"):
    """
    Decorator to cache function responses in Redis
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        prefix: Cache key prefix
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if redis_client is None:
                # If Redis is unavailable, execute function without caching
                return await func(*args, **kwargs)
            
            # Generate cache key
            key = f"{prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            try:
                cached = redis_client.get(key)
                if cached:
                    record_cache_hit(key)
                    record_cache_operation('get', True)
                    return json.loads(cached)
                else:
                    record_cache_miss(key)
                    record_cache_operation('get', True)
            except Exception as e:
                print(f"Cache read error: {e}")
                record_cache_operation('get', False)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            try:
                redis_client.setex(key, ttl, json.dumps(result, default=str))
                record_cache_operation('set', True)
            except Exception as e:
                print(f"Cache write error: {e}")
                record_cache_operation('set', False)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Invalidate cache entries matching pattern
    
    Args:
        pattern: Redis key pattern (e.g., "cache:signals:*")
    """
    if redis_client is None:
        return
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        print(f"Cache invalidation error: {e}")


def get_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    if redis_client is None:
        return None
    
    try:
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        print(f"Cache get error: {e}")
    
    return None


def set_cache(key: str, value: Any, ttl: int = 300):
    """Set value in cache"""
    if redis_client is None:
        return
    
    try:
        redis_client.setex(key, ttl, json.dumps(value, default=str))
    except Exception as e:
        print(f"Cache set error: {e}")

