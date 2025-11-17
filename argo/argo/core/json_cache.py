#!/usr/bin/env python3
"""
JSON Serialization Cache
OPTIMIZATION 11: Caches JSON serialization to reduce CPU usage
"""
import json
import hashlib
import logging
from typing import Any, Optional, Dict
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class JSONCache:
    """Cache for JSON serialization (OPTIMIZATION 11)"""
    
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, str] = {}  # {hash: serialized_json}
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
    
    def serialize(self, data: Any) -> str:
        """
        Serialize data with caching
        
        Args:
            data: Data to serialize
        
        Returns:
            Serialized JSON string
        """
        # Create hash of data
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            data_hash = hashlib.md5(data_str.encode()).hexdigest()
        except (TypeError, ValueError) as e:
            # If serialization fails, just serialize directly
            logger.debug(f"Could not hash data: {e}, serializing directly")
            return json.dumps(data, default=str)
        
        # Check cache
        if data_hash in self._cache:
            self._hits += 1
            logger.debug(f"✅ JSON cache hit (hits: {self._hits}, misses: {self._misses})")
            return self._cache[data_hash]
        
        # Serialize and cache
        self._misses += 1
        serialized = json.dumps(data, sort_keys=True, default=str)
        
        # Cache management
        if len(self._cache) >= self._max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[data_hash] = serialized
        return serialized
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': round(hit_rate, 2),
            'cache_size': len(self._cache),
            'max_size': self._max_size
        }
    
    def clear(self):
        """Clear cache"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

# Global instance
_json_cache_instance = None

def get_json_cache() -> JSONCache:
    """Get global JSON cache instance"""
    global _json_cache_instance
    if _json_cache_instance is None:
        _json_cache_instance = JSONCache()
    return _json_cache_instance

