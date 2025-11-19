#!/usr/bin/env python3
"""
Database queries to track SHORT positions and SELL signal execution

This script provides SQL queries to:
1. Find SELL signals that opened SHORT positions
2. Track SHORT position lifecycle
3. Analyze SHORT vs LONG signal execution rates
4. Monitor SHORT position P&L
"""

import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

def get_db_path():
    """Find the signals database"""
    db_paths = [
        Path("data/signals_unified.db"),
        Path("argo/data/signals.db"),
        Path("data/signals.db"),
    ]
    
    for db_path in db_paths:
        if db_path.exists():
            return str(db_path)
    
    return None


def query_sell_signals_with_execution():
    """Query SELL signals and their execution status"""
    db_path = get_db_path()
    if not db_path:
        print("❌ Database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 80)
    print("📊 SELL SIGNALS WITH EXECUTION STATUS")
    print("=" * 80)
    
    query = """
    SELECT 
        symbol,
        action,
        confidence,
        entry_price,
        stop_price,
        target_price,
        timestamp,
        order_id,
        CASE 
            WHEN order_id IS NOT NULL THEN 'EXECUTED'
            ELSE 'PENDING'
        END as status
    FROM signals
    WHERE action = 'SELL'
    ORDER BY timestamp DESC
    LIMIT 50
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if not results:
        print("No SELL signals found")
        conn.close()
        return
    
    print(f"\nFound {len(results)} SELL signals")
    print("-" * 80)
    print(f"{'Symbol':<10} {'Conf':<8} {'Entry':<10} {'Stop':<10} {'Target':<10} {'Status':<10} {'Order ID':<20}")
    print("-" * 80)
    
    executed = 0
    pending = 0
    
    for row in results:
        symbol, action, conf, entry, stop, target, ts, order_id, status = row
        executed += 1 if status == 'EXECUTED' else 0
        pending += 1 if status == 'PENDING' else 0
        
        order_display = order_id[:18] + ".." if order_id and len(order_id) > 20 else (order_id or "N/A")
        print(f"{symbol:<10} {conf:<8.1f} ${entry:<9.2f} ${stop or 0:<9.2f} ${target or 0:<9.2f} {status:<10} {order_display:<20}")
    
    print("-" * 80)
    print(f"Executed: {executed} | Pending: {pending} | Execution Rate: {(executed/len(results)*100):.1f}%")
    
    conn.close()


def query_short_vs_long_execution():
    """Compare SHORT vs LONG signal execution rates"""
    db_path = get_db_path()
    if not db_path:
        print("❌ Database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 80)
    print("📊 SHORT vs LONG EXECUTION COMPARISON")
    print("=" * 80)
    
    query = """
    SELECT 
        action,
        COUNT(*) as total_signals,
        COUNT(CASE WHEN order_id IS NOT NULL THEN 1 END) as executed,
        AVG(confidence) as avg_confidence,
        MIN(confidence) as min_confidence,
        MAX(confidence) as max_confidence
    FROM signals
    WHERE action IN ('BUY', 'SELL')
    GROUP BY action
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if not results:
        print("No signals found")
        conn.close()
        return
    
    print(f"\n{'Action':<10} {'Total':<10} {'Executed':<10} {'Rate':<10} {'Avg Conf':<10} {'Min Conf':<10} {'Max Conf':<10}")
    print("-" * 80)
    
    for row in results:
        action, total, executed, avg_conf, min_conf, max_conf = row
        rate = (executed / total * 100) if total > 0 else 0
        print(f"{action:<10} {total:<10} {executed:<10} {rate:<9.1f}% {avg_conf:<9.1f}% {min_conf:<9.1f}% {max_conf:<9.1f}%")
    
    conn.close()


def query_recent_short_positions():
    """Query recent signals that should have opened SHORT positions"""
    db_path = get_db_path()
    if not db_path:
        print("❌ Database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 80)
    print("📊 RECENT SHORT POSITION SIGNALS (Last 24 Hours)")
    print("=" * 80)
    
    # Get signals from last 24 hours
    query = """
    SELECT 
        symbol,
        action,
        confidence,
        entry_price,
        stop_price,
        target_price,
        timestamp,
        order_id
    FROM signals
    WHERE action = 'SELL'
    AND timestamp >= datetime('now', '-1 day')
    ORDER BY timestamp DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if not results:
        print("No SELL signals in last 24 hours")
        conn.close()
        return
    
    print(f"\nFound {len(results)} SELL signals in last 24 hours")
    print("-" * 80)
    print(f"{'Symbol':<10} {'Conf':<8} {'Entry':<10} {'Stop':<10} {'Target':<10} {'Executed':<10} {'Time'}")
    print("-" * 80)
    
    for row in results:
        symbol, action, conf, entry, stop, target, ts, order_id = row
        executed = "✅ YES" if order_id else "⏳ NO"
        time_display = ts[:19] if ts and len(ts) > 19 else ts
        print(f"{symbol:<10} {conf:<8.1f} ${entry:<9.2f} ${stop or 0:<9.2f} ${target or 0:<9.2f} {executed:<10} {time_display}")
    
    conn.close()


def query_symbol_short_activity():
    """Query SHORT activity by symbol"""
    db_path = get_db_path()
    if not db_path:
        print("❌ Database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 80)
    print("📊 SHORT ACTIVITY BY SYMBOL")
    print("=" * 80)
    
    query = """
    SELECT 
        symbol,
        COUNT(*) as sell_signals,
        COUNT(CASE WHEN order_id IS NOT NULL THEN 1 END) as executed,
        AVG(confidence) as avg_confidence
    FROM signals
    WHERE action = 'SELL'
    GROUP BY symbol
    ORDER BY sell_signals DESC
    LIMIT 20
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if not results:
        print("No SELL signals found")
        conn.close()
        return
    
    print(f"\n{'Symbol':<10} {'SELL Signals':<15} {'Executed':<10} {'Rate':<10} {'Avg Conf':<10}")
    print("-" * 80)
    
    for row in results:
        symbol, total, executed, avg_conf = row
        rate = (executed / total * 100) if total > 0 else 0
        print(f"{symbol:<10} {total:<15} {executed:<10} {rate:<9.1f}% {avg_conf:<9.1f}%")
    
    conn.close()


def main():
    """Run all queries"""
    print("\n" + "=" * 80)
    print("🔍 SHORT POSITION DATABASE QUERIES")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    query_sell_signals_with_execution()
    query_short_vs_long_execution()
    query_recent_short_positions()
    query_symbol_short_activity()
    
    print("\n" + "=" * 80)
    print("✅ QUERIES COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

