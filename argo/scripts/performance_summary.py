#!/usr/bin/env python3
"""
Performance Summary
Quick summary of current performance status
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

def get_latest_report(reports_dir: str = "reports") -> Path:
    """Get latest evaluation report"""
    reports_path = Path(reports_dir)
    if not reports_path.exists():
        return None
    
    reports = list(reports_path.glob("daily_evaluation_*.json"))
    if not reports:
        reports = list(reports_path.glob("performance_evaluation*.json"))
    
    if not reports:
        return None
    
    reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return reports[0]

def print_summary(report_path: Path):
    """Print performance summary"""
    try:
        with open(report_path, 'r') as f:
            report = json.load(f)
    except Exception:
        print("❌ Could not read report")
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

if __name__ == '__main__':
    report = get_latest_report()
    if report:
        print_summary(report)
    else:
        print("⚠️  No performance reports found. Run evaluation first.")
