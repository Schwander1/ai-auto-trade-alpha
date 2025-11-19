#!/usr/bin/env python3
"""
SHORT Position Dashboard - Comprehensive status overview

Shows all SHORT position metrics in one place:
- Current positions
- Execution rates
- Performance metrics
- Recent alerts
- System health
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.monitor_short_positions import ShortPositionMonitor
    from scripts.short_position_performance_tracker import ShortPositionPerformanceTracker
    from scripts.alert_short_position_issues import ShortPositionAlerter
except ImportError:
    print("❌ Could not import required modules")
    sys.exit(1)


class ShortPositionDashboard:
    """Comprehensive dashboard for SHORT positions"""
    
    def __init__(self):
        self.monitor = ShortPositionMonitor()
        self.tracker = ShortPositionPerformanceTracker()
        self.alerter = ShortPositionAlerter()
    
    def generate_dashboard(self):
        """Generate comprehensive dashboard"""
        print("\n" + "=" * 80)
        print("📊 SHORT POSITION DASHBOARD")
        print("=" * 80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Get all data
        monitor_results = self.monitor.run_check()
        performance_report = self.tracker.generate_report()
        alerts = self.alerter.run_all_checks()
        
        # Current Status
        print("\n📈 CURRENT STATUS")
        print("-" * 80)
        
        positions = monitor_results.get('short_positions', {})
        if positions:
            count = positions.get('count', 0)
            avg_pnl = positions.get('avg_pnl', 0)
            total_pnl = positions.get('total_pnl', 0)
            
            print(f"SHORT Positions Open: {count}")
            if count > 0:
                print(f"  Average P&L: {avg_pnl:+.2f}%")
                print(f"  Total P&L: {total_pnl:+.2f}%")
                
                # Show individual positions
                pos_list = positions.get('positions', [])
                if pos_list:
                    print("\n  Positions:")
                    for pos in pos_list:
                        pnl_sign = "+" if pos['pnl_pct'] >= 0 else ""
                        print(f"    {pos['symbol']:<8} {pnl_sign}{pos['pnl_pct']:>7.2f}%  "
                              f"Entry: ${pos['entry_price']:<8.2f}  Current: ${pos['current_price']:<8.2f}")
        else:
            print("SHORT Positions Open: 0")
        
        # Execution Metrics
        print("\n📉 EXECUTION METRICS")
        print("-" * 80)
        
        execution_rate = monitor_results.get('execution_rate', {})
        if execution_rate:
            rate = execution_rate.get('rate', 0)
            executed = execution_rate.get('executed', 0)
            total = execution_rate.get('total', 0)
            
            # Color coding
            if rate >= 70:
                status = "✅"
            elif rate >= 50:
                status = "⚠️"
            else:
                status = "❌"
            
            print(f"{status} SELL Signal Execution Rate: {rate:.1f}% ({executed}/{total})")
        
        # Performance Summary
        print("\n⚖️  PERFORMANCE SUMMARY")
        print("-" * 80)
        
        comparison = performance_report.get('long_vs_short', {})
        if comparison:
            long_data = comparison.get('long', {})
            short_data = comparison.get('short', {})
            
            print(f"LONG:  {long_data.get('count', 0)} positions  "
                  f"Total P&L: {long_data.get('total_pnl', 0):+7.2f}%  "
                  f"Avg: {long_data.get('avg_pnl', 0):+6.2f}%")
            print(f"SHORT: {short_data.get('count', 0)} positions  "
                  f"Total P&L: {short_data.get('total_pnl', 0):+7.2f}%  "
                  f"Avg: {short_data.get('avg_pnl', 0):+6.2f}%")
        
        # Recent Statistics
        print("\n📊 RECENT STATISTICS (30 Days)")
        print("-" * 80)
        
        stats_30d = performance_report.get('sell_signal_stats_30d', {})
        if stats_30d:
            print(f"SELL Signals: {stats_30d.get('total_signals', 0)}")
            print(f"  Executed: {stats_30d.get('executed', 0)}")
            print(f"  Execution Rate: {stats_30d.get('execution_rate', 0):.1f}%")
            print(f"  Avg Confidence: {stats_30d.get('avg_confidence', 0):.1f}%")
        
        # Alerts
        print("\n🚨 ALERTS")
        print("-" * 80)
        
        if alerts:
            error_count = sum(1 for a in alerts if a.get('severity') == 'ERROR')
            warning_count = sum(1 for a in alerts if a.get('severity') == 'WARNING')
            
            print(f"Total: {len(alerts)} ({error_count} errors, {warning_count} warnings)")
            
            for i, alert in enumerate(alerts[:5], 1):  # Show first 5
                severity_icon = "❌" if alert['severity'] == 'ERROR' else "⚠️"
                print(f"  {i}. {severity_icon} {alert.get('title', alert.get('message', 'Alert'))}")
        else:
            print("✅ No alerts - All systems operational")
        
        # System Health
        print("\n💚 SYSTEM HEALTH")
        print("-" * 80)
        
        account_status = monitor_results.get('account_status', {})
        if account_status:
            trading_blocked = account_status.get('trading_blocked', False)
            account_blocked = account_status.get('account_blocked', False)
            
            if trading_blocked or account_blocked:
                print("❌ Account Issues Detected:")
                if trading_blocked:
                    print("  - Trading is blocked")
                if account_blocked:
                    print("  - Account is blocked")
            else:
                print("✅ Account Status: Healthy")
        
        rejected_orders = monitor_results.get('rejected_orders', {})
        if rejected_orders:
            rejected_count = rejected_orders.get('rejected_count', 0)
            if rejected_count > 0:
                print(f"⚠️  Rejected SELL Orders: {rejected_count}")
            else:
                print("✅ No rejected orders")
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 SUMMARY")
        print("=" * 80)
        
        # Calculate overall health score
        health_score = 100
        if alerts:
            health_score -= len(alerts) * 10
        if execution_rate and execution_rate.get('rate', 100) < 50:
            health_score -= 20
        if account_status and (account_status.get('trading_blocked') or account_status.get('account_blocked')):
            health_score -= 30
        
        health_score = max(0, min(100, health_score))
        
        if health_score >= 80:
            health_status = "✅ Excellent"
        elif health_score >= 60:
            health_status = "⚠️  Good"
        elif health_score >= 40:
            health_status = "⚠️  Fair"
        else:
            health_status = "❌ Poor"
        
        print(f"Overall Health: {health_status} ({health_score}/100)")
        print("=" * 80)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'monitor_results': monitor_results,
            'performance_report': performance_report,
            'alerts': alerts,
            'health_score': health_score
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SHORT Position Dashboard")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", help="Save dashboard to file")
    
    args = parser.parse_args()
    
    dashboard = ShortPositionDashboard()
    results = dashboard.generate_dashboard()
    
    if args.json:
        print("\n" + "=" * 80)
        print("JSON OUTPUT")
        print("=" * 80)
        print(json.dumps(results, indent=2, default=str))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Dashboard saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

