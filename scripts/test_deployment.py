#!/usr/bin/env python3
"""
Deployment smoke tests
Tests service health and functionality after deployment
"""

import requests
import json
import sys
import time
from typing import Dict, List, Tuple


def test_health_endpoint(base_url: str, timeout: int = 10) -> Tuple[bool, str]:
    """Test health endpoint returns valid response"""
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        # Validate response structure
        required_keys = ['status', 'version', 'services', 'system']
        for key in required_keys:
            if key not in data:
                return False, f"Missing key in health response: {key}"
        
        # Check status is valid
        if data['status'] not in ['healthy', 'degraded', 'unhealthy']:
            return False, f"Invalid status: {data['status']}"
        
        return True, f"Status: {data['status']}, Version: {data.get('version', 'unknown')}"
    except requests.exceptions.Timeout:
        return False, "Health endpoint timeout"
    except requests.exceptions.ConnectionError:
        return False, "Health endpoint connection error"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON response: {e}"
    except Exception as e:
        return False, f"Health endpoint test failed: {e}"


def test_optimization_modules(base_url: str, timeout: int = 10) -> Tuple[bool, str]:
    """Test that optimization modules are loaded"""
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=timeout)
        data = response.json()
        
        perf = data.get('services', {}).get('performance', {})
        if not perf:
            return False, "Performance metrics not available in health response"
        
        if 'error' in perf:
            return False, f"Performance metrics error: {perf['error']}"
        
        return True, "Performance metrics available"
    except Exception as e:
        return False, f"Optimization modules test failed: {e}"


def test_data_source_health(base_url: str, timeout: int = 10) -> Tuple[bool, str]:
    """Test data source health monitoring"""
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=timeout)
        data = response.json()
        
        ds = data.get('services', {}).get('data_sources', {})
        if not ds:
            return False, "Data source health not available"
        
        if 'sources' not in ds:
            return False, "Data source details not available"
        
        # Check if massive is present (even if unhealthy)
        if 'massive' not in ds['sources']:
            return False, "Massive data source not found in health response"
        
        massive_status = ds['sources']['massive'].get('status', 'unknown')
        return True, f"Data source health available (Massive: {massive_status})"
    except Exception as e:
        return False, f"Data source health test failed: {e}"


def test_metrics_endpoint(base_url: str, timeout: int = 10) -> Tuple[bool, str]:
    """Test Prometheus metrics endpoint"""
    try:
        response = requests.get(f"{base_url}/metrics", timeout=timeout)
        response.raise_for_status()
        
        # Check if response contains Prometheus format
        if '#' not in response.text or 'argo_' not in response.text:
            return False, "Metrics endpoint doesn't appear to be Prometheus format"
        
        return True, "Metrics endpoint responding"
    except Exception as e:
        return False, f"Metrics endpoint test failed: {e}"


def wait_for_service(base_url: str, max_retries: int = 30, retry_delay: int = 2) -> bool:
    """Wait for service to become available"""
    print(f"⏳ Waiting for service at {base_url}...")
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/api/v1/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Service is available after {i * retry_delay} seconds")
                return True
        except:
            pass
        
        if i < max_retries - 1:
            time.sleep(retry_delay)
            print(f"  [{i+1}/{max_retries}] Waiting...")
    
    print(f"❌ Service not available after {max_retries * retry_delay} seconds")
    return False


def run_tests(base_url: str) -> Dict[str, Tuple[bool, str]]:
    """Run all deployment tests"""
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Optimization Modules", test_optimization_modules),
        ("Data Source Health", test_data_source_health),
        ("Metrics Endpoint", test_metrics_endpoint),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        success, message = test_func(base_url)
        results[test_name] = (success, message)
        
        if success:
            print(f"  ✅ {message}")
        else:
            print(f"  ❌ {message}")
    
    return results


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://178.156.194.174:8000"
    
    print("🧪 Running deployment smoke tests")
    print("=" * 50)
    print(f"Target: {base_url}")
    
    # Wait for service to be available
    if not wait_for_service(base_url):
        print("\n❌ Service is not available. Exiting.")
        sys.exit(1)
    
    # Run tests
    results = run_tests(base_url)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for success, _ in results.values() if success)
    total = len(results)
    
    for test_name, (success, message) in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
    
    print(f"\n📊 Tests: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()


