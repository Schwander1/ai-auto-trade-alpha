#!/usr/bin/env python3
"""
Comprehensive Trading Report
Checks all databases and provides complete trading activity summary
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

def find_all_databases() -> List[Path]:
    """Find all signal databases"""
    db_paths = [
        Path("/root/argo-production") / "data" / "signals_unified.db",
        Path("/root/argo-production-green") / "data" / "signals_unified.db",
        Path("/root/argo-production-blue") / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "argo" / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "data" / "signals.db",
        Path(__file__).parent.parent / "argo" / "data" / "signals.db",
    ]

    found = []
    for db_path in db_paths:
        if db_path.exists():
            found.append(db_path)

    return found

def get_today_signals(db_path: Path) -> List[Dict]:
    """Get today's signals from database"""
    try:
        conn = sqlite3.connect(str(db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check table structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signals'")
        if not cursor.fetchone():
            conn.close()
            return []

        # Get column names
        cursor.execute("PRAGMA table_info(signals)")
        columns = [row[1] for row in cursor.fetchall()]

        # Determine timestamp column
        timestamp_col = 'timestamp' if 'timestamp' in columns else 'created_at'

        # Today's date range
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now()

        # Build query based on available columns
        available_cols = set(columns)
        select_cols = ['signal_id', 'symbol', 'action', 'entry_price', 'confidence',
                      timestamp_col + ' as timestamp', 'order_id', 'outcome']
        if 'strategy' in available_cols:
            select_cols.append('strategy')
        if 'regime' in available_cols:
            select_cols.append('regime')

        query = f"""
            SELECT {', '.join(select_cols)}
            FROM signals
            WHERE {timestamp_col} >= ? AND {timestamp_col} <= ?
            ORDER BY {timestamp_col} DESC
        """

        cursor.execute(query, (today_start.isoformat(), today_end.isoformat()))

        signals = []
        for row in cursor.fetchall():
            signal = {}
            for col in ['signal_id', 'symbol', 'action', 'entry_price', 'confidence',
                       'timestamp', 'order_id', 'outcome']:
                try:
                    signal[col] = row[col] if col in row.keys() else None
                except (KeyError, IndexError):
                    signal[col] = None
            if 'strategy' in available_cols:
                signal['strategy'] = row['strategy'] if 'strategy' in row.keys() else None
            if 'regime' in available_cols:
                signal['regime'] = row['regime'] if 'regime' in row.keys() else None
            signals.append(signal)

        conn.close()
        return signals
    except Exception as e:
        print(f"⚠️  Error reading {db_path}: {e}")
        return []

def generate_comprehensive_report():
    """Generate comprehensive trading report"""
    print("=" * 80)
    print("📊 COMPREHENSIVE TRADING REPORT")
    print("=" * 80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # Find databases
    databases = find_all_databases()

    if not databases:
        print("⚠️  No signal databases found")
        print("\nSearched locations:")
        for path in [
            "/root/argo-production/data/signals_unified.db",
            "data/signals_unified.db",
            "argo/data/signals_unified.db",
        ]:
            print(f"   - {path}")
        return

    print(f"✅ Found {len(databases)} database(s):")
    for db in databases:
        print(f"   - {db}")
    print()

    # Collect all signals
    all_signals = []
    for db_path in databases:
        signals = get_today_signals(db_path)
        all_signals.extend(signals)
        if signals:
            print(f"📊 {db_path.name}: {len(signals)} signals today")

    if not all_signals:
        print("\n⚠️  No signals found for today")
        print("\nChecking recent signals (last 24 hours)...")

        # Check last 24 hours
        for db_path in databases:
            try:
                conn = sqlite3.connect(str(db_path), timeout=10.0)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signals'")
                if not cursor.fetchone():
                    conn.close()
                    continue

                cursor.execute("PRAGMA table_info(signals)")
                columns = [row[1] for row in cursor.fetchall()]
                timestamp_col = 'timestamp' if 'timestamp' in columns else 'created_at'

                yesterday = datetime.now() - timedelta(days=1)
                query = f"""
                    SELECT COUNT(*) as count
                    FROM signals
                    WHERE {timestamp_col} >= ?
                """
                cursor.execute(query, (yesterday.isoformat(),))
                count = cursor.fetchone()['count']
                print(f"   {db_path.name}: {count} signals in last 24 hours")
                conn.close()
            except Exception as e:
                pass

        return

    print()
    print("=" * 80)
    print("📈 TODAY'S TRADING SUMMARY")
    print("=" * 80)

    # Overall statistics
    total = len(all_signals)
    buy_count = sum(1 for s in all_signals if s['action'] in ['BUY', 'LONG'])
    sell_count = sum(1 for s in all_signals if s['action'] in ['SELL', 'SHORT'])
    executed_count = sum(1 for s in all_signals if s.get('order_id') and s['order_id'] != 'N/A')
    avg_confidence = sum(s['confidence'] for s in all_signals if s['confidence']) / total if total > 0 else 0

    wins = sum(1 for s in all_signals if s.get('outcome') == 'win')
    losses = sum(1 for s in all_signals if s.get('outcome') == 'loss')
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

    print(f"\n📊 OVERALL STATISTICS")
    print("-" * 80)
    print(f"Total Signals Generated:     {total:>6}")
    print(f"Signals Executed:            {executed_count:>6} ({executed_count/total*100:5.1f}%)")
    print(f"Signals Not Executed:        {total - executed_count:>6} ({(total-executed_count)/total*100:5.1f}%)")
    print()
    print(f"BUY/LONG Signals:            {buy_count:>6} ({buy_count/total*100:5.1f}%)")
    print(f"SELL/SHORT Signals:          {sell_count:>6} ({sell_count/total*100:5.1f}%)")
    print()
    print(f"Average Confidence:          {avg_confidence:>6.2f}%")
    print(f"High Confidence (90%+):      {sum(1 for s in all_signals if s.get('confidence', 0) >= 90):>6}")
    print(f"Very High Confidence (95%+): {sum(1 for s in all_signals if s.get('confidence', 0) >= 95):>6}")
    print()
    if wins + losses > 0:
        print(f"Completed Trades:            {wins + losses:>6}")
        print(f"Wins:                        {wins:>6}")
        print(f"Losses:                      {losses:>6}")
        print(f"Win Rate:                    {win_rate:>6.2f}%")

    # By symbol
    symbols = {}
    for signal in all_signals:
        symbol = signal['symbol']
        if symbol not in symbols:
            symbols[symbol] = {'total': 0, 'executed': 0, 'buy': 0, 'sell': 0, 'avg_conf': 0, 'confidences': []}
        symbols[symbol]['total'] += 1
        if signal.get('order_id') and signal['order_id'] != 'N/A':
            symbols[symbol]['executed'] += 1
        if signal['action'] in ['BUY', 'LONG']:
            symbols[symbol]['buy'] += 1
        else:
            symbols[symbol]['sell'] += 1
        if signal.get('confidence'):
            symbols[symbol]['confidences'].append(signal['confidence'])

    for symbol in symbols:
        if symbols[symbol]['confidences']:
            symbols[symbol]['avg_conf'] = sum(symbols[symbol]['confidences']) / len(symbols[symbol]['confidences'])

    if symbols:
        print(f"\n📊 BY SYMBOL")
        print("-" * 80)
        print(f"{'Symbol':<12} {'Total':<8} {'Executed':<10} {'BUY':<8} {'SELL':<8} {'Avg Conf':<10}")
        print("-" * 80)
        for symbol in sorted(symbols.keys()):
            s = symbols[symbol]
            print(f"{symbol:<12} {s['total']:<8} {s['executed']:<10} {s['buy']:<8} {s['sell']:<8} {s['avg_conf']:>8.2f}%")

    # Executed signals
    executed_signals = [s for s in all_signals if s.get('order_id') and s['order_id'] != 'N/A']
    if executed_signals:
        print(f"\n✅ EXECUTED SIGNALS ({len(executed_signals)})")
        print("-" * 80)
        print(f"{'Time':<20} {'Symbol':<10} {'Action':<8} {'Price':<12} {'Conf':<8} {'Order ID':<20} {'Outcome':<10}")
        print("-" * 80)
        for sig in executed_signals[:20]:  # Show first 20
            timestamp = sig['timestamp'][:19] if sig.get('timestamp') else 'N/A'
            symbol = sig['symbol']
            action = sig['action']
            price = f"${sig['entry_price']:.2f}" if sig.get('entry_price') else "N/A"
            conf = f"{sig['confidence']:.1f}%" if sig.get('confidence') else "N/A"
            order_id = str(sig.get('order_id', 'N/A'))[:18]
            outcome = sig.get('outcome', 'N/A') or 'N/A'
            print(f"{timestamp:<20} {symbol:<10} {action:<8} {price:<12} {conf:<8} {order_id:<20} {outcome:<10}")
        if len(executed_signals) > 20:
            print(f"... and {len(executed_signals) - 20} more executed signals")

    # High confidence signals not executed
    high_conf_not_executed = [s for s in all_signals
                              if s.get('confidence', 0) >= 90
                              and (not s.get('order_id') or s['order_id'] == 'N/A')]
    if high_conf_not_executed:
        print(f"\n⚠️  HIGH CONFIDENCE SIGNALS NOT EXECUTED ({len(high_conf_not_executed)})")
        print("-" * 80)
        print(f"{'Time':<20} {'Symbol':<10} {'Action':<8} {'Price':<12} {'Conf':<8}")
        print("-" * 80)
        for sig in high_conf_not_executed[:10]:  # Show first 10
            timestamp = sig['timestamp'][:19] if sig.get('timestamp') else 'N/A'
            symbol = sig['symbol']
            action = sig['action']
            price = f"${sig['entry_price']:.2f}" if sig.get('entry_price') else "N/A"
            conf = f"{sig['confidence']:.1f}%" if sig.get('confidence') else "N/A"
            print(f"{timestamp:<20} {symbol:<10} {action:<8} {price:<12} {conf:<8}")
        if len(high_conf_not_executed) > 10:
            print(f"... and {len(high_conf_not_executed) - 10} more")

    print()
    print("=" * 80)

if __name__ == '__main__':
    try:
        generate_comprehensive_report()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
