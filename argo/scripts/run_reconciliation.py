#!/usr/bin/env python3
"""
Run Reconciliation with Alpaca
Usage: python scripts/run_reconciliation.py [--period 30] [--auto-fix]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.validation.reconciliation import ReconciliationSystem
from argo.tracking.unified_tracker import UnifiedPerformanceTracker

def main():
    parser = argparse.ArgumentParser(description="Run reconciliation with Alpaca")
    parser.add_argument("--period", type=int, default=30, help="Period in days (default: 30)")
    parser.add_argument("--auto-fix", action="store_true", help="Automatically fix issues")
    parser.add_argument("--output", type=str, help="Output file path (default: stdout)")
    
    args = parser.parse_args()
    
    tracker = UnifiedPerformanceTracker()
    # Note: In production, pass trading_engine here
    reconciliation = ReconciliationSystem(tracker, trading_engine=None)
    
    report = reconciliation.get_reconciliation_report(period_days=args.period)
    
    output = json.dumps(report, indent=2)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output)
        print(f"✅ Reconciliation report saved to {args.output}")
    else:
        print(output)
    
    # Print summary
    print(f"\n📊 Reconciliation Summary:")
    print(f"  Total Trades: {report['total_trades']}")
    print(f"  Verified: {report['verified_trades']}")
    print(f"  Success Rate: {report['success_rate']}%")
    print(f"  Issues: {report['issues_summary']['total']} (Critical: {report['issues_summary']['critical']}, Warnings: {report['issues_summary']['warning']})")

if __name__ == "__main__":
    main()

