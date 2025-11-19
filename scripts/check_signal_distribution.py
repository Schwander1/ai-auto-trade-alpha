#!/usr/bin/env python3
"""
Check Signal Distribution
Verifies if signals are being distributed to executors
"""
import sys
import json
import urllib.request
from pathlib import Path

def check_distributor_logs():
    """Check if distributor is logging activity"""
    print("📋 Checking Signal Distribution...")
    print("")

    # Check main service logs for distributor activity
    log_paths = [
        Path(__file__).parent.parent / "argo" / "logs" / "service.log",
        Path(__file__).parent.parent / "logs" / "service.log",
        Path("/tmp/argo.log"),
    ]

    distributor_activity = False
    for log_path in log_paths:
        if log_path.exists():
            try:
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-100:]  # Last 100 lines

                    for line in recent_lines:
                        if "distributing signal" in line.lower() or "distributed to" in line.lower():
                            distributor_activity = True
                            print(f"   ✅ Found distributor activity in {log_path.name}")
                            print(f"      {line.strip()[:100]}")
                            break
            except Exception as e:
                pass

    if not distributor_activity:
        print("   ⚠️  No distributor activity found in logs")
        print("   This suggests signals may not be distributed to executors")

    return distributor_activity

def check_executor_reception():
    """Check if executors are receiving signals"""
    print("\n📥 Checking Executor Signal Reception...")
    print("")

    # Check if we can query executor logs or status
    try:
        # Check Argo executor
        with urllib.request.urlopen('http://localhost:8000/api/v1/trading/status', timeout=5) as response:
            argo_status = json.loads(response.read())
            print(f"   ✅ Argo Executor: {argo_status.get('status', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Argo Executor: {e}")

    try:
        # Check Prop Firm executor
        with urllib.request.urlopen('http://localhost:8001/api/v1/trading/status', timeout=5) as response:
            prop_status = json.loads(response.read())
            print(f"   ✅ Prop Firm Executor: {prop_status.get('status', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Prop Firm Executor: {e}")

def main():
    """Main function"""
    print("=" * 70)
    print("🔍 Checking Signal Distribution")
    print("=" * 70)

    check_distributor_logs()
    check_executor_reception()

    print("\n" + "=" * 70)
    print("💡 Recommendations:")
    print("=" * 70)
    print("1. Check if signal distributor is initialized in signal generation service")
    print("2. Verify signals have 'service_type: both' to reach both executors")
    print("3. Check market hours - executors may block stock trades when market is closed")
    print("4. Review executor logs for signal reception and validation failures")
    print("5. Test with crypto signals (BTC-USD, ETH-USD) which should work 24/7")
    print("=" * 70)

if __name__ == "__main__":
    main()
