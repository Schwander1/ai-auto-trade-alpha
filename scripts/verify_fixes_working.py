#!/usr/bin/env python3
"""
Verify All Fixes Are Working
Checks that all fixes are properly applied and working
"""
import sys
import os
import json
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta

def check_24_7_mode():
    """Check if 24/7 mode is enabled"""
    print("1️⃣  Checking 24/7 Mode...")
    mode = os.getenv("ARGO_24_7_MODE", "").lower()
    if mode in ["true", "1", "yes"]:
        print("   ✅ ARGO_24_7_MODE is enabled")
        return True
    else:
        print(f"   ⚠️  ARGO_24_7_MODE is not set (current: {mode})")
        print("   Set it with: export ARGO_24_7_MODE=true")
        return False

def check_services_running():
    """Check if services are running"""
    print("\n2️⃣  Checking Services...")

    services_ok = True

    # Check main service
    try:
        with urllib.request.urlopen('http://localhost:8000/health', timeout=5) as response:
            health = json.loads(response.read())
            print("   ✅ Main service (port 8000) is running")
            if 'signal_generation' in health:
                sg = health['signal_generation']
                if sg.get('background_task_running'):
                    print("   ✅ Signal generation is active")
                else:
                    print("   ⚠️  Signal generation background task may not be running")
    except Exception as e:
        print(f"   ❌ Main service (port 8000) is not accessible: {e}")
        services_ok = False

    # Check Prop Firm executor
    try:
        with urllib.request.urlopen('http://localhost:8001/api/v1/trading/status', timeout=5) as response:
            status = json.loads(response.read())
            print("   ✅ Prop Firm executor (port 8001) is running")
            print(f"      Status: {status.get('status', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Prop Firm executor (port 8001) is not accessible: {e}")
        services_ok = False

    return services_ok

def test_signal_execution():
    """Test if signal execution works"""
    print("\n3️⃣  Testing Signal Execution...")

    test_signal = {
        "symbol": "BTC-USD",  # Use crypto for 24/7 testing
        "action": "BUY",
        "confidence": 85.0,
        "entry_price": 50000.0,
        "timestamp": datetime.utcnow().isoformat(),
        "regime": "UNKNOWN"
    }

    # Test Argo executor
    print("   Testing Argo executor...")
    try:
        req = urllib.request.Request(
            'http://localhost:8000/api/v1/trading/execute',
            data=json.dumps(test_signal).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            if result.get('success'):
                print(f"   ✅ Argo executor can execute signals (Order ID: {result.get('order_id', 'N/A')})")
            else:
                print(f"   ⚠️  Argo executor returned: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Argo executor test failed: {e}")

    # Test Prop Firm executor
    print("   Testing Prop Firm executor...")
    try:
        req = urllib.request.Request(
            'http://localhost:8001/api/v1/trading/execute',
            data=json.dumps(test_signal).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            if result.get('success'):
                print(f"   ✅ Prop Firm executor can execute signals (Order ID: {result.get('order_id', 'N/A')})")
            else:
                print(f"   ⚠️  Prop Firm executor returned: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Prop Firm executor test failed: {e}")

def check_recent_signals():
    """Check recent signals for execution"""
    print("\n4️⃣  Checking Recent Signals...")

    try:
        import sqlite3
        from pathlib import Path

        db_paths = [
            Path("/root/argo-production") / "data" / "signals_unified.db",
            Path(__file__).parent.parent / "data" / "signals_unified.db",
            Path(__file__).parent.parent / "argo" / "data" / "signals_unified.db",
        ]

        db_path = None
        for path in db_paths:
            if path.exists():
                db_path = path
                break

        if not db_path:
            print("   ⚠️  Signal database not found")
            return

        conn = sqlite3.connect(str(db_path), timeout=5.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get signals from last hour
        one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
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
            LIMIT 10
        """, (one_hour_ago,))

        signals = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        if signals:
            executed = 0
            for s in signals:
                sig_dict = {col: s[col] for col in columns}
                if sig_dict.get('order_id'):
                    executed += 1

            total = len(signals)
            print(f"   Found {total} signals in last hour")
            if total > 0:
                print(f"   Executed: {executed} ({executed/total*100:.1f}%)")

            if executed > 0:
                print("   ✅ Some signals are being executed!")
                for sig in signals[:3]:
                    sig_dict = {col: sig[col] for col in columns}
                    if sig_dict.get('order_id'):
                        print(f"      - {sig_dict['symbol']} {sig_dict['action']} @ {sig_dict['confidence']:.1f}% → Order: {sig_dict.get('order_id', 'N/A')}")
            else:
                print("   ⚠️  No signals executed yet (may need to wait for new signals)")
        else:
            print("   ⚠️  No recent signals found")

    except Exception as e:
        print(f"   ⚠️  Error checking signals: {e}")

def main():
    """Main function"""
    print("=" * 70)
    print("🔍 Verifying All Fixes Are Working")
    print("=" * 70)
    print("")

    checks = []
    checks.append(check_24_7_mode())
    checks.append(check_services_running())
    test_signal_execution()
    check_recent_signals()

    print("\n" + "=" * 70)
    print("📋 Summary")
    print("=" * 70)

    if all(checks):
        print("✅ All critical checks passed!")
        print("")
        print("Next steps:")
        print("  1. Monitor signal execution: python scripts/show_recent_signals.py 20")
        print("  2. Check distribution logs: tail -f argo/logs/service.log | grep -i distribut")
        print("  3. Wait for new signals to be generated and executed")
    else:
        print("⚠️  Some checks failed - review above output")

    print("=" * 70)

if __name__ == "__main__":
    main()
