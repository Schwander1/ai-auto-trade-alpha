#!/usr/bin/env python3
"""
Debug signal storage and generation
"""
import asyncio
import sys
import os
import sqlite3
from datetime import datetime
sys.path.insert(0, "/root/argo-production-green")

async def debug_signal_storage():
    print("🔍 Debugging Signal Storage and Generation...")
    print("")
    
    # Check database
    db_path = "/root/argo-production-green/data/signals.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM signals")
    count = cursor.fetchone()[0]
    print(f"📊 Total signals in database: {count}")
    
    cursor.execute("SELECT symbol, action, confidence, timestamp FROM signals ORDER BY timestamp DESC LIMIT 5")
    recent = cursor.fetchall()
    print(f"Recent signals:")
    for sig in recent:
        print(f"  {sig[0]} {sig[1]} @ {sig[2]}% - {sig[3]}")
    conn.close()
    
    # Check service
    try:
        from argo.core.signal_generation_service import get_signal_service
        from argo.core.signal_tracker import SignalTracker
        
        service = get_signal_service()
        tracker = SignalTracker()
        
        print(f"\n🔧 Service Status:")
        print(f"  Running: {service.running}")
        print(f"  Auto-execute: {service.auto_execute}")
        print(f"  Confidence threshold: {service.confidence_threshold}%")
        print(f"  Pending signals in queue: {len(tracker._pending_signals)}")
        
        # Test signal generation
        print(f"\n🧪 Testing signal generation for AAPL...")
        signal = await service.generate_signal_for_symbol("AAPL")
        
        if signal:
            print(f"✅ Signal generated:")
            print(f"  Symbol: {signal.get('symbol')}")
            print(f"  Action: {signal.get('action')}")
            print(f"  Confidence: {signal.get('confidence')}%")
            print(f"  Entry Price: ${signal.get('entry_price')}")
            
            # Test storage
            print(f"\n💾 Testing signal storage...")
            signal_id = await tracker.log_signal_async(signal)
            print(f"  Signal ID: {signal_id}")
            print(f"  Pending after log: {len(tracker._pending_signals)}")
            
            # Force flush
            print(f"\n🔄 Flushing batch...")
            await tracker._flush_batch_async()
            print(f"  Pending after flush: {len(tracker._pending_signals)}")
            
            # Check database again
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM signals")
            new_count = cursor.fetchone()[0]
            conn.close()
            print(f"\n📊 Database count after test: {new_count}")
            
            if new_count > count:
                print("✅ Signal successfully stored!")
            else:
                print("❌ Signal not stored - check for errors")
        else:
            print("❌ No signal generated - check data sources and thresholds")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_signal_storage())

