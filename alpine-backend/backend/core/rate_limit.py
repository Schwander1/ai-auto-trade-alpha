"""Redis-based rate limiting with per-user/tier support"""
import redis
import time
import logging
from typing import Optional, Dict
from enum import Enum
from backend.core.config import settings
# Metrics recording handled by metrics middleware

logger = logging.getLogger(__name__)

# Rate limit configuration per tier
class RateLimitTier(str, Enum):
    """Rate limit tiers"""
    ANONYMOUS = "anonymous"
    STARTER = "starter"
    PRO = "pro"
    ELITE = "elite"
    ADMIN = "admin"

# Rate limit configuration: (requests_per_minute, requests_per_hour)
RATE_LIMIT_CONFIG: Dict[RateLimitTier, tuple] = {
    RateLimitTier.ANONYMOUS: (10, 100),      # 10/min, 100/hour
    RateLimitTier.STARTER: (30, 500),        # 30/min, 500/hour
    RateLimitTier.PRO: (100, 2000),          # 100/min, 2000/hour
    RateLimitTier.ELITE: (500, 10000),       # 500/min, 10000/hour
    RateLimitTier.ADMIN: (1000, 50000),      # 1000/min, 50000/hour
}

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
    logger.warning(f"Redis connection for rate limiting failed: {e}. Using in-memory fallback.")
    rate_limit_redis = None
    # Fallback to in-memory storage
    rate_limit_store = {}


def get_rate_limit_for_tier(tier: Optional[RateLimitTier] = None) -> tuple:
    """
    Get rate limit configuration for a tier

    Args:
        tier: User tier (defaults to ANONYMOUS)

    Returns:
        Tuple of (requests_per_minute, requests_per_hour)
    """
    if tier is None:
        tier = RateLimitTier.ANONYMOUS
    return RATE_LIMIT_CONFIG.get(tier, RATE_LIMIT_CONFIG[RateLimitTier.ANONYMOUS])


def check_rate_limit(
    client_id: str,
    max_requests: Optional[int] = None,
    window: int = 60,
    tier: Optional[RateLimitTier] = None
) -> bool:
    """
    Check if client has exceeded rate limit using Redis

    Args:
        client_id: Unique identifier for the client (e.g., user email, IP address, user_id)
        max_requests: Maximum number of requests allowed in the window (overrides tier if provided)
        window: Time window in seconds (60 for per-minute, 3600 for per-hour)
        tier: User tier for tier-based rate limiting

    Returns:
        True if request is allowed, False if rate limit exceeded
    """
    # Use tier-based limits if tier provided and max_requests not specified
    if max_requests is None and tier is not None:
        requests_per_min, requests_per_hour = get_rate_limit_for_tier(tier)
        # Use per-minute limit for 60s window, per-hour for 3600s window
        max_requests = requests_per_min if window == 60 else requests_per_hour
    elif max_requests is None:
        max_requests = 100  # Default fallback

    if rate_limit_redis is None:
        # Fallback to in-memory rate limiting
        return _check_rate_limit_memory(client_id, max_requests, window)

    try:
        # Include tier in key for separate tracking per tier
        tier_suffix = f":{tier.value}" if tier else ""
        key = f"rate_limit:{client_id}{tier_suffix}:{window}"
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
        logger.error(f"Rate limit check error: {e}", exc_info=True)

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


def get_rate_limit_status(
    client_id: str,
    window: int = 60,
    tier: Optional[RateLimitTier] = None,
    max_requests: Optional[int] = None
) -> dict:
    """
    Get current rate limit status for a client

    Args:
        client_id: Unique identifier for the client
        window: Time window in seconds
        tier: User tier for tier-based rate limiting
        max_requests: Maximum requests (overrides tier if provided)

    Returns:
        Dictionary with current request count, remaining requests, and limit info
    """
    # Get max requests from tier if not provided
    if max_requests is None and tier is not None:
        requests_per_min, requests_per_hour = get_rate_limit_for_tier(tier)
        max_requests = requests_per_min if window == 60 else requests_per_hour
    elif max_requests is None:
        max_requests = 100  # Default fallback

    if rate_limit_redis is None:
        return {
            "current": 0,
            "remaining": max_requests,
            "limit": max_requests,
            "reset_in": window,
            "tier": tier.value if tier else None
        }

    try:
        tier_suffix = f":{tier.value}" if tier else ""
        key = f"rate_limit:{client_id}{tier_suffix}:{window}"
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
            "limit": max_requests,
            "reset_in": reset_in,
            "tier": tier.value if tier else None
        }
    except Exception as e:
        logger.error(f"Rate limit status error: {e}", exc_info=True)
        return {
            "current": 0,
            "remaining": max_requests,
            "limit": max_requests,
            "reset_in": window,
            "tier": tier.value if tier else None
        }
