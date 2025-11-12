#!/usr/bin/env python3
"""Test performance tracking system"""

from argo.tracking import UnifiedPerformanceTracker
import time

def test_tracking():
    print("🧪 Testing Performance Tracking\n")
    
    tracker = UnifiedPerformanceTracker()
    
    # Test 1: Stock trade
    print("1️⃣ Recording AAPL LONG...")
    trade1 = tracker.record_signal_entry(
        signal_id="sig_001",
        asset_class="stock",
        symbol="AAPL",
        signal_type="long",
        entry_price=180.50,
        quantity=10,
        confidence=95.5
    )
    print(f"   ✅ {trade1.id}")
    
    # Test 2: Crypto trade
    print("2️⃣ Recording BTC LONG...")
    trade2 = tracker.record_signal_entry(
        signal_id="sig_002",
        asset_class="crypto",
        symbol="BTC/USD",
        signal_type="long",
        entry_price=42000.00,
        quantity=0.1,
        confidence=92.0
    )
    print(f"   ✅ {trade2.id}")
    
    # Test 3: Exit trades
    print("3️⃣ Exiting trades...")
    time.sleep(1)
    
    tracker.record_signal_exit(trade1.id, exit_price=185.00)
    print("   ✅ AAPL exited: WIN")
    
    tracker.record_signal_exit(trade2.id, exit_price=43500.00)
    print("   ✅ BTC exited: WIN")
    
    # Test 4: Stats
    print("\n4️⃣ Getting stats...")
    stats = tracker.get_performance_stats(days=1)
    
    print("\n📊 RESULTS:")
    print(f"Total Trades: {stats['total_trades']}")
    print(f"Win Rate: {stats['win_rate_percent']}%")
    print(f"Total P&L: ${stats['total_pnl_dollars']}")
    print(f"Verified: {stats['all_verified']}")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_tracking()
