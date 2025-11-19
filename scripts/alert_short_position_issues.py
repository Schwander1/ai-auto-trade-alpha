#!/usr/bin/env python3
"""
Alerting system for SHORT position issues

This script checks for critical issues and sends alerts:
- Low SELL signal execution rates
- Large SHORT position losses
- Rejected SELL orders
- Account restrictions
- Short selling failures

Can send alerts via:
- Console output
- Log file
- Email (if configured)
- Webhook (if configured)
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from argo.core.paper_trading_engine import PaperTradingEngine
except ImportError:
    print("❌ Could not import required modules")
    sys.exit(1)


class ShortPositionAlerter:
    """Alert system for SHORT position issues"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.engine = None
        self.config_path = config_path
        self.alerts: List[Dict] = []
        self.alert_thresholds = {
            'execution_rate_min': 50.0,  # Minimum execution rate %
            'short_loss_threshold': -5.0,  # Alert on losses > 5%
            'max_rejected_orders': 3,  # Alert if more than 3 rejected
        }
    
    def check_execution_rate(self, min_rate: float = 50.0) -> Optional[Dict]:
        """Check SELL signal execution rate"""
        try:
            from scripts.monitor_short_positions import ShortPositionMonitor
            monitor = ShortPositionMonitor()
            execution_rate = monitor.check_sell_signal_execution_rate()
            
            if execution_rate and execution_rate['total'] > 10:
                rate = execution_rate['rate']
                if rate < min_rate:
                    self.alerts.append({
                        'type': 'LOW_EXECUTION_RATE',
                        'severity': 'WARNING',
                        'title': 'Low SELL Signal Execution Rate',
                        'message': f'Only {rate:.1f}% of SELL signals are being executed ({execution_rate["executed"]}/{execution_rate["total"]})',
                        'threshold': min_rate,
                        'actual': rate,
                        'recommendation': 'Check for short selling restrictions or execution failures'
                    })
                    return execution_rate
            
        except Exception as e:
            print(f"❌ Error checking execution rate: {e}")
        
        return None
    
    def check_short_positions(self, loss_threshold: float = -5.0) -> Optional[Dict]:
        """Check for large SHORT position losses"""
        try:
            if not self.engine:
                self.engine = PaperTradingEngine()
            
            if not self.engine.alpaca_enabled:
                return None
            
            positions = self.engine.get_positions()
            short_positions = [p for p in positions if p.get("side") == "SHORT"]
            
            for pos in short_positions:
                pnl = pos.get("pnl_pct", 0)
                if pnl < loss_threshold:
                    self.alerts.append({
                        'type': 'LARGE_SHORT_LOSS',
                        'severity': 'WARNING',
                        'title': f'Large SHORT Position Loss: {pos["symbol"]}',
                        'message': f'SHORT position in {pos["symbol"]} has {pnl:.2f}% loss (Entry: ${pos["entry_price"]:.2f}, Current: ${pos["current_price"]:.2f})',
                        'symbol': pos["symbol"],
                        'pnl': pnl,
                        'entry_price': pos["entry_price"],
                        'current_price': pos["current_price"],
                        'recommendation': 'Consider closing position or adjusting stop loss'
                    })
            
            return {'count': len(short_positions), 'positions': short_positions}
            
        except Exception as e:
            print(f"❌ Error checking positions: {e}")
            return None
    
    def check_rejected_orders(self, max_rejected: int = 3) -> Optional[Dict]:
        """Check for rejected SELL orders"""
        try:
            if not self.engine:
                self.engine = PaperTradingEngine()
            
            if not self.engine.alpaca_enabled:
                return None
            
            orders = self.engine.get_all_orders(status="all", limit=100)
            rejected_sell = [o for o in orders if o.get("status") == "rejected" and o.get("side") == "sell"]
            
            if len(rejected_sell) > max_rejected:
                recent_rejected = rejected_sell[:5]
                symbols = list(set([o.get("symbol") for o in recent_rejected]))
                
                self.alerts.append({
                    'type': 'MULTIPLE_REJECTED_ORDERS',
                    'severity': 'ERROR',
                    'title': 'Multiple SELL Orders Rejected',
                    'message': f'{len(rejected_sell)} SELL orders have been rejected. Symbols: {", ".join(symbols)}',
                    'count': len(rejected_sell),
                    'symbols': symbols,
                    'recommendation': 'Check for short selling restrictions or insufficient buying power'
                })
            
            return {'rejected_count': len(rejected_sell), 'orders': rejected_sell}
            
        except Exception as e:
            print(f"❌ Error checking rejected orders: {e}")
            return None
    
    def check_account_restrictions(self) -> Optional[Dict]:
        """Check for account restrictions"""
        try:
            if not self.engine:
                self.engine = PaperTradingEngine()
            
            if not self.engine.alpaca_enabled:
                return None
            
            account = self.engine.get_account_details()
            if not account:
                return None
            
            if account.get('trading_blocked'):
                self.alerts.append({
                    'type': 'TRADING_BLOCKED',
                    'severity': 'ERROR',
                    'title': 'Trading Blocked',
                    'message': 'Account trading is blocked - SHORT positions cannot be opened',
                    'recommendation': 'Contact broker to resolve trading restrictions'
                })
            
            if account.get('account_blocked'):
                self.alerts.append({
                    'type': 'ACCOUNT_BLOCKED',
                    'severity': 'ERROR',
                    'title': 'Account Blocked',
                    'message': 'Account is blocked - SHORT positions cannot be opened',
                    'recommendation': 'Contact broker immediately to resolve account issues'
                })
            
            return {
                'trading_blocked': account.get('trading_blocked', False),
                'account_blocked': account.get('account_blocked', False)
            }
            
        except Exception as e:
            print(f"❌ Error checking account: {e}")
            return None
    
    def run_all_checks(self):
        """Run all alert checks"""
        self.alerts = []
        
        self.check_execution_rate(self.alert_thresholds['execution_rate_min'])
        self.check_short_positions(self.alert_thresholds['short_loss_threshold'])
        self.check_rejected_orders(self.alert_thresholds['max_rejected_orders'])
        self.check_account_restrictions()
        
        return self.alerts
    
    def send_alerts(self, output_file: Optional[str] = None):
        """Send alerts via configured channels"""
        if not self.alerts:
            print("✅ No alerts to send")
            return
        
        # Console output
        print("\n" + "=" * 80)
        print("🚨 SHORT POSITION ALERTS")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Total Alerts: {len(self.alerts)}\n")
        
        for i, alert in enumerate(self.alerts, 1):
            severity_icon = "❌" if alert['severity'] == 'ERROR' else "⚠️"
            print(f"{i}. {severity_icon} [{alert['severity']}] {alert['title']}")
            print(f"   {alert['message']}")
            if 'recommendation' in alert:
                print(f"   💡 Recommendation: {alert['recommendation']}")
            print()
        
        # File output
        if output_file:
            alert_data = {
                'timestamp': datetime.now().isoformat(),
                'alerts': self.alerts
            }
            with open(output_file, 'w') as f:
                json.dump(alert_data, f, indent=2)
            print(f"📄 Alerts saved to: {output_file}")
        
        # TODO: Add email/webhook support if needed
        # if email_config:
        #     self.send_email_alerts()
        # if webhook_url:
        #     self.send_webhook_alerts()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Alert on SHORT position issues")
    parser.add_argument("--output", help="Save alerts to JSON file")
    parser.add_argument("--execution-rate-threshold", type=float, default=50.0, help="Minimum execution rate % (default: 50.0)")
    parser.add_argument("--loss-threshold", type=float, default=-5.0, help="Loss threshold % for alerts (default: -5.0)")
    parser.add_argument("--max-rejected", type=int, default=3, help="Max rejected orders before alert (default: 3)")
    
    args = parser.parse_args()
    
    alerter = ShortPositionAlerter()
    alerter.alert_thresholds = {
        'execution_rate_min': args.execution_rate_threshold,
        'short_loss_threshold': args.loss_threshold,
        'max_rejected_orders': args.max_rejected,
    }
    
    alerts = alerter.run_all_checks()
    alerter.send_alerts(args.output)
    
    # Exit with error code if alerts found
    return 1 if alerts else 0


if __name__ == "__main__":
    sys.exit(main())

