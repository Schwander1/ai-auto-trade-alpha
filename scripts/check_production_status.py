#!/usr/bin/env python3
"""
Check Production Server Trade Execution Status
Run this on the production server to verify everything is working
"""
import sys
import subprocess
from pathlib import Path

def check_alpaca_sdk():
    """Check if Alpaca SDK is installed"""
    try:
        import alpaca
        print("✅ Alpaca SDK: Installed")
        return True
    except ImportError:
        print("❌ Alpaca SDK: Not installed")
        print("   Install with: pip install alpaca-py")
        return False

def check_alpaca_connection():
    """Check Alpaca connection"""
    try:
        sys.path.insert(0, str(Path("/root/argo-production-unified")))
        from argo.core.paper_trading_engine import PaperTradingEngine
        engine = PaperTradingEngine()
        if engine.alpaca_enabled:
            account = engine.get_account_details()
            if account:
                print("✅ Alpaca Connection: Connected")
                print(f"   Account: {engine.account_name}")
                return True
        print("❌ Alpaca Connection: Not connected")
        return False
    except Exception as e:
        print(f"❌ Alpaca Connection: Error - {e}")
        return False

def check_services():
    """Check if services are running"""
    services = {
        'argo-signal-generator.service': 7999,
        'argo-trading-executor.service': 8000,
        'argo-prop-firm-executor.service': 8001,
    }
    
    print("\n📊 Service Status:")
    for service, port in services.items():
        result = subprocess.run(
            ['systemctl', 'is-active', service],
            capture_output=True,
            text=True
        )
        status = result.stdout.strip()
        if status == 'active':
            print(f"   ✅ {service}: Running (port {port})")
        else:
            print(f"   ❌ {service}: Not running")

def main():
    print("=" * 80)
    print("🔍 PRODUCTION SERVER STATUS CHECK")
    print("=" * 80)
    
    sdk_ok = check_alpaca_sdk()
    if sdk_ok:
        check_alpaca_connection()
    check_services()
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
