#!/usr/bin/env python3
"""
Check if distributor is sending signals and what responses it's getting
"""
import requests
import json
import time
from datetime import datetime

def check_executor_health():
    """Check if executor endpoints are healthy"""
    print("\n" + "="*70)
    print("🔍 CHECKING EXECUTOR HEALTH")
    print("="*70)
    
    executors = [
        ("Argo Executor", "http://localhost:8000/api/v1/trading/status"),
    ]
    
    for name, url in executors:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"\n✅ {name}:")
                print(f"   Status: {status.get('status', 'unknown')}")
                print(f"   Executor ID: {status.get('executor_id', 'unknown')}")
                if 'account' in status:
                    acc = status['account']
                    print(f"   Portfolio: ${acc.get('portfolio_value', 0):,.2f}")
            else:
                print(f"\n⚠️  {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"\n❌ {name}: {e}")

def test_signal_execution():
    """Test signal execution endpoint"""
    print("\n" + "="*70)
    print("🧪 TESTING SIGNAL EXECUTION")
    print("="*70)
    
    # Create a test signal
    test_signal = {
        "symbol": "AAPL",
        "action": "BUY",
        "entry_price": 175.50,
        "target_price": 180.00,
        "stop_price": 170.00,
        "confidence": 95.5,
        "strategy": "test",
        "asset_type": "stock",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    print(f"\nSending test signal: {test_signal['symbol']} {test_signal['action']} @ ${test_signal['entry_price']:.2f}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/trading/execute",
            json=test_signal,
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print(f"\n✅ Execution successful! Order ID: {result.get('order_id')}")
        else:
            print(f"\n⚠️  Execution failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

def monitor_recent_signals():
    """Monitor recent signals and their execution status"""
    print("\n" + "="*70)
    print("📊 RECENT SIGNALS STATUS")
    print("="*70)
    
    try:
        response = requests.get("http://localhost:8000/api/signals/latest?limit=10", timeout=5)
        if response.status_code == 200:
            signals = response.json()
            print(f"\nTotal signals: {len(signals)}")
            
            executed = [s for s in signals if s.get('order_id')]
            not_executed = [s for s in signals if not s.get('order_id')]
            high_conf = [s for s in signals if s.get('confidence', 0) >= 75]
            
            print(f"Executed: {len(executed)}")
            print(f"Not executed: {len(not_executed)}")
            print(f"High confidence (≥75%): {len(high_conf)}")
            
            if high_conf:
                print(f"\nHigh Confidence Signals:")
                for sig in high_conf[:5]:
                    status = "✅ EXECUTED" if sig.get('order_id') else "⏭️  NOT EXECUTED"
                    print(f"  {status} | {sig.get('symbol')} {sig.get('action')} @ ${sig.get('entry_price', sig.get('price', 0)):.2f} ({sig.get('confidence', 0):.1f}%)")
        else:
            print(f"Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_executor_health()
    monitor_recent_signals()
    test_signal_execution()
    print("\n" + "="*70 + "\n")

