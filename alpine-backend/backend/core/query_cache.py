"""
Query Result Caching Utilities
Provides caching for expensive database queries to improve performance.
"""
from typing import Any, Optional, Callable, TypeVar, Hashable
from functools import wraps
import hashlib
import json
import logging
from datetime import datetime, timedelta

try:
    from backend.core.cache import get_cache, set_cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

logger = logging.getLogger(__name__)

T = TypeVar('T')


def cache_query_result(
    ttl: int = 300,
    key_prefix: str = "query",
    key_fields: Optional[list] = None
):
    """
    Decorator to cache query results.

    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
        key_fields: List of function argument names to include in cache key

    Example:
        ```python
        @cache_query_result(ttl=600, key_prefix="user_stats")
        def get_user_statistics(user_id: int, days: int = 30):
            # Expensive query
            return db.query(...).all()
        ```
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if not CACHE_AVAILABLE:
                # Cache not available, execute function directly
                return func(*args, **kwargs)

            # Generate cache key
            cache_key = _generate_cache_key(
                func.__name__,
                key_prefix,
                args,
                kwargs,
                key_fields
            )

            # Try to get from cache
            cached_result = get_cache(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__} with key {cache_key}")
                return cached_result

            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__} with key {cache_key}")
            result = func(*args, **kwargs)
            set_cache(cache_key, result, ttl=ttl)

            return result

        return wrapper
    return decorator


def _generate_cache_key(
    func_name: str,
    key_prefix: str,
    args: tuple,
    kwargs: dict,
    key_fields: Optional[list]
) -> str:
    """Generate a cache key from function arguments"""
    # Include function name and prefix
    key_parts = [key_prefix, func_name]

    # Include specified key fields from kwargs
    if key_fields:
        for field in key_fields:
            if field in kwargs:
                key_parts.append(f"{field}:{kwargs[field]}")
    else:
        # Include all kwargs
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")

    # Include args if any
    if args:
        key_parts.append(f"args:{hash(str(args))}")

    # Create hash of key parts
    key_string = "|".join(str(part) for part in key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()

    return f"{key_prefix}:{func_name}:{key_hash}"


def invalidate_query_cache(key_pattern: str) -> int:
    """
    Invalidate cache entries matching a pattern.

    Args:
        key_pattern: Pattern to match cache keys (supports wildcards)

    Returns:
        Number of cache entries invalidated

    Example:
        ```python
        # Invalidate all user statistics caches
        invalidate_query_cache("user_stats:*")
        ```
    """
    if not CACHE_AVAILABLE:
        return 0

    try:
        # This would need to be implemented based on your cache backend
        # For Redis, you could use SCAN with pattern matching
        logger.warning("Cache invalidation by pattern not fully implemented")
        return 0
    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")
        return 0


def cache_query_with_conditions(
    query_func: Callable[..., T],
    conditions: dict,
    ttl: int = 300,
    key_prefix: str = "query"
) -> T:
    """
    Cache a query result with specific conditions.

    Args:
        query_func: Function that executes the query
        conditions: Dictionary of conditions to include in cache key
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key

    Returns:
        Query result (from cache or execution)

    Example:
        ```python
        result = cache_query_with_conditions(
            lambda: db.query(User).filter(User.tier == 'pro').all(),
            conditions={'tier': 'pro', 'active': True},
            ttl=600
        )
        ```
    """
    if not CACHE_AVAILABLE:
        return query_func()

    # Generate cache key from conditions
    cache_key = _generate_cache_key(
        query_func.__name__ if hasattr(query_func, '__name__') else 'query',
        key_prefix,
        (),
        conditions,
        None
    )

    # Try to get from cache
    cached_result = get_cache(cache_key)
    if cached_result is not None:
        return cached_result

    # Execute query and cache result
    result = query_func()
    set_cache(cache_key, result, ttl=ttl)

    return result
