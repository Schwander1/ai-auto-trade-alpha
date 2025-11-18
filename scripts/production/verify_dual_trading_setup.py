#!/usr/bin/env python3
"""
Verify dual trading setup for production
"""
import json
import sys
from pathlib import Path

def check_config(config_path: str, expected_prop_firm: bool):
    """Check configuration"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        trading = config.get('trading', {})
        prop_firm = config.get('prop_firm', {})
        alpaca = config.get('alpaca', {})
        
        print(f"\n📋 Config: {config_path}")
        print("-" * 70)
        
        # Check trading settings
        auto_execute = trading.get('auto_execute', False)
        force_24_7 = trading.get('force_24_7_mode', False)
        
        print(f"   Trading:")
        print(f"      auto_execute: {auto_execute} {'✅' if auto_execute else '❌'}")
        print(f"      force_24_7_mode: {force_24_7} {'✅' if force_24_7 else '❌'}")
        
        # Check prop firm settings
        prop_firm_enabled = prop_firm.get('enabled', False)
        print(f"   Prop Firm:")
        print(f"      enabled: {prop_firm_enabled} {'✅' if prop_firm_enabled == expected_prop_firm else '❌'}")
        
        if prop_firm_enabled:
            account = prop_firm.get('account', '')
            risk_limits = prop_firm.get('risk_limits', {})
            print(f"      account: {account}")
            print(f"      min_confidence: {risk_limits.get('min_confidence', 'N/A')}%")
            print(f"      max_positions: {risk_limits.get('max_positions', 'N/A')}")
        
        # Check Alpaca accounts
        print(f"   Alpaca Accounts:")
        if 'api_key' in alpaca:
            print(f"      Argo account: {'✅ Configured' if alpaca.get('api_key') else '❌ Missing'}")
        
        prop_account_name = prop_firm.get('account', 'prop_firm_test')
        if prop_account_name in alpaca:
            prop_account = alpaca[prop_account_name]
            print(f"      Prop firm account ({prop_account_name}): {'✅ Configured' if prop_account.get('api_key') else '❌ Missing'}")
        else:
            print(f"      Prop firm account ({prop_account_name}): ❌ Not found")
        
        # Summary
        all_good = (
            auto_execute and
            force_24_7 and
            prop_firm_enabled == expected_prop_firm
        )
        
        return all_good
        
    except Exception as e:
        print(f"   ❌ Error reading config: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🔍 VERIFYING DUAL TRADING SETUP")
    print("="*70)
    
    configs = [
        ('/root/argo-production-green/config.json', False, 'Argo Trading'),
        ('/root/argo-production-prop-firm/config.json', True, 'Prop Firm Trading'),
        ('argo/config.json', True, 'Local Config (Testing)'),
    ]
    
    results = {}
    
    for config_path, expected_prop_firm, name in configs:
        if Path(config_path).exists():
            print(f"\n{name}:")
            results[name] = check_config(config_path, expected_prop_firm)
        else:
            print(f"\n{name}:")
            print(f"   ⚠️  Config not found: {config_path}")
            results[name] = None
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    all_configured = True
    for name, result in results.items():
        if result is None:
            print(f"   {name}: ⚠️  Not found")
        elif result:
            print(f"   {name}: ✅ Properly configured")
        else:
            print(f"   {name}: ❌ Needs configuration")
            all_configured = False
    
    if all_configured:
        print("\n✅ All configurations are properly set up!")
        print("\n📋 To run both services:")
        print("   1. Start Argo service on port 8000")
        print("   2. Start Prop Firm service on port 8001")
        print("   3. Both will execute trades simultaneously")
    else:
        print("\n⚠️  Some configurations need attention")
        print("   Run: ./enable_dual_trading_production.sh")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

