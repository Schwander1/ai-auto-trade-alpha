#!/usr/bin/env python3
"""
Performance Report Generator
Generates performance reports from collected metrics

Usage:
    python scripts/performance_report.py [--hours 24] [--json]
"""
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.core.performance_monitor import get_performance_monitor

def print_performance_report(stats: dict, json_output: bool = False):
    """Print performance report"""
    if json_output:
        print(json.dumps(stats, indent=2))
        return
    
    print("=" * 70)
    print("📊 PERFORMANCE REPORT")
    print("=" * 70)
    print(f"⏰ Period: Last {stats['period_hours']} hours")
    print(f"📅 Generated: {stats['timestamp']}")
    print()
    
    if not stats['metrics']:
        print("⚠️  No performance metrics collected")
        return
    
    print("📈 METRICS SUMMARY")
    print("-" * 70)
    print(f"{'Metric':<30} {'Count':<8} {'Avg':<10} {'Min':<10} {'Max':<10} {'P95':<10}")
    print("-" * 70)
    
    for metric_name, metric_stats in sorted(stats['metrics'].items()):
        print(f"{metric_name:<30} {metric_stats['count']:<8} "
              f"{metric_stats['avg']:<10.2f} {metric_stats['min']:<10.2f} "
              f"{metric_stats['max']:<10.2f} {metric_stats['p95']:<10.2f} {metric_stats['unit']}")
    
    print()
    
    if stats['counters']:
        print("🔢 COUNTERS")
        print("-" * 70)
        for counter_name, value in sorted(stats['counters'].items()):
            print(f"{counter_name:<30} {value}")
        print()
    
    # Performance alerts
    print("⚠️  PERFORMANCE ALERTS")
    print("-" * 70)
    alerts = []
    
    for metric_name, metric_stats in stats['metrics'].items():
        # Check for slow operations (> 1000ms)
        if metric_stats['unit'] == 'ms' and metric_stats['avg'] > 1000:
            alerts.append(f"⚠️  {metric_name} average is slow: {metric_stats['avg']:.2f}ms")
        
        # Check for high P95 (> 5000ms)
        if metric_stats['unit'] == 'ms' and metric_stats['p95'] > 5000:
            alerts.append(f"⚠️  {metric_name} P95 is very high: {metric_stats['p95']:.2f}ms")
    
    if alerts:
        for alert in alerts:
            print(alert)
    else:
        print("✅ No performance issues detected")
    print()

def main():
    parser = argparse.ArgumentParser(description='Generate performance report')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back (default: 24)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    monitor = get_performance_monitor()
    stats = monitor.get_all_stats(args.hours)
    print_performance_report(stats, args.json)

if __name__ == "__main__":
    main()

