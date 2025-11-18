#!/usr/bin/env python3
"""
Fix Alpaca connection issues and verify trading engine initialization
"""
import sys
import json
from pathlib import Path

def check_alpaca_config(config_path: str, service_name: str):
    """Check Alpaca configuration"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        alpaca = config.get('alpaca', {})
        prop_firm = config.get('prop_firm', {})
        prop_firm_enabled = prop_firm.get('enabled', False)
        
        print(f"\n📋 {service_name} Alpaca Configuration:")
        print("-" * 70)
        
        if prop_firm_enabled:
            # Check prop firm account
            prop_account_name = prop_firm.get('account', 'prop_firm_test')
            prop_account = alpaca.get(prop_account_name, {})
            
            api_key = prop_account.get('api_key', '')
            secret_key = prop_account.get('secret_key', '')
            
            print(f"   Prop Firm Account: {prop_account_name}")
            print(f"   API Key: {'✅ Set' if api_key and api_key != 'YOUR_ALPACA_API_KEY' else '❌ Not Set'}")
            print(f"   Secret Key: {'✅ Set' if secret_key and secret_key != 'YOUR_ALPACA_SECRET_KEY' else '❌ Not Set'}")
            
            if not api_key or api_key == 'YOUR_ALPACA_API_KEY':
                print(f"\n   ⚠️  ACTION REQUIRED: Add Prop Firm Alpaca credentials")
                print(f"   Edit: {config_path}")
                print(f"   Add to: alpaca.{prop_account_name}.api_key and secret_key")
                return False
        else:
            # Check standard account
            api_key = alpaca.get('api_key', '')
            secret_key = alpaca.get('secret_key', '')
            
            print(f"   Standard Account")
            print(f"   API Key: {'✅ Set' if api_key and api_key != 'YOUR_ALPACA_API_KEY' else '❌ Not Set'}")
            print(f"   Secret Key: {'✅ Set' if secret_key and secret_key != 'YOUR_ALPACA_SECRET_KEY' else '❌ Not Set'}")
            
            if not api_key or api_key == 'YOUR_ALPACA_API_KEY':
                print(f"\n   ⚠️  ACTION REQUIRED: Add Argo Alpaca credentials")
                print(f"   Edit: {config_path}")
                print(f"   Add to: alpaca.api_key and alpaca.secret_key")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking config: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🔍 ALPACA CONNECTION CHECK")
    print("="*70)
    
    configs = [
        ('/root/argo-production-green/config.json', 'Argo Trading Service'),
        ('/root/argo-production-prop-firm/config.json', 'Prop Firm Trading Service'),
    ]
    
    all_configured = True
    
    for config_path, service_name in configs:
        if Path(config_path).exists():
            if not check_alpaca_config(config_path, service_name):
                all_configured = False
        else:
            print(f"\n⚠️  Config not found: {config_path}")
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    if all_configured:
        print("   ✅ All Alpaca credentials are configured")
        print("   ⚠️  If services show alpaca_connected: false, check:")
        print("      1. Credentials are correct")
        print("      2. Alpaca API is accessible")
        print("      3. Account is active")
        print("      4. Check service logs for connection errors")
    else:
        print("   ⚠️  Some Alpaca credentials need to be added")
        print("   Add credentials to config files and restart services")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

