#!/usr/bin/env python3
"""
Health Check for v5.0 Optimizations
Validates all new optimizations are working correctly
"""
import sys
import logging
from pathlib import Path

# Add paths
argo_path = Path(__file__).parent.parent
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_parquet_support():
    """Check if Parquet support is available"""
    try:
        import pandas as pd
        import pyarrow.parquet as pq
        logger.info("✅ Parquet support: Available (pandas + pyarrow)")
        return True
    except ImportError as e:
        logger.warning(f"⚠️  Parquet support: Not available ({e})")
        logger.warning("   Install: pip install pyarrow pandas")
        return False

def check_ml_support():
    """Check if ML libraries are available"""
    try:
        from sklearn.isotonic import IsotonicRegression
        logger.info("✅ ML support: Available (scikit-learn)")
        return True
    except ImportError:
        logger.warning("⚠️  ML support: Not available (scikit-learn)")
        logger.warning("   Install: pip install scikit-learn")
        logger.warning("   Note: Confidence calibration will use simple method")
        return False

def check_backup_manager():
    """Check if backup manager is working"""
    try:
        from argo.compliance.daily_backup import BackupManager
        manager = BackupManager()
        logger.info("✅ Backup Manager: Initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Backup Manager: Failed ({e})")
        return False

def check_confidence_calibrator():
    """Check if confidence calibrator is working"""
    try:
        from argo.ml.confidence_calibrator import ConfidenceCalibrator
        calibrator = ConfidenceCalibrator()
        logger.info("✅ Confidence Calibrator: Initialized successfully")
        
        # Test calibration
        test_conf = 85.0
        calibrated = calibrator.calibrate(test_conf)
        logger.info(f"   Test calibration: {test_conf}% → {calibrated}%")
        return True
    except Exception as e:
        logger.warning(f"⚠️  Confidence Calibrator: Not available ({e})")
        return False

def check_outcome_tracker():
    """Check if outcome tracker is working"""
    try:
        from argo.tracking.outcome_tracker import OutcomeTracker
        tracker = OutcomeTracker()
        logger.info("✅ Outcome Tracker: Initialized successfully")
        
        # Get statistics
        stats = tracker.get_outcome_statistics(days=30)
        if stats:
            logger.info(f"   Statistics available: {stats.get('total_signals', 0)} signals")
        return True
    except Exception as e:
        logger.warning(f"⚠️  Outcome Tracker: Not available ({e})")
        return False

def check_s3_lifecycle_manager():
    """Check if S3 lifecycle manager is available"""
    try:
        from argo.compliance.s3_lifecycle_policy import S3LifecyclePolicyManager
        manager = S3LifecyclePolicyManager()
        logger.info("✅ S3 Lifecycle Manager: Initialized successfully")
        return True
    except Exception as e:
        logger.warning(f"⚠️  S3 Lifecycle Manager: Not available ({e})")
        logger.warning("   Note: Requires AWS credentials configured")
        return False

def check_signal_generation_integration():
    """Check if signal generation has confidence calibration integrated"""
    try:
        from argo.core.signal_generation_service import SignalGenerationService
        service = SignalGenerationService()
        
        if hasattr(service, '_confidence_calibrator'):
            if service._confidence_calibrator:
                logger.info("✅ Signal Generation: Confidence calibration integrated")
            else:
                logger.warning("⚠️  Signal Generation: Confidence calibrator not initialized")
            return service._confidence_calibrator is not None
        else:
            logger.warning("⚠️  Signal Generation: Confidence calibration not integrated")
            return False
    except Exception as e:
        logger.warning(f"⚠️  Signal Generation: Could not check ({e})")
        return False

def main():
    """Run all health checks"""
    logger.info("=" * 60)
    logger.info("v5.0 Optimizations Health Check")
    logger.info("=" * 60)
    
    results = {
        'Parquet Support': check_parquet_support(),
        'ML Support': check_ml_support(),
        'Backup Manager': check_backup_manager(),
        'Confidence Calibrator': check_confidence_calibrator(),
        'Outcome Tracker': check_outcome_tracker(),
        'S3 Lifecycle Manager': check_s3_lifecycle_manager(),
        'Signal Generation Integration': check_signal_generation_integration(),
    }
    
    logger.info("=" * 60)
    logger.info("Health Check Summary")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, status in results.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"{status_icon} {name}: {'PASS' if status else 'FAIL'}")
    
    logger.info("=" * 60)
    logger.info(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("✅ All v5.0 optimizations are healthy!")
        return 0
    elif passed >= total * 0.7:
        logger.warning("⚠️  Most optimizations are working, but some optional features are missing")
        return 0
    else:
        logger.error("❌ Multiple optimizations are not working correctly")
        return 1

if __name__ == '__main__':
    sys.exit(main())

