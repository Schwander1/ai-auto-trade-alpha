#!/usr/bin/env python3
"""
Verify that Massive API key fix is working
"""
import requests
import json
import sys
from datetime import datetime

def check_service_health():
    """Check if service is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def check_latest_signals():
    """Check latest signals to see if Massive is working"""
    try:
        response = requests.get("http://localhost:8000/api/signals/latest?limit=5", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def check_config_key():
    """Check the key in config.json"""
    try:
        with open("argo/config.json", "r") as f:
            config = json.load(f)
        return config.get("massive", {}).get("api_key", "")
    except:
        return None

def main():
    print("\n" + "="*70)
    print("🔍 VERIFYING MASSIVE API KEY FIX")
    print("="*70)
    
    # Check config
    print("\n1️⃣  Configuration Check")
    print("-" * 70)
    config_key = check_config_key()
    if config_key:
        print(f"   ✅ Config key found: {config_key[:10]}... (len={len(config_key)})")
        if config_key == "KceSpyz5qE4TO_VPQ7Yh7_EXURQcZqOb":
            print("   ✅ New key is in config")
        else:
            print("   ⚠️  Key in config doesn't match new key")
    else:
        print("   ❌ Could not read config")
    
    # Check service health
    print("\n2️⃣  Service Health")
    print("-" * 70)
    health = check_service_health()
    if health:
        print(f"   ✅ Service is running")
        print(f"   Status: {health.get('status')}")
        signal_status = health.get('signal_generation', {}).get('status', 'unknown')
        print(f"   Signal Generation: {signal_status}")
    else:
        print("   ❌ Service is not responding")
        print("   ⚠️  Service may need to be restarted to load new key")
        return
    
    # Check recent signals
    print("\n3️⃣  Recent Signals")
    print("-" * 70)
    signals = check_latest_signals()
    if signals and isinstance(signals, list) and len(signals) > 0:
        print(f"   ✅ Found {len(signals)} recent signals")
        for s in signals[:3]:
            timestamp = datetime.fromisoformat(s['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   • {s['symbol']}: {s['action']} @ ${s['price']:.2f} ({s['confidence']:.1f}%) - {timestamp}")
    else:
        print("   ⚠️  No recent signals found")
        print("   This could mean:")
        print("      - Service just restarted (wait a few minutes)")
        print("      - Signals are still being generated")
        print("      - Check logs for Massive API errors")
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    if config_key == "KceSpyz5qE4TO_VPQ7Yh7_EXURQcZqOb" and health:
        print("   ✅ New API key is in config")
        print("   ✅ Service is running")
        print("\n   ⚠️  If signals aren't generating yet:")
        print("      - Wait 1-2 minutes for service to initialize")
        print("      - Check logs: tail -f /tmp/argo-restart.log | grep -i massive")
        print("      - Verify no 401 errors in logs")
    else:
        print("   ⚠️  Some checks failed - see above for details")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

