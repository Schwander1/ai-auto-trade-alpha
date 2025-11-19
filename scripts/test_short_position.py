#!/usr/bin/env python3
"""
Test script to verify SHORT position opening

This script:
1. Generates a test SELL signal
2. Attempts to execute it to open a SHORT position
3. Verifies the SHORT position was opened
4. Checks bracket orders were placed
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from argo.core.paper_trading_engine import PaperTradingEngine
    from argo.core.signal_generation_service import get_signal_service
except ImportError:
    print("❌ Could not import required modules")
    sys.exit(1)


def create_test_sell_signal(symbol: str = "SPY"):
    """Create a test SELL signal for opening a SHORT position"""
    current_price = 450.0  # Default test price
    
    # Try to get current price
    try:
        engine = PaperTradingEngine()
        if engine.alpaca_enabled:
            price = engine.get_current_price(symbol)
            if price:
                current_price = price
    except:
        pass
    
    # Calculate stop and target for SHORT
    stop_price = current_price * 1.02  # 2% above entry (stop loss for SHORT)
    target_price = current_price * 0.98  # 2% below entry (take profit for SHORT)
    
    signal = {
        "symbol": symbol,
        "action": "SELL",
        "entry_price": current_price,
        "stop_price": stop_price,
        "target_price": target_price,
        "confidence": 85.0,
        "strategy": "test_short_position",
        "timestamp": datetime.now().isoformat(),
    }
    
    return signal


def test_short_position_opening(symbol: str = "SPY", dry_run: bool = False):
    """Test opening a SHORT position from a SELL signal"""
    print("\n" + "=" * 80)
    print("🧪 TEST: SHORT POSITION OPENING")
    print("=" * 80)
    print(f"Symbol: {symbol}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE TEST'}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        engine = PaperTradingEngine()
        
        if not engine.alpaca_enabled:
            print("\n⚠️  Alpaca not enabled - cannot test SHORT position opening")
            return False
        
        # Check if symbol already has a position
        positions = engine.get_positions()
        existing_position = next((p for p in positions if p.get("symbol") == symbol), None)
        
        if existing_position:
            print(f"\n⚠️  Symbol {symbol} already has a {existing_position.get('side')} position")
            print(f"   Entry: ${existing_position.get('entry_price'):.2f}")
            print(f"   Current: ${existing_position.get('current_price'):.2f}")
            print(f"   P&L: {existing_position.get('pnl_pct'):+.2f}%")
            response = input("\n   Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("   Test cancelled")
                return False
        
        # Create test signal
        print("\n📝 Creating test SELL signal...")
        signal = create_test_sell_signal(symbol)
        print(f"   Symbol: {signal['symbol']}")
        print(f"   Action: {signal['action']}")
        print(f"   Entry Price: ${signal['entry_price']:.2f}")
        print(f"   Stop Loss: ${signal['stop_price']:.2f} (2% above entry)")
        print(f"   Take Profit: ${signal['target_price']:.2f} (2% below entry)")
        print(f"   Confidence: {signal['confidence']:.1f}%")
        
        if dry_run:
            print("\n🔷 DRY RUN MODE - Would execute:")
            print(f"   SELL {signal['symbol']} @ ${signal['entry_price']:.2f}")
            print(f"   Stop Loss: ${signal['stop_price']:.2f}")
            print(f"   Take Profit: ${signal['target_price']:.2f}")
            return True
        
        # Execute the signal
        print("\n🚀 Executing SELL signal to open SHORT position...")
        order_id = engine.execute_signal(signal)
        
        if not order_id:
            print("\n❌ Failed to execute signal - no order ID returned")
            return False
        
        print(f"\n✅ Order placed: {order_id}")
        
        # Wait a moment for order to process
        print("\n⏳ Waiting for order to process...")
        time.sleep(3)
        
        # Check order status
        order_status = engine.get_order_status(order_id)
        if order_status:
            print(f"\n📊 Order Status:")
            print(f"   Status: {order_status.get('status')}")
            print(f"   Side: {order_status.get('side')}")
            print(f"   Quantity: {order_status.get('qty')}")
            print(f"   Filled: {order_status.get('filled_qty', 0)}")
            if order_status.get('filled_avg_price'):
                print(f"   Fill Price: ${order_status.get('filled_avg_price'):.2f}")
        
        # Check for SHORT position
        print("\n🔍 Checking for SHORT position...")
        time.sleep(2)  # Give position time to appear
        
        positions = engine.get_positions()
        short_position = next((p for p in positions if p.get("symbol") == symbol and p.get("side") == "SHORT"), None)
        
        if short_position:
            print("\n✅ SHORT POSITION OPENED SUCCESSFULLY!")
            print("-" * 80)
            print(f"Symbol: {short_position['symbol']}")
            print(f"Side: {short_position['side']}")
            print(f"Quantity: {short_position['qty']}")
            print(f"Entry Price: ${short_position['entry_price']:.2f}")
            print(f"Current Price: ${short_position['current_price']:.2f}")
            print(f"P&L: {short_position['pnl_pct']:+.2f}%")
            if short_position.get('stop_price'):
                print(f"Stop Loss: ${short_position['stop_price']:.2f}")
            if short_position.get('target_price'):
                print(f"Take Profit: ${short_position['target_price']:.2f}")
            
            # Check for bracket orders
            print("\n🔍 Checking for bracket orders...")
            all_orders = engine.get_all_orders(status="all", limit=20)
            related_orders = [o for o in all_orders if o.get('symbol') == symbol]
            
            stop_orders = [o for o in related_orders if 'stop' in str(o.get('order_type', '')).lower()]
            profit_orders = [o for o in related_orders if 'profit' in str(o.get('order_type', '')).lower() or 'limit' in str(o.get('order_type', '')).lower()]
            
            if stop_orders:
                print(f"   ✅ Stop Loss Order: {len(stop_orders)} found")
                for so in stop_orders:
                    print(f"      Order ID: {so.get('id')}, Status: {so.get('status')}")
            else:
                print("   ⚠️  No stop loss orders found")
            
            if profit_orders:
                print(f"   ✅ Take Profit Order: {len(profit_orders)} found")
                for po in profit_orders:
                    print(f"      Order ID: {po.get('id')}, Status: {po.get('status')}")
            else:
                print("   ⚠️  No take profit orders found")
            
            return True
        else:
            print("\n⚠️  SHORT position not found after execution")
            print("   This could mean:")
            print("   - Order is still pending")
            print("   - Order was rejected")
            print("   - Position detection issue")
            
            # Check all positions for the symbol
            all_positions = [p for p in positions if p.get("symbol") == symbol]
            if all_positions:
                print(f"\n   Found {len(all_positions)} position(s) for {symbol}:")
                for pos in all_positions:
                    print(f"      {pos.get('side')}: {pos.get('qty')} @ ${pos.get('entry_price'):.2f}")
            
            return False
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the test"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test SHORT position opening")
    parser.add_argument("--symbol", default="SPY", help="Symbol to test (default: SPY)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (don't actually execute)")
    
    args = parser.parse_args()
    
    success = test_short_position_opening(args.symbol, dry_run=args.dry_run)
    
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST COMPLETED")
    else:
        print("❌ TEST FAILED")
    print("=" * 80)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

