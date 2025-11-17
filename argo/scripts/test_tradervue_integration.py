#!/usr/bin/env python3
"""
Test script for Tradervue Enhanced Integration
Verifies configuration, tests API endpoints, and validates functionality
"""
import sys
import os
from pathlib import Path

# Add argo to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported"""
    print("\n" + "="*60)
    print("1. Testing Imports")
    print("="*60)
    
    try:
        from argo.integrations.tradervue_client import TradervueClient, get_tradervue_client
        print("✅ tradervue_client imported successfully")
    except Exception as e:
        print(f"❌ Failed to import tradervue_client: {e}")
        return False
    
    try:
        from argo.integrations.tradervue_integration import TradervueIntegration, get_tradervue_integration
        print("✅ tradervue_integration imported successfully")
    except Exception as e:
        print(f"❌ Failed to import tradervue_integration: {e}")
        return False
    
    return True

def test_client_initialization():
    """Test Tradervue client initialization"""
    print("\n" + "="*60)
    print("2. Testing Client Initialization")
    print("="*60)
    
    try:
        from argo.integrations.tradervue_client import get_tradervue_client
        
        client = get_tradervue_client()
        
        print(f"   Enabled: {client.enabled}")
        print(f"   Username: {client.username if client.enabled else 'Not configured'}")
        print(f"   Has Password: {'Yes' if client.password else 'No'}")
        
        if client.enabled:
            print("✅ Tradervue client initialized and configured")
            return True
        else:
            print("⚠️  Tradervue client initialized but not configured")
            print("   Set TRADERVUE_USERNAME and TRADERVUE_PASSWORD environment variables")
            print("   Or configure in AWS Secrets Manager:")
            print("   - argo-capital/argo/tradervue-username")
            print("   - argo-capital/argo/tradervue-password")
            print("   Note: Tradervue uses account username and password (not API token)")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_initialization():
    """Test Tradervue integration initialization"""
    print("\n" + "="*60)
    print("3. Testing Integration Initialization")
    print("="*60)
    
    try:
        from argo.integrations.tradervue_integration import get_tradervue_integration
        
        integration = get_tradervue_integration()
        
        print(f"   Client Enabled: {integration.client.enabled}")
        print(f"   Tracker Available: {integration.tracker is not None}")
        
        if integration.client.enabled:
            print("✅ Tradervue integration initialized successfully")
            return True
        else:
            print("⚠️  Integration initialized but client not configured")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints (if server is running)"""
    print("\n" + "="*60)
    print("4. Testing API Endpoints")
    print("="*60)
    
    import requests
    
    base_url = "http://localhost:8000"
    
    endpoints = [
        ("/api/v1/tradervue/status", "GET"),
        ("/api/v1/tradervue/widget-url", "GET"),
        ("/api/v1/tradervue/profile-url", "GET"),
        ("/api/v1/tradervue/metrics?days=30", "GET"),
    ]
    
    print(f"   Testing against: {base_url}")
    print("   (Note: Server must be running for these tests)")
    
    results = []
    for endpoint, method in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {method} {endpoint} - OK")
                results.append(True)
            elif response.status_code == 503:
                print(f"⚠️  {method} {endpoint} - Not configured (503)")
                results.append(False)
            else:
                print(f"❌ {method} {endpoint} - HTTP {response.status_code}")
                results.append(False)
        except requests.exceptions.ConnectionError:
            print(f"⚠️  {method} {endpoint} - Server not running")
            results.append(None)
        except Exception as e:
            print(f"❌ {method} {endpoint} - Error: {e}")
            results.append(False)
    
    if all(r is None for r in results):
        print("\n   ⚠️  API server is not running. Start it with:")
        print("   cd argo && python -m uvicorn argo.api.server:app --reload")
        return None
    
    return any(r for r in results if r is not None)

def test_trade_sync():
    """Test trade syncing functionality"""
    print("\n" + "="*60)
    print("5. Testing Trade Sync Functionality")
    print("="*60)
    
    try:
        from argo.integrations.tradervue_integration import get_tradervue_integration
        from argo.tracking.unified_tracker import UnifiedPerformanceTracker
        
        integration = get_tradervue_integration()
        
        if not integration.client.enabled:
            print("⚠️  Tradervue not configured - skipping sync test")
            return None
        
        # Test sync_recent_trades method exists
        if hasattr(integration, 'sync_recent_trades'):
            print("✅ sync_recent_trades method available")
            
            # Test with 0 days (should return stats)
            stats = integration.sync_recent_trades(days=0)
            print(f"   Sync stats structure: {list(stats.keys())}")
            print("✅ Trade sync functionality available")
            return True
        else:
            print("❌ sync_recent_trades method not found")
            return False
            
    except Exception as e:
        print(f"❌ Trade sync test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_widget_urls():
    """Test widget URL generation"""
    print("\n" + "="*60)
    print("6. Testing Widget URL Generation")
    print("="*60)
    
    try:
        from argo.integrations.tradervue_integration import get_tradervue_integration
        
        integration = get_tradervue_integration()
        
        if not integration.client.enabled:
            print("⚠️  Tradervue not configured - skipping widget test")
            return None
        
        widget_types = ["equity", "trades", "performance"]
        
        for widget_type in widget_types:
            url = integration.get_widget_url(widget_type)
            if url:
                print(f"✅ {widget_type} widget URL: {url[:60]}...")
            else:
                print(f"⚠️  {widget_type} widget URL not available")
        
        profile_url = integration.get_profile_url()
        if profile_url:
            print(f"✅ Profile URL: {profile_url}")
        else:
            print("⚠️  Profile URL not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Widget URL test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TRADERVUE ENHANCED INTEGRATION TEST SUITE")
    print("="*60)
    
    results = {}
    
    # Test 1: Imports
    results['imports'] = test_imports()
    if not results['imports']:
        print("\n❌ Import tests failed - cannot continue")
        return 1
    
    # Test 2: Client initialization
    results['client'] = test_client_initialization()
    
    # Test 3: Integration initialization
    results['integration'] = test_integration_initialization()
    
    # Test 4: API endpoints (optional - requires server)
    results['api'] = test_api_endpoints()
    
    # Test 5: Trade sync
    results['sync'] = test_trade_sync()
    
    # Test 6: Widget URLs
    results['widgets'] = test_widget_urls()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        elif result is None:
            status = "⚠️  SKIP"
        else:
            status = "❓ UNKNOWN"
        
        print(f"   {test_name:15} {status}")
    
    # Overall status
    critical_tests = ['imports', 'client', 'integration']
    if all(results.get(t) for t in critical_tests):
        print("\n✅ All critical tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed or were skipped")
        print("\nNext steps:")
        print("1. Configure Tradervue credentials:")
        print("   export TRADERVUE_USERNAME=your_username")
        print("   export TRADERVUE_PASSWORD=your_password")
        print("2. Or configure in AWS Secrets Manager")
        print("3. Start API server: cd argo && python -m uvicorn argo.api.server:app")
        return 1

if __name__ == "__main__":
    sys.exit(main())

