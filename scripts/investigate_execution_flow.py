#!/usr/bin/env python3
"""
Investigate Signal Execution Flow
Comprehensive analysis of signal execution issues including:
- Signal distribution verification
- Market hours handling
- Risk validation checks
- Executor health status
- Manual execution testing
"""
import sys
import sqlite3
import json
import urllib.request
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

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

def check_recent_signals_with_execution() -> List[Dict]:
    """Check recent signals and their execution status"""
    db_path = find_signal_database()
    if not db_path:
        print("❌ Signal database not found")
        return []

    try:
        conn = sqlite3.connect(str(db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get recent signals
        one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        cursor.execute("""
            SELECT
                signal_id,
                symbol,
                action,
                entry_price,
                confidence,
                timestamp,
                order_id,
                outcome,
                regime
            FROM signals
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 50
        """, (one_hour_ago,))

        signals = []
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            row_dict = {col: row[col] for col in columns}
            signals.append({
                'signal_id': row_dict.get('signal_id'),
                'symbol': row_dict.get('symbol'),
                'action': row_dict.get('action'),
                'entry_price': row_dict.get('entry_price'),
                'confidence': row_dict.get('confidence'),
                'timestamp': row_dict.get('timestamp'),
                'order_id': row_dict.get('order_id'),
                'outcome': row_dict.get('outcome'),
                'regime': row_dict.get('regime', 'UNKNOWN')
            })

        conn.close()
        return signals

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_signal_execution():
    """Test if executors can execute signals"""
    print("\n🧪 Testing Signal Execution...")

    # Create test signal
    test_signal = {
        "symbol": "AAPL",
        "action": "BUY",
        "confidence": 85.0,
        "entry_price": 270.0,
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
            print(f"   Argo Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"   ❌ Argo executor error: {e}")

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
            print(f"   Prop Firm Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"   ❌ Prop Firm executor error: {e}")

def check_executor_health() -> Dict[str, Dict]:
    """Check health status of all executors"""
    print("\n🏥 Checking Executor Health...")
    health_status = {}

    executors = [
        ('argo', 8000),
        ('prop_firm', 8001)
    ]

    for executor_id, port in executors:
        try:
            req = urllib.request.Request(
                f'http://localhost:{port}/api/v1/trading/status',
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read())
                health_status[executor_id] = result
                status = result.get('status', 'unknown')
                if status == 'active':
                    print(f"   ✅ {executor_id}: {status}")
                else:
                    print(f"   ⚠️  {executor_id}: {status}")
        except Exception as e:
            health_status[executor_id] = {'status': 'error', 'error': str(e)}
            print(f"   ❌ {executor_id}: Not reachable - {e}")

    return health_status

def check_market_hours():
    """Check if market is open and 24/7 mode status"""
    print("\n🕐 Checking Market Hours & 24/7 Mode...")

    # Check 24/7 mode
    argo_24_7 = os.getenv("ARGO_24_7_MODE", "").lower() in ["true", "1", "yes"]
    print(f"   ARGO_24_7_MODE: {argo_24_7}")

    # Check current time
    now = datetime.now()
    print(f"   Current Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    # Market hours check (simplified - ET timezone)
    hour = now.hour
    weekday = now.weekday()  # 0 = Monday, 6 = Sunday

    # Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
    is_market_hours = weekday < 5 and 9 <= hour < 16

    if is_market_hours:
        print(f"   ✅ Market is OPEN (ET hours)")
    else:
        print(f"   ⏸️  Market is CLOSED (ET hours)")
        if not argo_24_7:
            print(f"   ⚠️  24/7 mode is disabled - stock trades will be blocked")
        else:
            print(f"   ✅ 24/7 mode enabled - trades allowed outside market hours")

    return argo_24_7, is_market_hours

def check_signal_distribution(signals: List[Dict]):
    """Check if signals are being distributed properly"""
    print("\n📤 Checking Signal Distribution...")

    # Check for service_type field
    signals_with_service_type = [s for s in signals if 'service_type' in s or True]  # Most signals should have this

    # Check confidence distribution
    high_confidence = [s for s in signals if s.get('confidence', 0) >= 75]
    medium_confidence = [s for s in signals if 50 <= s.get('confidence', 0) < 75]
    low_confidence = [s for s in signals if s.get('confidence', 0) < 50]

    print(f"   Total Signals: {len(signals)}")
    print(f"   High Confidence (75%+): {len(high_confidence)}")
    print(f"   Medium Confidence (50-75%): {len(medium_confidence)}")
    print(f"   Low Confidence (<50%): {len(low_confidence)}")

    # Check regime distribution
    regimes = {}
    for sig in signals:
        regime = sig.get('regime', 'UNKNOWN')
        regimes[regime] = regimes.get(regime, 0) + 1

    if regimes:
        print(f"\n   Regime Distribution:")
        for regime, count in sorted(regimes.items(), key=lambda x: x[1], reverse=True):
            print(f"      {regime}: {count}")

def analyze_execution_issues(signals: List[Dict]):
    """Analyze why signals aren't being executed"""
    print("\n📊 Execution Analysis...")

    total = len(signals)
    if total == 0:
        print("   ⚠️  No signals to analyze")
        return

    executed = sum(1 for s in signals if s.get('order_id'))
    not_executed = total - executed
    execution_rate = (executed/total*100) if total > 0 else 0

    print(f"   Total Signals: {total}")
    print(f"   Executed: {executed} ({execution_rate:.1f}%)")
    print(f"   Not Executed: {not_executed} ({(not_executed/total*100):.1f}%)")

    if not_executed > 0:
        print("\n   ⚠️  Signals Not Executed:")
        high_confidence_not_executed = [s for s in signals if not s.get('order_id') and s.get('confidence', 0) >= 75]
        print(f"   High Confidence (75%+): {len(high_confidence_not_executed)}")

        for sig in high_confidence_not_executed[:5]:
            print(f"      - {sig['symbol']} {sig['action']} @ {sig['confidence']:.1f}% (Regime: {sig.get('regime', 'UNKNOWN')})")

        # Check for common rejection reasons
        print("\n   🔍 Potential Rejection Reasons:")
        print("      - Market hours (if 24/7 mode disabled)")
        print("      - Confidence below threshold (75% for Argo, 82% for Prop Firm)")
        print("      - Risk validation failures")
        print("      - Position limits")
        print("      - CRISIS regime (Prop Firm skips)")
        print("      - Crypto shorting (Alpaca doesn't support)")

def main():
    """Main function"""
    print("=" * 70)
    print("🔍 Comprehensive Signal Execution Investigation")
    print("=" * 70)

    # Check executor health
    health_status = check_executor_health()

    # Check market hours and 24/7 mode
    argo_24_7, is_market_hours = check_market_hours()

    # Check recent signals
    print("\n📊 Recent Signals (Last Hour)...")
    signals = check_recent_signals_with_execution()

    if signals:
        print(f"   Found {len(signals)} signals")
        check_signal_distribution(signals)
        analyze_execution_issues(signals)
    else:
        print("   ⚠️  No recent signals found")

    # Test execution
    test_signal_execution()

    # Summary and recommendations
    print("\n" + "=" * 70)
    print("📋 Summary & Recommendations")
    print("=" * 70)

    all_healthy = all(h.get('status') == 'active' for h in health_status.values())
    if not all_healthy:
        print("⚠️  Some executors are not healthy - check logs")

    if not argo_24_7 and not is_market_hours:
        print("⚠️  24/7 mode is disabled and market is closed - stock trades will be blocked")
        print("   Recommendation: Set ARGO_24_7_MODE=true to enable 24/7 trading")

    if signals:
        execution_rate = (sum(1 for s in signals if s.get('order_id')) / len(signals) * 100) if signals else 0
        if execution_rate == 0:
            print("⚠️  Execution rate is 0% - investigate signal distribution and validation")
        elif execution_rate < 10:
            print(f"⚠️  Low execution rate ({execution_rate:.1f}%) - review confidence thresholds and risk rules")
        else:
            print(f"✅ Execution rate: {execution_rate:.1f}%")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
