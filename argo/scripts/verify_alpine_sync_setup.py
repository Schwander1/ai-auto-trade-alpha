#!/usr/bin/env python3
"""
Verify Alpine Sync Setup
Quick verification script to check if Alpine sync is properly configured
"""
import sys
import os
from pathlib import Path

# Add argo to path
workspace_root = Path(__file__).parent.parent.parent
argo_path = workspace_root / "argo"
sys.path.insert(0, str(argo_path))

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import httpx
        print(f"  ✅ httpx {httpx.__version__}")
    except ImportError:
        print("  ❌ httpx not installed")
        print("     Install with: pip install httpx>=0.25.0")
        return False
    
    return True

def check_configuration():
    """Check if configuration is set"""
    print("\n🔍 Checking configuration...")
    
    alpine_url = os.getenv('ALPINE_API_URL')
    api_key = os.getenv('ARGO_API_KEY')
    sync_enabled = os.getenv('ALPINE_SYNC_ENABLED', 'true').lower()
    
    if alpine_url:
        print(f"  ✅ ALPINE_API_URL: {alpine_url}")
    else:
        print("  ⚠️  ALPINE_API_URL not set (will try config.json)")
    
    if api_key:
        print(f"  ✅ ARGO_API_KEY: {'*' * min(len(api_key), 8)}...")
    else:
        print("  ⚠️  ARGO_API_KEY not set (will try config.json)")
    
    if sync_enabled == 'false':
        print("  ⚠️  ALPINE_SYNC_ENABLED=false (sync is disabled)")
    else:
        print(f"  ✅ ALPINE_SYNC_ENABLED={sync_enabled}")
    
    # Try to load from config
    try:
        from argo.core.config_loader import ConfigLoader
        config, config_path = ConfigLoader.load_config()
        if config and 'alpine' in config:
            print(f"  ✅ Found Alpine config in {config_path}")
        else:
            print("  ⚠️  No Alpine config in config.json")
    except Exception as e:
        print(f"  ⚠️  Could not check config.json: {e}")
    
    return True

def check_service_import():
    """Check if service can be imported"""
    print("\n🔍 Checking service import...")
    
    try:
        from argo.core.alpine_sync import get_alpine_sync_service
        print("  ✅ Alpine sync service can be imported")
        
        # Try to initialize
        service = get_alpine_sync_service()
        if service._sync_enabled:
            print(f"  ✅ Service initialized and enabled")
            print(f"     Alpine URL: {service.alpine_url}")
        else:
            print("  ⚠️  Service initialized but disabled (missing configuration)")
        
        return True
    except Exception as e:
        print(f"  ❌ Error importing service: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main verification function"""
    print("=" * 60)
    print("Alpine Sync Setup Verification")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # Check dependencies
    if not check_dependencies():
        all_ok = False
    
    # Check configuration
    check_configuration()
    
    # Check service
    if not check_service_import():
        all_ok = False
    
    print()
    print("=" * 60)
    if all_ok:
        print("✅ Setup verification complete!")
        print("\nNext steps:")
        print("  1. Run: python3 scripts/test_alpine_sync.py")
        print("  2. Monitor logs for sync confirmations")
        return 0
    else:
        print("⚠️  Setup verification found issues")
        print("\nPlease fix the issues above before proceeding")
        return 1

if __name__ == '__main__':
    sys.exit(main())

