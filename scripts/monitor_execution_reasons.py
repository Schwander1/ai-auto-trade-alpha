#!/usr/bin/env python3
"""
Execution Monitoring Script
Monitors signal execution and tracks rejection reasons
"""
import sqlite3
import json
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict

def find_signal_database() -> Path:
    """Find signal database"""
    db_paths = [
        Path("/root/argo-production") / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "argo" / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "data" / "signals.db",
        Path(__file__).parent.parent / "argo" / "data" / "signals.db",
    ]

    for db_path in db_paths:
        if db_path.exists():
            return db_path
    return None

def get_executor_state():
    """Get current state of all executors"""
    executors = {}

    for executor_id, port in [('argo', 8000), ('prop_firm', 8001)]:
        try:
            req = urllib.request.Request(
                f'http://localhost:{port}/api/v1/trading/status',
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read())
                account = result.get('account', {})
                executors[executor_id] = {
                    'status': result.get('status', 'unknown'),
                    'positions_count': result.get('positions_count', 0),
                    'buying_power': account.get('buying_power', 0),
                    'cash': account.get('cash', 0),
                    'portfolio_value': account.get('portfolio_value', 0)
                }
        except Exception as e:
            executors[executor_id] = {'error': str(e)}

    return executors

def analyze_execution_patterns(signals: List[Dict], executor_state: Dict):
    """Analyze execution patterns and rejection reasons"""
    print("\n📊 Execution Pattern Analysis...")

    executed = [s for s in signals if s.get('order_id')]
    not_executed = [s for s in signals if not s.get('order_id')]

    print(f"\n   Total Signals: {len(signals)}")
    print(f"   Executed: {len(executed)} ({len(executed)/len(signals)*100:.1f}%)")
    print(f"   Not Executed: {len(not_executed)} ({len(not_executed)/len(signals)*100:.1f}%)")

    # Analyze by action
    by_action = defaultdict(lambda: {'executed': 0, 'not_executed': 0})
    for sig in signals:
        action = sig.get('action', 'UNKNOWN')
        if sig.get('order_id'):
            by_action[action]['executed'] += 1
        else:
            by_action[action]['not_executed'] += 1

    print(f"\n   By Action:")
    for action, counts in by_action.items():
        total = counts['executed'] + counts['not_executed']
        exec_rate = (counts['executed'] / total * 100) if total > 0 else 0
        print(f"      {action}: {counts['executed']}/{total} executed ({exec_rate:.1f}%)")

    # Analyze by symbol
    by_symbol = defaultdict(lambda: {'executed': 0, 'not_executed': 0})
    for sig in signals:
        symbol = sig.get('symbol', 'UNKNOWN')
        if sig.get('order_id'):
            by_symbol[symbol]['executed'] += 1
        else:
            by_symbol[symbol]['not_executed'] += 1

    print(f"\n   Top Symbols (Not Executed):")
    for symbol, counts in sorted(by_symbol.items(), key=lambda x: x[1]['not_executed'], reverse=True)[:5]:
        if counts['not_executed'] > 0:
            print(f"      {symbol}: {counts['not_executed']} not executed, {counts['executed']} executed")

    # Infer rejection reasons
    print(f"\n   Inferred Rejection Reasons:")

    # Check buying power
    argo_bp = executor_state.get('argo', {}).get('buying_power', 0)
    prop_bp = executor_state.get('prop_firm', {}).get('buying_power', 0)

    buy_signals_not_executed = [s for s in not_executed if s.get('action') == 'BUY']
    if buy_signals_not_executed and (argo_bp == 0 and prop_bp == 0):
        print(f"      ⚠️  BUY signals: No buying power (Argo: ${argo_bp}, Prop Firm: ${prop_bp})")

    sell_signals_not_executed = [s for s in not_executed if s.get('action') == 'SELL']
    if sell_signals_not_executed:
        print(f"      ⚠️  SELL signals: May require positions to close or buying power to short")

    # Check confidence
    low_confidence = [s for s in not_executed if s.get('confidence', 0) < 75]
    if low_confidence:
        print(f"      ⚠️  Low confidence: {len(low_confidence)} signals below 75% threshold")

def main():
    """Main function"""
    print("=" * 70)
    print("📊 Signal Execution Monitoring")
    print("=" * 70)

    # Get executor state
    print("\n🏥 Executor State...")
    executor_state = get_executor_state()
    for executor_id, state in executor_state.items():
        if 'error' in state:
            print(f"   ❌ {executor_id}: {state['error']}")
        else:
            print(f"   {executor_id.upper()}:")
            print(f"      Status: {state.get('status', 'unknown')}")
            print(f"      Positions: {state.get('positions_count', 0)}")
            print(f"      Buying Power: ${state.get('buying_power', 0):,.2f}")
            print(f"      Portfolio Value: ${state.get('portfolio_value', 0):,.2f}")

    # Get recent signals
    db_path = find_signal_database()
    if not db_path:
        print("\n❌ Signal database not found")
        return

    try:
        conn = sqlite3.connect(str(db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        cursor.execute("""
            SELECT symbol, action, confidence, order_id, regime, service_type, timestamp
            FROM signals
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 100
        """, (one_hour_ago,))

        signals = []
        for row in cursor.fetchall():
            signals.append({
                'symbol': row['symbol'],
                'action': row['action'],
                'confidence': row['confidence'],
                'order_id': row['order_id'],
                'regime': row.get('regime', 'UNKNOWN'),
                'service_type': row.get('service_type', 'both'),
                'timestamp': row['timestamp']
            })

        conn.close()

        if signals:
            analyze_execution_patterns(signals, executor_state)
        else:
            print("\n⚠️  No recent signals found")

    except Exception as e:
        print(f"\n❌ Error: {e}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
