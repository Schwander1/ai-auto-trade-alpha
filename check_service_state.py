#!/usr/bin/env python3
"""
Check Service State - Query the running service for execution state
"""
import sys
import requests
import json
from pathlib import Path

# Add paths
argo_path = Path(__file__).parent / "argo"
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))

try:
    from argo.core.signal_generation_service import SignalGenerationService
except ImportError as e:
    print(f"Error importing: {e}")
    sys.exit(1)

def check_service_state():
    """Check the actual service state"""
    print("\n" + "="*70)
    print("🔍 SERVICE STATE CHECK")
    print("="*70)
    
    try:
        service = SignalGenerationService()
        
        print("\n1️⃣  Execution Conditions")
        print("-"*70)
        print(f"   Auto-execute: {service.auto_execute}")
        print(f"   Trading Engine: {'Initialized' if service.trading_engine else 'Not Initialized'}")
        print(f"   Service Paused: {service._paused}")
        print(f"   Trading Paused: {getattr(service, '_trading_paused', False)}")
        
        if service.trading_engine:
            print(f"   Alpaca Enabled: {service.trading_engine.alpaca_enabled}")
            if service.trading_engine.alpaca_enabled:
                account = service.trading_engine.get_account_details()
                if account:
                    print(f"   Account Status: {account.get('status', 'unknown')}")
                    print(f"   Trading Blocked: {account.get('trading_blocked', False)}")
                    print(f"   Account Blocked: {account.get('account_blocked', False)}")
        
        print("\n2️⃣  Configuration")
        print("-"*70)
        trading_config = service.trading_config
        print(f"   Min Confidence: {trading_config.get('min_confidence', 75)}%")
        print(f"   Position Size: {trading_config.get('position_size_pct', 10)}%")
        print(f"   Max Position Size: {trading_config.get('max_position_size_pct', 15)}%")
        print(f"   Daily Loss Limit: {trading_config.get('daily_loss_limit_pct', 5)}%")
        print(f"   Max Drawdown: {trading_config.get('max_drawdown_pct', 10)}%")
        
        print("\n3️⃣  Execution Check")
        print("-"*70)
        
        # Check if all conditions are met
        conditions = {
            "auto_execute": service.auto_execute,
            "trading_engine": service.trading_engine is not None,
            "not_paused": not service._paused,
            "not_trading_paused": not getattr(service, '_trading_paused', False),
        }
        
        if service.trading_engine:
            conditions["alpaca_enabled"] = service.trading_engine.alpaca_enabled
            if service.trading_engine.alpaca_enabled:
                account = service.trading_engine.get_account_details()
                if account:
                    conditions["account_available"] = account is not None
                    conditions["trading_not_blocked"] = not account.get('trading_blocked', False)
                    conditions["account_not_blocked"] = not account.get('account_blocked', False)
        
        all_met = all(conditions.values())
        
        for condition, met in conditions.items():
            status = "✅" if met else "❌"
            print(f"   {status} {condition}: {met}")
        
        if not all_met:
            print("\n   ⚠️  NOT ALL CONDITIONS MET - Trades will NOT execute!")
            failed = [k for k, v in conditions.items() if not v]
            print(f"   Failed conditions: {', '.join(failed)}")
        else:
            print("\n   ✅ ALL CONDITIONS MET - Trades SHOULD execute")
            print("   ⚠️  But signals show no order IDs - check risk validation!")
        
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_service_state()

