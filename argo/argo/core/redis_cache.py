#!/usr/bin/env python3
"""
Redis Cache Utility for Distributed Caching
Provides persistent, shared cache across instances with async support
OPTIMIZATION: Enhanced with async operations and better error handling
"""
import json
import logging
import pickle
import asyncio
from typing import Optional, Any, Dict
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Try to import Redis
try:
    import redis
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - using in-memory fallback")

# Try to import settings
try:
    from argo.core.config import settings
except ImportError:
    try:
        from core.config import settings
    except ImportError:
        settings = None

class RedisCache:
    """Redis-based distributed cache with async support"""
    
    def __init__(self):
        self.client = None
        self.async_client = None
        self._fallback_cache: Dict[str, tuple] = {}  # In-memory fallback
        self._async_fallback_cache: Dict[str, tuple] = {}  # Async fallback
        self._use_redis = False
        
        if REDIS_AVAILABLE and settings:
            try:
                # Sync client
                self.client = redis.Redis(
                    host=settings.REDIS_HOST if hasattr(settings, 'REDIS_HOST') else 'localhost',
                    port=settings.REDIS_PORT if hasattr(settings, 'REDIS_PORT') else 6379,
                    password=settings.REDIS_PASSWORD if hasattr(settings, 'REDIS_PASSWORD') else None,
                    db=settings.REDIS_DB if hasattr(settings, 'REDIS_DB') else 0,
                    decode_responses=False,  # We'll handle encoding/decoding
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                # Test connection
                self.client.ping()
                
                # Async client
                redis_url = f"redis://{settings.REDIS_HOST if hasattr(settings, 'REDIS_HOST') else 'localhost'}:{settings.REDIS_PORT if hasattr(settings, 'REDIS_PORT') else 6379}/{settings.REDIS_DB if hasattr(settings, 'REDIS_DB') else 0}"
                if hasattr(settings, 'REDIS_PASSWORD') and settings.REDIS_PASSWORD:
                    redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST if hasattr(settings, 'REDIS_HOST') else 'localhost'}:{settings.REDIS_PORT if hasattr(settings, 'REDIS_PORT') else 6379}/{settings.REDIS_DB if hasattr(settings, 'REDIS_DB') else 0}"
                
                self.async_client = aioredis.from_url(
                    redis_url,
                    decode_responses=False,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                
                self._use_redis = True
                logger.info(f"✅ Redis cache connected: {settings.REDIS_HOST if hasattr(settings, 'REDIS_HOST') else 'localhost'}:{settings.REDIS_PORT if hasattr(settings, 'REDIS_PORT') else 6379}")
            except Exception as e:
                logger.warning(f"⚠️  Redis connection failed: {e}. Using in-memory fallback.")
                self.client = None
                self.async_client = None
                self._use_redis = False
        else:
            logger.warning("⚠️  Redis not available - using in-memory fallback")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (sync)"""
        if self._use_redis and self.client:
            try:
                data = self.client.get(key)
                if data:
                    try:
                        return pickle.loads(data)
                    except (pickle.UnpicklingError, TypeError, AttributeError) as e:
                        # If unpickling fails, try to clear the corrupted cache entry
                        logger.debug(f"Redis unpickle error for {key}: {e}, clearing cache entry")
                        try:
                            self.client.delete(key)
                        except Exception:
                            pass
                        return None
            except Exception as e:
                logger.debug(f"Redis get error for {key}: {e}")
                return None
        else:
            # In-memory fallback
            if key in self._fallback_cache:
                value, expiry = self._fallback_cache[key]
                if expiry is None or datetime.now(timezone.utc).timestamp() < expiry:
                    return value
                else:
                    del self._fallback_cache[key]
        return None
    
    async def aget(self, key: str) -> Optional[Any]:
        """Get value from cache (async)"""
        if self._use_redis and self.async_client:
            try:
                data = await self.async_client.get(key)
                if data:
                    return pickle.loads(data)
            except Exception as e:
                logger.debug(f"Redis async get error for {key}: {e}")
                return None
        else:
            # In-memory fallback
            if key in self._async_fallback_cache:
                value, expiry = self._async_fallback_cache[key]
                if expiry is None or datetime.now(timezone.utc).timestamp() < expiry:
                    return value
                else:
                    del self._async_fallback_cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL (sync)"""
        if self._use_redis and self.client:
            try:
                data = pickle.dumps(value)
                if ttl:
                    self.client.setex(key, ttl, data)
                else:
                    self.client.set(key, data)
            except Exception as e:
                logger.debug(f"Redis set error for {key}: {e}")
        else:
            # In-memory fallback
            expiry = None
            if ttl:
                expiry = datetime.now(timezone.utc).timestamp() + ttl
            self._fallback_cache[key] = (value, expiry)
            # Clean up expired entries periodically
            if len(self._fallback_cache) > 1000:
                self._cleanup_expired()
    
    async def aset(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL (async)"""
        if self._use_redis and self.async_client:
            try:
                data = pickle.dumps(value)
                if ttl:
                    await self.async_client.setex(key, ttl, data)
                else:
                    await self.async_client.set(key, data)
            except Exception as e:
                logger.debug(f"Redis async set error for {key}: {e}")
        else:
            # In-memory fallback
            expiry = None
            if ttl:
                expiry = datetime.now(timezone.utc).timestamp() + ttl
            self._async_fallback_cache[key] = (value, expiry)
            # Clean up expired entries periodically
            if len(self._async_fallback_cache) > 1000:
                await self._acleanup_expired()
    
    def delete(self, key: str):
        """Delete key from cache (sync)"""
        if self._use_redis and self.client:
            try:
                self.client.delete(key)
            except Exception as e:
                logger.debug(f"Redis delete error for {key}: {e}")
        else:
            self._fallback_cache.pop(key, None)
    
    async def adelete(self, key: str):
        """Delete key from cache (async)"""
        if self._use_redis and self.async_client:
            try:
                await self.async_client.delete(key)
            except Exception as e:
                logger.debug(f"Redis async delete error for {key}: {e}")
        else:
            self._async_fallback_cache.pop(key, None)
    
    def exists(self, key: str) -> bool:
        """Check if key exists (sync)"""
        if self._use_redis and self.client:
            try:
                return bool(self.client.exists(key))
            except Exception as e:
                logger.debug(f"Redis exists error for {key}: {e}")
                return False
        else:
            if key in self._fallback_cache:
                value, expiry = self._fallback_cache[key]
                if expiry is None or datetime.now(timezone.utc).timestamp() < expiry:
                    return True
                else:
                    del self._fallback_cache[key]
            return False
    
    async def aexists(self, key: str) -> bool:
        """Check if key exists (async)"""
        if self._use_redis and self.async_client:
            try:
                return bool(await self.async_client.exists(key))
            except Exception as e:
                logger.debug(f"Redis async exists error for {key}: {e}")
                return False
        else:
            if key in self._async_fallback_cache:
                value, expiry = self._async_fallback_cache[key]
                if expiry is None or datetime.now(timezone.utc).timestamp() < expiry:
                    return True
                else:
                    del self._async_fallback_cache[key]
            return False
    
    def _cleanup_expired(self):
        """Clean up expired entries from fallback cache (sync)"""
        now = datetime.now(timezone.utc).timestamp()
        expired = [k for k, (v, e) in self._fallback_cache.items() if e and now >= e]
        for k in expired:
            del self._fallback_cache[k]
    
    async def _acleanup_expired(self):
        """Clean up expired entries from fallback cache (async)"""
        now = datetime.now(timezone.utc).timestamp()
        expired = [k for k, (v, e) in self._async_fallback_cache.items() if e and now >= e]
        for k in expired:
            del self._async_fallback_cache[k]
    
    async def close(self):
        """Close async Redis connection"""
        if self.async_client:
            await self.async_client.close()

# Global cache instance
_cache_instance = None

def get_redis_cache() -> RedisCache:
    """Get global Redis cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance
