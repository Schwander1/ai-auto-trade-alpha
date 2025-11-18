#!/usr/bin/env python3
"""
Signal Storage Configuration Checker
Verifies and helps configure signal storage settings
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_environment_variables():
    """Check environment variables for Alpine sync"""
    print("1️⃣  Environment Variables")
    print("-" * 60)
    
    env_vars = {
        'ALPINE_API_URL': os.getenv('ALPINE_API_URL'),
        'ARGO_API_KEY': os.getenv('ARGO_API_KEY'),
        'ALPINE_SYNC_ENABLED': os.getenv('ALPINE_SYNC_ENABLED', 'true'),
    }
    
    all_set = True
    
    for var, value in env_vars.items():
        if value:
            if var == 'ARGO_API_KEY':
                display_value = f"{'*' * min(len(value), 8)}..." if value else "Not set"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            if var == 'ALPINE_SYNC_ENABLED':
                print(f"  ⚠️  {var}: Not set (defaults to 'true')")
            else:
                print(f"  ❌ {var}: Not set")
                all_set = False
    
    return all_set

def check_config_file():
    """Check config.json for Alpine sync settings"""
    print("\n2️⃣  Config File")
    print("-" * 60)
    
    try:
        from argo.core.config_loader import ConfigLoader
        config, _ = ConfigLoader.load_config()
        
        if config and 'alpine' in config:
            alpine_config = config['alpine']
            print("  ✅ Alpine config found in config.json")
            
            if alpine_config.get('api_url'):
                print(f"  ✅ api_url: {alpine_config['api_url']}")
            else:
                print(f"  ⚠️  api_url: Not set")
            
            if alpine_config.get('api_key'):
                print(f"  ✅ api_key: {'*' * 8}...")
            else:
                print(f"  ⚠️  api_key: Not set")
            
            if 'sync_enabled' in alpine_config:
                print(f"  ✅ sync_enabled: {alpine_config['sync_enabled']}")
            else:
                print(f"  ⚠️  sync_enabled: Not set (defaults to true)")
            
            return True
        else:
            print("  ⚠️  No Alpine config in config.json")
            return False
            
    except Exception as e:
        print(f"  ⚠️  Could not load config: {e}")
        return False

def check_alpine_sync_service():
    """Check Alpine sync service configuration"""
    print("\n3️⃣  Alpine Sync Service")
    print("-" * 60)
    
    try:
        from argo.core.alpine_sync import get_alpine_sync_service
        sync_service = get_alpine_sync_service()
        
        if sync_service._sync_enabled:
            print("  ✅ Alpine sync is ENABLED")
            print(f"  ✅ Alpine URL: {sync_service.alpine_url}")
            print(f"  ✅ API key configured: {'Yes' if sync_service.api_key else 'No'}")
            print(f"  ✅ Endpoint: {sync_service.endpoint}")
            return True
        else:
            print("  ⚠️  Alpine sync is DISABLED")
            print("     Reason: Missing configuration (ALPINE_API_URL or ARGO_API_KEY)")
            return False
            
    except Exception as e:
        print(f"  ❌ Alpine sync service check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_paths():
    """Check database file paths"""
    print("\n4️⃣  Database Paths")
    print("-" * 60)
    
    try:
        from argo.core.signal_tracker import SignalTracker
        tracker = SignalTracker()
        
        db_path = tracker.db_file
        log_path = tracker.signals_log
        
        print(f"  Database: {db_path}")
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"    ✅ Exists ({size_mb:.2f} MB)")
        else:
            print(f"    ⚠️  Does not exist (will be created on first signal)")
        
        print(f"  Log file: {log_path}")
        if log_path.exists():
            size_kb = log_path.stat().st_size / 1024
            print(f"    ✅ Exists ({size_kb:.2f} KB)")
        else:
            print(f"    ⚠️  Does not exist (will be created on first signal)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database path check failed: {e}")
        return False

def print_configuration_help():
    """Print configuration help"""
    print("\n" + "=" * 60)
    print("Configuration Help")
    print("=" * 60)
    print()
    print("To enable Alpine sync, set the following environment variables:")
    print()
    print("  export ALPINE_API_URL='http://91.98.153.49:8001'")
    print("  export ARGO_API_KEY='your-secure-api-key-here'")
    print("  export ALPINE_SYNC_ENABLED='true'")
    print()
    print("Or add to config.json:")
    print()
    print('  {')
    print('    "alpine": {')
    print('      "api_url": "http://91.98.153.49:8001",')
    print('      "api_key": "your-secure-api-key-here",')
    print('      "sync_enabled": true')
    print('    }')
    print('  }')
    print()
    print("For production, you can also use AWS Secrets Manager:")
    print("  - Secret path: argo-alpine/argo/argo-api-key")
    print("  - Secret path: argo-alpine/argo/alpine-api-url (optional)")
    print()

def main():
    """Main function"""
    print("=" * 60)
    print("Signal Storage Configuration Checker")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Environment Variables", check_environment_variables()))
    results.append(("Config File", check_config_file()))
    results.append(("Alpine Sync Service", check_alpine_sync_service()))
    results.append(("Database Paths", check_database_paths()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Configuration Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ OK" if result else "⚠️  ISSUE"
        print(f"  {status}: {name}")
    
    print()
    
    # Check if Alpine sync is configured
    try:
        from argo.core.alpine_sync import get_alpine_sync_service
        sync_service = get_alpine_sync_service()
        if not sync_service._sync_enabled:
            print("⚠️  Alpine sync is not configured")
            print_configuration_help()
    except:
        pass
    
    if passed == total:
        print("✅ All configuration checks passed!")
        return 0
    else:
        print("⚠️  Some configuration issues found")
        return 1

if __name__ == '__main__':
    sys.exit(main())

