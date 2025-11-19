#!/usr/bin/env python3
"""
Diagnose and Fix Signal Generation Issues
Comprehensive diagnostic and fix script
"""
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def check_signal_generation_status() -> Dict:
    """Check if signal generation is running"""
    results = {
        'signal_generator_running': False,
        'last_signal_time': None,
        'signals_in_last_hour': 0,
        'signals_in_last_24h': 0,
        'executor_status': {},
        'issues': []
    }

    # Check database for recent signals
    db_path = find_signal_database()
    if db_path and db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path), timeout=10.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get last signal
            cursor.execute("""
                SELECT timestamp FROM signals
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                results['last_signal_time'] = row['timestamp']
                last_signal = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                now = datetime.now(last_signal.tzinfo)
                time_since_last = (now - last_signal).total_seconds() / 60  # minutes

                if time_since_last < 10:
                    results['signal_generator_running'] = True
                elif time_since_last > 60:
                    results['issues'].append(f"⚠️  No signals generated in {int(time_since_last)} minutes")

            # Count signals in last hour
            one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) as count FROM signals
                WHERE timestamp > ?
            """, (one_hour_ago,))
            row = cursor.fetchone()
            results['signals_in_last_hour'] = row['count'] if row else 0

            # Count signals in last 24 hours
            one_day_ago = (datetime.now() - timedelta(hours=24)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) as count FROM signals
                WHERE timestamp > ?
            """, (one_day_ago,))
            row = cursor.fetchone()
            results['signals_in_last_24h'] = row['count'] if row else 0

            conn.close()
        except Exception as e:
            results['issues'].append(f"❌ Database error: {e}")

    # Check executor status
    import urllib.request
    try:
        with urllib.request.urlopen('http://localhost:8000/api/v1/trading/status', timeout=5) as response:
            data = json.loads(response.read())
            results['executor_status']['argo'] = data
    except Exception as e:
        results['issues'].append(f"⚠️  Argo executor not accessible: {e}")

    try:
        with urllib.request.urlopen('http://localhost:8001/api/v1/trading/status', timeout=5) as response:
            data = json.loads(response.read())
            results['executor_status']['prop_firm'] = data
    except Exception as e:
        results['issues'].append(f"⚠️  Prop Firm executor not accessible: {e}")

    return results

def find_signal_database() -> Optional[Path]:
    """Find the signal database file"""
    db_paths = [
        Path("/root/argo-production") / "data" / "signals_unified.db",
        Path("/root/argo-production-green") / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "argo" / "data" / "signals_unified.db",
        Path(__file__).parent.parent / "data" / "signals.db",
        Path(__file__).parent.parent / "argo" / "data" / "signals.db",
    ]

    for db_path in db_paths:
        if db_path.exists():
            return db_path
    return None

def check_market_hours_restrictions() -> Dict:
    """Check if market hours are restricting signal generation"""
    results = {
        'current_time_utc': datetime.utcnow().isoformat(),
        'current_time_et': None,
        'is_market_hours': False,
        'market_status': 'unknown'
    }

    try:
        from datetime import timezone
        import pytz

        utc_now = datetime.now(timezone.utc)
        et = pytz.timezone('US/Eastern')
        et_now = utc_now.astimezone(et)
        results['current_time_et'] = et_now.strftime('%Y-%m-%d %H:%M:%S %Z')

        # Market hours: 9:30 AM - 4:00 PM ET, Mon-Fri
        hour = et_now.hour
        minute = et_now.minute
        weekday = et_now.weekday()  # 0=Monday, 6=Sunday

        if weekday < 5:  # Monday-Friday
            if (hour == 9 and minute >= 30) or (10 <= hour < 16) or (hour == 16 and minute == 0):
                results['is_market_hours'] = True
                results['market_status'] = 'OPEN'
            else:
                results['market_status'] = 'CLOSED'
        else:
            results['market_status'] = 'WEEKEND'

    except ImportError:
        results['issues'] = 'pytz not available for timezone conversion'

    return results

def generate_fixes(status: Dict, market: Dict) -> List[str]:
    """Generate fix recommendations"""
    fixes = []

    if not status['signal_generator_running']:
        fixes.append("1. Start signal generation service:")
        fixes.append("   - Check if main.py is running with background task")
        fixes.append("   - Verify ARGO_24_7_MODE=true is set")
        fixes.append("   - Check logs for errors")

    if status['signals_in_last_hour'] == 0:
        fixes.append("2. No signals in last hour - check:")
        fixes.append("   - Signal generation service status")
        fixes.append("   - Data source connectivity")
        fixes.append("   - Configuration settings")

    if market['market_status'] == 'CLOSED' and not status.get('force_24_7', False):
        fixes.append("3. Market is closed - enable 24/7 mode:")
        fixes.append("   - Set ARGO_24_7_MODE=true environment variable")
        fixes.append("   - Or set config.trading.force_24_7_mode=true")
        fixes.append("   - This allows signal generation outside market hours")

    if not status['executor_status'].get('argo'):
        fixes.append("4. Argo executor not accessible:")
        fixes.append("   - Check if service is running on port 8000")
        fixes.append("   - Verify executor configuration")

    if not status['executor_status'].get('prop_firm'):
        fixes.append("5. Prop Firm executor not accessible:")
        fixes.append("   - Check if service is running on port 8001")
        fixes.append("   - This is optional if not using prop firm trading")

    return fixes

def main():
    """Main diagnostic function"""
    print("🔍 Diagnosing Signal Generation Issues...")
    print("=" * 60)

    # Check signal generation status
    print("\n📊 Signal Generation Status:")
    status = check_signal_generation_status()
    print(f"   Running: {'✅ Yes' if status['signal_generator_running'] else '❌ No'}")
    print(f"   Last Signal: {status['last_signal_time'] or 'N/A'}")
    print(f"   Signals (1h): {status['signals_in_last_hour']}")
    print(f"   Signals (24h): {status['signals_in_last_24h']}")

    # Check market hours
    print("\n🕐 Market Hours Status:")
    market = check_market_hours_restrictions()
    print(f"   Current Time (ET): {market.get('current_time_et', 'N/A')}")
    print(f"   Market Status: {market['market_status']}")
    print(f"   Is Market Hours: {'✅ Yes' if market['is_market_hours'] else '❌ No'}")

    # Check executors
    print("\n⚙️  Executor Status:")
    if status['executor_status'].get('argo'):
        print("   Argo Executor: ✅ Accessible")
        argo = status['executor_status']['argo']
        print(f"      Account: {argo.get('account_name', 'N/A')}")
        print(f"      Status: {argo.get('account_status', 'N/A')}")
    else:
        print("   Argo Executor: ❌ Not accessible")

    if status['executor_status'].get('prop_firm'):
        print("   Prop Firm Executor: ✅ Accessible")
    else:
        print("   Prop Firm Executor: ⚠️  Not accessible (optional)")

    # Show issues
    if status['issues']:
        print("\n⚠️  Issues Found:")
        for issue in status['issues']:
            print(f"   {issue}")

    # Generate fixes
    print("\n🔧 Recommended Fixes:")
    fixes = generate_fixes(status, market)
    if fixes:
        for fix in fixes:
            print(f"   {fix}")
    else:
        print("   ✅ No issues detected!")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
