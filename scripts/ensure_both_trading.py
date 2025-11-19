#!/usr/bin/env python3
"""
Ensure Both Argo and Prop Firm Are Trading
Comprehensive script to verify and fix all trading operations
"""
import os
import sys
import subprocess
import time
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

def check_service_running(port: int, name: str) -> bool:
    """Check if a service is running on a port"""
    try:
        with urllib.request.urlopen(f'http://localhost:{port}/api/v1/trading/status', timeout=5) as response:
            data = json.loads(response.read())
            print(f"✅ {name} is running on port {port}")
            print(f"   Executor ID: {data.get('executor_id', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            return True
    except Exception as e:
        print(f"❌ {name} is NOT running on port {port}: {e}")
        return False

def start_prop_firm_executor():
    """Start Prop Firm executor in background"""
    print("\n🚀 Starting Prop Firm Executor...")

    # Check if already running
    if check_service_running(8001, "Prop Firm Executor"):
        print("   Already running!")
        return True

    # Find the argo directory
    workspace_root = Path(__file__).parent.parent
    argo_dir = workspace_root / "argo"

    if not argo_dir.exists():
        print(f"❌ Argo directory not found: {argo_dir}")
        return False

    # Set environment variables
    env = os.environ.copy()
    env['EXECUTOR_ID'] = 'prop_firm'
    env['EXECUTOR_CONFIG_PATH'] = str(argo_dir / 'config.json')
    env['PORT'] = '8001'
    env['PYTHONPATH'] = str(argo_dir)

    # Start the executor
    try:
        cmd = [
            sys.executable, '-m', 'uvicorn',
            'argo.core.trading_executor:app',
            '--host', '0.0.0.0',
            '--port', '8001'
        ]

        print(f"   Command: {' '.join(cmd)}")
        print(f"   Working Directory: {argo_dir}")

        # Start in background
        process = subprocess.Popen(
            cmd,
            cwd=str(argo_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )

        print(f"   Started with PID: {process.pid}")
        print("   Waiting for service to start...")

        # Wait for service to be ready
        for i in range(30):
            time.sleep(1)
            if check_service_running(8001, "Prop Firm Executor"):
                print("   ✅ Prop Firm Executor started successfully!")
                return True
            print(f"   Waiting... ({i+1}/30)")

        print("   ⚠️  Service started but not responding yet")
        return False

    except Exception as e:
        print(f"   ❌ Failed to start Prop Firm Executor: {e}")
        return False

def check_signal_generation():
    """Check if signal generation is running"""
    print("\n📊 Checking Signal Generation...")

    try:
        with urllib.request.urlopen('http://localhost:8000/health', timeout=5) as response:
            data = json.loads(response.read())
            signal_gen = data.get('signal_generation', {})

            if signal_gen.get('background_task_running'):
                print("✅ Signal generation is running")
                print(f"   Status: {signal_gen.get('status', 'N/A')}")
                return True
            else:
                print("❌ Signal generation background task is NOT running")
                return False
    except Exception as e:
        print(f"❌ Cannot check signal generation: {e}")
        return False

def enable_24_7_mode():
    """Ensure 24/7 mode is enabled"""
    print("\n🔄 Ensuring 24/7 Mode is Enabled...")

    # Check environment variable
    if os.getenv('ARGO_24_7_MODE', '').lower() in ['true', '1', 'yes']:
        print("✅ ARGO_24_7_MODE is set in environment")
        return True

    # Check if we can set it
    print("⚠️  ARGO_24_7_MODE not set in environment")
    print("   Setting ARGO_24_7_MODE=true for this session...")
    os.environ['ARGO_24_7_MODE'] = 'true'
    print("   ✅ 24/7 mode enabled for this session")
    print("   Note: Restart the main service with ARGO_24_7_MODE=true to persist")
    return True

def test_signal_distribution():
    """Test if signals are being distributed to both executors"""
    print("\n🧪 Testing Signal Distribution...")

    # Create a test signal
    test_signal = {
        "symbol": "AAPL",
        "action": "BUY",
        "confidence": 85.0,
        "entry_price": 270.0,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Test Argo executor
    print("   Testing Argo executor (port 8000)...")
    try:
        req = urllib.request.Request(
            'http://localhost:8000/api/v1/trading/execute',
            data=json.dumps(test_signal).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            if result.get('success') or 'error' in result:
                print(f"   ✅ Argo executor responding: {result.get('error', 'OK')}")
            else:
                print(f"   ⚠️  Argo executor response: {result}")
    except Exception as e:
        print(f"   ❌ Argo executor test failed: {e}")

    # Test Prop Firm executor
    print("   Testing Prop Firm executor (port 8001)...")
    try:
        req = urllib.request.Request(
            'http://localhost:8001/api/v1/trading/execute',
            data=json.dumps(test_signal).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            if result.get('success') or 'error' in result:
                print(f"   ✅ Prop Firm executor responding: {result.get('error', 'OK')}")
            else:
                print(f"   ⚠️  Prop Firm executor response: {result}")
    except Exception as e:
        print(f"   ❌ Prop Firm executor test failed: {e}")

def check_recent_signals():
    """Check recent signal generation"""
    print("\n📈 Checking Recent Signals...")

    try:
        # Import the show_recent_signals script
        sys.path.insert(0, str(Path(__file__).parent))
        from show_recent_signals import get_recent_signals

        signals = get_recent_signals(5)
        if signals:
            print(f"   ✅ Found {len(signals)} recent signals")
            latest = signals[0]
            print(f"   Latest: {latest['symbol']} {latest['action']} @ {latest['confidence']:.1f}%")
            print(f"   Time: {latest['timestamp']}")
        else:
            print("   ⚠️  No recent signals found")
    except Exception as e:
        print(f"   ⚠️  Could not check signals: {e}")

def main():
    """Main function"""
    print("=" * 70)
    print("🔧 Ensuring Both Argo and Prop Firm Are Trading")
    print("=" * 70)

    # Step 1: Check Argo executor
    print("\n1️⃣  Checking Argo Executor...")
    argo_running = check_service_running(8000, "Argo Executor")

    # Step 2: Check Prop Firm executor
    print("\n2️⃣  Checking Prop Firm Executor...")
    prop_firm_running = check_service_running(8001, "Prop Firm Executor")

    # Step 3: Start Prop Firm if not running
    if not prop_firm_running:
        start_prop_firm_executor()
        time.sleep(2)
        prop_firm_running = check_service_running(8001, "Prop Firm Executor")

    # Step 4: Check signal generation
    signal_gen_running = check_signal_generation()

    # Step 5: Enable 24/7 mode
    enable_24_7_mode()

    # Step 6: Check recent signals
    check_recent_signals()

    # Step 7: Test signal distribution
    if argo_running and prop_firm_running:
        test_signal_distribution()

    # Summary
    print("\n" + "=" * 70)
    print("📋 Summary")
    print("=" * 70)
    print(f"   Argo Executor: {'✅ Running' if argo_running else '❌ Not Running'}")
    print(f"   Prop Firm Executor: {'✅ Running' if prop_firm_running else '❌ Not Running'}")
    print(f"   Signal Generation: {'✅ Running' if signal_gen_running else '❌ Not Running'}")

    if argo_running and prop_firm_running and signal_gen_running:
        print("\n✅ All systems operational! Both executors are ready to trade.")
    else:
        print("\n⚠️  Some systems are not operational. Please check the errors above.")

    print("=" * 70)

if __name__ == "__main__":
    main()
