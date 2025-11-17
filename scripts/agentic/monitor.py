#!/usr/bin/env python3
"""
Monitor agentic feature usage and performance
Usage: python scripts/agentic/monitor.py [command]
"""

import os
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Callable, Any
from dataclasses import dataclass, asdict
from functools import wraps

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


@dataclass
class AgenticMetric:
    """Metric for agentic operation"""
    tool: str  # "copilot", "claude", "cursor"
    operation: str  # "deploy", "refactor", "debug"
    duration: float
    success: bool
    cost: Optional[float] = None
    tokens_used: Optional[int] = None
    error: Optional[str] = None


class AgenticMonitor:
    """Monitor agentic feature usage"""
    
    def __init__(self, log_file: Optional[Path] = None):
        if log_file is None:
            workspace_dir = Path(__file__).parent.parent.parent
            log_file = workspace_dir / "logs" / "agentic_metrics.jsonl"
        
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize Prometheus metrics if available
        if PROMETHEUS_AVAILABLE:
            self.requests_counter = Counter(
                'agentic_requests_total',
                'Total agentic API requests',
                ['tool', 'operation', 'status']
            )
            self.duration_histogram = Histogram(
                'agentic_duration_seconds',
                'Agentic operation duration',
                ['tool', 'operation']
            )
            self.cost_gauge = Gauge(
                'agentic_cost_usd',
                'Total cost of agentic operations',
                ['tool']
            )
    
    def log_metric(self, metric: AgenticMetric):
        """Log a metric"""
        entry = {
            **asdict(metric),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        # Export to Prometheus if available
        if PROMETHEUS_AVAILABLE:
            status = "success" if metric.success else "failure"
            self.requests_counter.labels(
                tool=metric.tool,
                operation=metric.operation,
                status=status
            ).inc()
            
            self.duration_histogram.labels(
                tool=metric.tool,
                operation=metric.operation
            ).observe(metric.duration)
            
            if metric.cost:
                self.cost_gauge.labels(tool=metric.tool).set(metric.cost)
    
    def track_operation(
        self,
        tool: str,
        operation: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Track an agentic operation"""
        start_time = time.time()
        cost = None
        tokens_used = None
        error = None
        success = False
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            success = True
            
            # Try to extract cost/tokens from result if available
            if isinstance(result, dict):
                cost = result.get("cost")
                tokens_used = result.get("tokens_used") or result.get("total_tokens")
            
            metric = AgenticMetric(
                tool=tool,
                operation=operation,
                duration=duration,
                success=success,
                cost=cost,
                tokens_used=tokens_used
            )
            self.log_metric(metric)
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            error = str(e)
            
            metric = AgenticMetric(
                tool=tool,
                operation=operation,
                duration=duration,
                success=False,
                error=error
            )
            self.log_metric(metric)
            raise
    
    def get_stats(self, days: int = 7) -> dict:
        """Get statistics for the last N days"""
        if not self.log_file.exists():
            return {
                "total_operations": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "total_cost": 0.0,
                "by_tool": {},
                "by_operation": {}
            }
        
        from datetime import timedelta
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        total_ops = 0
        successful_ops = 0
        total_duration = 0.0
        total_cost = 0.0
        by_tool = {}
        by_operation = {}
        
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_date_str = entry["timestamp"]
                    # Handle both timezone-aware and naive datetimes
                    if entry_date_str.endswith('Z'):
                        entry_date_str = entry_date_str[:-1] + '+00:00'
                    entry_date = datetime.fromisoformat(entry_date_str.replace('Z', '+00:00'))
                    # Make timezone-aware if needed
                    if entry_date.tzinfo is None:
                        entry_date = entry_date.replace(tzinfo=timezone.utc)
                    
                    if entry_date < cutoff_date:
                        continue
                    
                    total_ops += 1
                    if entry["success"]:
                        successful_ops += 1
                    
                    total_duration += entry["duration"]
                    if entry.get("cost"):
                        total_cost += entry["cost"]
                    
                    tool = entry["tool"]
                    if tool not in by_tool:
                        by_tool[tool] = {"count": 0, "success": 0, "cost": 0.0}
                    by_tool[tool]["count"] += 1
                    if entry["success"]:
                        by_tool[tool]["success"] += 1
                    if entry.get("cost"):
                        by_tool[tool]["cost"] += entry.get("cost", 0)
                    
                    operation = entry["operation"]
                    if operation not in by_operation:
                        by_operation[operation] = {"count": 0, "success": 0}
                    by_operation[operation]["count"] += 1
                    if entry["success"]:
                        by_operation[operation]["success"] += 1
                        
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return {
            "total_operations": total_ops,
            "success_rate": (successful_ops / total_ops * 100) if total_ops > 0 else 0.0,
            "avg_duration": (total_duration / total_ops) if total_ops > 0 else 0.0,
            "total_cost": round(total_cost, 2),
            "by_tool": by_tool,
            "by_operation": by_operation,
            "period_days": days
        }
    
    def report(self, days: int = 7):
        """Print monitoring report"""
        stats = self.get_stats(days)
        
        print("=" * 60)
        print(f"Agentic Features Monitoring Report (Last {days} days)")
        print("=" * 60)
        print(f"Total Operations: {stats['total_operations']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print(f"Average Duration: {stats['avg_duration']:.2f}s")
        print(f"Total Cost: ${stats['total_cost']:.2f}")
        print()
        
        if stats['by_tool']:
            print("By Tool:")
            for tool, data in stats['by_tool'].items():
                success_rate = (data['success'] / data['count'] * 100) if data['count'] > 0 else 0
                print(f"  {tool}:")
                print(f"    Operations: {data['count']}")
                print(f"    Success Rate: {success_rate:.1f}%")
                print(f"    Cost: ${data['cost']:.2f}")
            print()
        
        if stats['by_operation']:
            print("By Operation:")
            for operation, data in stats['by_operation'].items():
                success_rate = (data['success'] / data['count'] * 100) if data['count'] > 0 else 0
                print(f"  {operation}:")
                print(f"    Operations: {data['count']}")
                print(f"    Success Rate: {success_rate:.1f}%")
        
        print("=" * 60)


# Decorator for easy tracking
def track_agentic(tool: str, operation: str):
    """Decorator to track agentic operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = AgenticMonitor()
            return monitor.track_operation(tool, operation, func, *args, **kwargs)
        return wrapper
    return decorator


def main():
    monitor = AgenticMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "report":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            monitor.report(days)
        elif command == "stats":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            stats = monitor.get_stats(days)
            print(json.dumps(stats, indent=2))
        else:
            print(f"Unknown command: {command}")
            print("Available commands: report, stats")
            sys.exit(1)
    else:
        # Default: show report
        monitor.report(7)


if __name__ == "__main__":
    main()

