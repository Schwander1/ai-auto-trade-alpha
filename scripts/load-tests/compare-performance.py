#!/usr/bin/env python3
"""Compare performance test results with baseline"""
import json
import sys
import argparse
from typing import Dict, Any

THRESHOLDS = {
    'http_req_duration': {
        'p95': 500,  # 95th percentile < 500ms
        'p99': 1000,  # 99th percentile < 1000ms
    },
    'http_req_failed': {
        'rate': 0.01,  # Error rate < 1%
    },
}


def get_metric_value(metrics: Dict, metric_name: str, value_key: str) -> float:
    """Get metric value from results"""
    if metric_name not in metrics:
        return None

    metric = metrics[metric_name]
    values = metric.get('values', {})
    return values.get(value_key)


def compare_results(baseline_file: str, current_file: str, threshold: float = 0.1):
    """Compare current results with baseline"""
    with open(baseline_file) as f:
        baseline = json.load(f)

    with open(current_file) as f:
        current = json.load(f)

    baseline_metrics = baseline.get('metrics', {})
    current_metrics = current.get('metrics', {})

    regressions = []
    improvements = []

    # Compare key metrics
    for metric_name, thresholds in THRESHOLDS.items():
        if metric_name not in baseline_metrics or metric_name not in current_metrics:
            continue

        baseline_metric = baseline_metrics[metric_name]
        current_metric = current_metrics[metric_name]

        for threshold_name, threshold_value in thresholds.items():
            baseline_value = get_metric_value(baseline_metrics, metric_name, threshold_name)
            current_value = get_metric_value(current_metrics, metric_name, threshold_name)

            if baseline_value is None or current_value is None:
                continue

            # Calculate percentage change
            if baseline_value == 0:
                change_pct = 0 if current_value == 0 else float('inf')
            else:
                change_pct = ((current_value - baseline_value) / baseline_value) * 100

            # Check for regression (worse performance)
            if change_pct > threshold * 100:  # threshold is decimal (0.1 = 10%)
                regressions.append({
                    'metric': metric_name,
                    'threshold': threshold_name,
                    'baseline': baseline_value,
                    'current': current_value,
                    'change_pct': change_pct,
                    'threshold_value': threshold_value
                })
            elif change_pct < -threshold * 100:  # Improvement
                improvements.append({
                    'metric': metric_name,
                    'threshold': threshold_name,
                    'baseline': baseline_value,
                    'current': current_value,
                    'change_pct': change_pct
                })

    # Print results
    print("Performance Comparison Results")
    print("=" * 50)

    if regressions:
        print("\n❌ PERFORMANCE REGRESSIONS DETECTED:")
        for reg in regressions:
            print(f"  {reg['metric']} ({reg['threshold']}):")
            print(f"    Baseline: {reg['baseline']:.2f}")
            print(f"    Current:  {reg['current']:.2f}")
            print(f"    Change:   +{reg['change_pct']:.2f}%")
            print(f"    Threshold: {reg['threshold_value']}")
            print()

    if improvements:
        print("\n✅ PERFORMANCE IMPROVEMENTS:")
        for imp in improvements:
            print(f"  {imp['metric']} ({imp['threshold']}):")
            print(f"    Baseline: {imp['baseline']:.2f}")
            print(f"    Current:  {imp['current']:.2f}")
            print(f"    Change:   {imp['change_pct']:.2f}%")
            print()

    if not regressions and not improvements:
        print("\n✅ No significant performance changes detected")

    # Check absolute thresholds
    print("\nThreshold Checks:")
    threshold_failures = []
    for metric_name, thresholds in THRESHOLDS.items():
        if metric_name not in current_metrics:
            continue

        for threshold_name, threshold_value in thresholds.items():
            current_value = get_metric_value(current_metrics, metric_name, threshold_name)
            if current_value is None:
                continue

            if current_value > threshold_value:
                threshold_failures.append({
                    'metric': metric_name,
                    'threshold': threshold_name,
                    'value': current_value,
                    'limit': threshold_value
                })
                print(f"  ❌ {metric_name} ({threshold_name}): {current_value:.2f} > {threshold_value}")
            else:
                print(f"  ✅ {metric_name} ({threshold_name}): {current_value:.2f} <= {threshold_value}")

    # Exit with error if regressions or threshold failures
    if regressions or threshold_failures:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare performance test results')
    parser.add_argument('baseline', help='Baseline results JSON file')
    parser.add_argument('current', help='Current results JSON file')
    parser.add_argument('--threshold', type=float, default=0.1,
                       help='Regression threshold (default: 0.1 = 10%%)')

    args = parser.parse_args()
    compare_results(args.baseline, args.current, args.threshold)
