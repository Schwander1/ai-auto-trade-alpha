#!/usr/bin/env python3
"""
Switch to Prop Firm Test Account
Configures the system to use the prop firm paper trading account
"""
import json
import sys
from pathlib import Path

config_path = Path(__file__).parent.parent / "argo" / "config.json"

def switch_to_prop_firm_account():
    """Switch active Alpaca account to prop firm test account"""
    if not config_path.exists():
        print("❌ Config file not found")
        return False
    
    with open(config_path) as f:
        config = json.load(f)
    
    # Check if prop firm account exists
    alpaca = config.get('alpaca', {})
    prop_firm = alpaca.get('prop_firm_test')
    
    if not prop_firm:
        print("❌ Prop firm test account not found in config")
        return False
    
    print("=" * 70)
    print("🔄 SWITCHING TO PROP FIRM TEST ACCOUNT")
    print("=" * 70)
    print()
    
    print("📊 PROP FIRM TEST ACCOUNT:")
    print(f"   Account Name: {prop_firm.get('account_name', 'Prop Firm Test Account')}")
    print(f"   API Key: {prop_firm.get('api_key', '')[:20]}...")
    print(f"   Paper Trading: {prop_firm.get('paper', True)}")
    print()
    
    print("⚙️  RISK LIMITS:")
    risk_limits = prop_firm.get('risk_limits', {})
    print(f"   Max Drawdown: {risk_limits.get('max_drawdown_pct', 2.0)}%")
    print(f"   Daily Loss Limit: {risk_limits.get('daily_loss_limit_pct', 4.5)}%")
    print(f"   Max Position Size: {risk_limits.get('max_position_size_pct', 10)}%")
    print()
    
    print("✅ CONFIGURATION:")
    print("   The prop firm test account is configured in config.json")
    print("   To use this account, update your trading code to use:")
    print("   config['alpaca']['prop_firm_test']")
    print()
    
    print("📋 NEXT STEPS:")
    print("   1. Update trading code to use prop_firm_test account")
    print("   2. Verify account connection")
    print("   3. Start paper trading with prop firm rules")
    print("   4. Monitor risk limits continuously")
    print()
    
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    try:
        switch_to_prop_firm_account()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

