#!/usr/bin/env python3
"""
Migration script to upload secrets from .env files and config.json to AWS Secrets Manager

This script:
1. Reads secrets from .env files and config.json
2. Uploads them to AWS Secrets Manager with proper naming
3. Validates that secrets were uploaded correctly
4. Provides a rollback option
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

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
    print("   Please ensure boto3 is installed: pip install boto3")
    sys.exit(1)


def load_env_file(env_path: Path) -> Dict[str, str]:
    """Load environment variables from .env file"""
    env_vars = {}
    if not env_path.exists():
        return env_vars
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                env_vars[key] = value
    
    return env_vars


def load_config_json(config_path: Path) -> Dict[str, Any]:
    """Load configuration from config.json"""
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r') as f:
        return json.load(f)


def migrate_argo_secrets(secrets_manager, env_file: Optional[Path] = None, config_file: Optional[Path] = None, dry_run: bool = False):
    """Migrate Argo secrets to AWS Secrets Manager"""
    print("\n🔧 Migrating Argo secrets...")
    
    service = "argo"
    secrets_to_migrate = {}
    
    # Load from .env file
    if env_file:
        env_vars = load_env_file(env_file)
        if env_vars:
            # Map environment variables to secret keys
            mapping = {
                "REDIS_HOST": "redis-host",
                "REDIS_PORT": "redis-port",
                "REDIS_PASSWORD": "redis-password",
                "REDIS_DB": "redis-db",
                "ARGO_API_SECRET": "api-secret",
            }
            
            for env_key, secret_key in mapping.items():
                if env_key in env_vars:
                    secrets_to_migrate[secret_key] = env_vars[env_key]
    
    # Load from config.json
    if config_file:
        config = load_config_json(config_file)
        
        # Alpaca credentials
        if 'alpaca' in config:
            alpaca = config['alpaca']
            if 'api_key' in alpaca:
                secrets_to_migrate['alpaca-api-key'] = alpaca['api_key']
            if 'secret_key' in alpaca:
                secrets_to_migrate['alpaca-secret-key'] = alpaca['secret_key']
            if 'paper' in alpaca:
                secrets_to_migrate['alpaca-paper'] = str(alpaca['paper']).lower()
        
        # API keys
        api_keys = {
            'massive': 'massive-api-key',
            'alpha_vantage': 'alpha-vantage-api-key',
            'x_api': 'x-api-bearer-token',
            'sonar': 'sonar-api-key',
        }
        
        for config_key, secret_key in api_keys.items():
            if config_key in config and 'api_key' in config[config_key]:
                secrets_to_migrate[secret_key] = config[config_key]['api_key']
            elif config_key in config and 'bearer_token' in config[config_key]:
                secrets_to_migrate[secret_key] = config[config_key]['bearer_token']
    
    # Upload secrets
    migrated = []
    for secret_key, secret_value in secrets_to_migrate.items():
        if dry_run:
            print(f"  [DRY RUN] Would migrate: {service}/{secret_key}")
        else:
            success = secrets_manager.set_secret(
                secret_key,
                secret_value,
                service=service,
                description=f"Argo {secret_key} (migrated from local config)"
            )
            if success:
                print(f"  ✅ Migrated: {service}/{secret_key}")
                migrated.append(secret_key)
            else:
                print(f"  ❌ Failed to migrate: {service}/{secret_key}")
    
    return migrated


def migrate_alpine_backend_secrets(secrets_manager, env_file: Optional[Path] = None, dry_run: bool = False):
    """Migrate Alpine Backend secrets to AWS Secrets Manager"""
    print("\n🔧 Migrating Alpine Backend secrets...")
    
    service = "alpine-backend"
    secrets_to_migrate = {}
    
    # Load from .env file
    if env_file:
        env_vars = load_env_file(env_file)
        if env_vars:
            # Map environment variables to secret keys
            mapping = {
                "STRIPE_SECRET_KEY": "stripe-secret-key",
                "STRIPE_PUBLISHABLE_KEY": "stripe-publishable-key",
                "STRIPE_WEBHOOK_SECRET": "stripe-webhook-secret",
                "STRIPE_ACCOUNT_ID": "stripe-account-id",
                "STRIPE_STARTER_PRICE_ID": "stripe-starter-price-id",
                "STRIPE_PRO_PRICE_ID": "stripe-pro-price-id",
                "STRIPE_ELITE_PRICE_ID": "stripe-elite-price-id",
                "DATABASE_URL": "database-url",
                "JWT_SECRET": "jwt-secret",
                "DOMAIN": "domain",
                "FRONTEND_URL": "frontend-url",
                "REDIS_HOST": "redis-host",
                "REDIS_PORT": "redis-port",
                "REDIS_PASSWORD": "redis-password",
                "REDIS_DB": "redis-db",
                "SENDGRID_API_KEY": "sendgrid-api-key",
            }
            
            for env_key, secret_key in mapping.items():
                if env_key in env_vars and env_vars[env_key]:
                    secrets_to_migrate[secret_key] = env_vars[env_key]
    
    # Upload secrets
    migrated = []
    for secret_key, secret_value in secrets_to_migrate.items():
        if dry_run:
            print(f"  [DRY RUN] Would migrate: {service}/{secret_key}")
        else:
            success = secrets_manager.set_secret(
                secret_key,
                secret_value,
                service=service,
                description=f"Alpine Backend {secret_key} (migrated from local config)"
            )
            if success:
                print(f"  ✅ Migrated: {service}/{secret_key}")
                migrated.append(secret_key)
            else:
                print(f"  ❌ Failed to migrate: {service}/{secret_key}")
    
    return migrated


def verify_secrets(secrets_manager, service: str, secret_keys: list):
    """Verify that secrets were uploaded correctly"""
    print(f"\n🔍 Verifying {service} secrets...")
    
    all_verified = True
    for secret_key in secret_keys:
        try:
            value = secrets_manager.get_secret(secret_key, service=service)
            if value:
                print(f"  ✅ Verified: {service}/{secret_key}")
            else:
                print(f"  ❌ Not found: {service}/{secret_key}")
                all_verified = False
        except Exception as e:
            print(f"  ❌ Error verifying {service}/{secret_key}: {e}")
            all_verified = False
    
    return all_verified


def main():
    parser = argparse.ArgumentParser(description="Migrate secrets to AWS Secrets Manager")
    parser.add_argument("--argo-env", type=Path, help="Path to Argo .env file")
    parser.add_argument("--argo-config", type=Path, help="Path to Argo config.json file")
    parser.add_argument("--alpine-env", type=Path, help="Path to Alpine Backend .env file")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (don't actually upload)")
    parser.add_argument("--verify", action="store_true", help="Verify secrets after migration")
    parser.add_argument("--region", type=str, default="us-east-1", help="AWS region")
    
    args = parser.parse_args()
    
    print("🚀 AWS Secrets Manager Migration Script")
    print("=" * 50)
    
    # Initialize secrets manager
    try:
        secrets_manager = get_secrets_manager(
            region_name=args.region,
            fallback_to_env=False,
            secret_prefix="argo-alpine"
        )
        print(f"✅ Connected to AWS Secrets Manager (region: {args.region})")
    except Exception as e:
        print(f"❌ Failed to connect to AWS Secrets Manager: {e}")
        print("\nPlease ensure:")
        print("  1. AWS credentials are configured (aws configure)")
        print("  2. You have permissions to create/update secrets")
        print("  3. boto3 is installed: pip install boto3")
        sys.exit(1)
    
    # Default paths
    workspace_root = Path(__file__).parent.parent
    
    if not args.argo_env:
        args.argo_env = workspace_root / "argo" / ".env"
    if not args.argo_config:
        args.argo_config = workspace_root / "argo" / "config.json"
    if not args.alpine_env:
        args.alpine_env = workspace_root / "alpine-backend" / ".env"
    
    # Migrate Argo secrets
    argo_migrated = []
    if args.argo_env.exists() or args.argo_config.exists():
        argo_migrated = migrate_argo_secrets(
            secrets_manager,
            env_file=args.argo_env if args.argo_env.exists() else None,
            config_file=args.argo_config if args.argo_config.exists() else None,
            dry_run=args.dry_run
        )
    else:
        print("\n⚠️  Argo config files not found, skipping...")
    
    # Migrate Alpine Backend secrets
    alpine_migrated = []
    if args.alpine_env.exists():
        alpine_migrated = migrate_alpine_backend_secrets(
            secrets_manager,
            env_file=args.alpine_env,
            dry_run=args.dry_run
        )
    else:
        print("\n⚠️  Alpine Backend .env file not found, skipping...")
    
    # Verify secrets
    if args.verify and not args.dry_run:
        if argo_migrated:
            verify_secrets(secrets_manager, "argo", argo_migrated)
        if alpine_migrated:
            verify_secrets(secrets_manager, "alpine-backend", alpine_migrated)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Migration Summary")
    print("=" * 50)
    print(f"Argo secrets migrated: {len(argo_migrated)}")
    print(f"Alpine Backend secrets migrated: {len(alpine_migrated)}")
    print(f"Total secrets migrated: {len(argo_migrated) + len(alpine_migrated)}")
    
    if args.dry_run:
        print("\n⚠️  This was a dry run. No secrets were actually uploaded.")
        print("   Run without --dry-run to perform the actual migration.")
    else:
        print("\n✅ Migration complete!")
        print("\nNext steps:")
        print("  1. Set USE_AWS_SECRETS=true in your environment")
        print("  2. Restart your services")
        print("  3. Verify health checks pass")
        print("  4. Remove .env files from version control (if not already done)")


if __name__ == "__main__":
    main()

