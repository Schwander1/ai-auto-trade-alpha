"""API response caching utilities for Argo endpoints"""
import json
import hashlib
import logging
from typing import Optional, Any, Dict, Callable
from functools import wraps
from datetime import datetime

try:
    from argo.core.redis_cache import RedisCache
except ImportError:
    try:
        from core.redis_cache import RedisCache
    except ImportError:
        # Fallback if redis_cache doesn't exist
        RedisCache = None

try:
    from argo.core.config import settings
except ImportError:
    from core.config import settings

logger = logging.getLogger(__name__)

# Global cache instance
_cache_instance: Optional[RedisCache] = None

def get_cache() -> Optional[RedisCache]:
    """Get or create cache instance"""
    global _cache_instance
    if _cache_instance is None:
        if RedisCache is None:
            logger.warning("RedisCache not available - caching disabled")
            return None
        try:
            _cache_instance = RedisCache()
        except Exception as e:
            logger.warning(f"Failed to initialize cache: {e}")
            _cache_instance = None
    return _cache_instance


def cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate cache key from prefix and arguments"""
    key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cache_response(ttl: int = 10, prefix: str = "api"):
    """
    Decorator to cache API endpoint responses
    
    Args:
        ttl: Time to live in seconds (default: 10 seconds for signals)
        prefix: Cache key prefix
    
    Usage:
        @cache_response(ttl=10, prefix="signals")
        async def get_signals():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key
            key = f"{prefix}:{func.__name__}:{cache_key(prefix, *args, **kwargs)}"
            
            # Try to get from cache
            if cache:
                try:
                    cached = cache.get(key)
                    if cached is not None:
                        logger.debug(f"Cache hit: {key}")
                        return cached
                    logger.debug(f"Cache miss: {key}")
                except Exception as e:
                    logger.debug(f"Cache read error: {e}")
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            if cache:
                try:
                    cache.set(key, result, ttl=ttl)
                except Exception as e:
                    logger.debug(f"Cache write error: {e}")
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str):
    """
    Invalidate cache entries matching a pattern
    
    Args:
        pattern: Cache key pattern to match (e.g., "signals:*")
    """
    cache = get_cache()
    if cache and hasattr(cache, 'client') and cache.client:
        try:
            # Get all keys matching pattern
            keys = cache.client.keys(f"*{pattern}*")
            if keys:
                cache.client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries matching {pattern}")
        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")


def get_cached_signals(key: str) -> Optional[Any]:
    """Get cached signals by key"""
    cache = get_cache()
    if cache:
        return cache.get(key)
    return None


def set_cached_signals(key: str, value: Any, ttl: int = 10):
    """Set cached signals with TTL"""
    cache = get_cache()
    if cache:
        cache.set(key, value, ttl=ttl)

