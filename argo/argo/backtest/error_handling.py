#!/usr/bin/env python3
"""
Error Handling Utilities
Standardized error handling patterns for backtesting
"""
from typing import Optional, TypeVar, Callable, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


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

