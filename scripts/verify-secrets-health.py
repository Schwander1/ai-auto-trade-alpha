#!/usr/bin/env python3
"""
Verify that all services can access secrets from AWS Secrets Manager
and that health checks pass
"""

import sys
import requests
import time
from pathlib import Path

# Add shared package to path
script_dir = Path(__file__).parent
workspace_root = script_dir.parent
shared_path = workspace_root / "packages" / "shared"
if shared_path.exists():
    sys.path.insert(0, str(shared_path))

try:
    from utils.secrets_manager import get_secrets_manager
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    print("❌ Error: AWS Secrets Manager utilities not found")
    sys.exit(1)


def check_secret(secrets_manager, service: str, key: str, required: bool = True) -> tuple[bool, str]:
    """Check if a secret is accessible"""
    try:
        value = secrets_manager.get_secret(key, service=service, required=required)
        if value:
            return True, "✅"
        else:
            return False, "❌ (not found)"
    except Exception as e:
        return False, f"❌ ({str(e)})"


def check_service_health(url: str, service_name: str) -> tuple[bool, dict]:
    """Check service health endpoint"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            checks = data.get("checks", {})
            return status == "healthy", data
        else:
            return False, {"error": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}


def main():
    print("🔍 Verifying AWS Secrets Manager Setup")
    print("=" * 60)
    
    # Initialize secrets manager
    try:
        secrets_manager = get_secrets_manager(
            fallback_to_env=True,
            secret_prefix="argo-alpine"
        )
        print("✅ AWS Secrets Manager client initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize AWS Secrets Manager: {e}")
        sys.exit(1)
    
    # Check Argo secrets
    print("📊 Checking Argo Secrets:")
    print("-" * 60)
    argo_secrets = [
        ("api-secret", True),
        ("redis-host", False),
        ("redis-port", False),
        ("redis-password", False),
        ("alpaca-api-key", False),
        ("alpaca-secret-key", False),
    ]
    
    argo_ok = True
    for key, required in argo_secrets:
        ok, status = check_secret(secrets_manager, "argo", key, required)
        print(f"  {key:30s} {status}")
        if required and not ok:
            argo_ok = False
    
    # Check Alpine Backend secrets
    print("\n📊 Checking Alpine Backend Secrets:")
    print("-" * 60)
    alpine_secrets = [
        ("stripe-secret-key", True),
        ("stripe-publishable-key", True),
        ("stripe-webhook-secret", True),
        ("database-url", True),
        ("jwt-secret", True),
        ("domain", True),
        ("frontend-url", True),
        ("redis-host", False),
    ]
    
    alpine_ok = True
    for key, required in alpine_secrets:
        ok, status = check_secret(secrets_manager, "alpine-backend", key, required)
        print(f"  {key:30s} {status}")
        if required and not ok:
            alpine_ok = False
    
    # Check service health endpoints
    print("\n🏥 Checking Service Health:")
    print("-" * 60)
    
    services = [
        ("Argo", "http://localhost:8000/health"),
        ("Alpine Backend", "http://localhost:9001/health"),
    ]
    
    health_ok = True
    for service_name, url in services:
        print(f"\n  {service_name}:")
        ok, data = check_service_health(url, service_name)
        if ok:
            print(f"    ✅ Health check passed")
            if "checks" in data:
                for check_name, check_status in data["checks"].items():
                    status_icon = "✅" if check_status == "healthy" else "⚠️"
                    print(f"      {status_icon} {check_name}: {check_status}")
        else:
            print(f"    ❌ Health check failed: {data.get('error', 'unknown error')}")
            health_ok = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Summary:")
    print("=" * 60)
    print(f"Argo Secrets:        {'✅ All OK' if argo_ok else '❌ Some missing'}")
    print(f"Alpine Backend:      {'✅ All OK' if alpine_ok else '❌ Some missing'}")
    print(f"Service Health:      {'✅ All OK' if health_ok else '❌ Some failed'}")
    
    if argo_ok and alpine_ok and health_ok:
        print("\n✅ All checks passed! AWS Secrets Manager is working correctly.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

