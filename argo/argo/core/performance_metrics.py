#!/usr/bin/env python3
"""
Performance Metrics and Benchmarks
Tracks optimization improvements and system performance
"""
import time
import logging
from typing import Dict, List, Optional
from collections import defaultdict, deque
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class PerformanceMetrics:
    """Track performance metrics for optimization monitoring"""
    
    def __init__(self):
        self.metrics = {
            'signal_generation_times': deque(maxlen=100),  # Last 100 cycles
            'api_calls_per_cycle': deque(maxlen=100),
            'cache_hits': 0,
            'cache_misses': 0,
            'skipped_symbols': 0,
            'total_symbols_processed': 0,
            'data_source_latencies': defaultdict(lambda: deque(maxlen=50)),
            'errors': defaultdict(int),
        }
        self.start_time = time.time()
    
    def record_signal_generation_time(self, duration: float):
        """Record signal generation cycle duration"""
        self.metrics['signal_generation_times'].append(duration)
    
    def record_api_call(self, source: str, duration: float):
        """Record API call with latency"""
        self.metrics['api_calls_per_cycle'].append(1)
        self.metrics['data_source_latencies'][source].append(duration)
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.metrics['cache_hits'] += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.metrics['cache_misses'] += 1
    
    def record_skipped_symbol(self):
        """Record skipped symbol (unchanged)"""
        self.metrics['skipped_symbols'] += 1
    
    def record_symbol_processed(self):
        """Record symbol processed"""
        self.metrics['total_symbols_processed'] += 1
    
    def record_error(self, source: str, error_type: str):
        """Record error"""
        self.metrics['errors'][f"{source}:{error_type}"] += 1
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.metrics['cache_hits'] + self.metrics['cache_misses']
        if total == 0:
            return 0.0
        return (self.metrics['cache_hits'] / total) * 100
    
    def get_avg_signal_generation_time(self) -> float:
        """Get average signal generation time"""
        times = self.metrics['signal_generation_times']
        if not times:
            return 0.0
        return sum(times) / len(times)
    
    def get_avg_api_latency(self, source: Optional[str] = None) -> float:
        """Get average API latency"""
        if source:
            latencies = self.metrics['data_source_latencies'].get(source, deque())
        else:
            # Average across all sources
            all_latencies = []
            for latencies in self.metrics['data_source_latencies'].values():
                all_latencies.extend(latencies)
            latencies = all_latencies
        
        if not latencies:
            return 0.0
        return sum(latencies) / len(latencies)
    
    def get_skip_rate(self) -> float:
        """Get symbol skip rate"""
        total = self.metrics['total_symbols_processed']
        if total == 0:
            return 0.0
        return (self.metrics['skipped_symbols'] / total) * 100
    
    def get_summary(self) -> Dict:
        """Get performance summary"""
        return {
            'uptime_seconds': time.time() - self.start_time,
            'avg_signal_generation_time': self.get_avg_signal_generation_time(),
            'cache_hit_rate': self.get_cache_hit_rate(),
            'skip_rate': self.get_skip_rate(),
            'total_cache_hits': self.metrics['cache_hits'],
            'total_cache_misses': self.metrics['cache_misses'],
            'total_skipped_symbols': self.metrics['skipped_symbols'],
            'total_symbols_processed': self.metrics['total_symbols_processed'],
            'avg_api_latency': self.get_avg_api_latency(),
            'errors': dict(self.metrics['errors']),
            'data_source_latencies': {
                source: self.get_avg_api_latency(source)
                for source in self.metrics['data_source_latencies'].keys()
            }
        }

# Global metrics instance
_metrics_instance = None

def get_performance_metrics() -> PerformanceMetrics:
    """Get global performance metrics instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = PerformanceMetrics()
    return _metrics_instance

