#!/usr/bin/env python3
"""
Monitor Trade Execution in Real-time
"""
import time
import requests
import json

def monitor_execution():
    """Monitor execution for a few cycles"""
    print("\n" + "="*70)
    print("🔍 MONITORING TRADE EXECUTION")
    print("="*70)
    print("\nMonitoring for 30 seconds...\n")
    
    start_time = time.time()
    last_signal_count = 0
    
    while time.time() - start_time < 30:
        try:
            # Check signals
            response = requests.get("http://localhost:8000/api/signals/latest?limit=10", timeout=5)
            if response.status_code == 200:
                signals = response.json()
                current_count = len(signals)
                
                if current_count != last_signal_count:
                    executed = sum(1 for s in signals if s.get('order_id'))
                    print(f"📊 Signals: {current_count} total, {executed} executed")
                    
                    # Show latest signal
                    if signals:
                        latest = signals[0]
                        order_id = latest.get('order_id', 'None')
                        status = "✅ EXECUTED" if order_id else "⏭️  SKIPPED"
                        print(f"   Latest: {latest.get('symbol')} {latest.get('action')} @ ${latest.get('price', 0):.2f} ({latest.get('confidence', 0):.1f}%) - {status}")
                        if order_id:
                            print(f"      Order ID: {order_id}")
                    
                    last_signal_count = current_count
        except Exception as e:
            print(f"   Error: {e}")
        
        time.sleep(5)
    
    print("\n" + "="*70)
    print("✅ Monitoring complete")
    print("="*70 + "\n")

if __name__ == "__main__":
    monitor_execution()

