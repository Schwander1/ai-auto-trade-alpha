#!/usr/bin/env python3
"""
Comprehensive Signal Execution Diagnosis and Fix
Diagnoses why signals aren't executing and provides fixes
"""
import json
import os
import sqlite3
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


def find_signal_database() -> Optional[Path]:
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


def check_executor_positions():
    """Check positions on both executors"""
    print("\n📊 Checking Executor Positions...")

    executors = [("argo", 8000), ("prop_firm", 8001)]

    for executor_id, port in executors:
        try:
            req = urllib.request.Request(
                f"http://localhost:{port}/api/v1/trading/status",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read())
                account = result.get("account", {})
                positions_count = result.get("positions_count", 0)
                buying_power = account.get("buying_power", 0)

                print(f"\n   {executor_id.upper()}:")
                print(f"      Positions: {positions_count}")
                print(f"      Buying Power: ${buying_power:,.2f}")
                print(f"      Cash: ${account.get('cash', 0):,.2f}")
                print(f"      Portfolio Value: ${account.get('portfolio_value', 0):,.2f}")

                if positions_count > 0:
                    # Try to get actual positions
                    try:
                        positions_req = urllib.request.Request(
                            f"http://localhost:{port}/api/v1/trading/positions",
                            headers={"Content-Type": "application/json"},
                        )
                        with urllib.request.urlopen(positions_req, timeout=5) as pos_response:
                            positions = json.loads(pos_response.read())
                            if isinstance(positions, list):
                                print(
                                    f"      Position Symbols: {[p.get('symbol') for p in positions]}"
                                )
                    except:
                        pass
        except Exception as e:
            print(f"   ❌ {executor_id}: {e}")


def analyze_signal_rejections(signals: List[Dict]):
    """Analyze why signals are being rejected"""
    print("\n🔍 Analyzing Signal Rejections...")

    seell_signals = [s for s in signals if s.get("action") == "SELL" and not s.get("order_id")]
    buy_signals = [s for s in signals if s.get("action") == "BUY" and not s.get("order_id")]

    print(f"\n   SELL Signals Not Executed: {len(seell_signals)}")
    if seell_signals:
        symbols = {}
        for sig in seell_signals:
            sym = sig.get("symbol", "UNKNOWN")
            symbols[sym] = symbols.get(sym, 0) + 1
        print(f"      By Symbol: {symbols}")
        print(f"      ⚠️  SELL signals without positions = SHORT positions (requires buying power)")

    print(f"\n   BUY Signals Not Executed: {len(buy_signals)}")
    if buy_signals:
        symbols = {}
        for sig in buy_signals:
            sym = sig.get("symbol", "UNKNOWN")
            symbols[sym] = symbols.get(sym, 0) + 1
        print(f"      By Symbol: {symbols}")
        print(f"      ⚠️  BUY signals require buying power")


def test_signal_with_position_check():
    """Test signal execution with position awareness"""
    print("\n🧪 Testing Signal Execution with Position Check...")

    # Get current positions
    try:
        req = urllib.request.Request(
            "http://localhost:8001/api/v1/trading/status",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read())
            positions_count = result.get("positions_count", 0)
            buying_power = result.get("account", {}).get("buying_power", 0)

            print(f"   Prop Firm Status:")
            print(f"      Positions: {positions_count}")
            print(f"      Buying Power: ${buying_power:,.2f}")

            # Test BUY signal (requires buying power)
            if buying_power > 0:
                print(f"\n   Testing BUY signal (has buying power)...")
                test_signal = {
                    "symbol": "AAPL",
                    "action": "BUY",
                    "confidence": 85.0,
                    "entry_price": 270.0,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                try:
                    req = urllib.request.Request(
                        "http://localhost:8001/api/v1/trading/execute",
                        data=json.dumps(test_signal).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                    )
                    with urllib.request.urlopen(req, timeout=10) as response:
                        result = json.loads(response.read())
                        print(f"      Result: {json.dumps(result, indent=6)}")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                print(f"   ⚠️  No buying power - cannot test BUY signals")
                print(f"   💡 SELL signals can only close existing positions")
    except Exception as e:
        print(f"   ❌ Error checking positions: {e}")


def provide_recommendations(signals: List[Dict]):
    """Provide actionable recommendations"""
    print("\n" + "=" * 70)
    print("💡 RECOMMENDATIONS")
    print("=" * 70)

    seell_count = len([s for s in signals if s.get("action") == "SELL" and not s.get("order_id")])
    buy_count = len([s for s in signals if s.get("action") == "BUY" and not s.get("order_id")])

    print("\n1. SELL Signal Issues:")
    if seell_count > 0:
        print("   ⚠️  SELL signals without positions = SHORT positions")
        print("   ✅ Solution: Only generate SELL signals when positions exist")
        print("   ✅ Or: Ensure account has buying power for shorting")
    else:
        print("   ✅ No SELL signal issues")

    print("\n2. BUY Signal Issues:")
    if buy_count > 0:
        print("   ⚠️  BUY signals require buying power")
        print("   ✅ Solution: Check account buying power")
        print("   ✅ Or: Close existing positions to free up capital")
    else:
        print("   ✅ No BUY signal issues")

    print("\n3. Signal Distribution:")
    print("   ✅ Verify distributor is initialized in signal generation service")
    print("   ✅ Check logs for 'distributing signal' messages")
    print("   ✅ Ensure signals have correct service_type ('both' or executor-specific)")

    print("\n4. Execution Rate:")
    execution_rate = (
        (sum(1 for s in signals if s.get("order_id")) / len(signals) * 100) if signals else 0
    )
    if execution_rate < 10:
        print(f"   ⚠️  Low execution rate ({execution_rate:.1f}%)")
        print("   ✅ Focus on fixing signal generation to match account state")
        print("   ✅ Generate BUY signals when buying power available")
        print("   ✅ Generate SELL signals only when positions exist")
    else:
        print(f"   ✅ Execution rate acceptable ({execution_rate:.1f}%)")


def main():
    """Main function"""
    print("=" * 70)
    print("🔍 Comprehensive Signal Execution Diagnosis")
    print("=" * 70)

    # Check positions
    check_executor_positions()

    # Get recent signals
    db_path = find_signal_database()
    if db_path:
        try:
            conn = sqlite3.connect(str(db_path), timeout=10.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            cursor.execute(
                """
                SELECT symbol, action, confidence, order_id, regime, service_type
                FROM signals
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 50
            """,
                (one_hour_ago,),
            )

            signals = []
            for row in cursor.fetchall():
                signals.append(
                    {
                        "symbol": row["symbol"],
                        "action": row["action"],
                        "confidence": row["confidence"],
                        "order_id": row["order_id"],
                        "regime": row.get("regime", "UNKNOWN"),
                        "service_type": row.get("service_type", "both"),
                    }
                )

            conn.close()

            if signals:
                analyze_signal_rejections(signals)
        except Exception as e:
            print(f"❌ Error reading signals: {e}")

    # Test execution
    test_signal_with_position_check()

    # Provide recommendations
    if "signals" in locals():
        provide_recommendations(signals)

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
