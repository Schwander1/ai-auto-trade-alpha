#!/usr/bin/env python3
"""
Fix signal storage by ensuring batch flush is working
"""
import asyncio
import sys
import os
sys.path.insert(0, "/root/argo-production-green")

async def fix_signal_storage():
    try:
        from argo.core.signal_tracker import SignalTracker
        tracker = SignalTracker()
        
        print(f"Pending signals in queue: {len(tracker._pending_signals)}")
        
        # Force flush any pending signals
        if tracker._pending_signals:
            print(f"Flushing {len(tracker._pending_signals)} pending signals...")
            if hasattr(tracker, "_flush_batch_async"):
                await tracker._flush_batch_async()
                print("✅ Batch flushed successfully")
            else:
                # Use sync flush as fallback
                tracker._flush_batch()
                print("✅ Batch flushed (sync)")
        else:
            print("No pending signals to flush")
            
        # Check database
        import sqlite3
        db_path = "/root/argo-production-green/data/signals.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM signals")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"Total signals in database: {count}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_signal_storage())

