#!/usr/bin/env python3
"""
Troubleshoot and fix Massive API key issues
Tests different API formats and updates the key if needed
"""
import json
import sys
import requests
from pathlib import Path
from typing import Optional, Tuple

def load_config() -> Tuple[dict, str]:
    """Load config.json"""
    config_paths = [
        Path("argo/config.json"),
        Path("config.json"),
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                return config, str(config_path)
            except Exception as e:
                print(f"❌ Error reading {config_path}: {e}")
    
    return {}, None

def save_config(config: dict, config_path: str):
    """Save config.json"""
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Config saved to {config_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False

def test_api_key(api_key: str, test_name: str = "") -> Tuple[bool, str]:
    """Test Massive API key with different formats"""
    if not api_key:
        return False, "No API key provided"
    
    # Test different parameter formats and endpoints
    test_configs = [
        {
            "name": "api.massive.com with apiKey",
            "url": "https://api.massive.com/v2/aggs/ticker/X:BTCUSD/range/1/day/2024-01-01/2024-01-02",
            "params": {'adjusted': 'true', 'sort': 'asc', 'limit': 1, 'apiKey': api_key}
        },
        {
            "name": "api.massive.com with apikey (lowercase)",
            "url": "https://api.massive.com/v2/aggs/ticker/X:BTCUSD/range/1/day/2024-01-01/2024-01-02",
            "params": {'adjusted': 'true', 'sort': 'asc', 'limit': 1, 'apikey': api_key}
        },
        {
            "name": "api.polygon.io (legacy) with apiKey",
            "url": "https://api.polygon.io/v2/aggs/ticker/X:BTCUSD/range/1/day/2024-01-01/2024-01-02",
            "params": {'adjusted': 'true', 'sort': 'asc', 'limit': 1, 'apiKey': api_key}
        },
        {
            "name": "api.polygon.io (legacy) with apikey (lowercase)",
            "url": "https://api.polygon.io/v2/aggs/ticker/X:BTCUSD/range/1/day/2024-01-01/2024-01-02",
            "params": {'adjusted': 'true', 'sort': 'asc', 'limit': 1, 'apikey': api_key}
        },
    ]
    
    print(f"\n🔍 Testing API key: {api_key[:10]}... (len={len(api_key)})")
    if test_name:
        print(f"   Test: {test_name}")
    print()
    
    for test_config in test_configs:
        try:
            print(f"   Testing: {test_config['name']}...", end=" ")
            response = requests.get(
                test_config['url'],
                params=test_config['params'],
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK' or data.get('results'):
                    print("✅ SUCCESS")
                    return True, f"Working with: {test_config['name']}"
                else:
                    print(f"❌ Status: {data.get('status', 'UNKNOWN')}")
            elif response.status_code == 401:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('error', response.text[:100])
                print(f"❌ 401: {error_msg}")
            else:
                print(f"❌ Status {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
    
    return False, "All test configurations failed"

def update_massive_key(new_key: str, config_path: str) -> bool:
    """Update Massive API key in config"""
    config, path = load_config()
    if not config:
        print("❌ Could not load config")
        return False
    
    if 'massive' not in config:
        config['massive'] = {}
    
    config['massive']['api_key'] = new_key
    config['massive']['enabled'] = True
    
    return save_config(config, path or config_path)

def main():
    print("\n" + "="*70)
    print("🔧 MASSIVE API KEY TROUBLESHOOTER")
    print("="*70)
    
    # Load current config
    config, config_path = load_config()
    if not config:
        print("❌ Could not find config.json")
        sys.exit(1)
    
    current_key = config.get('massive', {}).get('api_key', '')
    
    print(f"\n📋 Current Configuration:")
    print(f"   Config file: {config_path}")
    print(f"   Current key: {current_key[:10]}... (len={len(current_key)})" if current_key else "   Current key: NOT SET")
    
    # Test current key
    if current_key:
        print("\n" + "-"*70)
        print("1️⃣  Testing Current Key")
        print("-"*70)
        is_valid, message = test_api_key(current_key, "Current config key")
        if is_valid:
            print(f"\n✅ Current key is valid: {message}")
            print("   No update needed!")
            return
        else:
            print(f"\n❌ Current key is invalid: {message}")
    
    # Ask for new key
    print("\n" + "-"*70)
    print("2️⃣  Update API Key")
    print("-"*70)
    print("   The current key is invalid or not set.")
    print("   Please provide your Massive.com API key.")
    print("   Get it from: https://massive.com/dashboard")
    print()
    
    new_key = input("Enter new Massive API key (or press Enter to skip): ").strip()
    
    if not new_key:
        print("\n⚠️  No key provided. Exiting.")
        print("\n💡 To update later, run this script again or edit config.json manually:")
        print(f"   {config_path}")
        return
    
    # Validate key format
    key_len = len(new_key)
    has_dash = "-" in new_key
    
    print(f"\n🔍 Key validation:")
    print(f"   Length: {key_len}")
    print(f"   Has dash: {has_dash}")
    
    if has_dash or key_len > 40:
        print("\n⚠️  WARNING: This looks like an S3 access key, not a REST API key.")
        print("   S3 keys are for flat files. You need the REST API key from Massive.com dashboard.")
        confirm = input("   Continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            print("   Cancelled.")
            return
    
    # Test new key
    print("\n" + "-"*70)
    print("3️⃣  Testing New Key")
    print("-"*70)
    is_valid, message = test_api_key(new_key, "New key")
    
    if not is_valid:
        print(f"\n❌ New key test failed: {message}")
        print("   Please verify the key is correct from https://massive.com/dashboard")
        confirm = input("   Update config anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            print("   Cancelled.")
            return
    
    # Update config
    print("\n" + "-"*70)
    print("4️⃣  Updating Configuration")
    print("-"*70)
    if update_massive_key(new_key, config_path):
        print(f"✅ Massive API key updated successfully!")
        print(f"   New key: {new_key[:10]}... (len={len(new_key)})")
        print("\n⚠️  IMPORTANT: Restart the service for changes to take effect")
        print("   The running service needs to reload the config")
    else:
        print("❌ Failed to update config")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("✅ TROUBLESHOOTING COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

