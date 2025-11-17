#!/usr/bin/env python3
"""
Circuit Breaker Pattern
Prevents cascading failures and provides automatic recovery
"""
import time
import logging
from enum import Enum
from typing import Callable, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5  # Open after N failures
    success_threshold: int = 2  # Close after N successes in half-open
    timeout: float = 60.0  # Time before trying half-open
    expected_exception: type = Exception

class CircuitBreaker:
    """Circuit breaker for data sources"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_success_time: Optional[float] = None
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        # Check if circuit should transition
        self._check_state_transition()
        
        # Reject if circuit is open
        if self.state == CircuitState.OPEN:
            logger.warning(f"⚠️  Circuit breaker OPEN for {self.name} - rejecting request")
            raise Exception(f"Circuit breaker is OPEN for {self.name}")
        
        # Try to execute
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        self._check_state_transition()
        
        if self.state == CircuitState.OPEN:
            logger.warning(f"⚠️  Circuit breaker OPEN for {self.name} - rejecting request")
            raise Exception(f"Circuit breaker is OPEN for {self.name}")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        self.last_success_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._close()
        else:
            self.failure_count = 0  # Reset on success
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self._open()
    
    def _open(self):
        """Open the circuit"""
        if self.state != CircuitState.OPEN:
            logger.error(f"🔴 Circuit breaker OPENED for {self.name} after {self.failure_count} failures")
            self.state = CircuitState.OPEN
            self.success_count = 0
    
    def _close(self):
        """Close the circuit"""
        logger.info(f"🟢 Circuit breaker CLOSED for {self.name}")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
    
    def _check_state_transition(self):
        """Check if circuit should transition states"""
        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self.last_failure_time and (time.time() - self.last_failure_time) >= self.config.timeout:
                logger.info(f"🟡 Circuit breaker HALF_OPEN for {self.name} - testing recovery")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0

