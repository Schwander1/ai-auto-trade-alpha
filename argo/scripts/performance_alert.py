#!/usr/bin/env python3
"""
Performance Alert System
Checks performance evaluation reports and sends alerts on issues
"""
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_latest_report(reports_dir: str) -> Optional[Path]:
    """Find latest performance evaluation report with improved error handling"""
    try:
        reports_path = Path(reports_dir)
        if not reports_path.exists():
            logger.warning(f"Reports directory does not exist: {reports_dir}")
            return None
        
        # Try daily evaluation reports first
        reports = list(reports_path.glob("daily_evaluation_*.json"))
        if not reports:
            # Fallback to any evaluation report
            reports = list(reports_path.glob("performance_evaluation*.json"))
        
        if not reports:
            logger.debug(f"No performance reports found in {reports_dir}")
            return None
        
        # Sort by modification time, most recent first
        reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return reports[0]
    except Exception as e:
        logger.error(f"Error finding latest report: {e}", exc_info=True)
        return None

def check_performance_alerts(report_path: Path) -> List[Dict]:
    """Check for performance issues and generate alerts with improved error handling"""
    alerts = []
    
    try:
        if not report_path.exists():
            alerts.append({
                'level': 'error',
                'component': 'system',
                'message': f"Report file does not exist: {report_path}",
                'action': 'Verify report path and run evaluation'
            })
            return alerts
        
        with open(report_path, 'r') as f:
            report = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {report_path}: {e}")
        alerts.append({
            'level': 'error',
            'component': 'system',
            'message': f"Invalid JSON in report: {e}",
            'action': 'Check report file format'
        })
        return alerts
    except PermissionError as e:
        logger.error(f"Permission error reading {report_path}: {e}")
        alerts.append({
            'level': 'error',
            'component': 'system',
            'message': f"Permission denied reading report: {e}",
            'action': 'Check file permissions'
        })
        return alerts
    except Exception as e:
        logger.error(f"Error reading report {report_path}: {e}", exc_info=True)
        alerts.append({
            'level': 'error',
            'component': 'system',
            'message': f"Could not read report: {e}",
            'action': 'Check report file'
        })
        return alerts
    
    # Check each component
    for component in ['signal_generator', 'production_trading', 'prop_firm_trading']:
        if component not in report:
            continue
        
        comp_data = report[component]
        grade = comp_data.get('performance_grade', 'N/A')
        metrics = comp_data.get('metrics', {})
        
        # Check for D grade
        if 'D' in grade or 'Needs Improvement' in grade:
            alerts.append({
                'level': 'critical',
                'component': component,
                'message': f"Performance grade is {grade}",
                'action': 'Review recommendations and take action',
                'grade': grade
            })
        
        # Component-specific checks
        if component == 'signal_generator':
            gen_time = metrics.get('avg_signal_generation_time_seconds', 0)
            cache_hit = metrics.get('cache_hit_rate_percent', 0)
            
            if gen_time > 1.0:
                alerts.append({
                    'level': 'warning',
                    'component': component,
                    'message': f"Signal generation time is {gen_time:.2f}s (target: <0.3s)",
                    'action': 'Optimize signal generation',
                    'metric': 'generation_time',
                    'value': gen_time,
                    'target': 0.3
                })
            
            if cache_hit < 30:
                alerts.append({
                    'level': 'warning',
                    'component': component,
                    'message': f"Cache hit rate is {cache_hit:.1f}% (target: >80%)",
                    'action': 'Improve cache strategy',
                    'metric': 'cache_hit_rate',
                    'value': cache_hit,
                    'target': 80
                })
        
        elif component == 'production_trading':
            win_rate = metrics.get('win_rate_percent', 0)
            profit_factor = metrics.get('profit_factor', 0)
            
            if win_rate > 0 and win_rate < 35:
                alerts.append({
                    'level': 'warning',
                    'component': component,
                    'message': f"Win rate is {win_rate:.1f}% (target: >45%)",
                    'action': 'Review signal quality and entry criteria',
                    'metric': 'win_rate',
                    'value': win_rate,
                    'target': 45
                })
            
            if profit_factor > 0 and profit_factor < 1.0:
                alerts.append({
                    'level': 'critical',
                    'component': component,
                    'message': f"Profit factor is {profit_factor:.2f} (target: >1.5)",
                    'action': 'Review risk/reward ratios and exit strategies',
                    'metric': 'profit_factor',
                    'value': profit_factor,
                    'target': 1.5
                })
        
        elif component == 'prop_firm_trading':
            compliance = metrics.get('compliance_metrics', {})
            
            # Check for compliance breaches
            drawdown_breaches = compliance.get('drawdown_breaches')
            if drawdown_breaches and drawdown_breaches > 0:
                alerts.append({
                    'level': 'critical',
                    'component': component,
                    'message': f"CRITICAL: {drawdown_breaches} drawdown breach(es) detected",
                    'action': 'IMMEDIATE ACTION REQUIRED - Review risk management',
                    'metric': 'drawdown_breaches',
                    'value': drawdown_breaches
                })
            
            daily_loss_breaches = compliance.get('daily_loss_breaches')
            if daily_loss_breaches and daily_loss_breaches > 0:
                alerts.append({
                    'level': 'critical',
                    'component': component,
                    'message': f"CRITICAL: {daily_loss_breaches} daily loss breach(es) detected",
                    'action': 'IMMEDIATE ACTION REQUIRED - Review position sizing',
                    'metric': 'daily_loss_breaches',
                    'value': daily_loss_breaches
                })
            
            trading_halted = compliance.get('trading_halted')
            if trading_halted:
                alerts.append({
                    'level': 'critical',
                    'component': component,
                    'message': "CRITICAL: Trading has been halted",
                    'action': 'Review compliance breaches and resolve before resuming',
                    'metric': 'trading_halted',
                    'value': True
                })
    
    return alerts

def print_alerts(alerts: List[Dict], json_output: bool = False):
    """Print alerts"""
    if json_output:
        print(json.dumps(alerts, indent=2))
        return
    
    if not alerts:
        print("✅ No performance alerts")
        return
    
    critical = [a for a in alerts if a['level'] == 'critical']
    warnings = [a for a in alerts if a['level'] == 'warning']
    errors = [a for a in alerts if a['level'] == 'error']
    
    print("\n" + "=" * 70)
    print("PERFORMANCE ALERTS")
    print("=" * 70)
    
    if critical:
        print(f"\n🔴 CRITICAL ALERTS ({len(critical)}):")
        for alert in critical:
            print(f"\n  Component: {alert['component']}")
            print(f"  Message: {alert['message']}")
            print(f"  Action: {alert['action']}")
            if 'metric' in alert:
                print(f"  Metric: {alert['metric']} = {alert.get('value', 'N/A')}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for alert in warnings:
            print(f"\n  Component: {alert['component']}")
            print(f"  Message: {alert['message']}")
            print(f"  Action: {alert['action']}")
            if 'metric' in alert:
                print(f"  Metric: {alert['metric']} = {alert.get('value', 'N/A')}")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for alert in errors:
            print(f"\n  Component: {alert['component']}")
            print(f"  Message: {alert['message']}")
            print(f"  Action: {alert['action']}")
    
    print("\n" + "=" * 70)

def main():
    parser = argparse.ArgumentParser(description='Performance Alert System')
    parser.add_argument('--check', action='store_true', help='Check for alerts')
    parser.add_argument('--report', help='Path to specific report file')
    parser.add_argument('--reports-dir', default='reports', help='Reports directory')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--exit-code', action='store_true', help='Exit with non-zero code if alerts found')
    
    args = parser.parse_args()
    
    # Find report
    if args.report:
        report_path = Path(args.report)
    else:
        report_path = find_latest_report(args.reports_dir)
    
    if not report_path or not report_path.exists():
        print("⚠️  No performance evaluation report found")
        if args.exit_code:
            sys.exit(1)
        return
    
    # Check for alerts
    alerts = check_performance_alerts(report_path)
    
    # Print alerts
    print_alerts(alerts, args.json)
    
    # Exit code
    if args.exit_code:
        critical_count = len([a for a in alerts if a['level'] == 'critical'])
        if critical_count > 0:
            sys.exit(2)  # Critical alerts
        elif len(alerts) > 0:
            sys.exit(1)  # Warnings/errors
        else:
            sys.exit(0)  # No alerts

if __name__ == '__main__':
    main()
