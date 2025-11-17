#!/usr/bin/env python3
"""
Monitor Signal Generation - Check for 80%+ confidence signals
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Database path
db_path = Path(__file__).parent.parent / "argo" / "data" / "signals.db"

def check_signals():
    """Check recent signals and their confidence levels"""
    if not db_path.exists():
        print("⚠️  Signal database not found. Service may still be initializing...")
        return
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get signals from last hour
    one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
    
    # Total signals
    cursor.execute("""
        SELECT COUNT(*) as total,
               COUNT(CASE WHEN confidence >= 80.0 THEN 1 END) as high_confidence,
               AVG(confidence) as avg_confidence,
               MAX(confidence) as max_confidence,
               MIN(confidence) as min_confidence
        FROM signals
        WHERE created_at >= ?
    """, (one_hour_ago,))
    
    stats = cursor.fetchone()
    
    # Recent signals
    cursor.execute("""
        SELECT symbol, action, confidence, entry_price, timestamp, created_at
        FROM signals
        WHERE created_at >= ?
        ORDER BY created_at DESC
        LIMIT 10
    """, (one_hour_ago,))
    
    recent = cursor.fetchall()
    
    print("=" * 70)
    print("📊 SIGNAL GENERATION MONITOR")
    print("=" * 70)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if stats['total'] == 0:
        print("⚠️  No signals generated in the last hour")
        print("   Service may still be initializing...")
        print()
        print("💡 Check service logs:")
        print("   tail -f argo/logs/service_startup_*.log")
        conn.close()
        return
    
    print("📈 STATISTICS (Last Hour):")
    print(f"   Total Signals: {stats['total']}")
    print(f"   High Confidence (80%+): {stats['high_confidence']} ({stats['high_confidence']/stats['total']*100:.1f}%)")
    print(f"   Average Confidence: {stats['avg_confidence']:.2f}%")
    print(f"   Max Confidence: {stats['max_confidence']:.2f}%")
    print(f"   Min Confidence: {stats['min_confidence']:.2f}%")
    print()
    
    if stats['high_confidence'] > 0:
        print(f"✅ SUCCESS: {stats['high_confidence']} signals meet 80%+ threshold!")
    else:
        print("⚠️  WARNING: No signals meet 80%+ confidence threshold")
        print("   Current threshold: 80.0%")
        print("   Consider checking signal generation logic")
    print()
    
    print("📋 RECENT SIGNALS (Last 10):")
    print("-" * 70)
    print(f"{'Symbol':<8} {'Action':<6} {'Confidence':<12} {'Price':<12} {'Time':<20}")
    print("-" * 70)
    
    for row in recent:
        confidence = row['confidence']
        confidence_str = f"{confidence:.2f}%"
        if confidence >= 80.0:
            confidence_str = f"✅ {confidence_str}"
        elif confidence >= 75.0:
            confidence_str = f"⚠️  {confidence_str}"
        else:
            confidence_str = f"❌ {confidence_str}"
        
        timestamp = row['created_at'] or row['timestamp']
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M:%S')
            except:
                time_str = str(timestamp)[:19]
        else:
            time_str = "N/A"
        
        print(f"{row['symbol']:<8} {row['action']:<6} {confidence_str:<15} ${row['entry_price']:<11.2f} {time_str}")
    
    print("-" * 70)
    print()
    
    # Check configuration
    config_path = Path(__file__).parent.parent / "argo" / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            min_conf = config.get('trading', {}).get('min_confidence', 75.0)
            print(f"⚙️  CONFIGURATION:")
            print(f"   Min Confidence Threshold: {min_conf}%")
            print(f"   Target: 80%+ confidence signals")
            print()
    
    conn.close()

if __name__ == '__main__':
    try:
        check_signals()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

