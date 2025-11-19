#!/usr/bin/env python3
"""
Investigate Execution Status
Comprehensive investigation of why trades are/aren't executing
NO CHANGES - INVESTIGATION ONLY
"""
import sys
import sqlite3
import json
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta

def check_today_executions():
    """Check if any trades executed today"""
    db_paths = [
        Path("/root/argo-production") / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "argo" / "data" / "signals_unified.db",
    ]

    db_path = None
    for p in db_paths:
        if p.exists():
            db_path = p
            break

    if not db_path:
        print("❌ Signal database not found")
        return False

    try:
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        today = datetime.now().date().isoformat()

        # Get today's stats
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN order_id IS NOT NULL AND order_id != '' THEN 1 ELSE 0 END) as executed
            FROM signals
            WHERE DATE(timestamp) = ?
        """, (today,))

        stats = cursor.fetchone()
        total = stats['total'] or 0
        executed = stats['executed'] or 0

        # Get executed signals
        cursor.execute("""
            SELECT symbol, action, entry_price, confidence, timestamp, order_id, executor_id
            FROM signals
            WHERE DATE(timestamp) = ? AND order_id IS NOT NULL AND order_id != ''
            ORDER BY timestamp DESC
        """, (today,))

        executed_signals = cursor.fetchall()
        conn.close()

        print("=" * 70)
        print("📊 TODAY'S EXECUTION STATUS")
        print("=" * 70)
        print(f"Date: {today}")
        print(f"Total Signals Generated: {total}")
        print(f"Executed: {executed}")
        if total > 0:
            print(f"Execution Rate: {executed/total*100:.1f}%")
        print("=" * 70)

        if executed_signals:
            print(f"\n✅ EXECUTED TRADES TODAY ({len(executed_signals)}):")
            print("-" * 70)
            for sig in executed_signals:
                print(f"  {sig['symbol']} {sig['action']} @ ${sig['entry_price']:.2f} | {sig['confidence']:.1f}% | Order: {sig['order_id']} | Executor: {sig.get('executor_id', 'N/A')}")
            return True
        else:
            print("\n❌ NO TRADES EXECUTED TODAY")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_executor_status():
    """Check executor status"""
    print("\n" + "=" * 70)
    print("🔍 EXECUTOR STATUS")
    print("=" * 70)

    # Check Argo executor
    try:
        with urllib.request.urlopen('http://localhost:8000/api/v1/trading/status', timeout=5) as response:
            status = json.loads(response.read())
            print("✅ Argo Executor (port 8000): Running")
            print(f"   Status: {status.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Argo Executor (port 8000): Not accessible - {e}")

    # Check Prop Firm executor
    try:
        with urllib.request.urlopen('http://localhost:8001/api/v1/trading/status', timeout=5) as response:
            status = json.loads(response.read())
            print("✅ Prop Firm Executor (port 8001): Running")
            print(f"   Status: {status.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Prop Firm Executor (port 8001): Not accessible - {e}")

def analyze_recent_signals():
    """Analyze recent signals"""
    print("\n" + "=" * 70)
    print("📈 RECENT SIGNAL ANALYSIS")
    print("=" * 70)

    db_paths = [
        Path("/root/argo-production") / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "argo" / "data" / "signals_unified.db",
    ]

    db_path = None
    for p in db_paths:
        if p.exists():
            db_path = p
            break

    if not db_path:
        print("❌ Signal database not found")
        return

    try:
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get signals from last 2 hours
        two_hours_ago = (datetime.now() - timedelta(hours=2)).isoformat()
        cursor.execute("""
            SELECT
                symbol,
                action,
                confidence,
                service_type,
                timestamp,
                order_id
            FROM signals
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 30
        """, (two_hours_ago,))

        signals = cursor.fetchall()
        conn.close()

        if not signals:
            print("⚠️  No recent signals found")
            return

        total = len(signals)
        executed = sum(1 for s in signals if s.get('order_id'))
        high_conf = [s for s in signals if s.get('confidence', 0) >= 75]
        argo_eligible = [s for s in high_conf if s.get('confidence', 0) >= 75]
        prop_eligible = [s for s in high_conf if s.get('confidence', 0) >= 82]

        print(f"Total Signals (last 2h): {total}")
        print(f"Executed: {executed} ({executed/total*100:.1f}%)")
        print(f"High Confidence (75%+): {len(high_conf)}")
        print(f"Argo Eligible (75%+): {len(argo_eligible)}")
        print(f"Prop Firm Eligible (82%+): {len(prop_eligible)}")
        print()

        print("Sample Recent Signals:")
        for sig in signals[:5]:
            exec_status = "✅ EXECUTED" if sig.get('order_id') else "❌ NOT EXECUTED"
            print(f"  {exec_status} | {sig['symbol']} {sig['action']} @ {sig.get('confidence', 0):.1f}% | Service: {sig.get('service_type', 'N/A')}")

    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main investigation"""
    print("=" * 70)
    print("🔍 EXECUTION STATUS INVESTIGATION")
    print("=" * 70)
    print("NO CHANGES - INVESTIGATION ONLY")
    print("=" * 70)

    has_executions = check_today_executions()
    check_executor_status()
    analyze_recent_signals()

    print("\n" + "=" * 70)
    print("📋 SUMMARY")
    print("=" * 70)

    if has_executions:
        print("✅ TRADES ARE BEING EXECUTED TODAY")
    else:
        print("❌ NO TRADES EXECUTED TODAY")
        print("\nPossible reasons:")
        print("  1. Signals not being distributed to executors")
        print("  2. Market hours restrictions (if 24/7 mode not working)")
        print("  3. Risk validation rejecting signals")
        print("  4. Executors not receiving signals")
        print("  5. Confidence thresholds not met")

    print("=" * 70)

if __name__ == "__main__":
    main()
