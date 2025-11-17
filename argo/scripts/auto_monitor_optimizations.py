#!/usr/bin/env python3
"""
Automated Optimization Monitor & Rollback System
Monitors system health after enabling optimizations and automatically rolls back if issues detected
"""
import sys
import time
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.core.feature_flags import get_feature_flags

# Import health checker with proper path handling
try:
    from argo.scripts.health_check_unified import UnifiedHealthChecker
except ImportError:
    # Fallback: import directly
    import importlib.util
    health_check_path = Path(__file__).parent / "health_check_unified.py"
    spec = importlib.util.spec_from_file_location("health_check_unified", health_check_path)
    health_check_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(health_check_module)
    UnifiedHealthChecker = health_check_module.UnifiedHealthChecker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MonitoringThresholds:
    """Thresholds for automatic rollback"""
    max_error_rate: float = 0.10  # 10% error rate triggers rollback
    min_health_score: float = 0.70  # 70% health score minimum
    max_signal_generation_time: float = 2.0  # 2 seconds max
    min_signal_count_per_hour: int = 1  # At least 1 signal per hour
    max_consecutive_failures: int = 3  # 3 consecutive failures = rollback

class AutoOptimizationMonitor:
    """Automated monitoring and rollback system"""
    
    def __init__(
        self,
        check_interval: int = 60,  # Check every 60 seconds
        monitoring_duration: int = 3600,  # Monitor for 1 hour
        auto_rollback: bool = True,
        thresholds: Optional[MonitoringThresholds] = None
    ):
        self.check_interval = check_interval
        self.monitoring_duration = monitoring_duration
        self.auto_rollback = auto_rollback
        self.thresholds = thresholds or MonitoringThresholds()
        
        self.start_time = datetime.now()
        self.health_checks: List[Dict] = []
        self.consecutive_failures = 0
        self.rollback_triggered = False
        
    def check_health(self) -> Dict:
        """Run health check and return results"""
        try:
            checker = UnifiedHealthChecker(level=2)
            results = checker.run_all_checks()
            
            # Calculate health score
            total_checks = len(results)
            passed_checks = sum(1 for r in results.values() if r.get('status') == 'healthy')
            health_score = passed_checks / total_checks if total_checks > 0 else 0.0
            
            # Check for errors
            error_count = sum(1 for r in results.values() if r.get('status') == 'unhealthy')
            error_rate = error_count / total_checks if total_checks > 0 else 0.0
            
            return {
                'timestamp': datetime.now().isoformat(),
                'health_score': health_score,
                'error_rate': error_rate,
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'failed_checks': error_count,
                'results': results,
                'healthy': health_score >= self.thresholds.min_health_score and error_rate < self.thresholds.max_error_rate
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'health_score': 0.0,
                'error_rate': 1.0,
                'healthy': False,
                'error': str(e)
            }
    
    def check_performance_metrics(self) -> Dict:
        """Check performance metrics from signal generation service"""
        try:
            from argo.core.signal_generation_service import get_signal_service
            
            service = get_signal_service()
            if not service or not hasattr(service, 'performance_metrics'):
                return {'available': False}
            
            metrics = service.performance_metrics
            if not metrics:
                return {'available': False}
            
            # Get recent signal generation times
            gen_times = list(metrics.metrics.get('signal_generation_times', []))
            avg_gen_time = sum(gen_times) / len(gen_times) if gen_times else 0.0
            
            # Get cache hit rate
            cache_hits = metrics.metrics.get('cache_hits', 0)
            cache_misses = metrics.metrics.get('cache_misses', 0)
            total_cache = cache_hits + cache_misses
            cache_hit_rate = (cache_hits / total_cache * 100) if total_cache > 0 else 0.0
            
            # Get error count
            errors = metrics.metrics.get('errors', {})
            total_errors = sum(errors.values()) if errors else 0
            
            return {
                'available': True,
                'avg_signal_generation_time': avg_gen_time,
                'cache_hit_rate': cache_hit_rate,
                'total_errors': total_errors,
                'healthy': avg_gen_time < self.thresholds.max_signal_generation_time
            }
        except Exception as e:
            logger.debug(f"Performance metrics not available: {e}")
            return {'available': False, 'error': str(e)}
    
    def should_rollback(self, health_result: Dict, perf_result: Dict) -> Tuple[bool, str]:
        """Determine if rollback should be triggered"""
        reasons = []
        
        # Check health score
        if health_result.get('health_score', 0) < self.thresholds.min_health_score:
            reasons.append(f"Health score too low: {health_result.get('health_score', 0):.2%}")
        
        # Check error rate
        if health_result.get('error_rate', 0) > self.thresholds.max_error_rate:
            reasons.append(f"Error rate too high: {health_result.get('error_rate', 0):.2%}")
        
        # Check performance
        if perf_result.get('available') and perf_result.get('avg_signal_generation_time', 0) > self.thresholds.max_signal_generation_time:
            reasons.append(f"Signal generation too slow: {perf_result.get('avg_signal_generation_time', 0):.2f}s")
        
        # Check consecutive failures
        if not health_result.get('healthy', False):
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.thresholds.max_consecutive_failures:
                reasons.append(f"Consecutive failures: {self.consecutive_failures}")
        else:
            self.consecutive_failures = 0
        
        should_rollback = len(reasons) > 0
        reason = "; ".join(reasons) if reasons else "All checks passed"
        
        return should_rollback, reason
    
    def rollback_optimizations(self):
        """Rollback all optimization feature flags"""
        try:
            flags = get_feature_flags()
            
            optimization_flags = [
                'optimized_weights',
                'regime_based_weights',
                'confidence_threshold_88',
                'incremental_confidence',
                'async_batch_db',
                'request_coalescing'
            ]
            
            logger.warning("🔄 AUTOMATIC ROLLBACK TRIGGERED - Disabling all optimizations")
            for flag in optimization_flags:
                flags.disable(flag)
            
            self.rollback_triggered = True
            logger.warning("✅ Rollback complete - All optimization flags disabled")
            
            return True
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    async def monitor(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting automated optimization monitoring")
        logger.info(f"   Check interval: {self.check_interval}s")
        logger.info(f"   Monitoring duration: {self.monitoring_duration}s")
        logger.info(f"   Auto-rollback: {self.auto_rollback}")
        
        end_time = self.start_time + timedelta(seconds=self.monitoring_duration)
        check_count = 0
        
        while datetime.now() < end_time and not self.rollback_triggered:
            check_count += 1
            elapsed = (datetime.now() - self.start_time).total_seconds()
            
            logger.info(f"\n📊 Health Check #{check_count} (Elapsed: {elapsed:.0f}s)")
            
            # Run health check
            health_result = self.check_health()
            perf_result = self.check_performance_metrics()
            
            # Store results
            self.health_checks.append({
                'check_number': check_count,
                'elapsed_seconds': elapsed,
                'health': health_result,
                'performance': perf_result
            })
            
            # Log results
            logger.info(f"   Health Score: {health_result.get('health_score', 0):.2%}")
            logger.info(f"   Error Rate: {health_result.get('error_rate', 0):.2%}")
            if perf_result.get('available'):
                logger.info(f"   Avg Signal Gen Time: {perf_result.get('avg_signal_generation_time', 0):.3f}s")
                logger.info(f"   Cache Hit Rate: {perf_result.get('cache_hit_rate', 0):.1f}%")
            
            # Check if rollback needed
            should_rollback, reason = self.should_rollback(health_result, perf_result)
            
            if should_rollback:
                logger.warning(f"⚠️  Rollback condition detected: {reason}")
                
                if self.auto_rollback:
                    self.rollback_optimizations()
                    break
                else:
                    logger.warning("   Auto-rollback disabled - Manual intervention required")
            else:
                logger.info(f"   ✅ System healthy: {reason}")
            
            # Wait for next check
            if datetime.now() < end_time and not self.rollback_triggered:
                await asyncio.sleep(self.check_interval)
        
        # Generate summary report
        self.generate_report()
    
    def generate_report(self):
        """Generate monitoring report"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        report = {
            'monitoring_start': self.start_time.isoformat(),
            'monitoring_end': datetime.now().isoformat(),
            'duration_seconds': duration,
            'total_checks': len(self.health_checks),
            'rollback_triggered': self.rollback_triggered,
            'final_status': 'ROLLED_BACK' if self.rollback_triggered else 'HEALTHY',
            'health_checks': self.health_checks
        }
        
        # Save report
        report_file = Path(__file__).parent.parent / "reports" / f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n📄 Monitoring report saved: {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("MONITORING SUMMARY")
        print("="*60)
        print(f"Duration: {duration/60:.1f} minutes")
        print(f"Total Checks: {len(self.health_checks)}")
        print(f"Final Status: {report['final_status']}")
        if self.rollback_triggered:
            print("⚠️  ROLLBACK TRIGGERED - Optimizations disabled")
        else:
            print("✅ System remained healthy - Optimizations active")
        print("="*60)

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated optimization monitoring')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds (default: 60)')
    parser.add_argument('--duration', type=int, default=3600, help='Monitoring duration in seconds (default: 3600 = 1 hour)')
    parser.add_argument('--no-rollback', action='store_true', help='Disable automatic rollback')
    parser.add_argument('--max-error-rate', type=float, default=0.10, help='Max error rate for rollback (default: 0.10)')
    parser.add_argument('--min-health-score', type=float, default=0.70, help='Min health score (default: 0.70)')
    
    args = parser.parse_args()
    
    thresholds = MonitoringThresholds(
        max_error_rate=args.max_error_rate,
        min_health_score=args.min_health_score
    )
    
    monitor = AutoOptimizationMonitor(
        check_interval=args.interval,
        monitoring_duration=args.duration,
        auto_rollback=not args.no_rollback,
        thresholds=thresholds
    )
    
    await monitor.monitor()

if __name__ == "__main__":
    asyncio.run(main())

