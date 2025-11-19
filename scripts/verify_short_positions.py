#!/usr/bin/env python3
"""
Verification script to check SHORT position execution and tracking

This script:
1. Checks database for SELL signals that should have opened SHORT positions
2. Verifies Alpaca positions to see if SHORT positions exist
3. Checks order history for SHORT position opens
4. Monitors for short selling errors
"""

import sys
import os
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

def check_database_signals(db_path: str = "data/signals_unified.db"):
    """Check database for SELL signals and their execution status"""
    print("\n" + "=" * 80)
    print("📊 DATABASE SIGNAL ANALYSIS")
    print("=" * 80)
    
    if not os.path.exists(db_path):
        print(f"⚠️  Database not found: {db_path}")
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if signals table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signals'")
        if not cursor.fetchone():
            print("⚠️  Signals table not found in database")
            conn.close()
            return []
        
        # Get recent SELL signals
        query = """
        SELECT 
            symbol, 
            action, 
            confidence, 
            entry_price,
            timestamp,
            order_id
        FROM signals 
        WHERE action = 'SELL' 
        ORDER BY timestamp DESC 
        LIMIT 20
        """
        
        cursor.execute(query)
        sell_signals = cursor.fetchall()
        
        print(f"\n📉 Recent SELL Signals: {len(sell_signals)}")
        print("-" * 80)
        print(f"{'Symbol':<10} {'Confidence':<12} {'Entry Price':<12} {'Order ID':<20} {'Timestamp'}")
        print("-" * 80)
        
        executed_count = 0
        for signal in sell_signals:
            symbol, action, confidence, entry_price, timestamp, order_id = signal
            executed = "✅" if order_id else "⏳"
            if order_id:
                executed_count += 1
            print(f"{symbol:<10} {confidence:<12.2f} ${entry_price:<11.2f} {order_id or 'PENDING':<20} {timestamp}")
        
        print(f"\n📊 Summary: {executed_count}/{len(sell_signals)} SELL signals executed")
        
        # Get signal statistics
        cursor.execute("""
            SELECT 
                action,
                COUNT(*) as count,
                COUNT(CASE WHEN order_id IS NOT NULL THEN 1 END) as executed,
                AVG(confidence) as avg_confidence
            FROM signals
            WHERE action IN ('BUY', 'SELL')
            GROUP BY action
        """)
        
        stats = cursor.fetchall()
        print("\n📈 Signal Statistics:")
        print("-" * 80)
        for stat in stats:
            action, count, executed, avg_conf = stat
            execution_rate = (executed / count * 100) if count > 0 else 0
            print(f"{action}: {count} total, {executed} executed ({execution_rate:.1f}%), avg confidence: {avg_conf:.2f}%")
        
        conn.close()
        return sell_signals
        
    except Exception as e:
        print(f"❌ Error querying database: {e}")
        import traceback
        traceback.print_exc()
        return []


def check_alpaca_positions():
    """Check Alpaca for current SHORT positions"""
    print("\n" + "=" * 80)
    print("📊 ALPACA POSITION ANALYSIS")
    print("=" * 80)
    
    try:
        engine = PaperTradingEngine()
        
        if not engine.alpaca_enabled:
            print("⚠️  Alpaca not enabled - cannot check positions")
            return []
        
        positions = engine.get_positions()
        
        if not positions:
            print("\n📭 No open positions")
            return []
        
        long_positions = [p for p in positions if p.get("side") == "LONG"]
        short_positions = [p for p in positions if p.get("side") == "SHORT"]
        
        print(f"\n📊 Current Positions: {len(positions)} total")
        print(f"   📈 LONG: {len(long_positions)}")
        print(f"   📉 SHORT: {len(short_positions)}")
        
        if short_positions:
            print("\n📉 SHORT Positions:")
            print("-" * 80)
            print(f"{'Symbol':<10} {'Qty':<10} {'Entry':<12} {'Current':<12} {'P&L %':<10}")
            print("-" * 80)
            for pos in short_positions:
                pnl_sign = "+" if pos["pnl_pct"] >= 0 else ""
                print(
                    f"{pos['symbol']:<10} {pos['qty']:<10} "
                    f"${pos['entry_price']:<11.2f} ${pos['current_price']:<11.2f} "
                    f"{pnl_sign}{pos['pnl_pct']:<9.2f}%"
                )
        else:
            print("\n⚠️  No SHORT positions found")
        
        if long_positions:
            print("\n📈 LONG Positions:")
            print("-" * 80)
            print(f"{'Symbol':<10} {'Qty':<10} {'Entry':<12} {'Current':<12} {'P&L %':<10}")
            print("-" * 80)
            for pos in long_positions:
                pnl_sign = "+" if pos["pnl_pct"] >= 0 else ""
                print(
                    f"{pos['symbol']:<10} {pos['qty']:<10} "
                    f"${pos['entry_price']:<11.2f} ${pos['current_price']:<11.2f} "
                    f"{pnl_sign}{pos['pnl_pct']:<9.2f}%"
                )
        
        return positions
        
    except Exception as e:
        print(f"❌ Error checking Alpaca positions: {e}")
        import traceback
        traceback.print_exc()
        return []


def check_order_history():
    """Check Alpaca order history for SHORT position opens"""
    print("\n" + "=" * 80)
    print("📊 ORDER HISTORY ANALYSIS")
    print("=" * 80)
    
    try:
        engine = PaperTradingEngine()
        
        if not engine.alpaca_enabled:
            print("⚠️  Alpaca not enabled - cannot check order history")
            return []
        
        # Get recent orders
        orders = engine.get_all_orders(status="all", limit=50)
        
        if not orders:
            print("\n📭 No orders found")
            return []
        
        # Filter for SELL orders (which open SHORT positions)
        sell_orders = [o for o in orders if o.get("side") == "sell"]
        
        print(f"\n📊 Recent Orders: {len(orders)} total")
        print(f"   📉 SELL orders (SHORT opens): {len(sell_orders)}")
        
        if sell_orders:
            print("\n📉 SELL Orders (SHORT Position Opens):")
            print("-" * 80)
            print(f"{'Symbol':<10} {'Side':<6} {'Qty':<10} {'Status':<12} {'Created'}")
            print("-" * 80)
            for order in sell_orders[:20]:  # Show last 20
                created = order.get("created_at", "N/A")
                if created and len(created) > 19:
                    created = created[:19]  # Truncate timestamp
                print(
                    f"{order.get('symbol', 'N/A'):<10} "
                    f"{order.get('side', 'N/A'):<6} "
                    f"{order.get('qty', 0):<10} "
                    f"{order.get('status', 'N/A'):<12} "
                    f"{created}"
                )
        else:
            print("\n⚠️  No SELL orders found in recent history")
        
        return orders
        
    except Exception as e:
        print(f"❌ Error checking order history: {e}")
        import traceback
        traceback.print_exc()
        return []


def check_short_selling_errors():
    """Check for any short selling errors in logs or order rejections"""
    print("\n" + "=" * 80)
    print("🔍 SHORT SELLING ERROR CHECK")
    print("=" * 80)
    
    try:
        engine = PaperTradingEngine()
        
        if not engine.alpaca_enabled:
            print("⚠️  Alpaca not enabled - cannot check for errors")
            return
        
        # Get rejected orders
        orders = engine.get_all_orders(status="all", limit=100)
        rejected_orders = [o for o in orders if o.get("status") == "rejected"]
        rejected_sell_orders = [o for o in rejected_orders if o.get("side") == "sell"]
        
        if rejected_sell_orders:
            print(f"\n⚠️  Found {len(rejected_sell_orders)} rejected SELL orders:")
            print("-" * 80)
            for order in rejected_sell_orders:
                print(f"   ❌ {order.get('symbol')}: {order.get('status')} - {order.get('id', 'N/A')}")
        else:
            print("\n✅ No rejected SELL orders found")
        
        # Check account for short selling restrictions
        account = engine.get_account_details()
        if account:
            print(f"\n📊 Account Status:")
            print(f"   Trading Blocked: {account.get('trading_blocked', False)}")
            print(f"   Account Blocked: {account.get('account_blocked', False)}")
            print(f"   Pattern Day Trader: {account.get('pattern_day_trader', False)}")
            
            if account.get('trading_blocked'):
                print("   ⚠️  Trading is blocked - this may prevent SHORT positions")
            if account.get('account_blocked'):
                print("   ⚠️  Account is blocked - this may prevent SHORT positions")
        
    except Exception as e:
        print(f"❌ Error checking for short selling errors: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all verification checks"""
    print("\n" + "=" * 80)
    print("🔍 SHORT POSITION VERIFICATION")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check database signals
    sell_signals = check_database_signals()
    
    # Check Alpaca positions
    positions = check_alpaca_positions()
    
    # Check order history
    orders = check_order_history()
    
    # Check for errors
    check_short_selling_errors()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    
    short_positions = [p for p in positions if p.get("side") == "SHORT"]
    sell_orders = [o for o in (orders or []) if o.get("side") == "sell"]
    
    print(f"\n✅ SELL Signals in DB: {len(sell_signals)}")
    print(f"✅ SHORT Positions Open: {len(short_positions)}")
    print(f"✅ SELL Orders in History: {len(sell_orders)}")
    
    if len(sell_signals) > 0 and len(short_positions) == 0:
        print("\n⚠️  WARNING: SELL signals exist but no SHORT positions found")
        print("   This could indicate:")
        print("   - SELL signals are closing LONG positions (not opening SHORT)")
        print("   - SHORT positions were closed")
        print("   - Short selling restrictions")
        print("   - Execution failures")
    elif len(short_positions) > 0:
        print("\n✅ SHORT positions are being opened successfully!")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

