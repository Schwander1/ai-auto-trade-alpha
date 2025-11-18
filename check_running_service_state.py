#!/usr/bin/env python3
"""
Check the actual running service's state via API
"""
import requests
import json

def check_service_via_api():
    """Check service state via API endpoints"""
    print("\n" + "="*70)
    print("🔍 CHECKING RUNNING SERVICE STATE VIA API")
    print("="*70)
    
    # Check health
    try:
        health = requests.get("http://localhost:8000/health", timeout=5).json()
        print("\n✅ Service Health:")
        print(f"   Status: {health.get('status')}")
        signal_gen = health.get('signal_generation', {})
        print(f"   Signal Generation: {signal_gen.get('status')}")
        print(f"   Background Task: {'Running' if signal_gen.get('background_task_running') else 'Not Running'}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Check trading status
    try:
        status = requests.get("http://localhost:8000/api/v1/trading/status", timeout=5).json()
        print("\n✅ Trading Status:")
        print(f"   Alpaca Connected: {status.get('alpaca_connected')}")
        print(f"   Trading Blocked: {status.get('trading_blocked')}")
        print(f"   Portfolio: ${status.get('portfolio_value', 0):,.2f}")
        print(f"   Buying Power: ${status.get('buying_power', 0):,.2f}")
    except Exception as e:
        print(f"   ⚠️  Could not check trading status: {e}")
    
    # Check recent signals
    try:
        signals = requests.get("http://localhost:8000/api/signals/latest?limit=5", timeout=5).json()
        print(f"\n✅ Recent Signals: {len(signals)}")
        
        executed = sum(1 for s in signals if s.get('order_id'))
        high_conf = sum(1 for s in signals if s.get('confidence', 0) >= 75)
        
        print(f"   High Confidence (≥75%): {high_conf}")
        print(f"   With Order IDs: {executed}")
        print(f"   Without Order IDs: {len(signals) - executed}")
        
        if executed == 0 and high_conf > 0:
            print("\n   ⚠️  High confidence signals not executing!")
            print("   Checking signal details...")
            for sig in signals[:3]:
                print(f"      {sig.get('symbol')}: {sig.get('action')} @ ${sig.get('price', 0):.2f} ({sig.get('confidence', 0):.1f}%) - Order ID: {sig.get('order_id', 'None')}")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    check_service_via_api()

