#!/usr/bin/env python3
"""
Monitor Trade Execution in Real-Time
Shows signals being generated and executed
"""
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta

def find_database():
    """Find signal database"""
    db_paths = [
        Path("data/signals_unified.db"),
        Path("argo/data/signals.db"),
        Path("/root/argo-production-unified/data/signals_unified.db"),
    ]
    
    for db_path in db_paths:
        if db_path.exists():
            return db_path
    return None

def get_recent_signals(db_path, minutes=5):
    """Get recent signals"""
    try:
        conn = sqlite3.connect(str(db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(minutes=minutes)).isoformat()
        cursor.execute("""
            SELECT symbol, action, entry_price, confidence, timestamp, order_id
            FROM signals
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (cutoff,))
        
        signals = []
        for row in cursor.fetchall():
            signals.append({
                'symbol': row['symbol'],
                'action': row['action'],
                'price': row['entry_price'],
                'confidence': row['confidence'],
                'timestamp': row['timestamp'],
                'order_id': row['order_id']
            })
        
        conn.close()
        return signals
    except Exception as e:
        print(f"Error: {e}")
        return []

def monitor(duration_minutes=10):
    """Monitor trade execution"""
    db_path = find_database()
    if not db_path:
        print("❌ Database not found")
        return
    
    print("=" * 80)
    print("📊 TRADE EXECUTION MONITOR")
    print("=" * 80)
    print(f"Monitoring for {duration_minutes} minutes...")
    print("Press Ctrl+C to stop early")
    print("=" * 80)
    
    seen_signals = set()
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    try:
        while datetime.now() < end_time:
            signals = get_recent_signals(db_path, minutes=1)
            
            for sig in signals:
                sig_id = f"{sig['symbol']}-{sig['timestamp']}"
                if sig_id not in seen_signals:
                    seen_signals.add(sig_id)
                    
                    executed = "✅ EXECUTED" if sig['order_id'] and sig['order_id'] != 'N/A' else "⏭️  NOT EXECUTED"
                    print(f"{executed} | {sig['symbol']} {sig['action']} @ ${sig['price']:.2f} "
                          f"({sig['confidence']:.1f}%) | {sig['timestamp'][:19]}")
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    
    print("\n" + "=" * 80)
    print("📊 Summary:")
    print(f"   Signals seen: {len(seen_signals)}")
    executed = sum(1 for sig in get_recent_signals(db_path, minutes=duration_minutes) 
                   if sig.get('order_id') and sig['order_id'] != 'N/A')
    print(f"   Executed: {executed}")

if __name__ == '__main__':
    monitor(10)
