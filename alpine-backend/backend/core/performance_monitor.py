"""
Performance Monitoring Utilities
Provides query performance tracking and monitoring.
"""
import time
import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps
from contextlib import contextmanager
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and track performance metrics"""

    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.thresholds: Dict[str, float] = {
            "query": 1.0,  # 1 second
            "api_call": 2.0,  # 2 seconds
            "cache_operation": 0.1,  # 100ms
        }

    def record_metric(self, operation: str, duration: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a performance metric.

        Args:
            operation: Operation name (e.g., "query", "api_call")
            duration: Duration in seconds
            metadata: Optional metadata dictionary
        """
        if operation not in self.metrics:
            self.metrics[operation] = []

        metric = {
            "duration": duration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }

        self.metrics[operation].append(metric)

        # Check threshold
        threshold = self.thresholds.get(operation)
        if threshold and duration > threshold:
            logger.warning(
                f"Slow {operation}: {duration:.3f}s (threshold: {threshold}s) | "
                f"Metadata: {metadata}"
            )

    def get_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics.

        Args:
            operation: Operation name (None for all operations)

        Returns:
            Statistics dictionary
        """
        if operation:
            metrics = self.metrics.get(operation, [])
        else:
            metrics = [m for metrics_list in self.metrics.values() for m in metrics_list]

        if not metrics:
            return {}

        durations = [m["duration"] for m in metrics]

        return {
            "count": len(durations),
            "min": min(durations),
            "max": max(durations),
            "avg": sum(durations) / len(durations),
            "p50": sorted(durations)[len(durations) // 2],
            "p95": sorted(durations)[int(len(durations) * 0.95)],
            "p99": sorted(durations)[int(len(durations) * 0.99)]
        }

    def reset(self, operation: Optional[str] = None) -> None:
        """Reset metrics for operation or all operations"""
        if operation:
            self.metrics[operation] = []
        else:
            self.metrics.clear()


# Global performance monitor instance
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    return _performance_monitor


@contextmanager
def measure_performance(operation: str, metadata: Optional[Dict[str, Any]] = None):
    """
    Context manager for measuring performance.

    Args:
        operation: Operation name
        metadata: Optional metadata

    Example:
        ```python
        with measure_performance("database_query", {"table": "signals"}):
            result = db.query(Signal).all()
        ```
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        _performance_monitor.record_metric(operation, duration, metadata)


def monitor_performance(operation: str, metadata: Optional[Dict[str, Any]] = None):
    """
    Decorator for measuring function performance.

    Args:
        operation: Operation name
        metadata: Optional metadata

    Example:
        ```python
        @monitor_performance("get_signals", {"endpoint": "/api/signals"})
        def get_signals():
            return db.query(Signal).all()
        ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with measure_performance(operation, metadata):
                return func(*args, **kwargs)
        return wrapper

    return decorator


async def monitor_performance_async(operation: str, metadata: Optional[Dict[str, Any]] = None):
    """
    Decorator for measuring async function performance.

    Args:
        operation: Operation name
        metadata: Optional metadata

    Example:
        ```python
        @monitor_performance_async("fetch_signals")
        async def fetch_signals():
            return await db.query(Signal).all()
        ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with measure_performance(operation, metadata):
                return await func(*args, **kwargs)
        return wrapper

    return decorator
