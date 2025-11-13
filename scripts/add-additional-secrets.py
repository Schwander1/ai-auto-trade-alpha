#!/usr/bin/env python3
"""
Add additional API keys and secrets to AWS Secrets Manager

This script adds:
- Anthropic API key
- Sonar API key (Perplexity)
- X.AI (Grok) API key
- Sonar Administration key
- Figma API key
- NextAuth secret
- Tradervue Gold credentials (if provided)
"""

import sys
import argparse
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
    print("   Please ensure boto3 is installed: pip install boto3")
    sys.exit(1)


def add_secret(secrets_manager, service: str, key: str, value: str, description: str, dry_run: bool = False):
    """Add a secret to AWS Secrets Manager"""
    if dry_run:
        print(f"  [DRY RUN] Would add: {service}/{key}")
        return True
    
    # Use force_create=True to skip existence check (handles permission issues)
    success = secrets_manager.set_secret(
        key,
        value,
        service=service,
        description=description,
        force_create=True
    )
    
    if success:
        print(f"  ✅ Added: {service}/{key}")
        return True
    else:
        print(f"  ❌ Failed to add: {service}/{key}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Add additional secrets to AWS Secrets Manager")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (don't actually upload)")
    parser.add_argument("--region", type=str, default="us-east-1", help="AWS region")
    parser.add_argument("--tradervue-username", type=str, help="Tradervue Gold username")
    parser.add_argument("--tradervue-token", type=str, help="Tradervue Gold API token")
    
    args = parser.parse_args()
    
    print("🔐 Adding Additional Secrets to AWS Secrets Manager")
    print("=" * 60)
    
    # Initialize secrets manager
    try:
        secrets_manager = get_secrets_manager(
            region_name=args.region,
            fallback_to_env=False,
            secret_prefix="argo-alpine"
        )
        print(f"✅ Connected to AWS Secrets Manager (region: {args.region})\n")
    except Exception as e:
        print(f"❌ Failed to connect to AWS Secrets Manager: {e}")
        print("\nPlease ensure:")
        print("  1. AWS credentials are configured (aws configure)")
        print("  2. You have permissions to create/update secrets")
        print("  3. boto3 is installed: pip install boto3")
        sys.exit(1)
    
    # Define secrets to add
    secrets_to_add = [
        # Argo secrets
        {
            "service": "argo",
            "key": "anthropic-api-key",
            "value": "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",
            "description": "Anthropic Claude API key for sentiment analysis"
        },
        {
            "service": "argo",
            "key": "perplexity-api-key",
            "value": "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",
            "description": "Perplexity Sonar API key for news research"
        },
        {
            "service": "argo",
            "key": "xai-api-key",
            "value": "xai-ZZrAK9BXQNAlCeaem6cZMVMZtOB42pE9WtAmXGcPyFz6Yuiha8TuC2Y4wxKWiQ0rt3vlNFDnsumf3q3h",
            "description": "X.AI (Grok) API key"
        },
        {
            "service": "argo",
            "key": "sonar-admin-key",
            "value": "squ_4a0d61cdd0e37e20d2c5928c639f5bc6e4beb478",
            "description": "Sonar Administration API key"
        },
        {
            "service": "argo",
            "key": "figma-api-key",
            "value": "figd_UBvI6J7L_N7XLqCuY0cpPi1jb7GMVW00PYn11Epr",
            "description": "Figma API key (Primary)"
        },
        # Alpine Frontend secrets
        {
            "service": "alpine-frontend",
            "key": "nextauth-secret",
            "value": "iOgv8d7F96pLruaD9t+2Bc2b/5x38jWf4zqX2mRgj+o=",
            "description": "NextAuth.js secret for session encryption"
        },
    ]
    
    # Add Tradervue credentials if provided
    if args.tradervue_username and args.tradervue_token:
        secrets_to_add.extend([
            {
                "service": "argo",
                "key": "tradervue-username",
                "value": args.tradervue_username,
                "description": "Tradervue Gold username"
            },
            {
                "service": "argo",
                "key": "tradervue-api-token",
                "value": args.tradervue_token,
                "description": "Tradervue Gold API token"
            },
        ])
    
    # Add all secrets
    print("📤 Adding secrets...\n")
    added_count = 0
    failed_count = 0
    
    for secret in secrets_to_add:
        success = add_secret(
            secrets_manager,
            secret["service"],
            secret["key"],
            secret["value"],
            secret["description"],
            dry_run=args.dry_run
        )
        if success:
            added_count += 1
        else:
            failed_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print("=" * 60)
    print(f"Secrets added: {added_count}")
    if failed_count > 0:
        print(f"Secrets failed: {failed_count}")
    
    if args.dry_run:
        print("\n⚠️  This was a dry run. No secrets were actually uploaded.")
        print("   Run without --dry-run to perform the actual upload.")
    else:
        print("\n✅ All secrets added successfully!")
        
        if not args.tradervue_username or not args.tradervue_token:
            print("\n⚠️  Note: Tradervue Gold credentials were not provided.")
            print("   To add them later, run:")
            print("   python scripts/add-additional-secrets.py --tradervue-username USERNAME --tradervue-token TOKEN")


if __name__ == "__main__":
    main()

