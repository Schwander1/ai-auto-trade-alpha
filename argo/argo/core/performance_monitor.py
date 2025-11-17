#!/usr/bin/env python3
"""
Performance Monitoring and Metrics Collection
Tracks system performance metrics for optimization and monitoring
"""
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    timestamp: datetime
    unit: str = "ms"
    metadata: Optional[Dict] = None

class PerformanceMonitor:
    """Monitor and track performance metrics"""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.counters: Dict[str, int] = defaultdict(int)
        self.timers: Dict[str, float] = {}
        self.log_file = Path(__file__).parent.parent.parent / "logs" / "performance.json"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def record_metric(self, name: str, value: float, unit: str = "ms", metadata: Optional[Dict] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            unit=unit,
            metadata=metadata
        )
        self.metrics[name].append(metric)

    def start_timer(self, name: str):
        """Start a performance timer"""
        self.timers[name] = time.time()

    def end_timer(self, name: str, record: bool = True) -> float:
        """End a performance timer and optionally record the metric"""
        if name not in self.timers:
            logger.warning(f"Timer '{name}' was not started")
            return 0.0

        elapsed = (time.time() - self.timers[name]) * 1000  # Convert to ms
        del self.timers[name]

        if record:
            self.record_metric(name, elapsed, unit="ms")

        return elapsed

    def increment_counter(self, name: str, value: int = 1):
        """Increment a counter"""
        self.counters[name] += value

    def get_metric_stats(self, name: str, hours: int = 24) -> Optional[Dict]:
        """Get statistics for a metric"""
        if name not in self.metrics:
            return None

        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics[name]
            if m.timestamp >= cutoff_time
        ]

        if not recent_metrics:
            return None

        values = [m.value for m in recent_metrics]

        return {
            'name': name,
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'median': sorted(values)[len(values) // 2],
            'p95': sorted(values)[int(len(values) * 0.95)] if len(values) > 20 else max(values),
            'p99': sorted(values)[int(len(values) * 0.99)] if len(values) > 100 else max(values),
            'unit': recent_metrics[0].unit
        }

    def get_all_stats(self, hours: int = 24) -> Dict:
        """Get statistics for all metrics"""
        stats = {}
        for metric_name in self.metrics.keys():
            stat = self.get_metric_stats(metric_name, hours)
            if stat:
                stats[metric_name] = stat

        return {
            'timestamp': datetime.now().isoformat(),
            'period_hours': hours,
            'metrics': stats,
            'counters': dict(self.counters)
        }

    def export_metrics(self, hours: int = 24) -> Dict:
        """Export metrics for analysis"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        exported = {}
        for name, metrics_deque in self.metrics.items():
            recent = [
                asdict(m) for m in metrics_deque
                if m.timestamp >= cutoff_time
            ]
            if recent:
                exported[name] = recent

        return {
            'timestamp': datetime.now().isoformat(),
            'period_hours': hours,
            'metrics': exported,
            'counters': dict(self.counters)
        }

    def save_to_file(self, hours: int = 24):
        """Save metrics to file"""
        try:
            data = self.export_metrics(hours)
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug(f"Performance metrics saved to {self.log_file}")
        except Exception as e:
            logger.error(f"Error saving performance metrics: {e}")

# Global instance
_performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
