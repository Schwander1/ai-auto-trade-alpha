#!/usr/bin/env python3
"""
Fix Trade Execution Issues
Enable 24/7 mode and verify trade execution is working
"""
import sys
import json
import os
from pathlib import Path

def fix_config():
    """Fix configuration to enable 24/7 mode and ensure auto-execute is enabled"""
    print("\n" + "="*70)
    print("🔧 FIXING TRADE EXECUTION CONFIGURATION")
    print("="*70)
    
    config_paths = [
        Path("argo/config.json"),
        Path("config.json"),
    ]
    
    config_found = False
    for config_path in config_paths:
        if config_path.exists():
            try:
                print(f"\n📝 Reading config: {config_path}")
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Ensure trading section exists
                if 'trading' not in config:
                    config['trading'] = {}
                
                trading = config['trading']
                
                # Enable 24/7 mode
                if not trading.get('force_24_7_mode', False):
                    print("   ✅ Enabling 24/7 mode (force_24_7_mode: true)")
                    trading['force_24_7_mode'] = True
                else:
                    print("   ✅ 24/7 mode already enabled")
                
                # Ensure auto-execute is enabled
                if not trading.get('auto_execute', False):
                    print("   ✅ Enabling auto-execute (auto_execute: true)")
                    trading['auto_execute'] = True
                else:
                    print("   ✅ Auto-execute already enabled")
                
                # Save config
                print(f"\n💾 Saving config: {config_path}")
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print("\n✅ Configuration updated successfully!")
                print(f"   - force_24_7_mode: {trading.get('force_24_7_mode')}")
                print(f"   - auto_execute: {trading.get('auto_execute')}")
                
                config_found = True
                break
            except Exception as e:
                print(f"   ❌ Error reading/writing config: {e}")
                import traceback
                traceback.print_exc()
    
    if not config_found:
        print("\n⚠️  Config file not found. Creating example config...")
        # Try to create from example
        example_path = Path("argo/config.json.example")
        if example_path.exists():
            try:
                with open(example_path, 'r') as f:
                    config = json.load(f)
                
                # Enable 24/7 mode and auto-execute
                if 'trading' not in config:
                    config['trading'] = {}
                config['trading']['force_24_7_mode'] = True
                config['trading']['auto_execute'] = True
                
                # Save to config.json
                config_path = Path("argo/config.json")
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print(f"   ✅ Created config: {config_path}")
            except Exception as e:
                print(f"   ❌ Error creating config: {e}")
        else:
            print("   ❌ Could not find config.json.example either")
    
    return config_found

def set_environment_variable():
    """Set ARGO_24_7_MODE environment variable"""
    print("\n" + "-"*70)
    print("🌍 Setting Environment Variable")
    print("-"*70)
    
    os.environ['ARGO_24_7_MODE'] = 'true'
    print("   ✅ ARGO_24_7_MODE=true set")
    print("   Note: This will only affect new processes")
    print("   The running service may need to be restarted")

def main():
    """Main execution"""
    config_updated = fix_config()
    set_environment_variable()
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    if config_updated:
        print("   ✅ Configuration updated")
        print("   ✅ 24/7 mode enabled")
        print("   ✅ Auto-execute enabled")
        print("\n   ⚠️  IMPORTANT: Restart the service for changes to take effect")
        print("   The running service on port 8000 needs to be restarted")
    else:
        print("   ⚠️  Could not update configuration file")
        print("   You may need to manually enable:")
        print("   - force_24_7_mode: true")
        print("   - auto_execute: true")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

