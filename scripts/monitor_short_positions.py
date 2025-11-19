#!/usr/bin/env python3
"""
Continuous monitoring script for SHORT positions

This script monitors:
- SHORT position execution rates
- SHORT position P&L
- SELL signal generation
- Execution failures
- Short selling restrictions

Can run continuously or as a one-time check.
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from argo.core.paper_trading_engine import PaperTradingEngine
    from argo.core.signal_generation_service import get_signal_service
except ImportError:
    print("❌ Could not import required modules")
    sys.exit(1)


class ShortPositionMonitor:
    """Monitor SHORT positions and SELL signal execution"""
    
    def __init__(self):
        self.engine = None
        self.db_path = self._find_database()
        self.alerts = []
        self.metrics = {
            'sell_signals_total': 0,
            'sell_signals_executed': 0,
            'short_positions_open': 0,
            'short_positions_pnl': [],
            'execution_failures': 0,
            'last_check': None,
        }
    
    def _find_database(self):
        """Find the signals database"""
        db_paths = [
            Path("data/signals_unified.db"),
            Path("argo/data/signals.db"),
            Path("data/signals.db"),
        ]
        
        for db_path in db_paths:
            if db_path.exists():
                return str(db_path)
        
        return None
    
    def check_sell_signal_execution_rate(self):
        """Check SELL signal execution rate"""
        if not self.db_path:
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get SELL signals from last 24 hours
            query = """
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN order_id IS NOT NULL THEN 1 END) as executed
            FROM signals
            WHERE action = 'SELL'
            AND timestamp >= datetime('now', '-1 day')
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            conn.close()
            
            if result:
                total, executed = result
                rate = (executed / total * 100) if total > 0 else 0
                
                self.metrics['sell_signals_total'] = total
                self.metrics['sell_signals_executed'] = executed
                
                # Alert if execution rate is low
                if total > 10 and rate < 50:
                    self.alerts.append({
                        'type': 'LOW_EXECUTION_RATE',
                        'severity': 'WARNING',
                        'message': f'SELL signal execution rate is {rate:.1f}% ({executed}/{total})',
                        'threshold': 50,
                        'actual': rate
                    })
                
                return {'total': total, 'executed': executed, 'rate': rate}
            
        except Exception as e:
            print(f"❌ Error checking execution rate: {e}")
        
        return None
    
    def check_short_positions(self):
        """Check current SHORT positions"""
        try:
            if not self.engine:
                self.engine = PaperTradingEngine()
            
            if not self.engine.alpaca_enabled:
                return None
            
            positions = self.engine.get_positions()
            short_positions = [p for p in positions if p.get("side") == "SHORT"]
            
            self.metrics['short_positions_open'] = len(short_positions)
            
            # Track P&L
            pnl_values = [p.get("pnl_pct", 0) for p in short_positions]
            self.metrics['short_positions_pnl'] = pnl_values
            
            # Alert on large losses
            for pos in short_positions:
                pnl = pos.get("pnl_pct", 0)
                if pnl < -5.0:  # More than 5% loss
                    self.alerts.append({
                        'type': 'LARGE_SHORT_LOSS',
                        'severity': 'WARNING',
                        'message': f'SHORT position {pos["symbol"]} has {pnl:.2f}% loss',
                        'symbol': pos["symbol"],
                        'pnl': pnl
                    })
            
            return {
                'count': len(short_positions),
                'positions': short_positions,
                'avg_pnl': sum(pnl_values) / len(pnl_values) if pnl_values else 0,
                'total_pnl': sum(pnl_values)
            }
            
        except Exception as e:
            print(f"❌ Error checking positions: {e}")
            return None
    
    def check_rejected_orders(self):
        """Check for rejected SELL orders"""
        try:
            if not self.engine:
                self.engine = PaperTradingEngine()
            
            if not self.engine.alpaca_enabled:
                return None
            
            orders = self.engine.get_all_orders(status="all", limit=100)
            rejected_sell = [o for o in orders if o.get("status") == "rejected" and o.get("side") == "sell"]
            
            if rejected_sell:
                self.metrics['execution_failures'] = len(rejected_sell)
                
                # Alert on rejections
                for order in rejected_sell[:5]:  # Check last 5
                    self.alerts.append({
                        'type': 'REJECTED_SELL_ORDER',
                        'severity': 'ERROR',
                        'message': f'SELL order rejected for {order.get("symbol")}',
                        'symbol': order.get("symbol"),
                        'order_id': order.get("id")
                    })
            
            return {'rejected_count': len(rejected_sell), 'orders': rejected_sell}
            
        except Exception as e:
            print(f"❌ Error checking rejected orders: {e}")
            return None
    
    def check_account_restrictions(self):
        """Check for account restrictions that might prevent short selling"""
        try:
            if not self.engine:
                self.engine = PaperTradingEngine()
            
            if not self.engine.alpaca_enabled:
                return None
            
            account = self.engine.get_account_details()
            if not account:
                return None
            
            restrictions = []
            
            if account.get('trading_blocked'):
                restrictions.append('Trading Blocked')
                self.alerts.append({
                    'type': 'TRADING_BLOCKED',
                    'severity': 'ERROR',
                    'message': 'Account trading is blocked - SHORT positions cannot be opened'
                })
            
            if account.get('account_blocked'):
                restrictions.append('Account Blocked')
                self.alerts.append({
                    'type': 'ACCOUNT_BLOCKED',
                    'severity': 'ERROR',
                    'message': 'Account is blocked - SHORT positions cannot be opened'
                })
            
            return {
                'trading_blocked': account.get('trading_blocked', False),
                'account_blocked': account.get('account_blocked', False),
                'restrictions': restrictions
            }
            
        except Exception as e:
            print(f"❌ Error checking account: {e}")
            return None
    
    def run_check(self):
        """Run all monitoring checks"""
        print("\n" + "=" * 80)
        print("🔍 SHORT POSITION MONITORING CHECK")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        self.alerts = []
        self.metrics['last_check'] = datetime.now().isoformat()
        
        # Run all checks
        execution_rate = self.check_sell_signal_execution_rate()
        short_positions = self.check_short_positions()
        rejected_orders = self.check_rejected_orders()
        account_status = self.check_account_restrictions()
        
        # Print results
        print("\n📊 MONITORING RESULTS")
        print("-" * 80)
        
        if execution_rate:
            print(f"SELL Signal Execution Rate: {execution_rate['rate']:.1f}% ({execution_rate['executed']}/{execution_rate['total']})")
        
        if short_positions:
            print(f"SHORT Positions Open: {short_positions['count']}")
            if short_positions['count'] > 0:
                print(f"  Average P&L: {short_positions['avg_pnl']:+.2f}%")
                print(f"  Total P&L: {short_positions['total_pnl']:+.2f}%")
                print("\n  Positions:")
                for pos in short_positions['positions']:
                    pnl_sign = "+" if pos['pnl_pct'] >= 0 else ""
                    print(f"    {pos['symbol']}: {pnl_sign}{pos['pnl_pct']:.2f}% @ ${pos['current_price']:.2f}")
        
        if rejected_orders and rejected_orders['rejected_count'] > 0:
            print(f"\n⚠️  Rejected SELL Orders: {rejected_orders['rejected_count']}")
        
        if account_status and account_status['restrictions']:
            print(f"\n⚠️  Account Restrictions: {', '.join(account_status['restrictions'])}")
        
        # Print alerts
        if self.alerts:
            print("\n🚨 ALERTS")
            print("-" * 80)
            for alert in self.alerts:
                severity_icon = "❌" if alert['severity'] == 'ERROR' else "⚠️"
                print(f"{severity_icon} [{alert['severity']}] {alert['message']}")
        else:
            print("\n✅ No alerts - All checks passed")
        
        return {
            'execution_rate': execution_rate,
            'short_positions': short_positions,
            'rejected_orders': rejected_orders,
            'account_status': account_status,
            'alerts': self.alerts,
            'metrics': self.metrics
        }
    
    def run_continuous(self, interval_seconds=300):
        """Run monitoring continuously"""
        print(f"\n🔄 Starting continuous monitoring (check every {interval_seconds}s)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_check()
                print(f"\n⏳ Next check in {interval_seconds} seconds...")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor SHORT positions and SELL signal execution")
    parser.add_argument("--continuous", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=300, help="Check interval in seconds (default: 300)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    monitor = ShortPositionMonitor()
    
    if args.continuous:
        monitor.run_continuous(args.interval)
    else:
        results = monitor.run_check()
        
        if args.json:
            print("\n" + "=" * 80)
            print("JSON OUTPUT")
            print("=" * 80)
            print(json.dumps(results, indent=2, default=str))
        else:
            print("\n" + "=" * 80)
            print("✅ MONITORING CHECK COMPLETE")
            print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

