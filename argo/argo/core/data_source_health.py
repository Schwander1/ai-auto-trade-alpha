#!/usr/bin/env python3
"""
Data Source Health Monitoring
Tracks health status of all data sources for observability
"""
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Optional, List
from prometheus_client import Gauge, Counter, Histogram
from collections import defaultdict

logger = logging.getLogger(__name__)

# Prometheus metrics for data source health
data_source_status = Gauge(
    'argo_data_source_status',
    'Data source health status (1=healthy, 0=unhealthy)',
    ['source_name']
)

data_source_errors_total = Counter(
    'argo_data_source_errors_total',
    'Total errors from data source',
    ['source_name', 'error_type']
)

data_source_request_duration = Histogram(
    'argo_data_source_request_duration_seconds',
    'Data source request duration',
    ['source_name'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

data_source_success_rate = Gauge(
    'argo_data_source_success_rate',
    'Data source success rate (0-1)',
    ['source_name']
)

class DataSourceHealthMonitor:
    """Monitor health of all data sources"""
    
    def __init__(self):
        self.health_status: Dict[str, Dict] = {}
        self.error_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.success_counts: Dict[str, int] = defaultdict(int)
        self.total_requests: Dict[str, int] = defaultdict(int)
        self.last_success: Dict[str, float] = {}
        self.last_error: Dict[str, float] = {}
        self.consecutive_failures: Dict[str, int] = defaultdict(int)
        
        # Health thresholds
        self.max_consecutive_failures = 5
        self.max_time_since_success = 300  # 5 minutes
        
    def record_success(self, source_name: str, duration: float = None):
        """Record successful request from data source"""
        now = time.time()
        self.health_status[source_name] = {
            'status': 'healthy',
            'last_success': now,
            'last_check': now,
            'consecutive_failures': 0
        }
        self.success_counts[source_name] += 1
        self.total_requests[source_name] += 1
        self.last_success[source_name] = now
        self.consecutive_failures[source_name] = 0
        
        # Update Prometheus metrics
        data_source_status.labels(source_name=source_name).set(1)
        if duration is not None:
            data_source_request_duration.labels(source_name=source_name).observe(duration)
        
        # Calculate success rate
        if self.total_requests[source_name] > 0:
            rate = self.success_counts[source_name] / self.total_requests[source_name]
            data_source_success_rate.labels(source_name=source_name).set(rate)
    
    def record_error(self, source_name: str, error_type: str, duration: float = None):
        """Record error from data source"""
        now = time.time()
        self.error_counts[source_name][error_type] += 1
        self.total_requests[source_name] += 1
        self.last_error[source_name] = now
        self.consecutive_failures[source_name] += 1
        
        # Update health status
        is_healthy = self.consecutive_failures[source_name] < self.max_consecutive_failures
        self.health_status[source_name] = {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'last_success': self.last_success.get(source_name, 0),
            'last_error': now,
            'last_check': now,
            'consecutive_failures': self.consecutive_failures[source_name],
            'error_type': error_type
        }
        
        # Update Prometheus metrics
        data_source_status.labels(source_name=source_name).set(1 if is_healthy else 0)
        data_source_errors_total.labels(source_name=source_name, error_type=error_type).inc()
        if duration is not None:
            data_source_request_duration.labels(source_name=source_name).observe(duration)
        
        # Calculate success rate
        if self.total_requests[source_name] > 0:
            rate = self.success_counts[source_name] / self.total_requests[source_name]
            data_source_success_rate.labels(source_name=source_name).set(rate)
        
        # Log warning if unhealthy
        if not is_healthy:
            logger.warning(
                f"⚠️  Data source {source_name} is UNHEALTHY: "
                f"{self.consecutive_failures[source_name]} consecutive failures"
            )
    
    def get_health_status(self, source_name: Optional[str] = None) -> Dict:
        """Get health status for source(s)"""
        if source_name:
            return self.health_status.get(source_name, {
                'status': 'unknown',
                'last_check': 0
            })
        
        # Check all sources for staleness
        now = time.time()
        for name, status in self.health_status.items():
            time_since_success = now - status.get('last_success', 0)
            if time_since_success > self.max_time_since_success and status['status'] == 'healthy':
                status['status'] = 'degraded'
                status['reason'] = f'No success in {int(time_since_success)}s'
                data_source_status.labels(source_name=name).set(0.5)
        
        return self.health_status
    
    def get_summary(self) -> Dict:
        """Get health summary for all sources"""
        healthy = sum(1 for s in self.health_status.values() if s['status'] == 'healthy')
        unhealthy = sum(1 for s in self.health_status.values() if s['status'] == 'unhealthy')
        degraded = sum(1 for s in self.health_status.values() if s['status'] == 'degraded')
        total = len(self.health_status)
        
        return {
            'total_sources': total,
            'healthy': healthy,
            'unhealthy': unhealthy,
            'degraded': degraded,
            'sources': self.health_status
        }
    
    def reset_counters(self, source_name: Optional[str] = None):
        """Reset counters for a source or all sources"""
        if source_name:
            self.error_counts[source_name].clear()
            self.success_counts[source_name] = 0
            self.total_requests[source_name] = 0
            self.consecutive_failures[source_name] = 0
        else:
            self.error_counts.clear()
            self.success_counts.clear()
            self.total_requests.clear()
            self.consecutive_failures.clear()


# Global instance
_health_monitor = None

def get_health_monitor() -> DataSourceHealthMonitor:
    """Get global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = DataSourceHealthMonitor()
    return _health_monitor

