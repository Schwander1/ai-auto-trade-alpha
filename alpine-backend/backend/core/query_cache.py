"""Database query result caching utilities"""
from functools import wraps
from typing import Optional, Callable, Any
from backend.core.cache import get_cache, set_cache
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def cache_query_result(ttl: int = 300, key_prefix: str = "query"):
    """
    Cache database query results in Redis
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Cache key prefix
    
    Usage:
        @cache_query_result(ttl=300, key_prefix="signals")
        async def get_user_signals(user_id: int, limit: int = 10):
            # ... query logic
            return results
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            # Exclude 'db' and 'session' from cache key (they're not serializable)
            cache_kwargs = {k: v for k, v in kwargs.items() if k not in ['db', 'session']}
            cache_key_data = f"{func.__name__}:{json.dumps(cache_kwargs, sort_keys=True, default=str)}"
            cache_key = f"{key_prefix}:{hashlib.md5(cache_key_data.encode()).hexdigest()}"
            
            # Try cache first
            cached_result = get_cache(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute query
            logger.debug(f"Cache miss for {func.__name__}, executing query")
            result = await func(*args, **kwargs)
            
            # Cache result (only if it's serializable)
            try:
                set_cache(cache_key, result, ttl=ttl)
            except (TypeError, ValueError) as e:
                logger.warning(f"Could not cache result for {func.__name__}: {e}")
            
            return result
        return wrapper
    return decorator


def cache_sync_query_result(ttl: int = 300, key_prefix: str = "query"):
    """
    Cache synchronous database query results in Redis
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Cache key prefix
    
    Usage:
        @cache_sync_query_result(ttl=300, key_prefix="users")
        def get_user_by_email(email: str, db: Session):
            # ... query logic
            return user
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            # Exclude 'db' and 'session' from cache key
            cache_kwargs = {k: v for k, v in kwargs.items() if k not in ['db', 'session']}
            cache_key_data = f"{func.__name__}:{json.dumps(cache_kwargs, sort_keys=True, default=str)}"
            cache_key = f"{key_prefix}:{hashlib.md5(cache_key_data.encode()).hexdigest()}"
            
            # Try cache first
            cached_result = get_cache(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute query
            logger.debug(f"Cache miss for {func.__name__}, executing query")
            result = func(*args, **kwargs)
            
            # Cache result (only if it's serializable)
            try:
                # Convert SQLAlchemy objects to dict if needed
                if hasattr(result, '__dict__'):
                    # Try to serialize as dict
                    result_dict = {k: v for k, v in result.__dict__.items() if not k.startswith('_')}
                    set_cache(cache_key, result_dict, ttl=ttl)
                else:
                    set_cache(cache_key, result, ttl=ttl)
            except (TypeError, ValueError) as e:
                logger.warning(f"Could not cache result for {func.__name__}: {e}")
            
            return result
        return wrapper
    return decorator

