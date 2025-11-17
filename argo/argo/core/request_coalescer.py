#!/usr/bin/env python3
"""
Request Coalescer
Deduplicates and coalesces identical API requests across symbols
Compliance: Rule 01 (Naming), Rule 28 (Performance)
"""
import asyncio
from typing import Dict, Callable, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RequestCoalescer:
    """Coalesce identical requests across symbols"""
    
    def __init__(self, ttl_seconds: int = 5):
        """
        Initialize request coalescer
        
        Args:
            ttl_seconds: Time-to-live for coalesced requests
        """
        self._pending_requests: Dict[str, list] = {}
        self._lock = asyncio.Lock()
        self.ttl_seconds = ttl_seconds
    
    async def get_or_fetch(
        self,
        cache_key: str,
        fetch_func: Callable[[], Any]
    ) -> Any:
        """
        Coalesce identical requests
        
        Args:
            cache_key: Unique key for the request
            fetch_func: Async function to fetch data
        
        Returns:
            Result from fetch_func
        """
        async with self._lock:
            if cache_key in self._pending_requests:
                # Request already in flight, wait for it
                future = asyncio.Future()
                self._pending_requests[cache_key].append(future)
                logger.debug(f"⏳ Coalescing request: {cache_key} (waiting for in-flight request)")
            else:
                # Start new request
                futures = [asyncio.Future()]
                self._pending_requests[cache_key] = futures
                logger.debug(f"🚀 Starting new request: {cache_key}")
        
        # If we're waiting, await the future
        if 'future' in locals():
            return await future
        
        # Otherwise, we're the one making the request
        try:
            result = await fetch_func()
            # Resolve all waiting futures
            async with self._lock:
                for f in self._pending_requests[cache_key]:
                    if not f.done():
                        f.set_result(result)
                del self._pending_requests[cache_key]
            logger.debug(f"✅ Request completed: {cache_key} (resolved {len(self._pending_requests.get(cache_key, []))} waiting requests)")
            return result
        except Exception as e:
            # Reject all waiting futures
            async with self._lock:
                for f in self._pending_requests.get(cache_key, []):
                    if not f.done():
                        f.set_exception(e)
                if cache_key in self._pending_requests:
                    del self._pending_requests[cache_key]
            logger.error(f"❌ Request failed: {cache_key}: {e}")
            raise

# Global instance
_coalescer: Optional[RequestCoalescer] = None

def get_coalescer() -> RequestCoalescer:
    """Get global request coalescer instance"""
    global _coalescer
    if _coalescer is None:
        _coalescer = RequestCoalescer()
    return _coalescer

