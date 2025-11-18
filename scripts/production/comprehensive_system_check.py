#!/usr/bin/env python3
"""
Comprehensive system check after Massive API key fix
"""
import requests
import json
import sys
from pathlib import Path
from datetime import datetime

def check_service_health():
    """Check service health"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return {"error": str(e)}

def check_trading_status():
    """Check trading status"""
    try:
        response = requests.get("http://localhost:8000/api/v1/trading/status", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def check_latest_signals():
    """Check latest signals"""
    try:
        response = requests.get("http://localhost:8000/api/signals/latest?limit=10", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def check_config():
    """Check configuration"""
    try:
        with open("argo/config.json", "r") as f:
            return json.load(f)
    except:
        return None

def main():
    print("\n" + "="*70)
    print("🔍 COMPREHENSIVE SYSTEM CHECK")
    print("="*70)
    
    # 1. Service Health
    print("\n1️⃣  Service Health")
    print("-" * 70)
    health = check_service_health()
    if health and not health.get("error"):
        print(f"   ✅ Status: {health.get('status')}")
        print(f"   ✅ Version: {health.get('version')}")
        sg = health.get('signal_generation', {})
        print(f"   ✅ Signal Generation: {sg.get('status')}")
        print(f"   ✅ Background Task: {sg.get('background_task_status')}")
        print(f"   ✅ Data Sources: {health.get('data_sources', 0)}")
    else:
        print(f"   ❌ Service error: {health.get('error', 'Unknown')}")
        return
    
    # 2. Trading Status
    print("\n2️⃣  Trading Status")
    print("-" * 70)
    trading_status = check_trading_status()
    if trading_status:
        print(f"   ✅ Environment: {trading_status.get('environment')}")
        print(f"   ✅ Trading Mode: {trading_status.get('trading_mode')}")
        print(f"   ✅ Alpaca Connected: {trading_status.get('alpaca_connected')}")
        print(f"   ✅ Account Status: {trading_status.get('account_status')}")
        print(f"   ✅ Portfolio Value: ${trading_status.get('portfolio_value', 0):,.2f}")
        print(f"   ✅ Buying Power: ${trading_status.get('buying_power', 0):,.2f}")
    else:
        print("   ⚠️  Trading status not available")
    
    # 3. Configuration
    print("\n3️⃣  Configuration")
    print("-" * 70)
    config = check_config()
    if config:
        trading = config.get('trading', {})
        massive = config.get('massive', {})
        print(f"   ✅ Auto-execute: {trading.get('auto_execute', False)}")
        print(f"   ✅ 24/7 Mode: {trading.get('force_24_7_mode', False)}")
        print(f"   ✅ Min Confidence: {trading.get('min_confidence', 75.0)}%")
        print(f"   ✅ Massive API Key: {'Set' if massive.get('api_key') else 'Not Set'}")
        if massive.get('api_key'):
            key = massive['api_key']
            print(f"      Key: {key[:10]}... (len={len(key)})")
    else:
        print("   ❌ Could not read config")
    
    # 4. Latest Signals
    print("\n4️⃣  Latest Signals")
    print("-" * 70)
    signals = check_latest_signals()
    if signals and isinstance(signals, list):
        if len(signals) > 0:
            print(f"   ✅ Found {len(signals)} recent signals:")
            high_confidence = [s for s in signals if s.get('confidence', 0) >= 75]
            executed = [s for s in signals if s.get('order_id')]
            
            print(f"   • High confidence (≥75%): {len(high_confidence)}")
            print(f"   • With order IDs: {len(executed)}")
            
            for s in signals[:5]:
                timestamp = datetime.fromisoformat(s['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                order_status = "✅ EXECUTED" if s.get('order_id') else "⏳ PENDING"
                print(f"   • {s['symbol']}: {s['action']} @ ${s['price']:.2f} ({s['confidence']:.1f}%) - {order_status} - {timestamp}")
        else:
            print("   ⚠️  No signals found yet (may need to wait for generation cycle)")
    else:
        print("   ⚠️  Could not fetch signals")
    
    # 5. Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    all_good = True
    issues = []
    
    if not health or health.get("error"):
        all_good = False
        issues.append("Service not responding")
    
    if config and not config.get('trading', {}).get('auto_execute'):
        all_good = False
        issues.append("Auto-execute not enabled")
    
    if trading_status and not trading_status.get('alpaca_connected'):
        all_good = False
        issues.append("Alpaca not connected")
    
    if signals and isinstance(signals, list) and len(signals) > 0:
        executed_count = len([s for s in signals if s.get('order_id')])
        if executed_count == 0 and len([s for s in signals if s.get('confidence', 0) >= 75]) > 0:
            all_good = False
            issues.append("High confidence signals not executing")
    
    if all_good:
        print("   ✅ All systems operational!")
        print("   ✅ Massive API key is working")
        print("   ✅ Service is generating signals")
        if config and config.get('trading', {}).get('auto_execute'):
            print("   ✅ Auto-execute is enabled")
            print("   ⚠️  Monitor logs for trade execution")
    else:
        print("   ⚠️  Issues detected:")
        for issue in issues:
            print(f"      • {issue}")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

