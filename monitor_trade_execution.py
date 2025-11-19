#!/usr/bin/env python3
"""
Monitor Trade Execution
Watches for new signals and checks if they're being executed
"""
import time
import requests
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def get_recent_signals_from_api(limit: int = 10) -> List[Dict]:
    """Get recent signals from API"""
    try:
        response = requests.get(f"http://localhost:8000/api/signals/latest?limit={limit}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"⚠️  Error fetching signals: {e}")
    return []

def check_database_signals(db_path: Path, minutes: int = 5) -> List[Dict]:
    """Check database for signals in last N minutes"""
    if not db_path.exists():
        return []
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get table name
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%signal%'")
        tables = cursor.fetchall()
        if not tables:
            conn.close()
            return []
        
        table_name = tables[0][0]
        
        # Get recent signals
        cutoff_time = (datetime.now() - timedelta(minutes=minutes)).isoformat()
        cursor.execute(f"""
            SELECT signal_id, symbol, action, entry_price, confidence, timestamp, order_id
            FROM {table_name}
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        """, (cutoff_time,))
        
        signals = []
        for row in cursor.fetchall():
            signals.append({
                'signal_id': row[0],
                'symbol': row[1],
                'action': row[2],
                'entry_price': row[3],
                'confidence': row[4],
                'timestamp': row[5],
                'order_id': row[6]
            })
        
        conn.close()
        return signals
    except Exception as e:
        print(f"⚠️  Error reading database: {e}")
        return []

def monitor_executions(duration_minutes: int = 5):
    """Monitor for signal executions"""
    print("\n" + "="*70)
    print("🔍 MONITORING TRADE EXECUTION")
    print("="*70)
    print(f"Monitoring for {duration_minutes} minutes...")
    print("Watching for new signals and execution status...")
    print("="*70 + "\n")
    
    # Check database paths
    db_paths = [
        Path("argo/data/signals.db"),
        Path("data/signals.db"),
    ]
    db_path = None
    for path in db_paths:
        if path.exists():
            db_path = path
            break
    
    if not db_path:
        print("⚠️  No database found, using API only")
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    seen_signal_ids = set()
    executed_count = 0
    total_signals = 0
    
    try:
        while datetime.now() < end_time:
            # Get recent signals
            api_signals = get_recent_signals_from_api(limit=20)
            db_signals = check_database_signals(db_path, minutes=2) if db_path else []
            
            # Combine and deduplicate
            all_signals = {}
            for sig in api_signals:
                sig_id = sig.get('signal_id') or f"{sig.get('symbol')}-{sig.get('timestamp')}"
                all_signals[sig_id] = sig
            
            for sig in db_signals:
                sig_id = sig.get('signal_id')
                if sig_id and sig_id not in all_signals:
                    all_signals[sig_id] = sig
            
            # Check for new signals
            for sig_id, sig in all_signals.items():
                if sig_id not in seen_signal_ids:
                    seen_signal_ids.add(sig_id)
                    total_signals += 1
                    
                    symbol = sig.get('symbol', 'UNKNOWN')
                    action = sig.get('action', 'UNKNOWN')
                    price = sig.get('entry_price', sig.get('price', 0))
                    confidence = sig.get('confidence', 0)
                    order_id = sig.get('order_id')
                    timestamp = sig.get('timestamp', 'unknown')
                    
                    if order_id:
                        executed_count += 1
                        status = "✅ EXECUTED"
                        print(f"{status} | {symbol} {action} @ ${price:.2f} ({confidence:.1f}%) | Order: {order_id}")
                    else:
                        status = "⏭️  NOT EXECUTED"
                        print(f"{status} | {symbol} {action} @ ${price:.2f} ({confidence:.1f}%) | {timestamp}")
            
            # Print summary every 30 seconds
            elapsed = (datetime.now() - start_time).total_seconds()
            if int(elapsed) % 30 == 0 and int(elapsed) > 0:
                execution_rate = (executed_count / total_signals * 100) if total_signals > 0 else 0
                print(f"\n📊 Summary: {total_signals} signals, {executed_count} executed ({execution_rate:.1f}%)")
            
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped by user")
    
    # Final summary
    print("\n" + "="*70)
    print("📊 FINAL SUMMARY")
    print("="*70)
    print(f"Total signals seen: {total_signals}")
    print(f"Signals executed: {executed_count}")
    print(f"Signals not executed: {total_signals - executed_count}")
    if total_signals > 0:
        execution_rate = (executed_count / total_signals * 100)
        print(f"Execution rate: {execution_rate:.1f}%")
    print("="*70 + "\n")

if __name__ == "__main__":
    import sys
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    monitor_executions(duration)

