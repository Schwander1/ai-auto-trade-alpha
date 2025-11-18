#!/usr/bin/env python3
"""
Verify signal storage and identify issues
"""
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

def check_signal_storage():
    db_path = Path("/root/argo-production-green/data/signals.db")
    
    if not db_path.exists():
        print("❌ Database not found")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Total signals
    cursor.execute("SELECT COUNT(*) FROM signals")
    total = cursor.fetchone()[0]
    print(f"Total signals in database: {total}")
    
    # Recent signals (last hour)
    cursor.execute("SELECT COUNT(*) FROM signals WHERE timestamp > datetime('now', '-1 hour')")
    recent = cursor.fetchone()[0]
    print(f"Signals in last hour: {recent}")
    
    # Latest signals
    cursor.execute("SELECT symbol, action, confidence, timestamp FROM signals ORDER BY timestamp DESC LIMIT 10")
    latest = cursor.fetchall()
    print(f"\nLatest 10 signals:")
    for sig in latest:
        print(f"  {sig[0]} {sig[1]} @ {sig[2]}% - {sig[3]}")
    
    conn.close()

if __name__ == "__main__":
    check_signal_storage()

