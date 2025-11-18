#!/usr/bin/env python3
"""
Check Current Trading Status
Comprehensive check of trading system status including positions, orders, and configuration
"""
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

def check_api_status():
    """Check API service status"""
    print("\n" + "="*70)
    print("🔍 TRADING STATUS CHECK")
    print("="*70)
    
    # Check health
    try:
        health_url = "http://localhost:8000/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("\n✅ API Service: RUNNING")
            print(f"   Version: {health.get('version', 'unknown')}")
            print(f"   Uptime: {health.get('uptime', 'unknown')}")
            signal_gen = health.get('signal_generation', {})
            if signal_gen:
                print(f"   Signal Generation: {signal_gen.get('status', 'unknown')}")
                print(f"   Background Task: {'Running' if signal_gen.get('background_task_running') else 'Not Running'}")
            return True
        else:
            print(f"\n❌ API Service: ERROR (Status {response.status_code})")
            return False
    except Exception as e:
        print(f"\n❌ API Service: NOT ACCESSIBLE ({str(e)})")
        return False

def check_latest_signals():
    """Check latest generated signals"""
    print("\n" + "-"*70)
    print("📊 Latest Signals")
    print("-"*70)
    
    try:
        signals_url = "http://localhost:8000/api/signals/latest?limit=5"
        response = requests.get(signals_url, timeout=5)
        if response.status_code == 200:
            signals = response.json()
            if signals:
                print(f"   Found {len(signals)} recent signals:")
                for sig in signals[:5]:
                    timestamp = sig.get('timestamp', 'unknown')
                    # Parse timestamp if it's a string
                    if isinstance(timestamp, str):
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    print(f"   • {sig.get('symbol', 'N/A')}: {sig.get('action', 'N/A')} @ ${sig.get('price', 0):.2f} ({sig.get('confidence', 0):.1f}% confidence) - {timestamp}")
                return True
            else:
                print("   ⚠️  No signals found")
                return False
        else:
            print(f"   ❌ Error fetching signals (Status {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def check_trading_config():
    """Check trading configuration"""
    print("\n" + "-"*70)
    print("⚙️  Trading Configuration")
    print("-"*70)
    
    # Try to find config file
    config_paths = [
        Path("argo/config.json"),
        Path("/root/argo-production/config.json"),
        Path("/root/argo-production-prop-firm/config.json"),
    ]
    
    config_found = False
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    trading_config = config.get('trading', {})
                    print(f"   Config file: {config_path}")
                    print(f"   Auto-execute: {trading_config.get('auto_execute', False)}")
                    print(f"   Min confidence: {trading_config.get('min_confidence', 75)}%")
                    print(f"   Position size: {trading_config.get('position_size_pct', 10)}%")
                    print(f"   Stop loss: {trading_config.get('stop_loss', 0.03)*100:.1f}%")
                    print(f"   Take profit: {trading_config.get('profit_target', 0.05)*100:.1f}%")
                    config_found = True
                    break
            except Exception as e:
                print(f"   ⚠️  Error reading config: {e}")
    
    if not config_found:
        print("   ⚠️  Config file not found in expected locations")
    
    return config_found

def check_trading_status_api():
    """Check trading status via API"""
    print("\n" + "-"*70)
    print("💼 Trading Status (via API)")
    print("-"*70)
    
    try:
        # Try trading status endpoint (may require auth)
        status_url = "http://localhost:8000/api/v1/trading/status"
        response = requests.get(status_url, timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"   Environment: {status.get('environment', 'unknown')}")
            print(f"   Trading Mode: {status.get('trading_mode', 'unknown')}")
            print(f"   Portfolio Value: ${status.get('portfolio_value', 0):,.2f}")
            print(f"   Buying Power: ${status.get('buying_power', 0):,.2f}")
            print(f"   Alpaca Connected: {status.get('alpaca_connected', False)}")
            return True
        elif response.status_code == 401:
            print("   ⚠️  Authentication required (endpoint exists but needs auth)")
            return False
        else:
            print(f"   ⚠️  Endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ⚠️  Could not check trading status: {str(e)}")
        return False

def main():
    """Main execution"""
    api_running = check_api_status()
    
    if api_running:
        check_latest_signals()
        check_trading_config()
        check_trading_status_api()
    else:
        print("\n⚠️  Cannot check trading details - API service not accessible")
        print("   Make sure the service is running on port 8000")
    
    print("\n" + "="*70)
    print("✅ Status Check Complete")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

