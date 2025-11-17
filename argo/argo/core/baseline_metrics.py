#!/usr/bin/env python3
"""
Baseline Metrics Collection System
Captures comprehensive system state for before/after comparison
"""
import json
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class BaselineMetrics:
    """Comprehensive baseline metrics snapshot"""
    timestamp: str
    version: str
    
    # Performance Metrics
    signal_generation_avg_ms: float
    signal_generation_p95_ms: float
    signal_generation_p99_ms: float
    api_calls_per_cycle: float
    cache_hit_rate: float
    data_source_latencies: Dict[str, float]
    
    # Cost Metrics
    api_costs_daily: Dict[str, float]
    api_calls_daily: Dict[str, int]
    estimated_monthly_cost: float
    
    # Quality Metrics
    signal_quality_score: float
    data_quality_issues: int
    error_rate: float
    
    # Risk Metrics (if prop firm enabled)
    risk_breaches_prevented: int
    avg_position_size: float
    max_drawdown: float
    
    # System Health
    uptime_percentage: float
    error_count_by_type: Dict[str, int]
    data_source_health: Dict[str, float]

class BaselineCollector:
    """Collect and store baseline metrics"""
    
    def __init__(self, output_dir: Path = None):
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "baselines"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def collect_baseline(self, duration_minutes: int = 60, version: str = "pre-enhancement") -> BaselineMetrics:
        """
        Collect baseline metrics over specified duration.
        
        Args:
            duration_minutes: How long to collect metrics (default 60 minutes)
            version: Version identifier for this baseline
            
        Returns:
            BaselineMetrics object with collected data
        """
        logger.info(f"🔍 Starting baseline collection for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Initialize collectors
        try:
            from argo.core.performance_metrics import get_performance_metrics
            perf_metrics = get_performance_metrics()
        except ImportError:
            logger.warning("Performance metrics not available, using mock")
            perf_metrics = None
            
        try:
            from argo.core.enhanced_metrics import get_enhanced_metrics
            enhanced_metrics = get_enhanced_metrics()
        except ImportError:
            logger.warning("Enhanced metrics not available, using mock")
            enhanced_metrics = None
        
        # Collect metrics during observation period
        samples = []
        sample_count = 0
        while time.time() < end_time:
            sample = await self._collect_sample(perf_metrics, enhanced_metrics)
            samples.append(sample)
            sample_count += 1
            logger.info(f"📊 Collected sample {sample_count}/{duration_minutes}")
            await asyncio.sleep(60)  # Sample every minute
            
        # Calculate aggregated metrics
        baseline = self._aggregate_samples(samples, version)
        
        # Save baseline
        baseline_file = self.output_dir / f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(baseline_file, 'w') as f:
            json.dump(asdict(baseline), f, indent=2)
            
        logger.info(f"✅ Baseline saved to {baseline_file}")
        return baseline
        
    async def _collect_sample(self, perf_metrics, enhanced_metrics) -> Dict:
        """Collect a single sample of metrics"""
        sample = {
            'timestamp': datetime.now().isoformat(),
            'signal_times': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'api_calls': 0,
            'errors': {},
            'latencies': {}
        }
        
        if perf_metrics:
            try:
                sample['signal_times'] = list(perf_metrics.metrics.get('signal_generation_times', []))
                sample['cache_hits'] = perf_metrics.metrics.get('cache_hits', 0)
                sample['cache_misses'] = perf_metrics.metrics.get('cache_misses', 0)
                sample['api_calls'] = len(perf_metrics.metrics.get('api_calls_per_cycle', []))
                sample['errors'] = dict(perf_metrics.metrics.get('errors', {}))
                sample['latencies'] = {
                    source: list(times) 
                    for source, times in perf_metrics.metrics.get('data_source_latencies', {}).items()
                }
            except Exception as e:
                logger.warning(f"Error collecting performance metrics: {e}")
                
        return sample
        
    def _aggregate_samples(self, samples: List[Dict], version: str) -> BaselineMetrics:
        """Aggregate samples into baseline metrics"""
        if not samples:
            # Return empty baseline if no samples
            return BaselineMetrics(
                timestamp=datetime.now().isoformat(),
                version=version,
                signal_generation_avg_ms=0.0,
                signal_generation_p95_ms=0.0,
                signal_generation_p99_ms=0.0,
                api_calls_per_cycle=0.0,
                cache_hit_rate=0.0,
                data_source_latencies={},
                api_costs_daily={},
                api_calls_daily={},
                estimated_monthly_cost=0.0,
                signal_quality_score=0.0,
                data_quality_issues=0,
                error_rate=0.0,
                risk_breaches_prevented=0,
                avg_position_size=0.0,
                max_drawdown=0.0,
                uptime_percentage=100.0,
                error_count_by_type={},
                data_source_health={}
            )
        
        # Aggregate signal generation times
        all_signal_times = []
        for sample in samples:
            all_signal_times.extend(sample.get('signal_times', []))
            
        signal_times_ms = [t * 1000 for t in all_signal_times] if all_signal_times else [0]
        signal_times_ms.sort()
        
        # Calculate percentiles
        n = len(signal_times_ms)
        p95_idx = int(n * 0.95) if n > 0 else 0
        p99_idx = int(n * 0.99) if n > 0 else 0
        
        # Aggregate cache metrics
        total_hits = sum(s.get('cache_hits', 0) for s in samples)
        total_misses = sum(s.get('cache_misses', 0) for s in samples)
        cache_hit_rate = total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0
        
        # Aggregate API calls
        avg_api_calls = sum(s.get('api_calls', 0) for s in samples) / len(samples) if samples else 0
        
        # Aggregate latencies
        source_latencies = {}
        for sample in samples:
            for source, times in sample.get('latencies', {}).items():
                if source not in source_latencies:
                    source_latencies[source] = []
                source_latencies[source].extend(times)
                
        avg_latencies = {
            source: sum(times) / len(times) if times else 0
            for source, times in source_latencies.items()
        }
        
        # Aggregate errors
        error_counts = {}
        for sample in samples:
            for error_key, count in sample.get('errors', {}).items():
                error_counts[error_key] = error_counts.get(error_key, 0) + count
        
        return BaselineMetrics(
            timestamp=datetime.now().isoformat(),
            version=version,
            signal_generation_avg_ms=sum(signal_times_ms) / len(signal_times_ms) if signal_times_ms else 0,
            signal_generation_p95_ms=signal_times_ms[p95_idx] if signal_times_ms and p95_idx < len(signal_times_ms) else 0,
            signal_generation_p99_ms=signal_times_ms[p99_idx] if signal_times_ms and p99_idx < len(signal_times_ms) else 0,
            api_calls_per_cycle=avg_api_calls,
            cache_hit_rate=cache_hit_rate,
            data_source_latencies=avg_latencies,
            api_costs_daily={},  # Will be populated by cost tracker
            api_calls_daily={},  # Will be populated by cost tracker
            estimated_monthly_cost=0.0,
            signal_quality_score=0.0,  # Will be populated by quality validator
            data_quality_issues=0,
            error_rate=sum(error_counts.values()) / len(samples) if samples else 0.0,
            risk_breaches_prevented=0,
            avg_position_size=0.0,
            max_drawdown=0.0,
            uptime_percentage=100.0,
            error_count_by_type=error_counts,
            data_source_health={}
        )

# CLI for baseline collection
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect baseline metrics")
    parser.add_argument("--duration", type=int, default=60, help="Duration in minutes")
    parser.add_argument("--version", type=str, default="pre-enhancement", help="Version identifier")
    parser.add_argument("--output", type=str, help="Output directory for baselines")
    args = parser.parse_args()
    
    output_dir = Path(args.output) if args.output else None
    collector = BaselineCollector(output_dir=output_dir)
    asyncio.run(collector.collect_baseline(args.duration, args.version))

