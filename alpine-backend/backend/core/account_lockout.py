"""Account lockout mechanism for brute force protection"""
import redis
import time
from typing import Optional
from datetime import datetime, timedelta
from backend.core.config import settings
from backend.core.security_logging import log_account_locked, log_failed_login
import logging

logger = logging.getLogger(__name__)

# Initialize Redis client for account lockout
try:
    lockout_redis = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    lockout_redis.ping()
except Exception as e:
    logger.warning(f"Redis connection for account lockout failed: {e}. Using in-memory fallback.")
    lockout_redis = None
    # Fallback to in-memory storage
    lockout_store = {}


# Configuration
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes in seconds
ATTEMPT_WINDOW = 300  # 5 minutes window for counting attempts


def record_failed_login(email: str, ip_address: Optional[str] = None) -> bool:
    """
    Record a failed login attempt and check if account should be locked
    
    Returns:
        True if account is now locked, False otherwise
    """
    now = int(time.time())
    attempt_key = f"login_attempts:{email}"
    lockout_key = f"account_locked:{email}"
    
    if lockout_redis:
        try:
            # Check if already locked
            if lockout_redis.exists(lockout_key):
                return True
            
            # Get current attempts
            attempts = lockout_redis.get(attempt_key)
            if attempts:
                attempts = int(attempts)
            else:
                attempts = 0
            
            # Increment attempts
            attempts += 1
            lockout_redis.setex(attempt_key, ATTEMPT_WINDOW, attempts)
            
            # Check if lockout threshold reached
            if attempts >= MAX_FAILED_ATTEMPTS:
                lockout_redis.setex(lockout_key, LOCKOUT_DURATION, "1")
                log_account_locked(email, ip_address)
                logger.warning(f"Account locked: {email} after {attempts} failed attempts")
                return True
            
            log_failed_login(email, ip_address)
            return False
            
        except Exception as e:
            logger.error(f"Account lockout error: {e}")
            return False
    else:
        # In-memory fallback
        if email not in lockout_store:
            lockout_store[email] = {"attempts": [], "locked_until": None}
        
        # Remove old attempts outside window
        lockout_store[email]["attempts"] = [
            t for t in lockout_store[email]["attempts"]
            if now - t < ATTEMPT_WINDOW
        ]
        
        # Check if locked
        if lockout_store[email]["locked_until"] and now < lockout_store[email]["locked_until"]:
            return True
        
        # Add new attempt
        lockout_store[email]["attempts"].append(now)
        
        # Check if lockout threshold reached
        if len(lockout_store[email]["attempts"]) >= MAX_FAILED_ATTEMPTS:
            lockout_store[email]["locked_until"] = now + LOCKOUT_DURATION
            log_account_locked(email, ip_address)
            logger.warning(f"Account locked: {email} after {len(lockout_store[email]['attempts'])} failed attempts")
            return True
        
        log_failed_login(email, ip_address)
        return False


def clear_failed_attempts(email: str):
    """Clear failed login attempts (called on successful login)"""
    attempt_key = f"login_attempts:{email}"
    lockout_key = f"account_locked:{email}"
    
    if lockout_redis:
        try:
            lockout_redis.delete(attempt_key)
            lockout_redis.delete(lockout_key)
        except Exception as e:
            logger.error(f"Error clearing failed attempts: {e}")
    else:
        # In-memory fallback
        if email in lockout_store:
            lockout_store[email] = {"attempts": [], "locked_until": None}


def is_account_locked(email: str) -> bool:
    """
    Check if account is currently locked
    
    Returns:
        True if account is locked, False otherwise
    """
    lockout_key = f"account_locked:{email}"
    
    if lockout_redis:
        try:
            return lockout_redis.exists(lockout_key) > 0
        except Exception as e:
            logger.error(f"Error checking account lockout: {e}")
            return False
    else:
        # In-memory fallback
        if email not in lockout_store:
            return False
        
        if lockout_store[email]["locked_until"]:
            now = int(time.time())
            if now < lockout_store[email]["locked_until"]:
                return True
            else:
                # Lockout expired, clear it
                lockout_store[email]["locked_until"] = None
                return False
        
        return False


def get_lockout_remaining(email: str) -> Optional[int]:
    """
    Get remaining lockout time in seconds
    
    Returns:
        Remaining seconds or None if not locked
    """
    lockout_key = f"account_locked:{email}"
    
    if lockout_redis:
        try:
            ttl = lockout_redis.ttl(lockout_key)
            return ttl if ttl > 0 else None
        except Exception as e:
            logger.error(f"Error getting lockout remaining: {e}")
            return None
    else:
        # In-memory fallback
        if email not in lockout_store or not lockout_store[email]["locked_until"]:
            return None
        
        now = int(time.time())
        remaining = lockout_store[email]["locked_until"] - now
        return remaining if remaining > 0 else None

