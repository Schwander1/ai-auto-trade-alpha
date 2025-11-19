#!/usr/bin/env python3
"""
Health check script for SHORT position system

Quick health check that returns exit codes:
- 0: All systems healthy
- 1: Warnings detected
- 2: Critical issues detected
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.monitor_short_positions import ShortPositionMonitor
    from scripts.alert_short_position_issues import ShortPositionAlerter
except ImportError:
    print("❌ Could not import required modules")
    sys.exit(2)


def health_check():
    """Run health check and return status code"""
    monitor = ShortPositionMonitor()
    alerter = ShortPositionAlerter()
    
    # Run checks
    monitor_results = monitor.run_check()
    alerts = alerter.run_all_checks()
    
    # Count severity levels
    error_count = sum(1 for a in alerts if a.get('severity') == 'ERROR')
    warning_count = sum(1 for a in alerts if a.get('severity') == 'WARNING')
    
    # Check account status
    account_status = monitor_results.get('account_status', {})
    account_issues = (
        account_status.get('trading_blocked', False) or
        account_status.get('account_blocked', False)
    )
    
    # Determine exit code
    if error_count > 0 or account_issues:
        print(f"❌ Health Check FAILED: {error_count} errors, account issues: {account_issues}")
        return 2  # Critical
    elif warning_count > 0:
        print(f"⚠️  Health Check WARNING: {warning_count} warnings")
        return 1  # Warning
    else:
        print("✅ Health Check PASSED: All systems operational")
        return 0  # Healthy


if __name__ == "__main__":
    sys.exit(health_check())

