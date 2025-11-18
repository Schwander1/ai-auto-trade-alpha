#!/usr/bin/env python3
"""
Performance Summary
Quick summary of current performance status
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_latest_report(reports_dir: str = "reports") -> Optional[Path]:
    """Get latest evaluation report with improved error handling"""
    try:
        reports_path = Path(reports_dir)
        if not reports_path.exists():
            logger.warning(f"Reports directory does not exist: {reports_dir}")
            return None
        
        # Try daily evaluation reports first
        reports = list(reports_path.glob("daily_evaluation_*.json"))
        if not reports:
            # Fallback to any performance evaluation reports
            reports = list(reports_path.glob("performance_evaluation*.json"))
        
        if not reports:
            logger.warning(f"No performance reports found in {reports_dir}")
            return None
        
        # Sort by modification time, most recent first
        reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return reports[0]
    except Exception as e:
        logger.error(f"Error getting latest report: {e}", exc_info=True)
        return None

def print_summary(report_path: Path):
    """Print performance summary with improved error handling"""
    try:
        if not report_path.exists():
            print(f"❌ Report file does not exist: {report_path}")
            return
        
        with open(report_path, 'r') as f:
            report = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Could not parse report JSON: {e}")
        logger.error(f"JSON decode error in {report_path}: {e}")
        return
    except PermissionError as e:
        print(f"❌ Permission denied reading report: {e}")
        logger.error(f"Permission error reading {report_path}: {e}")
        return
    except Exception as e:
        print(f"❌ Could not read report: {e}")
        logger.error(f"Error reading report {report_path}: {e}", exc_info=True)
        return
    
    print("\n" + "=" * 70)
    print("PERFORMANCE SUMMARY")
    print("=" * 70)
    print(f"Report: {report_path.name}")
    print(f"Date: {datetime.fromtimestamp(report_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for component in ['signal_generator', 'production_trading', 'prop_firm_trading']:
        if component not in report:
            continue
        
        comp_data = report[component]
        grade = comp_data.get('performance_grade', 'N/A')
        metrics = comp_data.get('metrics', {})
        
        print(f"{component.replace('_', ' ').title()}: {grade}")
        
        if component == 'signal_generator':
            print(f"  Generation Time: {metrics.get('avg_signal_generation_time_seconds', 0):.3f}s")
            print(f"  Cache Hit Rate: {metrics.get('cache_hit_rate_percent', 0):.1f}%")
        elif component == 'production_trading':
            print(f"  Win Rate: {metrics.get('win_rate_percent', 0):.1f}%")
            print(f"  Profit Factor: {metrics.get('profit_factor', 0):.2f}")
            print(f"  Total Trades: {metrics.get('completed_trades', 0)}")
        elif component == 'prop_firm_trading':
            compliance = metrics.get('compliance_metrics', {})
            print(f"  Win Rate: {metrics.get('win_rate_percent', 0):.1f}%")
            if compliance.get('drawdown_breaches'):
                print(f"  ⚠️  Drawdown Breaches: {compliance.get('drawdown_breaches')}")
            if compliance.get('daily_loss_breaches'):
                print(f"  ⚠️  Daily Loss Breaches: {compliance.get('daily_loss_breaches')}")
        print()

def main():
    """Main entry point with command line argument support"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Performance Summary')
    parser.add_argument('--reports-dir', default='reports', help='Reports directory')
    parser.add_argument('--report', help='Specific report file to summarize')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Use specific report if provided, otherwise find latest
    if args.report:
        report_path = Path(args.report)
        if not report_path.exists():
            print(f"❌ Report file not found: {args.report}")
            sys.exit(1)
    else:
        report_path = get_latest_report(args.reports_dir)
        if not report_path:
            print(f"⚠️  No performance reports found in {args.reports_dir}. Run evaluation first.")
            sys.exit(1)
    
    print_summary(report_path)

if __name__ == '__main__':
    main()
