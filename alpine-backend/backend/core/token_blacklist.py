"""Redis-based token blacklist"""
import redis
import hashlib
import logging
from typing import Optional
from backend.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis client for token blacklist
try:
    blacklist_redis = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=False,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    blacklist_redis.ping()
except Exception as e:
    logger.warning(f"Redis connection for token blacklist failed: {e}. Using in-memory fallback.")
    blacklist_redis = None
    # Fallback to in-memory storage
    token_blacklist = set()


def blacklist_token(token: str, ttl: int = 86400) -> bool:
    """
    Add token to blacklist

    Args:
        token: JWT token to blacklist
        ttl: Time to live in seconds (default: 24 hours)

    Returns:
        True if successful, False otherwise
    """
    if blacklist_redis is None:
        # Fallback to in-memory blacklist
        token_blacklist.add(token)
        return True

    try:
        # Hash token for storage (security best practice)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        key = f"blacklist:{token_hash}"

        # Store with TTL
        blacklist_redis.setex(key, ttl, "1")
        return True
    except Exception as e:
        logger.error(f"Token blacklist error: {e}", exc_info=True)
        return False


def is_token_blacklisted(token: str) -> bool:
    """
    Check if token is blacklisted

    Args:
        token: JWT token to check

    Returns:
        True if token is blacklisted, False otherwise
    """
    if blacklist_redis is None:
        # Fallback to in-memory blacklist
        return token in token_blacklist

    try:
        # Hash token for lookup
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        key = f"blacklist:{token_hash}"

        # Check if key exists
        return blacklist_redis.exists(key) > 0
    except Exception as e:
        logger.error(f"Token blacklist check error: {e}", exc_info=True)
        return False  # Fail open (allow token if check fails)


def remove_from_blacklist(token: str) -> bool:
    """
    Remove token from blacklist (for testing/admin purposes)

    Args:
        token: JWT token to remove from blacklist

    Returns:
        True if successful, False otherwise
    """
    if blacklist_redis is None:
        # Fallback to in-memory blacklist
        token_blacklist.discard(token)
        return True

    try:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        key = f"blacklist:{token_hash}"
        blacklist_redis.delete(key)
        return True
    except Exception as e:
        logger.error(f"Token blacklist removal error: {e}", exc_info=True)
        return False
