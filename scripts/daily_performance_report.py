#!/usr/bin/env python3
"""
Daily Performance Report
Generates a comprehensive daily report of signal generation performance
"""
import sqlite3
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

def generate_report():
    """Generate daily performance report"""
    if not db_path.exists():
        print("⚠️  Signal database not found")
        return
    
    config = load_config()
    min_confidence = config.get('trading', {}).get('min_confidence', 80.0)
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Today's date range
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    today_end = datetime.now().isoformat()
    
    # Overall stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN confidence >= ? THEN 1 END) as high_conf,
            COUNT(CASE WHEN confidence >= 85.0 THEN 1 END) as very_high_conf,
            COUNT(CASE WHEN confidence >= 90.0 THEN 1 END) as excellent_conf,
            AVG(confidence) as avg_conf,
            MAX(confidence) as max_conf,
            MIN(confidence) as min_conf,
            COUNT(DISTINCT symbol) as unique_symbols,
            COUNT(DISTINCT action) as unique_actions
        FROM signals
        WHERE created_at >= ?
    """, (min_confidence, today_start))
    
    overall = cursor.fetchone()
    
    # By symbol
    cursor.execute("""
        SELECT 
            symbol,
            COUNT(*) as count,
            AVG(confidence) as avg_conf,
            MAX(confidence) as max_conf,
            COUNT(CASE WHEN confidence >= ? THEN 1 END) as high_conf_count
        FROM signals
        WHERE created_at >= ?
        GROUP BY symbol
        ORDER BY count DESC
    """, (min_confidence, today_start))
    
    by_symbol = cursor.fetchall()
    
    # By action
    cursor.execute("""
        SELECT 
            action,
            COUNT(*) as count,
            AVG(confidence) as avg_conf,
            MAX(confidence) as max_conf
        FROM signals
        WHERE created_at >= ?
        GROUP BY action
        ORDER BY count DESC
    """, (today_start,))
    
    by_action = cursor.fetchall()
    
    # Hourly distribution
    cursor.execute("""
        SELECT 
            strftime('%H', created_at) as hour,
            COUNT(*) as count,
            AVG(confidence) as avg_conf
        FROM signals
        WHERE created_at >= ?
        GROUP BY hour
        ORDER BY hour
    """, (today_start,))
    
    hourly = cursor.fetchall()
    
    conn.close()
    
    # Generate report
    print("=" * 70)
    print("📊 DAILY PERFORMANCE REPORT")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target Confidence: {min_confidence}%+")
    print("=" * 70)
    print()
    
    if overall['total'] == 0:
        print("⚠️  No signals generated today")
        return
    
    print("📈 OVERALL STATISTICS")
    print("-" * 70)
    print(f"Total Signals:        {overall['total']:>6}")
    print(f"High Confidence ({min_confidence}%+): {overall['high_conf']:>6} ({overall['high_conf']/overall['total']*100:5.1f}%)")
    print(f"Very High (85%+):     {overall['very_high_conf']:>6} ({overall['very_high_conf']/overall['total']*100:5.1f}%)")
    print(f"Excellent (90%+):     {overall['excellent_conf']:>6} ({overall['excellent_conf']/overall['total']*100:5.1f}%)")
    print(f"Average Confidence:   {overall['avg_conf']:>6.2f}%")
    print(f"Max Confidence:       {overall['max_conf']:>6.2f}%")
    print(f"Min Confidence:       {overall['min_conf']:>6.2f}%")
    print(f"Unique Symbols:       {overall['unique_symbols']:>6}")
    print(f"Unique Actions:       {overall['unique_actions']:>6}")
    print()
    
    if by_symbol:
        print("📊 BY SYMBOL")
        print("-" * 70)
        print(f"{'Symbol':<10} {'Count':<8} {'Avg Conf':<10} {'Max Conf':<10} {'High Conf':<10}")
        print("-" * 70)
        for row in by_symbol:
            print(f"{row['symbol']:<10} {row['count']:<8} {row['avg_conf']:>8.2f}% {row['max_conf']:>8.2f}% {row['high_conf_count']:>8} ({row['high_conf_count']/row['count']*100:5.1f}%)")
        print()
    
    if by_action:
        print("📊 BY ACTION")
        print("-" * 70)
        print(f"{'Action':<10} {'Count':<8} {'Avg Conf':<10} {'Max Conf':<10}")
        print("-" * 70)
        for row in by_action:
            print(f"{row['action']:<10} {row['count']:<8} {row['avg_conf']:>8.2f}% {row['max_conf']:>8.2f}%")
        print()
    
    if hourly:
        print("📊 HOURLY DISTRIBUTION")
        print("-" * 70)
        print(f"{'Hour':<8} {'Count':<8} {'Avg Conf':<10}")
        print("-" * 70)
        for row in hourly:
            print(f"{row['hour']:>2}:00     {row['count']:<8} {row['avg_conf']:>8.2f}%")
        print()
    
    # Quality assessment
    print("✅ QUALITY ASSESSMENT")
    print("-" * 70)
    high_conf_pct = overall['high_conf'] / overall['total'] * 100
    if high_conf_pct >= 80:
        print("✅ Excellent: 80%+ of signals meet quality threshold")
    elif high_conf_pct >= 60:
        print("✅ Good: 60-80% of signals meet quality threshold")
    elif high_conf_pct >= 40:
        print("⚠️  Fair: 40-60% of signals meet quality threshold")
    else:
        print("❌ Poor: <40% of signals meet quality threshold")
    
    if overall['avg_conf'] >= min_confidence:
        print(f"✅ Average confidence ({overall['avg_conf']:.2f}%) meets target ({min_confidence}%)")
    else:
        print(f"⚠️  Average confidence ({overall['avg_conf']:.2f}%) below target ({min_confidence}%)")
    print()
    
    print("=" * 70)

if __name__ == '__main__':
    try:
        generate_report()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

