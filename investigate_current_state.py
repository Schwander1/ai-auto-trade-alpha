#!/usr/bin/env python3
"""
Investigate Current Trading State
Check service status, signals, and execution
"""
import sys
import requests
import json
from pathlib import Path
from datetime import datetime

def check_service_health():
    """Check service health and 24/7 mode"""
    print("\n" + "="*70)
    print("🔍 SERVICE HEALTH CHECK")
    print("="*70)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("\n✅ Service is RUNNING")
            print(f"   Version: {health.get('version', 'unknown')}")
            print(f"   Uptime: {health.get('uptime', 'unknown')}")
            
            signal_gen = health.get('signal_generation', {})
            if signal_gen:
                print(f"\n   Signal Generation:")
                print(f"      Status: {signal_gen.get('status', 'unknown')}")
                print(f"      Background Task: {'Running' if signal_gen.get('background_task_running') else 'NOT Running'}")
                if signal_gen.get('background_task_error'):
                    print(f"      ⚠️  Error: {signal_gen.get('background_task_error')}")
            
            return True
        else:
            print(f"\n❌ Service returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"\n❌ Service not accessible: {e}")
        return False

def check_recent_signals():
    """Check recent signals and execution status"""
    print("\n" + "-"*70)
    print("📊 RECENT SIGNALS ANALYSIS")
    print("-"*70)
    
    try:
        response = requests.get("http://localhost:8000/api/signals/latest?limit=10", timeout=5)
        if response.status_code == 200:
            signals = response.json()
            
            if not signals:
                print("\n   ⚠️  No signals found")
                return []
            
            print(f"\n   Found {len(signals)} recent signals:")
            
            executed = 0
            skipped = 0
            high_conf = 0
            
            for sig in signals:
                symbol = sig.get('symbol', 'N/A')
                action = sig.get('action', 'N/A')
                price = sig.get('price', 0)
                confidence = sig.get('confidence', 0)
                order_id = sig.get('order_id')
                timestamp = sig.get('timestamp', '')
                
                if confidence >= 75:
                    high_conf += 1
                
                if order_id:
                    executed += 1
                    status = "✅ EXECUTED"
                else:
                    skipped += 1
                    status = "⏭️  SKIPPED"
                
                # Parse timestamp
                try:
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M:%S')
                    else:
                        time_str = str(timestamp)
                except:
                    time_str = str(timestamp)[:19] if timestamp else 'unknown'
                
                print(f"\n   {status} - {symbol}: {action} @ ${price:.2f} ({confidence:.1f}%)")
                print(f"      Time: {time_str}")
                if order_id:
                    print(f"      Order ID: {order_id}")
            
            print(f"\n   Summary:")
            print(f"      Total Signals: {len(signals)}")
            print(f"      High Confidence (≥75%): {high_conf}")
            print(f"      Executed (with Order ID): {executed}")
            print(f"      Skipped (no Order ID): {skipped}")
            print(f"      Execution Rate: {(executed/len(signals)*100):.1f}%")
            
            return signals
        else:
            print(f"\n   ❌ Error fetching signals: {response.status_code}")
            return []
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        return []

def check_trading_status():
    """Check trading status"""
    print("\n" + "-"*70)
    print("💼 TRADING STATUS")
    print("-"*70)
    
    try:
        response = requests.get("http://localhost:8000/api/v1/trading/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            
            print(f"\n   Environment: {status.get('environment', 'unknown')}")
            print(f"   Trading Mode: {status.get('trading_mode', 'unknown')}")
            print(f"   Alpaca Connected: {status.get('alpaca_connected', False)}")
            print(f"   Trading Blocked: {status.get('trading_blocked', False)}")
            print(f"   Portfolio Value: ${status.get('portfolio_value', 0):,.2f}")
            print(f"   Buying Power: ${status.get('buying_power', 0):,.2f}")
            
            if status.get('trading_blocked', False):
                print("\n   ⚠️  WARNING: Trading is BLOCKED!")
            
            return status
        else:
            print(f"\n   ⚠️  Could not check trading status: {response.status_code}")
            return None
    except Exception as e:
        print(f"\n   ⚠️  Error: {e}")
        return None

def check_config():
    """Check configuration"""
    print("\n" + "-"*70)
    print("⚙️  CONFIGURATION CHECK")
    print("-"*70)
    
    config_path = Path("argo/config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            trading = config.get('trading', {})
            print(f"\n   Config File: {config_path}")
            print(f"   Auto-execute: {trading.get('auto_execute', False)}")
            print(f"   Force 24/7 Mode: {trading.get('force_24_7_mode', False)}")
            print(f"   Min Confidence: {trading.get('min_confidence', 75)}%")
            
            if not trading.get('force_24_7_mode', False):
                print("\n   ⚠️  WARNING: 24/7 mode not enabled in config!")
            
            if not trading.get('auto_execute', False):
                print("\n   ⚠️  WARNING: Auto-execute not enabled!")
            
            return config
        except Exception as e:
            print(f"\n   ⚠️  Error reading config: {e}")
            return None
    else:
        print(f"\n   ⚠️  Config file not found: {config_path}")
        return None

def main():
    """Main investigation"""
    print("\n" + "="*70)
    print("🔍 INVESTIGATING CURRENT TRADING STATE")
    print("="*70)
    
    service_ok = check_service_health()
    signals = check_recent_signals()
    trading_status = check_trading_status()
    config = check_config()
    
    print("\n" + "="*70)
    print("📊 INVESTIGATION SUMMARY")
    print("="*70)
    
    if not service_ok:
        print("\n   ❌ Service is not running or not accessible")
        print("   Action: Start the service on port 8000")
        return
    
    if signals:
        executed = sum(1 for s in signals if s.get('order_id'))
        total = len(signals)
        rate = (executed/total*100) if total > 0 else 0
        
        print(f"\n   Execution Status:")
        print(f"      Signals: {total}")
        print(f"      Executed: {executed}")
        print(f"      Execution Rate: {rate:.1f}%")
        
        if executed == 0 and total > 0:
            print("\n   ⚠️  ISSUE: No trades are executing!")
            print("   Possible reasons:")
            print("      1. Service needs restart (config changes not loaded)")
            print("      2. Risk validation blocking trades")
            print("      3. Service paused (24/7 mode not active)")
            print("      4. Market hours restrictions")
            print("\n   Action: Check service logs for 'Skipping' messages")
        elif executed > 0:
            print("\n   ✅ Trades ARE executing!")
    
    if config:
        if not config.get('trading', {}).get('force_24_7_mode', False):
            print("\n   ⚠️  Config issue: 24/7 mode not enabled")
            print("   Action: Restart service after enabling 24/7 mode")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

