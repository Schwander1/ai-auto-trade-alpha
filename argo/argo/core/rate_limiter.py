#!/usr/bin/env python3
"""
Rate Limiter with Token Bucket Algorithm
Prevents API throttling and manages request rates
"""
import asyncio
import time
import logging
from typing import Dict, Optional
from collections import defaultdict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests_per_second: float
    burst_size: int = 10
    max_wait_time: float = 60.0

class TokenBucket:
    """Token bucket rate limiter"""
    
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # Tokens per second
        self.capacity = capacity  # Max tokens
        self.tokens = float(capacity)
        self.last_update = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens from bucket"""
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Add tokens based on elapsed time
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    async def wait_for_tokens(self, tokens: int = 1, max_wait: float = 60.0) -> bool:
        """Wait until tokens are available"""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if await self.acquire(tokens):
                return True
            await asyncio.sleep(0.1)  # Check every 100ms
        return False

class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self):
        self.limiters: Dict[str, TokenBucket] = {}
        self.configs: Dict[str, RateLimitConfig] = {}
    
    def configure(self, source_name: str, config: RateLimitConfig):
        """Configure rate limit for a data source"""
        self.configs[source_name] = config
        self.limiters[source_name] = TokenBucket(
            rate=config.requests_per_second,
            capacity=config.burst_size
        )
        logger.info(f"✅ Rate limiter configured for {source_name}: {config.requests_per_second} req/s")
    
    async def acquire(self, source_name: str, tokens: int = 1) -> bool:
        """Acquire permission to make request"""
        if source_name not in self.limiters:
            return True  # No limit configured
        
        return await self.limiters[source_name].acquire(tokens)
    
    async def wait_for_permission(self, source_name: str, tokens: int = 1) -> bool:
        """Wait for permission to make request"""
        if source_name not in self.limiters:
            return True
        
        config = self.configs.get(source_name)
        max_wait = config.max_wait_time if config else 60.0
        
        return await self.limiters[source_name].wait_for_tokens(tokens, max_wait)

# Global rate limiter instance
_rate_limiter = None

def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
        # Configure default rate limits
        _rate_limiter.configure('massive', RateLimitConfig(requests_per_second=5.0, burst_size=10))
        # Premium tier: 150 calls/min = 2.5 calls/sec, set to 2.0 calls/sec (120/min) to stay under limit
        _rate_limiter.configure('alpha_vantage', RateLimitConfig(requests_per_second=2.0, burst_size=10))  # Premium: 150/min
        _rate_limiter.configure('xai', RateLimitConfig(requests_per_second=1.0, burst_size=5))
        _rate_limiter.configure('sonar', RateLimitConfig(requests_per_second=1.0, burst_size=5))
    return _rate_limiter

