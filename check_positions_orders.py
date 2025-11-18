#!/usr/bin/env python3
"""
Check Current Positions and Orders
"""
import sys
from pathlib import Path

# Add paths
argo_path = Path(__file__).parent / "argo"
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))

try:
    from argo.core.paper_trading_engine import PaperTradingEngine
    from argo.tracking.unified_tracker import UnifiedPerformanceTracker
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def check_positions():
    """Check current positions"""
    print("\n" + "="*70)
    print("📈 CURRENT POSITIONS")
    print("="*70)
    
    try:
        engine = PaperTradingEngine()
        positions = engine.get_positions()
        
        if positions:
            print(f"\n✅ Found {len(positions)} open position(s):\n")
            total_pnl = 0
            for pos in positions:
                pnl = pos.get('pnl_pct', 0)
                total_pnl += pnl
                print(f"   {pos['symbol']}:")
                print(f"      Side: {pos['side']}")
                print(f"      Quantity: {pos['qty']}")
                print(f"      Entry Price: ${pos['entry_price']:.2f}")
                print(f"      Current Price: ${pos['current_price']:.2f}")
                print(f"      P&L: {pnl:.2f}%")
                if pos.get('stop_price'):
                    print(f"      Stop Loss: ${pos['stop_price']:.2f}")
                if pos.get('target_price'):
                    print(f"      Take Profit: ${pos['target_price']:.2f}")
                print()
            
            if len(positions) > 1:
                print(f"   Total P&L: {total_pnl:.2f}%")
        else:
            print("\n   ⚠️  No open positions")
        
        return positions
    except Exception as e:
        print(f"\n   ❌ Error checking positions: {e}")
        import traceback
        traceback.print_exc()
        return []

def check_recent_orders():
    """Check recent orders"""
    print("\n" + "="*70)
    print("📋 RECENT ORDERS")
    print("="*70)
    
    try:
        engine = PaperTradingEngine()
        orders = engine.get_all_orders(status="all", limit=20)
        
        if orders:
            print(f"\n✅ Found {len(orders)} recent order(s):\n")
            for order in orders[:10]:  # Show first 10
                print(f"   Order {order.get('id', 'N/A')}:")
                print(f"      Symbol: {order.get('symbol', 'N/A')}")
                print(f"      Side: {order.get('side', 'N/A')}")
                print(f"      Quantity: {order.get('qty', 0)}")
                print(f"      Status: {order.get('status', 'N/A')}")
                print(f"      Filled: {order.get('filled_qty', 0)}")
                if order.get('filled_avg_price'):
                    print(f"      Avg Fill Price: ${order['filled_avg_price']:.2f}")
                print()
        else:
            print("\n   ⚠️  No recent orders found")
        
        return orders
    except Exception as e:
        print(f"\n   ❌ Error checking orders: {e}")
        import traceback
        traceback.print_exc()
        return []

def check_performance_tracker():
    """Check performance tracker for recent trades"""
    print("\n" + "="*70)
    print("📊 PERFORMANCE TRACKER")
    print("="*70)
    
    try:
        tracker = UnifiedPerformanceTracker()
        recent_trades = tracker.get_recent_trades(limit=10)
        
        if recent_trades:
            print(f"\n✅ Found {len(recent_trades)} recent trade(s):\n")
            for trade in recent_trades[:10]:
                print(f"   {trade.get('symbol', 'N/A')}:")
                print(f"      Action: {trade.get('action', 'N/A')}")
                print(f"      Entry: ${trade.get('entry_price', 0):.2f}")
                if trade.get('exit_price'):
                    print(f"      Exit: ${trade['exit_price']:.2f}")
                    pnl = trade.get('pnl', 0)
                    pnl_pct = trade.get('pnl_pct', 0)
                    print(f"      P&L: ${pnl:.2f} ({pnl_pct:.2f}%)")
                print(f"      Timestamp: {trade.get('timestamp', 'N/A')}")
                print()
        else:
            print("\n   ⚠️  No recent trades in tracker")
        
        return recent_trades
    except Exception as e:
        print(f"\n   ⚠️  Error checking performance tracker: {e}")
        return []

def check_account_details():
    """Check account details"""
    print("\n" + "="*70)
    print("💼 ACCOUNT DETAILS")
    print("="*70)
    
    try:
        engine = PaperTradingEngine()
        account = engine.get_account_details()
        
        if account:
            print(f"\n   Account Number: {account.get('account_number', 'N/A')}")
            print(f"   Status: {account.get('status', 'N/A')}")
            print(f"   Portfolio Value: ${account.get('portfolio_value', 0):,.2f}")
            print(f"   Buying Power: ${account.get('buying_power', 0):,.2f}")
            print(f"   Cash: ${account.get('cash', 0):,.2f}")
            print(f"   Equity: ${account.get('equity', 0):,.2f}")
            print(f"   Trading Blocked: {account.get('trading_blocked', False)}")
            print(f"   Account Blocked: {account.get('account_blocked', False)}")
        else:
            print("\n   ⚠️  Could not retrieve account details")
        
        return account
    except Exception as e:
        print(f"\n   ❌ Error checking account: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main execution"""
    account = check_account_details()
    positions = check_positions()
    orders = check_recent_orders()
    trades = check_performance_tracker()
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"   Open Positions: {len(positions) if positions else 0}")
    print(f"   Recent Orders: {len(orders) if orders else 0}")
    print(f"   Tracked Trades: {len(trades) if trades else 0}")
    
    if account:
        print(f"   Portfolio Value: ${account.get('portfolio_value', 0):,.2f}")
        print(f"   Buying Power: ${account.get('buying_power', 0):,.2f}")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

