#!/usr/bin/env python3
"""
Error Handling Utilities
Standardized error handling patterns for backtesting
ENHANCED: Added retry logic and error recovery
"""
from typing import Optional, TypeVar, Callable, Any, List
from functools import wraps
import logging
import asyncio
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Retryable exceptions (transient errors that can be retried)
RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    OSError,
    IOError
)


def handle_backtest_error(
    default_return: Optional[T] = None,
    log_level: str = 'error'
) -> Callable:
    """
    Decorator for consistent error handling in backtest methods.
    
    Args:
        default_return: Value to return on error (default: None)
        log_level: Logging level ('error', 'warning', 'info', 'debug')
    
    Example:
        @handle_backtest_error(default_return=None, log_level='error')
        def _prepare_backtest_data(self, symbol: str) -> Optional[pd.DataFrame]:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_func = getattr(logger, log_level)
                log_func(f"Error in {func.__name__}: {e}", exc_info=True)
                return default_return
        return wrapper
    return decorator


def handle_backtest_error_async(
    default_return: Optional[T] = None,
    log_level: str = 'error'
) -> Callable:
    """
    Decorator for consistent error handling in async backtest methods.
    
    Args:
        default_return: Value to return on error (default: None)
        log_level: Logging level ('error', 'warning', 'info', 'debug')
    
    Example:
        @handle_backtest_error_async(default_return=None, log_level='error')
        async def run_backtest(self, symbol: str) -> Optional[BacktestMetrics]:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                log_func = getattr(logger, log_level)
                log_func(f"Error in {func.__name__}: {e}", exc_info=True)
                return default_return
        return wrapper
    return decorator


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple = RETRYABLE_EXCEPTIONS
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff
    ENHANCED: Retry logic for transient errors
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        retryable_exceptions: Tuple of exception types to retry
    
    Example:
        @retry_with_backoff(max_retries=3, initial_delay=1.0)
        async def fetch_data(symbol: str):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Retryable error in {func.__name__} (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        await asyncio.sleep(delay)
                        delay = min(delay * exponential_base, max_delay)
                    else:
                        logger.error(f"Max retries exceeded for {func.__name__}: {e}")
                        raise
                except Exception as e:
                    # Non-retryable exception, raise immediately
                    logger.error(f"Non-retryable error in {func.__name__}: {e}")
                    raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected error in {func.__name__}")
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Retryable error in {func.__name__} (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        time.sleep(delay)
                        delay = min(delay * exponential_base, max_delay)
                    else:
                        logger.error(f"Max retries exceeded for {func.__name__}: {e}")
                        raise
                except Exception as e:
                    # Non-retryable exception, raise immediately
                    logger.error(f"Non-retryable error in {func.__name__}: {e}")
                    raise
            
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected error in {func.__name__}")
        
        # Return appropriate wrapper based on whether function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class ErrorRecovery:
    """
    Error recovery utilities for backtesting
    ENHANCED: Comprehensive error recovery strategies
    """
    
    @staticmethod
    def should_retry(exception: Exception, max_retries: int, current_attempt: int) -> bool:
        """Determine if an error should be retried"""
        if current_attempt >= max_retries:
            return False
        
        # Retry transient errors
        if isinstance(exception, RETRYABLE_EXCEPTIONS):
            return True
        
        # Don't retry logic errors
        if isinstance(exception, (ValueError, TypeError, AttributeError)):
            return False
        
        # Default: don't retry
        return False
    
    @staticmethod
    def get_retry_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """Calculate retry delay with exponential backoff"""
        delay = base_delay * (2 ** attempt)
        return min(delay, max_delay)
    
    @staticmethod
    def create_fallback_result(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback result when backtest fails"""
        return {
            'success': False,
            'error': str(error),
            'error_type': type(error).__name__,
            'context': context,
            'metrics': None
        }

