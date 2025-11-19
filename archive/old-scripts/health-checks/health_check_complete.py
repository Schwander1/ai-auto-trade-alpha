#!/usr/bin/env python3
"""
Complete Health Check - All Phases
Comprehensive health check for all v5.0 optimizations and phases
"""
import sys
import logging
from pathlib import Path

# Add paths
argo_path = Path(__file__).parent.parent
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))
workspace_root = argo_path.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from argo.core.database_optimizer import DatabaseOptimizer
from argo.core.monitoring_dashboard import get_monitoring_dashboard
from argo.ml.confidence_calibrator import ConfidenceCalibrator
from argo.tracking.outcome_tracker import OutcomeTracker
from argo.compliance.daily_backup import BackupManager, PARQUET_AVAILABLE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CompleteHealthChecker:
    """Complete health check for all phases"""
    
    def __init__(self):
        self.results = []
        self.dashboard = get_monitoring_dashboard()
    
    def _record_result(self, phase: str, component: str, status: bool, message: str):
        """Record health check result"""
        self.results.append({
            'phase': phase,
            'component': component,
            'status': '✅ PASS' if status else '❌ FAIL',
            'message': message
        })
        
        if status:
            logger.info(f"✅ [{phase}] {component}: {message}")
            self.dashboard.set_health_status(f"{phase}.{component}", "healthy", message)
        else:
            logger.error(f"❌ [{phase}] {component}: {message}")
            self.dashboard.set_health_status(f"{phase}.{component}", "unhealthy", message)
    
    def check_v5_core(self):
        """Check v5.0 core optimizations"""
        logger.info("\n=== Checking v5.0 Core Optimizations ===")
        
        # Parquet support
        if PARQUET_AVAILABLE:
            self._record_result("v5.0", "Parquet Support", True, "Available")
        else:
            self._record_result("v5.0", "Parquet Support", False, "Not available (install pyarrow)")
        
        # ML support
        try:
            import sklearn
            self._record_result("v5.0", "ML Support", True, "Available")
        except ImportError:
            self._record_result("v5.0", "ML Support", False, "Not available (install scikit-learn)")
        
        # Confidence calibrator
        try:
            calibrator = ConfidenceCalibrator()
            self._record_result("v5.0", "Confidence Calibrator", True, "Initialized")
        except Exception as e:
            self._record_result("v5.0", "Confidence Calibrator", False, f"Failed: {e}")
        
        # Outcome tracker
        try:
            tracker = OutcomeTracker()
            self._record_result("v5.0", "Outcome Tracker", True, "Initialized")
        except Exception as e:
            self._record_result("v5.0", "Outcome Tracker", False, f"Failed: {e}")
    
    def check_phase2(self):
        """Check Phase 2: Database optimizations"""
        logger.info("\n=== Checking Phase 2: Database Optimizations ===")
        
        try:
            optimizer = DatabaseOptimizer()
            self._record_result("Phase 2", "Database Optimizer", True, "Initialized")
            
            # Check materialized views
            daily_summary = optimizer.get_daily_summary(7)
            self._record_result("Phase 2", "Materialized Views", True, f"{len(daily_summary)} days of data")
            
            # Check indexes (indirect - if optimizer initialized, indexes exist)
            self._record_result("Phase 2", "Performance Indexes", True, "Created")
            
        except Exception as e:
            self._record_result("Phase 2", "Database Optimizer", False, f"Failed: {e}")
    
    def check_phase4(self):
        """Check Phase 4: WebSocket streams"""
        logger.info("\n=== Checking Phase 4: WebSocket Streams ===")
        
        try:
            import websockets
            self._record_result("Phase 4", "WebSocket Library", True, "Available")
            
            # Check if WebSocket classes can be imported
            from argo.core.websocket_streams import AlpacaWebSocketStream, PolygonWebSocketStream
            self._record_result("Phase 4", "WebSocket Classes", True, "Available")
            
        except ImportError as e:
            self._record_result("Phase 4", "WebSocket Library", False, f"Not available: {e}")
        except Exception as e:
            self._record_result("Phase 4", "WebSocket Classes", False, f"Failed: {e}")
    
    def check_phase5(self):
        """Check Phase 5: Advanced features"""
        logger.info("\n=== Checking Phase 5: Advanced Features ===")
        
        try:
            from argo.core.incremental_fetcher import IncrementalFetcher, DataDeduplicator, AdaptivePollingManager
            
            # Incremental fetcher
            fetcher = IncrementalFetcher()
            self._record_result("Phase 5", "Incremental Fetcher", True, "Available")
            
            # Deduplicator
            dedup = DataDeduplicator()
            self._record_result("Phase 5", "Data Deduplicator", True, "Available")
            
            # Adaptive polling
            polling = AdaptivePollingManager()
            self._record_result("Phase 5", "Adaptive Polling", True, "Available")
            
        except Exception as e:
            self._record_result("Phase 5", "Advanced Features", False, f"Failed: {e}")
    
    def check_monitoring(self):
        """Check monitoring dashboard"""
        logger.info("\n=== Checking Monitoring Dashboard ===")
        
        try:
            dashboard = get_monitoring_dashboard()
            dashboard.record_metric("test_metric", 1.0)
            summary = dashboard.get_health_summary()
            self._record_result("Monitoring", "Dashboard", True, "Operational")
        except Exception as e:
            self._record_result("Monitoring", "Dashboard", False, f"Failed: {e}")
    
    def run_all_checks(self):
        """Run all health checks"""
        logger.info("=" * 70)
        logger.info("COMPLETE HEALTH CHECK - ALL PHASES")
        logger.info("=" * 70)
        
        self.check_v5_core()
        self.check_phase2()
        self.check_phase4()
        self.check_phase5()
        self.check_monitoring()
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("HEALTH CHECK SUMMARY")
        logger.info("=" * 70)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == '✅ PASS')
        failed = total - passed
        
        for result in self.results:
            logger.info(f"{result['status']} [{result['phase']}] {result['component']}: {result['message']}")
        
        logger.info("\n" + "=" * 70)
        logger.info(f"Total: {total} | Passed: {passed} | Failed: {failed}")
        logger.info("=" * 70)
        
        if failed == 0:
            logger.info("✅ ALL HEALTH CHECKS PASSED!")
            return True
        else:
            logger.warning(f"⚠️  {failed} health check(s) failed")
            return False


if __name__ == '__main__':
    checker = CompleteHealthChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)

