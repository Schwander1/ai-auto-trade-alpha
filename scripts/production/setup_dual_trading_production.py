#!/usr/bin/env python3
"""
Setup dual trading for production: Prop Firm + Argo
This script ensures both trading modes are properly configured and enabled
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional

def load_config(config_path: str) -> Dict:
    """Load configuration file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {config_path}: {e}")
        return {}

def save_config(config: Dict, config_path: str):
    """Save configuration file"""
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Saved config: {config_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving {config_path}: {e}")
        return False

def ensure_trading_enabled(config: Dict) -> bool:
    """Ensure trading is enabled in config"""
    if 'trading' not in config:
        config['trading'] = {}
    
    trading = config['trading']
    updated = False
    
    # Enable auto-execute
    if not trading.get('auto_execute', False):
        trading['auto_execute'] = True
        updated = True
        print("   ✅ Enabled auto_execute")
    
    # Enable 24/7 mode
    if not trading.get('force_24_7_mode', False):
        trading['force_24_7_mode'] = True
        updated = True
        print("   ✅ Enabled force_24_7_mode")
    
    # Ensure min_confidence is set
    if 'min_confidence' not in trading:
        trading['min_confidence'] = 75.0
        updated = True
        print("   ✅ Set min_confidence to 75.0%")
    
    return updated

def ensure_prop_firm_enabled(config: Dict) -> bool:
    """Ensure prop firm trading is enabled"""
    if 'prop_firm' not in config:
        config['prop_firm'] = {}
    
    prop_firm = config['prop_firm']
    updated = False
    
    # Enable prop firm mode
    if not prop_firm.get('enabled', False):
        prop_firm['enabled'] = True
        updated = True
        print("   ✅ Enabled prop_firm mode")
    
    # Ensure risk limits are set
    if 'risk_limits' not in prop_firm:
        prop_firm['risk_limits'] = {}
    
    risk_limits = prop_firm['risk_limits']
    
    defaults = {
        'max_drawdown_pct': 2.0,
        'daily_loss_limit_pct': 4.5,
        'max_position_size_pct': 3.0,
        'min_confidence': 82.0,
        'max_positions': 3,
        'max_stop_loss_pct': 1.5
    }
    
    for key, default_value in defaults.items():
        if key not in risk_limits:
            risk_limits[key] = default_value
            updated = True
            print(f"   ✅ Set prop_firm.risk_limits.{key} to {default_value}")
    
    # Ensure monitoring is enabled
    if 'monitoring' not in prop_firm:
        prop_firm['monitoring'] = {}
    
    monitoring = prop_firm['monitoring']
    if not monitoring.get('enabled', False):
        monitoring['enabled'] = True
        updated = True
        print("   ✅ Enabled prop_firm monitoring")
    
    # Ensure account name is set
    if 'account' not in prop_firm:
        prop_firm['account'] = 'prop_firm_test'
        updated = True
        print("   ✅ Set prop_firm account to 'prop_firm_test'")
    
    return updated

def ensure_alpaca_accounts(config: Dict) -> bool:
    """Ensure both Argo and prop firm Alpaca accounts are configured"""
    if 'alpaca' not in config:
        config['alpaca'] = {}
    
    alpaca = config['alpaca']
    updated = False
    
    # Ensure standard Argo account exists
    if 'api_key' not in alpaca or 'secret_key' not in alpaca:
        print("   ⚠️  Standard Argo Alpaca credentials not found")
        print("      Add them to alpaca.api_key and alpaca.secret_key")
        # Don't fail, just warn
    
    # Ensure prop firm account exists
    prop_firm_account_name = config.get('prop_firm', {}).get('account', 'prop_firm_test')
    
    if prop_firm_account_name not in alpaca:
        alpaca[prop_firm_account_name] = {
            'api_key': '',
            'secret_key': '',
            'account_name': 'Prop Firm Test Account',
            'paper': True
        }
        updated = True
        print(f"   ✅ Created prop firm account config: {prop_firm_account_name}")
        print("      ⚠️  Add API credentials to this account")
    
    return updated

def setup_production_configs():
    """Setup both production configs"""
    print("\n" + "="*70)
    print("🔧 SETTING UP DUAL TRADING FOR PRODUCTION")
    print("="*70)
    
    # Production config paths
    config_paths = {
        'argo': '/root/argo-production-green/config.json',
        'prop_firm': '/root/argo-production-prop-firm/config.json'
    }
    
    # Also check local config for testing
    local_config = Path('argo/config.json')
    if local_config.exists():
        config_paths['local'] = str(local_config)
    
    results = {}
    
    for name, config_path in config_paths.items():
        if not os.path.exists(config_path):
            print(f"\n⚠️  Config not found: {config_path}")
            print("   Skipping...")
            continue
        
        print(f"\n📝 Processing: {name} ({config_path})")
        print("-" * 70)
        
        config = load_config(config_path)
        if not config:
            continue
        
        updated = False
        
        # Always enable trading
        if ensure_trading_enabled(config):
            updated = True
        
        # For prop firm config, enable prop firm mode
        if 'prop_firm' in name or name == 'local':
            if ensure_prop_firm_enabled(config):
                updated = True
        
        # Ensure Alpaca accounts are configured
        if ensure_alpaca_accounts(config):
            updated = True
        
        if updated:
            if save_config(config, config_path):
                results[name] = 'updated'
                print(f"   ✅ Configuration updated successfully")
            else:
                results[name] = 'error'
        else:
            results[name] = 'no_changes'
            print("   ℹ️  No changes needed")
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    for name, result in results.items():
        status = "✅ Updated" if result == 'updated' else "ℹ️  No changes" if result == 'no_changes' else "❌ Error"
        print(f"   {name}: {status}")
    
    print("\n⚠️  IMPORTANT NEXT STEPS:")
    print("   1. Add Alpaca API credentials to both accounts in config.json")
    print("   2. For prop firm: Add credentials to alpaca.prop_firm_test")
    print("   3. For Argo: Add credentials to alpaca.api_key/secret_key")
    print("   4. Restart services to load new configuration")
    print("   5. Run separate service instances:")
    print("      - Prop firm service: Uses prop_firm.enabled=true")
    print("      - Argo service: Uses prop_firm.enabled=false")
    print("="*70 + "\n")
    
    return results

if __name__ == "__main__":
    setup_production_configs()

