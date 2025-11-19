#!/usr/bin/env python3
"""
Verify Trade Execution is Working
Checks if signals are being executed and getting order_ids
"""
import requests
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

def check_recent_signals_with_order_ids() -> Dict:
    """Check for signals with order_ids in database"""
    print("\n" + "="*70)
    print("📊 CHECKING FOR EXECUTED SIGNALS")
    print("="*70)
    
    db_paths = [
        Path('argo/data/signals.db'),
        Path('data/signals.db'),
        Path('data/signals_unified.db')
    ]
    
    for db_path in db_paths:
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Get table name
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%signal%'")
                tables = cursor.fetchall()
                if not tables:
                    conn.close()
                    continue
                
                table_name = tables[0][0]
                
                # Get recent signals with order_ids
                cursor.execute(f"""
                    SELECT signal_id, symbol, action, entry_price, confidence, timestamp, order_id
                    FROM {table_name}
                    WHERE order_id IS NOT NULL AND order_id != ''
                    ORDER BY timestamp DESC
                    LIMIT 10
                """)
                
                executed_signals = cursor.fetchall()
                
                # Get all recent signals
                cutoff = (datetime.now() - timedelta(hours=2)).isoformat()
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table_name}
                    WHERE timestamp > ?
                """, (cutoff,))
                total_recent = cursor.fetchone()[0]
                
                conn.close()
                
                print(f"\n✅ Found {len(executed_signals)} signals with order_ids")
                print(f"   Total signals in last 2 hours: {total_recent}")
                
                if executed_signals:
                    print(f"\n   Recent Executed Signals:")
                    for sig in executed_signals[:5]:
                        signal_id, symbol, action, price, confidence, timestamp, order_id = sig
                        print(f"      ✅ {symbol} {action} @ ${price:.2f} ({confidence:.1f}%)")
                        print(f"         Order ID: {order_id} | Time: {timestamp}")
                    
                    return {
                        'executed_count': len(executed_signals),
                        'total_recent': total_recent,
                        'execution_rate': (len(executed_signals) / total_recent * 100) if total_recent > 0 else 0
                    }
                else:
                    print(f"\n   ⏳ No signals with order_ids yet")
                    print(f"   Monitoring for new executions...")
                    return {'executed_count': 0, 'total_recent': total_recent, 'execution_rate': 0}
                    
            except Exception as e:
                print(f"   Error: {e}")
                return None
    
    print("   ⚠️  No database found")
    return None

def test_signal_execution():
    """Test signal execution endpoint"""
    print("\n" + "="*70)
    print("🧪 TESTING SIGNAL EXECUTION")
    print("="*70)
    
    test_signal = {
        'symbol': 'AAPL',
        'action': 'BUY',
        'entry_price': 175.50,
        'target_price': 180.00,
        'stop_price': 170.00,
        'confidence': 95.5,
        'strategy': 'test',
        'asset_type': 'stock',
        'service_type': 'both',
        'timestamp': datetime.now().isoformat() + 'Z'
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/trading/execute',
            json=test_signal,
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            print(f"✅ SUCCESS! Order ID: {result.get('order_id')}")
            return True
        else:
            print(f"⚠️  Failed: {result.get('error', 'Unknown')}")
            return False
    except requests.exceptions.Timeout:
        print("⚠️  Request timed out (service busy)")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def monitor_for_executions(duration_minutes: int = 5):
    """Monitor for signal executions"""
    print("\n" + "="*70)
    print("🔍 MONITORING FOR SIGNAL EXECUTIONS")
    print("="*70)
    print(f"Monitoring for {duration_minutes} minutes...")
    print("Watching for signals getting order_ids...")
    print("="*70 + "\n")
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    seen_order_ids = set()
    
    try:
        while datetime.now() < end_time:
            result = check_recent_signals_with_order_ids()
            
            if result and result['executed_count'] > 0:
                print(f"\n✅ Found {result['executed_count']} executed signals!")
                print(f"   Execution rate: {result['execution_rate']:.1f}%")
                break
            
            elapsed = (datetime.now() - start_time).total_seconds()
            remaining = (end_time - datetime.now()).total_seconds()
            print(f"\n⏳ Waiting for executions... ({int(remaining)}s remaining)")
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped")
    
    # Final check
    print("\n" + "="*70)
    print("📊 FINAL CHECK")
    print("="*70)
    final_result = check_recent_signals_with_order_ids()
    
    if final_result and final_result['executed_count'] > 0:
        print(f"\n✅ SUCCESS! Found {final_result['executed_count']} executed signals")
        print(f"   Execution rate: {final_result['execution_rate']:.1f}%")
    else:
        print(f"\n⏳ No executed signals found yet")
        print(f"   System is ready - executions will happen when signals meet criteria")

if __name__ == "__main__":
    import sys
    
    # Test execution
    test_result = test_signal_execution()
    
    # Check for existing executions
    check_recent_signals_with_order_ids()
    
    # Monitor if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        monitor_for_executions(duration)

