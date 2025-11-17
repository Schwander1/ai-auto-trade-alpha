#!/usr/bin/env python3
"""
Performance Budget Monitor
Monitors operation performance against defined budgets.
Alerts when operations exceed performance budgets.
"""
import time
import logging
from dataclasses import dataclass
from typing import Dict, List
from collections import defaultdict, deque
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@dataclass
class PerformanceBudget:
    operation: str
    max_duration_ms: float
    percentile_95_ms: float
    percentile_99_ms: float

class PerformanceMonitor:
    """
    Monitors operation performance against defined budgets.
    Alerts when operations exceed performance budgets.
    """
    def __init__(self, config=None):
        # Load budgets from config if available, otherwise use defaults
        if config and 'enhancements' in config and 'performance_budgets' in config['enhancements']:
            perf_config = config['enhancements']['performance_budgets']
            signal_max = perf_config.get('signal_generation_max_ms', 10000)
            risk_max = perf_config.get('risk_check_max_ms', 50)
            order_max = perf_config.get('order_execution_max_ms', 100)
            fetch_max = perf_config.get('data_source_fetch_max_ms', 5000)
        else:
            # Default values (realistic targets)
            signal_max = 10000  # 10 seconds (was 500ms - too strict)
            risk_max = 50
            order_max = 100
            fetch_max = 5000  # 5 seconds (was 200ms - too strict)
        
        self.budgets = {
            "signal_generation": PerformanceBudget(
                operation="signal_generation",
                max_duration_ms=signal_max,
                percentile_95_ms=signal_max * 0.6,
                percentile_99_ms=signal_max * 0.8
            ),
            "risk_check": PerformanceBudget(
                operation="risk_check",
                max_duration_ms=risk_max,
                percentile_95_ms=risk_max * 0.6,
                percentile_99_ms=risk_max * 0.8
            ),
            "order_execution": PerformanceBudget(
                operation="order_execution",
                max_duration_ms=order_max,
                percentile_95_ms=order_max * 0.6,
                percentile_99_ms=order_max * 0.8
            ),
            "data_source_fetch": PerformanceBudget(
                operation="data_source_fetch",
                max_duration_ms=fetch_max,
                percentile_95_ms=fetch_max * 0.6,
                percentile_99_ms=fetch_max * 0.8
            )
        }
        self.measurements: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.violations: Dict[str, int] = defaultdict(int)
        
    @contextmanager
    def measure(self, operation: str):
        """
        Context manager for measuring operation performance.
        Usage:
            with perf_monitor.measure("signal_generation"):
                signal = await generate_signal()
        """
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.record_measurement(operation, duration_ms)
            
    def record_measurement(self, operation: str, duration_ms: float):
        """Record a performance measurement"""
        if operation not in self.budgets:
            logger.warning(f"No budget defined for operation: {operation}")
            return
            
        self.measurements[operation].append(duration_ms)
        
        # Check against budget
        budget = self.budgets[operation]
        if duration_ms > budget.max_duration_ms:
            self.violations[operation] += 1
            logger.warning(
                f"⚠️  Performance budget exceeded for {operation}: "
                f"{duration_ms:.2f}ms > {budget.max_duration_ms}ms"
            )
            
    def get_statistics(self, operation: str) -> Dict:
        """Get performance statistics for an operation"""
        if operation not in self.measurements or not self.measurements[operation]:
            return {}
            
        measurements = sorted(self.measurements[operation])
        count = len(measurements)
        
        if count == 0:
            return {}
            
        p95_idx = int(count * 0.95) if count > 20 else count - 1
        p99_idx = int(count * 0.99) if count > 100 else count - 1
        
        budget = self.budgets.get(operation)
        
        return {
            "count": count,
            "mean_ms": sum(measurements) / count,
            "median_ms": measurements[count // 2],
            "p95_ms": measurements[p95_idx] if p95_idx < count else measurements[-1],
            "p99_ms": measurements[p99_idx] if p99_idx < count else measurements[-1],
            "max_ms": measurements[-1],
            "min_ms": measurements[0],
            "budget_max_ms": budget.max_duration_ms if budget else None,
            "budget_violations": self.violations.get(operation, 0),
            "budget_violation_rate": (self.violations.get(operation, 0) / count * 100) if count > 0 else 0
        }
        
    def get_all_statistics(self) -> Dict[str, Dict]:
        """Get statistics for all operations"""
        return {
            operation: self.get_statistics(operation)
            for operation in self.budgets.keys()
        }
        
    def reset(self):
        """Reset all measurements"""
        self.measurements.clear()
        self.violations.clear()

# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor(config=None, force_reload=False) -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None or force_reload or config:
        # If config provided, always recreate to use new values
        _performance_monitor = PerformanceMonitor(config=config)
    return _performance_monitor

