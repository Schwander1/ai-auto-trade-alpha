#!/usr/bin/env python3
"""
Performance Monitor
Monitor and profile backtesting performance
ENHANCED: Performance monitoring and profiling utilities
"""
import time
import functools
import logging
from typing import Dict, Optional, Callable
from contextlib import contextmanager
from collections import defaultdict

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """
    Monitor backtesting performance
    ENHANCED: Comprehensive performance tracking
    """

    def __init__(self):
        self.metrics: Dict[str, list] = defaultdict(list)
        self.timings: Dict[str, list] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)

    @contextmanager
    def time_operation(self, operation_name: str):
        """Context manager to time an operation"""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start_time
            self.timings[operation_name].append(elapsed)
            logger.debug(f"⏱️  {operation_name}: {elapsed:.4f}s")

    def record_metric(self, metric_name: str, value: float):
        """Record a performance metric"""
        self.metrics[metric_name].append(value)

    def increment_counter(self, counter_name: str, amount: int = 1):
        """Increment a counter"""
        self.counters[counter_name] += amount

    def get_statistics(self) -> Dict:
        """Get performance statistics"""
        stats = {
            'timings': {},
            'metrics': {},
            'counters': dict(self.counters)
        }

        # Calculate timing statistics
        for operation, times in self.timings.items():
            if times:
                stats['timings'][operation] = {
                    'count': len(times),
                    'total': sum(times),
                    'average': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times)
                }

        # Calculate metric statistics
        for metric, values in self.metrics.items():
            if values:
                stats['metrics'][metric] = {
                    'count': len(values),
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }

        return stats

    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()
        self.timings.clear()
        self.counters.clear()

    def log_summary(self):
        """Log performance summary"""
        stats = self.get_statistics()

        logger.info("📊 Performance Summary:")
        logger.info("=" * 50)

        if stats['timings']:
            logger.info("⏱️  Timings:")
            for operation, timing_stats in stats['timings'].items():
                logger.info(f"  {operation}:")
                logger.info(f"    Count: {timing_stats['count']}")
                logger.info(f"    Total: {timing_stats['total']:.4f}s")
                logger.info(f"    Average: {timing_stats['average']:.4f}s")
                logger.info(f"    Min: {timing_stats['min']:.4f}s")
                logger.info(f"    Max: {timing_stats['max']:.4f}s")

        if stats['counters']:
            logger.info("🔢 Counters:")
            for counter, value in stats['counters'].items():
                logger.info(f"  {counter}: {value}")

        logger.info("=" * 50)


def profile_backtest(func: Callable) -> Callable:
    """
    Decorator to profile a backtest function
    ENHANCED: Automatic performance profiling
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        monitor = PerformanceMonitor()

        # Store monitor in function context if possible
        if hasattr(args[0], '_performance_monitor'):
            args[0]._performance_monitor = monitor

        with monitor.time_operation(f"{func.__name__}_total"):
            result = await func(*args, **kwargs)

        monitor.log_summary()
        return result

    return wrapper


# Global performance monitor instance
_global_monitor = PerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    return _global_monitor
