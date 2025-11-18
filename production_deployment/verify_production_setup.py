#!/usr/bin/env python3
"""
Comprehensive production setup verification script
"""
import asyncio
import sys
import os
import sqlite3
import json
from datetime import datetime

def check_config_file(config_path, service_name):
    """Check configuration file"""
    print(f"\n📋 Checking {service_name} configuration...")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check trading settings
        trading = config.get('trading', {})
        print(f"  Auto-execute: {trading.get('auto_execute', False)}")
        print(f"  Force 24/7 mode: {trading.get('force_24_7_mode', False)}")
        print(f"  Min confidence: {trading.get('min_confidence', 'N/A')}%")
        
        # Check prop firm settings
        prop_firm = config.get('prop_firm', {})
        if prop_firm:
            print(f"  Prop firm enabled: {prop_firm.get('enabled', False)}")
            if prop_firm.get('enabled'):
                risk_limits = prop_firm.get('risk_limits', {})
                print(f"    Min confidence: {risk_limits.get('min_confidence', 'N/A')}%")
                print(f"    Max positions: {risk_limits.get('max_positions', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error reading config: {e}")
        return False

def check_database(db_path, service_name):
    """Check signal database"""
    print(f"\n💾 Checking {service_name} database...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM signals")
        total = cursor.fetchone()[0]
        print(f"  Total signals: {total}")
        
        cursor.execute("SELECT COUNT(*) FROM signals WHERE timestamp > datetime('now', '-1 hour')")
        recent = cursor.fetchone()[0]
        print(f"  Signals in last hour: {recent}")
        
        cursor.execute("SELECT symbol, action, confidence, timestamp FROM signals ORDER BY timestamp DESC LIMIT 3")
        recent_signals = cursor.fetchall()
        if recent_signals:
            print(f"  Recent signals:")
            for sig in recent_signals:
                print(f"    {sig[0]} {sig[1]} @ {sig[2]}% - {sig[3]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"  ❌ Error checking database: {e}")
        return False

async def check_service(service_path, service_name):
    """Check service configuration and status"""
    print(f"\n🔧 Checking {service_name} service...")
    try:
        sys.path.insert(0, service_path)
        from argo.core.signal_generation_service import get_signal_service
        
        service = get_signal_service()
        print(f"  Auto-execute: {service.auto_execute}")
        print(f"  24/7 mode: {not service._cursor_aware}")
        print(f"  Running: {service.running}")
        print(f"  Base confidence threshold: {service.confidence_threshold}%")
        print(f"  Regime thresholds: {service.regime_thresholds}")
        print(f"  Prop firm mode: {service.prop_firm_mode}")
        
        if service.trading_engine:
            account = service.trading_engine.get_account_details()
            if account:
                print(f"  Trading engine: ✅ Connected")
                print(f"    Account: {service.trading_engine.account_name}")
                print(f"    Portfolio: ${account['portfolio_value']:,.2f}")
            else:
                print(f"  Trading engine: ⚠️  Connected but no account details")
        else:
            print(f"  Trading engine: ❌ Not connected")
        
        return True
    except Exception as e:
        print(f"  ❌ Error checking service: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("=" * 60)
    print("PRODUCTION SETUP VERIFICATION")
    print("=" * 60)
    
    # Check Argo service
    argo_config = "/root/argo-production-green/config.json"
    argo_db = "/root/argo-production-green/data/signals.db"
    argo_path = "/root/argo-production-green"
    
    check_config_file(argo_config, "Argo Service")
    check_database(argo_db, "Argo Service")
    await check_service(argo_path, "Argo Service")
    
    # Check Prop Firm service
    prop_config = "/root/argo-production-prop-firm/config.json"
    prop_db = "/root/argo-production-prop-firm/data/signals.db"
    prop_path = "/root/argo-production-prop-firm"
    
    check_config_file(prop_config, "Prop Firm Service")
    check_database(prop_db, "Prop Firm Service")
    await check_service(prop_path, "Prop Firm Service")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

