#!/usr/bin/env python3
"""
Continuous Signal Quality Monitor
Monitors signal generation and provides real-time quality metrics
"""
import sqlite3
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Database path
db_path = Path(__file__).parent.parent / "argo" / "data" / "signals.db"
config_path = Path(__file__).parent.parent / "argo" / "config.json"

def load_config():
    """Load configuration"""
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

def get_signal_stats(minutes=10):
    """Get signal statistics for the last N minutes"""
    if not db_path.exists():
        return None
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    time_threshold = (datetime.now() - timedelta(minutes=minutes)).isoformat()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN confidence >= 80.0 THEN 1 END) as high_conf_80,
            COUNT(CASE WHEN confidence >= 85.0 THEN 1 END) as high_conf_85,
            COUNT(CASE WHEN confidence >= 90.0 THEN 1 END) as high_conf_90,
            AVG(confidence) as avg_conf,
            MAX(confidence) as max_conf,
            MIN(confidence) as min_conf,
            COUNT(DISTINCT symbol) as unique_symbols
        FROM signals
        WHERE created_at >= ?
    """, (time_threshold,))
    
    stats = cursor.fetchone()
    conn.close()
    
    return dict(stats) if stats else None

def monitor_loop(interval_seconds=60, window_minutes=10):
    """Continuous monitoring loop"""
    config = load_config()
    min_confidence = config.get('trading', {}).get('min_confidence', 80.0)
    
    print("=" * 70)
    print("📊 CONTINUOUS SIGNAL QUALITY MONITOR")
    print("=" * 70)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Monitoring window: Last {window_minutes} minutes")
    print(f"🎯 Target confidence: {min_confidence}%+")
    print(f"🔄 Update interval: {interval_seconds} seconds")
    print("=" * 70)
    print()
    
    try:
        while True:
            stats = get_signal_stats(window_minutes)
            
            if stats and stats['total'] > 0:
                print(f"\r⏰ {datetime.now().strftime('%H:%M:%S')} | ", end="")
                print(f"Total: {stats['total']:3d} | ", end="")
                print(f"80%+: {stats['high_conf_80']:3d} ({stats['high_conf_80']/stats['total']*100:5.1f}%) | ", end="")
                print(f"Avg: {stats['avg_conf']:5.1f}% | ", end="")
                print(f"Max: {stats['max_conf']:5.1f}% | ", end="")
                print(f"Symbols: {stats['unique_symbols']}", end="")
                sys.stdout.flush()
            else:
                print(f"\r⏰ {datetime.now().strftime('%H:%M:%S')} | ⚠️  No signals in last {window_minutes} minutes (service may be initializing...)", end="")
                sys.stdout.flush()
            
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped")
        sys.exit(0)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Continuous signal quality monitor')
    parser.add_argument('--interval', type=int, default=60, help='Update interval in seconds (default: 60)')
    parser.add_argument('--window', type=int, default=10, help='Time window in minutes (default: 10)')
    args = parser.parse_args()
    
    monitor_loop(args.interval, args.window)

