#!/usr/bin/env python3
"""
Enhanced Monitoring for Trade Execution
Monitors signal generation, distribution, and execution in real-time
"""
import time
import requests
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
sys.path.insert(0, 'argo')

def check_recent_signals_api() -> List[Dict]:
    """Get recent signals from API"""
    try:
        response = requests.get("http://localhost:8000/api/signals/latest?limit=20", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"⚠️  Error fetching signals: {e}")
    return []

def check_database_signals(db_path: Path, minutes: int = 2) -> List[Dict]:
    """Check database for very recent signals"""
    if not db_path.exists():
        return []
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cutoff_time = (datetime.now() - timedelta(minutes=minutes)).isoformat()
        cursor.execute("""
            SELECT signal_id, symbol, action, entry_price, confidence, timestamp, order_id
            FROM signals
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 50
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
        return []

def monitor_execution_flow(duration_minutes: int = 5):
    """Monitor the complete execution flow"""
    print("\n" + "="*70)
    print("🔍 ENHANCED TRADE EXECUTION MONITORING")
    print("="*70)
    print(f"Monitoring for {duration_minutes} minutes...")
    print("Watching: Signal Generation → Distribution → Execution")
    print("="*70 + "\n")
    
    # Find database
    db_paths = [Path("argo/data/signals.db"), Path("data/signals.db")]
    db_path = next((p for p in db_paths if p.exists()), None)
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    seen_signal_ids = set()
    stats = {
        'total_signals': 0,
        'executed': 0,
        'not_executed': 0,
        'high_confidence': 0,
        'distributed': 0
    }
    
    try:
        while datetime.now() < end_time:
            # Check API signals
            api_signals = check_recent_signals_api()
            
            # Check database signals
            db_signals = check_database_signals(db_path, minutes=2) if db_path else []
            
            # Combine signals
            all_signals = {}
            for sig in api_signals:
                sig_id = sig.get('signal_id') or f"{sig.get('symbol')}-{sig.get('timestamp')}"
                all_signals[sig_id] = sig
            
            for sig in db_signals:
                sig_id = sig.get('signal_id')
                if sig_id:
                    all_signals[sig_id] = sig
            
            # Process new signals
            for sig_id, sig in all_signals.items():
                if sig_id not in seen_signal_ids:
                    seen_signal_ids.add(sig_id)
                    stats['total_signals'] += 1
                    
                    symbol = sig.get('symbol', 'UNKNOWN')
                    action = sig.get('action', 'UNKNOWN')
                    price = sig.get('entry_price', sig.get('price', 0))
                    confidence = sig.get('confidence', 0)
                    order_id = sig.get('order_id')
                    timestamp = sig.get('timestamp', 'unknown')
                    
                    if confidence >= 75:
                        stats['high_confidence'] += 1
                    
                    if order_id:
                        stats['executed'] += 1
                        status = "✅ EXECUTED"
                        print(f"{status} | {symbol} {action} @ ${price:.2f} ({confidence:.1f}%) | Order: {order_id} | {timestamp}")
                    else:
                        stats['not_executed'] += 1
                        if confidence >= 75:
                            status = "⏭️  HIGH CONF NOT EXECUTED"
                            print(f"{status} | {symbol} {action} @ ${price:.2f} ({confidence:.1f}%) | {timestamp}")
            
            # Print stats every 30 seconds
            elapsed = (datetime.now() - start_time).total_seconds()
            if int(elapsed) % 30 == 0 and int(elapsed) > 0:
                exec_rate = (stats['executed'] / stats['total_signals'] * 100) if stats['total_signals'] > 0 else 0
                print(f"\n📊 Stats: {stats['total_signals']} signals | {stats['executed']} executed ({exec_rate:.1f}%) | {stats['high_confidence']} high conf")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped")
    
    # Final summary
    print("\n" + "="*70)
    print("📊 FINAL STATISTICS")
    print("="*70)
    print(f"Total signals: {stats['total_signals']}")
    print(f"Executed: {stats['executed']}")
    print(f"Not executed: {stats['not_executed']}")
    print(f"High confidence (≥75%): {stats['high_confidence']}")
    if stats['total_signals'] > 0:
        exec_rate = (stats['executed'] / stats['total_signals'] * 100)
        print(f"Execution rate: {exec_rate:.1f}%")
    print("="*70 + "\n")

if __name__ == "__main__":
    import sys
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    monitor_execution_flow(duration)

