#!/usr/bin/env python3
"""
Comprehensive Status Check
Check all aspects of the trading system
"""
import sys
import requests
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def check_service_health():
    """Check service health"""
    print("\n" + "="*70)
    print("1️⃣  SERVICE HEALTH")
    print("="*70)
    
    try:
        health = requests.get("http://localhost:8000/health", timeout=5).json()
        print(f"\n✅ Status: {health.get('status')}")
        print(f"✅ Version: {health.get('version')}")
        print(f"✅ Uptime: {health.get('uptime')}")
        
        signal_gen = health.get('signal_generation', {})
        print(f"\n   Signal Generation:")
        print(f"      Status: {signal_gen.get('status')}")
        print(f"      Background Task: {'Running' if signal_gen.get('background_task_running') else 'NOT Running'}")
        if signal_gen.get('background_task_error'):
            print(f"      ⚠️  Error: {signal_gen.get('background_task_error')}")
        
        return True
    except Exception as e:
        print(f"\n❌ Service not accessible: {e}")
        return False

def check_trading_status():
    """Check trading status"""
    print("\n" + "-"*70)
    print("2️⃣  TRADING STATUS")
    print("-"*70)
    
    try:
        status = requests.get("http://localhost:8000/api/v1/trading/status", timeout=5).json()
        print(f"\n✅ Environment: {status.get('environment')}")
        print(f"✅ Trading Mode: {status.get('trading_mode')}")
        print(f"✅ Alpaca Connected: {status.get('alpaca_connected')}")
        print(f"✅ Trading Blocked: {status.get('trading_blocked', False)}")
        print(f"✅ Portfolio Value: ${status.get('portfolio_value', 0):,.2f}")
        print(f"✅ Buying Power: ${status.get('buying_power', 0):,.2f}")
        print(f"✅ Account Status: {status.get('account_status')}")
        return status
    except Exception as e:
        print(f"\n⚠️  Error: {e}")
        return None

def check_recent_signals():
    """Check recent signals"""
    print("\n" + "-"*70)
    print("3️⃣  RECENT SIGNALS")
    print("-"*70)
    
    try:
        signals = requests.get("http://localhost:8000/api/signals/latest?limit=10", timeout=5).json()
        
        if not signals:
            print("\n⚠️  No signals returned from API")
            return []
        
        print(f"\n✅ Found {len(signals)} signals via API:")
        
        executed = 0
        for sig in signals[:5]:
            order_id = sig.get('order_id')
            status = "✅ EXECUTED" if order_id else "⏭️  SKIPPED"
            print(f"   {status} - {sig.get('symbol')}: {sig.get('action')} @ ${sig.get('price', 0):.2f} ({sig.get('confidence', 0):.1f}%)")
            if order_id:
                executed += 1
                print(f"      Order ID: {order_id}")
        
        print(f"\n   Summary: {executed}/{len(signals)} executed")
        return signals
    except Exception as e:
        print(f"\n⚠️  Error: {e}")
        return []

def check_database():
    """Check database for signals"""
    print("\n" + "-"*70)
    print("4️⃣  DATABASE SIGNALS")
    print("-"*70)
    
    db_path = Path("argo/data/signals.db")
    if not db_path.exists():
        print("\n⚠️  Database not found")
        return []
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get recent signals
        cursor.execute("""
            SELECT symbol, action, entry_price, confidence, timestamp, order_id
            FROM signals
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        print(f"\n✅ Found {len(rows)} recent signals in database:")
        
        executed = 0
        for row in rows[:5]:
            symbol, action, price, confidence, timestamp, order_id = row
            status = "✅ EXECUTED" if order_id else "⏭️  SKIPPED"
            print(f"   {status} - {symbol}: {action} @ ${price:.2f} ({confidence:.1f}%)")
            if order_id:
                executed += 1
                print(f"      Order ID: {order_id}")
            print(f"      Time: {timestamp}")
        
        print(f"\n   Summary: {executed}/{len(rows)} executed")
        conn.close()
        return rows
    except Exception as e:
        print(f"\n⚠️  Error: {e}")
        return []

def check_execution_logs():
    """Check execution logs"""
    print("\n" + "-"*70)
    print("5️⃣  EXECUTION LOGS")
    print("-"*70)
    
    log_file = Path("/tmp/argo-restart.log")
    if not log_file.exists():
        print("\n⚠️  Log file not found")
        return
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Get last 10000 lines
        recent_lines = lines[-10000:] if len(lines) > 10000 else lines
        
        execution_checks = [l for l in recent_lines if "Execution check for" in l]
        executed_trades = [l for l in recent_lines if "Executing trade for" in l or "Trade executed" in l]
        skipped_trades = [l for l in recent_lines if "Skipping" in l and "Failed conditions" in l]
        risk_blocks = [l for l in recent_lines if "Skipping" in l and ("reason" in l.lower() or "risk" in l.lower())]
        
        print(f"\n   Execution Checks: {len(execution_checks)}")
        print(f"   Executed Trades: {len(executed_trades)}")
        print(f"   Skipped (Failed Conditions): {len(skipped_trades)}")
        print(f"   Skipped (Risk Validation): {len(risk_blocks)}")
        
        if execution_checks:
            print(f"\n   Recent Execution Checks:")
            for line in execution_checks[-3:]:
                print(f"      {line.strip()}")
        
        if executed_trades:
            print(f"\n   Recent Executed Trades:")
            for line in executed_trades[-3:]:
                print(f"      {line.strip()}")
        
        if skipped_trades:
            print(f"\n   Recent Skipped Trades (Failed Conditions):")
            for line in skipped_trades[-3:]:
                print(f"      {line.strip()}")
        
        if risk_blocks:
            print(f"\n   Recent Skipped Trades (Risk Validation):")
            for line in risk_blocks[-3:]:
                print(f"      {line.strip()}")
        
    except Exception as e:
        print(f"\n⚠️  Error reading logs: {e}")

def check_configuration():
    """Check configuration"""
    print("\n" + "-"*70)
    print("6️⃣  CONFIGURATION")
    print("-"*70)
    
    config_path = Path("argo/config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            trading = config.get('trading', {})
            print(f"\n✅ Config File: {config_path}")
            print(f"   Auto-execute: {trading.get('auto_execute', False)}")
            print(f"   Force 24/7 Mode: {trading.get('force_24_7_mode', False)}")
            print(f"   Min Confidence: {trading.get('min_confidence', 75)}%")
            print(f"   Position Size: {trading.get('position_size_pct', 10)}%")
            
            return config
        except Exception as e:
            print(f"\n⚠️  Error: {e}")
            return None
    else:
        print(f"\n⚠️  Config file not found")
        return None

def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🔍 COMPREHENSIVE TRADING SYSTEM STATUS CHECK")
    print("="*70)
    
    service_ok = check_service_health()
    trading_status = check_trading_status()
    signals = check_recent_signals()
    db_signals = check_database()
    check_execution_logs()
    config = check_configuration()
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    if service_ok:
        print("\n✅ Service: Running and healthy")
    else:
        print("\n❌ Service: Not accessible")
    
    if trading_status:
        print(f"✅ Trading Engine: Connected (Alpaca: {trading_status.get('alpaca_connected')})")
        print(f"✅ Account: Active (${trading_status.get('portfolio_value', 0):,.2f})")
    
    print(f"\n📊 Signals:")
    print(f"   API: {len(signals)} signals")
    print(f"   Database: {len(db_signals)} signals")
    
    if signals:
        executed = sum(1 for s in signals if s.get('order_id'))
        print(f"   Executed: {executed}/{len(signals)}")
        print(f"   Execution Rate: {(executed/len(signals)*100):.1f}%")
    
    if config:
        if config.get('trading', {}).get('force_24_7_mode'):
            print("\n✅ 24/7 Mode: Enabled")
        if config.get('trading', {}).get('auto_execute'):
            print("✅ Auto-execute: Enabled")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

