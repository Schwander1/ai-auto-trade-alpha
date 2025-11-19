#!/usr/bin/env python3
"""
Monitor Signal Execution Live
Continuously monitors signal generation and execution
"""
import sys
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

def find_database():
    """Find signal database"""
    db_paths = [
        Path("/root/argo-production") / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "argo" / "data" / "signals_unified.db",
    ]

    for db_path in db_paths:
        if db_path.exists():
            return db_path
    return None

def monitor_execution(duration_minutes=5):
    """Monitor signal execution for specified duration"""
    db_path = find_database()
    if not db_path:
        print("❌ Signal database not found")
        return

    print("=" * 70)
    print("📊 Monitoring Signal Execution (Live)")
    print("=" * 70)
    print(f"Duration: {duration_minutes} minutes")
    print(f"Database: {db_path}")
    print("=" * 70)
    print("")

    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    seen_signal_ids = set()
    stats = {
        'total': 0,
        'executed': 0,
        'not_executed': 0,
        'by_symbol': defaultdict(int),
        'by_action': defaultdict(int),
    }

    try:
        while datetime.now() < end_time:
            try:
                conn = sqlite3.connect(str(db_path), timeout=5.0)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get signals from last 2 minutes
                two_minutes_ago = (datetime.now() - timedelta(minutes=2)).isoformat()
                cursor.execute("""
                    SELECT
                        signal_id,
                        symbol,
                        action,
                        confidence,
                        timestamp,
                        order_id,
                        executor_id
                    FROM signals
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                """, (two_minutes_ago,))

                signals = cursor.fetchall()
                conn.close()

                # Process new signals
                for sig in signals:
                    sig_id = sig['signal_id']
                    if sig_id not in seen_signal_ids:
                        seen_signal_ids.add(sig_id)
                        stats['total'] += 1
                        stats['by_symbol'][sig['symbol']] += 1
                        stats['by_action'][sig['action']] += 1

                        symbol = sig['symbol']
                        action = sig['action']
                        confidence = sig['confidence']
                        order_id = sig.get('order_id')
                        executor_id = sig.get('executor_id')
                        timestamp = sig['timestamp']

                        if order_id:
                            stats['executed'] += 1
                            status = "✅ EXECUTED"
                            print(f"{status} | {symbol} {action} @ {confidence:.1f}% | Order: {order_id} | Executor: {executor_id or 'N/A'} | {timestamp}")
                        else:
                            stats['not_executed'] += 1
                            if confidence >= 75:
                                status = "⏭️  HIGH CONF NOT EXECUTED"
                                print(f"{status} | {symbol} {action} @ {confidence:.1f}% | {timestamp}")

                # Print stats every 30 seconds
                elapsed = (datetime.now() - (end_time - timedelta(minutes=duration_minutes))).total_seconds()
                if int(elapsed) % 30 == 0 and int(elapsed) > 0:
                    if stats['total'] > 0:
                        exec_rate = (stats['executed'] / stats['total']) * 100
                        print(f"\n📊 Stats: {stats['total']} signals, {stats['executed']} executed ({exec_rate:.1f}%), {stats['not_executed']} not executed\n")

                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                print(f"⚠️  Error: {e}")
                time.sleep(5)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")

    # Final stats
    print("\n" + "=" * 70)
    print("📊 Final Statistics")
    print("=" * 70)
    print(f"Total Signals: {stats['total']}")
    print(f"Executed: {stats['executed']} ({stats['executed']/stats['total']*100:.1f}% if total > 0 else 0:.1f}%)")
    print(f"Not Executed: {stats['not_executed']}")
    print(f"\nBy Symbol: {dict(stats['by_symbol'])}")
    print(f"By Action: {dict(stats['by_action'])}")
    print("=" * 70)

if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    monitor_execution(duration)
