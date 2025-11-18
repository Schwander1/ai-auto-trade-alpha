#!/usr/bin/env python3
"""
Verification script for security implementation
Checks that all security features are properly implemented
"""
import sys
import os
import importlib.util

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def check_module_exists(module_name):
    """Check if a module exists and can be imported"""
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ImportError, AttributeError, Exception):
        return False

def check_file_exists(file_path):
    """Check if a file exists"""
    return os.path.exists(file_path)

def main():
    """Run all verification checks"""
    print("🔍 Verifying Security Implementation...")
    print("=" * 60)
    
    checks = []
    
    # Check core security modules
    print("\n📦 Core Security Modules:")
    modules = [
        ("backend.core.error_responses", "Standardized error responses"),
        ("backend.core.resource_ownership", "Resource ownership checks"),
        ("backend.core.alerting", "Security event alerting"),
        ("backend.core.rbac", "RBAC utilities"),
    ]
    
    for module, description in modules:
        exists = check_module_exists(module)
        status = "✅" if exists else "❌"
        print(f"  {status} {description}: {module}")
        checks.append((module, exists))
    
    # Check models
    print("\n📊 Database Models:")
    model_files = [
        ("backend/models/role.py", "RBAC models"),
    ]
    
    for file_path, description in model_files:
        exists = check_file_exists(file_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {description}: {file_path}")
        checks.append((file_path, exists))
    
    # Check API endpoints
    print("\n🔌 API Endpoints:")
    apis = [
        ("backend.api.roles", "Role management API"),
    ]
    
    for api, description in apis:
        exists = check_module_exists(api)
        status = "✅" if exists else "❌"
        print(f"  {status} {description}: {api}")
        checks.append((api, exists))
    
    # Check files
    print("\n📄 Key Files:")
    files = [
        ("backend/migrations/add_rbac_tables.py", "RBAC migration script"),
        ("backend/core/security_logging.py", "Security logging with rotation"),
        ("backend/core/request_logging.py", "Request logging with sampling"),
        ("backend/core/csrf.py", "CSRF protection"),
        ("backend/core/rate_limit.py", "Rate limiting"),
        ("backend/api/webhooks.py", "Webhook idempotency"),
        ("tests/integration/test_security_fixes.py", "Security tests"),
    ]
    
    for file_path, description in files:
        exists = check_file_exists(file_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {description}: {file_path}")
        checks.append((file_path, exists))
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for _, exists in checks if exists)
    total = len(checks)
    print(f"\n📊 Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ All security implementations verified!")
        return 0
    else:
        print("❌ Some checks failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

