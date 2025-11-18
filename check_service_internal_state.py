#!/usr/bin/env python3
"""
Check Service Internal State
Query the running service to see if it's paused or has issues
"""
import sys
from pathlib import Path

# Add paths
argo_path = Path(__file__).parent / "argo"
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))

try:
    from argo.core.signal_generation_service import get_signal_service
except ImportError:
    print("Could not import signal service")
    sys.exit(1)

def check_service_state():
    """Check the actual service instance state"""
    print("\n" + "="*70)
    print("🔍 SERVICE INTERNAL STATE CHECK")
    print("="*70)
    
    try:
        service = get_signal_service()
        
        if not service:
            print("\n   ⚠️  Service instance not available")
            print("   The service may not be initialized yet")
            return
        
        print("\n1️⃣  Execution Conditions")
        print("-"*70)
        print(f"   Auto-execute: {service.auto_execute}")
        print(f"   Trading Engine: {'Initialized' if service.trading_engine else 'Not Initialized'}")
        print(f"   Service Paused (_paused): {service._paused}")
        print(f"   Trading Paused (_trading_paused): {getattr(service, '_trading_paused', False)}")
        print(f"   Cursor Aware: {getattr(service, '_cursor_aware', 'Unknown')}")
        print(f"   Running: {getattr(service, 'running', False)}")
        
        if service.trading_engine:
            print(f"\n   Trading Engine Details:")
            print(f"      Alpaca Enabled: {service.trading_engine.alpaca_enabled}")
            if service.trading_engine.alpaca_enabled:
                account = service.trading_engine.get_account_details()
                if account:
                    print(f"      Account Status: {account.get('status', 'unknown')}")
                    print(f"      Trading Blocked: {account.get('trading_blocked', False)}")
        
        print("\n2️⃣  Configuration")
        print("-"*70)
        trading_config = service.trading_config
        print(f"   Min Confidence: {trading_config.get('min_confidence', 75)}%")
        print(f"   Auto-execute: {trading_config.get('auto_execute', False)}")
        print(f"   Force 24/7 Mode: {trading_config.get('force_24_7_mode', False)}")
        
        print("\n3️⃣  Analysis")
        print("-"*70)
        
        issues = []
        if not service.auto_execute:
            issues.append("❌ Auto-execute is False")
        if not service.trading_engine:
            issues.append("❌ Trading engine not initialized")
        if service._paused:
            issues.append(f"⚠️  Service is PAUSED (this blocks execution)")
        if getattr(service, '_trading_paused', False):
            issues.append("⚠️  Trading is PAUSED (daily loss limit?)")
        if getattr(service, '_cursor_aware', False):
            issues.append("⚠️  Cursor-aware mode active (may pause)")
        
        if issues:
            print("   Issues found:")
            for issue in issues:
                print(f"      {issue}")
        else:
            print("   ✅ All conditions appear correct")
            print("   ⚠️  But trades still not executing - check risk validation")
        
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_service_state()

