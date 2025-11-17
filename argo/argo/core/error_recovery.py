#!/usr/bin/env python3
"""
Error Recovery and Retry Mechanisms
Provides robust error handling and recovery for production systems
"""
import logging
import time
import asyncio
from typing import Callable, Optional, TypeVar, Any
from functools import wraps
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryStrategy(Enum):
    """Retry strategies"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    NO_RETRY = "no_retry"

class ErrorRecovery:
    """Error recovery and retry handler"""
    
    @staticmethod
    def retry_with_backoff(
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        exceptions: tuple = (Exception,),
        on_retry: Optional[Callable] = None
    ):
        """
        Decorator for retrying functions with backoff
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            strategy: Retry strategy
            exceptions: Tuple of exceptions to catch
            on_retry: Optional callback function called on each retry
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                delay = initial_delay
                last_exception = None
                
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt == max_attempts:
                            logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                            raise
                        
                        # Calculate delay based on strategy
                        if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                            delay = min(initial_delay * (2 ** (attempt - 1)), max_delay)
                        elif strategy == RetryStrategy.LINEAR_BACKOFF:
                            delay = min(initial_delay * attempt, max_delay)
                        elif strategy == RetryStrategy.FIXED_DELAY:
                            delay = initial_delay
                        else:
                            raise
                        
                        logger.warning(
                            f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        
                        if on_retry:
                            try:
                                on_retry(attempt, e, delay)
                            except Exception as retry_error:
                                logger.error(f"Error in on_retry callback: {retry_error}")
                        
                        time.sleep(delay)
                
                # Should never reach here, but just in case
                if last_exception:
                    raise last_exception
                raise RuntimeError("Unexpected error in retry logic")
            
            return wrapper
        
        return decorator
    
    @staticmethod
    async def async_retry_with_backoff(
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        exceptions: tuple = (Exception,),
        on_retry: Optional[Callable] = None
    ):
        """
        Decorator for retrying async functions with backoff
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                delay = initial_delay
                last_exception = None
                
                for attempt in range(1, max_attempts + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt == max_attempts:
                            logger.error(f"Async function {func.__name__} failed after {max_attempts} attempts: {e}")
                            raise
                        
                        # Calculate delay
                        if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                            delay = min(initial_delay * (2 ** (attempt - 1)), max_delay)
                        elif strategy == RetryStrategy.LINEAR_BACKOFF:
                            delay = min(initial_delay * attempt, max_delay)
                        elif strategy == RetryStrategy.FIXED_DELAY:
                            delay = initial_delay
                        else:
                            raise
                        
                        logger.warning(
                            f"Async function {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        
                        if on_retry:
                            try:
                                if asyncio.iscoroutinefunction(on_retry):
                                    await on_retry(attempt, e, delay)
                                else:
                                    on_retry(attempt, e, delay)
                            except Exception as retry_error:
                                logger.error(f"Error in on_retry callback: {retry_error}")
                        
                        await asyncio.sleep(delay)
                
                if last_exception:
                    raise last_exception
                raise RuntimeError("Unexpected error in async retry logic")
            
            return wrapper
        
        return decorator
    
    @staticmethod
    def circuit_breaker(
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        exceptions: tuple = (Exception,)
    ):
        """
        Circuit breaker pattern decorator
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time in seconds before attempting recovery
            exceptions: Exceptions that count as failures
        """
        failures = []
        circuit_open = False
        circuit_open_time = None
        
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                nonlocal circuit_open, circuit_open_time, failures
                
                # Check if circuit should be closed
                if circuit_open:
                    if time.time() - circuit_open_time >= recovery_timeout:
                        logger.info(f"Circuit breaker for {func.__name__} attempting recovery")
                        circuit_open = False
                        failures.clear()
                    else:
                        raise RuntimeError(
                            f"Circuit breaker is OPEN for {func.__name__}. "
                            f"Too many failures. Retry after {recovery_timeout}s"
                        )
                
                try:
                    result = func(*args, **kwargs)
                    # Success - reset failures
                    failures.clear()
                    return result
                except exceptions as e:
                    failures.append(time.time())
                    # Keep only recent failures
                    failures = [f for f in failures if time.time() - f < recovery_timeout]
                    
                    if len(failures) >= failure_threshold:
                        circuit_open = True
                        circuit_open_time = time.time()
                        logger.error(
                            f"Circuit breaker OPENED for {func.__name__} after {failure_threshold} failures"
                        )
                    
                    raise
            
            return wrapper
        
        return decorator

