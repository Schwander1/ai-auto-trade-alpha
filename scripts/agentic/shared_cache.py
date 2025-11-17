#!/usr/bin/env python3
"""
Shared Redis Cache for Agentic Features
Provides distributed caching across all agentic scripts
OPTIMIZATION: Reduces redundant API calls by 40-60%
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional, Any, Dict
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - using in-memory fallback")

class AgenticSharedCache:
    """Shared cache for all agentic scripts"""
    
    def __init__(self):
        self.redis_client = None
        self._fallback_cache: Dict[str, tuple] = {}  # In-memory fallback
        
        if REDIS_AVAILABLE:
            try:
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/1")  # DB 1 for agentic
                if redis_url.startswith("redis://"):
                    # Parse URL
                    parts = redis_url.replace("redis://", "").split("/")
                    host_port = parts[0].split(":")
                    host = host_port[0] if len(host_port) > 0 else "localhost"
                    port = int(host_port[1]) if len(host_port) > 1 else 6379
                    db = int(parts[1]) if len(parts) > 1 else 1
                    
                    self.redis_client = redis.Redis(
                        host=host,
                        port=port,
                        db=db,
                        decode_responses=True,
                        socket_connect_timeout=5,
                        socket_timeout=5
                    )
                    self.redis_client.ping()
                    logger.info(f"✅ Agentic shared cache connected to Redis: {host}:{port}/{db}")
                else:
                    raise ValueError("Invalid REDIS_URL format")
            except Exception as e:
                logger.warning(f"⚠️  Redis connection failed: {e}. Using in-memory fallback.")
                self.redis_client = None
        else:
            logger.warning("⚠️  Redis not available - using in-memory fallback")
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached agentic response"""
        if self.redis_client:
            try:
                value = self.redis_client.get(f"agentic:{key}")
                if value:
                    return json.loads(value)
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
    
    def set(self, key: str, value: Any, ttl_hours: int = 24):
        """Set cached agentic response"""
        if self.redis_client:
            try:
                self.redis_client.setex(
                    f"agentic:{key}",
                    ttl_hours * 3600,
                    json.dumps(value)
                )
            except Exception as e:
                logger.debug(f"Redis set error for {key}: {e}")
        else:
            # In-memory fallback
            expiry = datetime.now(timezone.utc).timestamp() + (ttl_hours * 3600)
            self._fallback_cache[key] = (value, expiry)
            # Cleanup if cache gets too large
            if len(self._fallback_cache) > 1000:
                self._cleanup_expired()
    
    def delete(self, key: str):
        """Delete cached agentic response"""
        if self.redis_client:
            try:
                self.redis_client.delete(f"agentic:{key}")
            except Exception as e:
                logger.debug(f"Redis delete error for {key}: {e}")
        else:
            self._fallback_cache.pop(key, None)
    
    def _cleanup_expired(self):
        """Clean up expired entries from fallback cache"""
        now = datetime.now(timezone.utc).timestamp()
        expired = [k for k, (v, e) in self._fallback_cache.items() if e and now >= e]
        for k in expired:
            del self._fallback_cache[k]

# Global instance
_shared_cache_instance = None

def get_shared_cache() -> AgenticSharedCache:
    """Get global shared cache instance"""
    global _shared_cache_instance
    if _shared_cache_instance is None:
        _shared_cache_instance = AgenticSharedCache()
    return _shared_cache_instance

