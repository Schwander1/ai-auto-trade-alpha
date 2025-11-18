#!/usr/bin/env python3
"""
Comprehensive verification script to check:
1. Are signals being generated and stored?
2. Are trades executing on both trading accounts?
"""
import sys
import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta

def check_signal_storage(config_path, service_name):
    """Check if signals are being stored in database"""
    print(f"\n{'='*60}")
    print(f"📊 {service_name} - Signal Storage Check")
    print(f"{'='*60}")
    
    # Determine database path based on config path
    if 'argo-production-green' in config_path:
        db_path = Path("/root/argo-production-green/data/signals.db")
    elif 'argo-production-prop-firm' in config_path:
        db_path = Path("/root/argo-production-prop-firm/data/signals.db")
    elif 'argo-production-blue' in config_path:
        db_path = Path("/root/argo-production-blue/data/signals.db")
    else:
        # Try to infer from config path
        config_dir = Path(config_path).parent
        db_path = config_dir / "data" / "signals.db"
    
    if not db_path.exists():
        print(f"  ❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Total signals
        cursor.execute("SELECT COUNT(*) FROM signals")
        total = cursor.fetchone()[0]
        print(f"  ✅ Total signals in database: {total:,}")
        
        # Signals in last hour
        cursor.execute("""
            SELECT COUNT(*) FROM signals 
            WHERE created_at >= datetime('now', '-1 hour')
        """)
        last_hour = cursor.fetchone()[0]
        print(f"  ✅ Signals in last hour: {last_hour}")
        
        # Signals in last 24 hours
        cursor.execute("""
            SELECT COUNT(*) FROM signals 
            WHERE created_at >= datetime('now', '-24 hours')
        """)
        last_24h = cursor.fetchone()[0]
        print(f"  ✅ Signals in last 24 hours: {last_24h}")
        
        # Latest signals
        cursor.execute("""
            SELECT symbol, action, confidence, created_at, order_id
            FROM signals 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        latest = cursor.fetchall()
        print(f"\n  📋 Latest 5 signals:")
        for sig in latest:
            order_status = "✅ EXECUTED" if sig[4] else "⏸️  NOT EXECUTED"
            print(f"    {sig[0]} {sig[1]} @ {sig[2]:.1f}% - {sig[3]} - {order_status}")
        
        # Signals with orders (executed trades)
        cursor.execute("""
            SELECT COUNT(*) FROM signals 
            WHERE order_id IS NOT NULL AND order_id != ''
        """)
        executed = cursor.fetchone()[0]
        print(f"\n  ✅ Signals with executed trades: {executed:,}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_trading_config(config_path, service_name):
    """Check trading configuration"""
    print(f"\n{'='*60}")
    print(f"⚙️  {service_name} - Trading Configuration")
    print(f"{'='*60}")
    
    if not os.path.exists(config_path):
        print(f"  ❌ Config file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        trading = config.get('trading', {})
        auto_execute = trading.get('auto_execute', False)
        min_confidence = trading.get('min_confidence', 'N/A')
        position_size = trading.get('position_size_pct', 'N/A')
        
        print(f"  Auto-execute: {'✅ ENABLED' if auto_execute else '❌ DISABLED'}")
        print(f"  Min confidence: {min_confidence}%")
        print(f"  Position size: {position_size}%")
        
        # Check prop firm settings
        prop_firm = config.get('prop_firm', {})
        if prop_firm:
            enabled = prop_firm.get('enabled', False)
            print(f"  Prop firm mode: {'✅ ENABLED' if enabled else '❌ DISABLED'}")
            if enabled:
                risk_limits = prop_firm.get('risk_limits', {})
                print(f"    Min confidence: {risk_limits.get('min_confidence', 'N/A')}%")
                print(f"    Max positions: {risk_limits.get('max_positions', 'N/A')}")
                print(f"    Max drawdown: {risk_limits.get('max_drawdown_pct', 'N/A')}%")
        
        # Check Alpaca account
        alpaca = config.get('alpaca', {})
        if alpaca:
            # Check for prop firm account
            if 'prop_firm_test' in alpaca:
                account_name = alpaca['prop_firm_test'].get('account_name', 'Prop Firm Test Account')
                api_key = alpaca['prop_firm_test'].get('api_key', '')
                print(f"  Alpaca account: {account_name}")
                print(f"  API key configured: {'✅ YES' if api_key else '❌ NO'}")
            else:
                account_name = alpaca.get('account_name', 'Standard Account')
                api_key = alpaca.get('api_key', '')
                print(f"  Alpaca account: {account_name}")
                print(f"  API key configured: {'✅ YES' if api_key else '❌ NO'}")
        
        return auto_execute
        
    except Exception as e:
        print(f"  ❌ Error reading config: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_service_status(port, service_name):
    """Check if service is running on port"""
    print(f"\n{'='*60}")
    print(f"🌐 {service_name} - Service Status")
    print(f"{'='*60}")
    
    try:
        import urllib.request
        import urllib.error
        
        url = f"http://localhost:{port}/health"
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                print(f"  ✅ Service is RUNNING on port {port}")
                print(f"  Status: {data.get('status', 'unknown')}")
                if 'signal_generation' in data:
                    sg = data['signal_generation']
                    print(f"  Signal generation: {sg.get('status', 'unknown')}")
                return True
        except urllib.error.URLError as e:
            print(f"  ❌ Service NOT RUNNING on port {port}")
            print(f"  Error: {e}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error checking service: {e}")
        return False

def main():
    print("="*60)
    print("🔍 SIGNAL GENERATION & TRADING STATUS VERIFICATION")
    print("="*60)
    
    # Check both production services
    services = [
        {
            "name": "Argo Trading Service",
            "config": "/root/argo-production-green/config.json",
            "port": 8000
        },
        {
            "name": "Prop Firm Trading Service",
            "config": "/root/argo-production-prop-firm/config.json",
            "port": 8001
        }
    ]
    
    results = {}
    
    for service in services:
        service_name = service["name"]
        config_path = service["config"]
        port = service["port"]
        
        # Check if config exists
        if not os.path.exists(config_path):
            print(f"\n⚠️  {service_name} config not found: {config_path}")
            print(f"   Skipping checks for this service...")
            continue
        
        # Check service status
        service_running = check_service_status(port, service_name)
        
        # Check configuration
        auto_execute = check_trading_config(config_path, service_name)
        
        # Check signal storage
        signals_stored = check_signal_storage(config_path, service_name)
        
        results[service_name] = {
            "service_running": service_running,
            "auto_execute": auto_execute,
            "signals_stored": signals_stored
        }
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    
    for service_name, result in results.items():
        print(f"\n{service_name}:")
        print(f"  Service running: {'✅' if result['service_running'] else '❌'}")
        print(f"  Auto-execute: {'✅' if result['auto_execute'] else '❌'}")
        print(f"  Signals stored: {'✅' if result['signals_stored'] else '❌'}")
        
        if result['service_running'] and result['auto_execute'] and result['signals_stored']:
            print(f"  Status: ✅ FULLY OPERATIONAL")
        elif result['service_running'] and result['signals_stored']:
            print(f"  Status: ⚠️  GENERATING SIGNALS (trading disabled)")
        elif result['service_running']:
            print(f"  Status: ⚠️  RUNNING (no signals stored)")
        else:
            print(f"  Status: ❌ NOT RUNNING")

if __name__ == "__main__":
    main()

