#!/usr/bin/env python3
"""
Add Alpaca account credentials to AWS Secrets Manager
Supports both dev and production paper trading accounts
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from argo.utils.secrets_manager import get_secrets_manager
    SECRETS_AVAILABLE = True
except ImportError:
    SECRETS_AVAILABLE = False
    print("⚠️  Secrets manager not available")

def add_alpaca_secrets():
    """Add Alpaca credentials to AWS Secrets Manager"""
    
    if not SECRETS_AVAILABLE:
        print("❌ Secrets manager not available")
        return False
    
    secrets = get_secrets_manager()
    service = "argo"
    
    print('\n' + '='*70)
    print('🔐 ADDING ALPACA CREDENTIALS TO AWS SECRETS MANAGER')
    print('='*70)
    
    # NOTE: This script is a one-time setup script that moves secrets from code to AWS Secrets Manager.
    # The secrets below are paper trading account credentials (safe to have in setup scripts).
    # After running this script, secrets are stored in AWS Secrets Manager and removed from code.
    # This is acceptable for setup scripts that are run once to migrate secrets.
    
    # Dev account credentials (paper trading - safe for setup scripts)
    dev_api_key = "PKKTZHTVMTOW7DPPYNOGYPKHWD"
    dev_secret_key = "56mYiK5MBahHS6wRH7ghC6Mtqt2nxwcTBB9odMjcTMc2"
    
    # Production account credentials (paper trading - safe for setup scripts)
    prod_api_key = "PKVFBDORPHOCX5NEOVEZNDTWVT"
    prod_secret_key = "ErscqTCdo21raoiFFyDzASzHpfgWB8L7xWVWKFukVa6b"
    
    results = []
    
    # Add dev account secrets
    print('\n📝 Adding Dev Account Credentials...')
    dev_api_result = secrets.set_secret(
        key="alpaca-api-key-dev",
        value=dev_api_key,
        service=service,
        description="Alpaca Paper Trading API Key - Dev Environment",
        force_create=True
    )
    results.append(("Dev API Key", dev_api_result))
    
    dev_secret_result = secrets.set_secret(
        key="alpaca-secret-key-dev",
        value=dev_secret_key,
        service=service,
        description="Alpaca Paper Trading Secret Key - Dev Environment",
        force_create=True
    )
    results.append(("Dev Secret Key", dev_secret_result))
    
    # Add production account secrets
    print('\n📝 Adding Production Account Credentials...')
    prod_api_result = secrets.set_secret(
        key="alpaca-api-key-production",
        value=prod_api_key,
        service=service,
        description="Alpaca Paper Trading API Key - Production Environment",
        force_create=True
    )
    results.append(("Production API Key", prod_api_result))
    
    prod_secret_result = secrets.set_secret(
        key="alpaca-secret-key-production",
        value=prod_secret_key,
        service=service,
        description="Alpaca Paper Trading Secret Key - Production Environment",
        force_create=True
    )
    results.append(("Production Secret Key", prod_secret_result))
    
    # Add paper mode flag (shared)
    print('\n📝 Adding Paper Mode Flag...')
    paper_result = secrets.set_secret(
        key="alpaca-paper",
        value="true",
        service=service,
        description="Alpaca Paper Trading Mode (true/false)",
        force_create=True
    )
    results.append(("Paper Mode", paper_result))
    
    # Summary
    print('\n' + '='*70)
    print('📊 SUMMARY')
    print('='*70)
    
    all_success = True
    for name, result in results:
        status = '✅' if result else '❌'
        print(f'   {status} {name}')
        if not result:
            all_success = False
    
    if all_success:
        print('\n✅ All secrets added successfully!')
        print('\nSecret Names:')
        print('   - argo-alpine/argo/alpaca-api-key-dev')
        print('   - argo-alpine/argo/alpaca-secret-key-dev')
        print('   - argo-alpine/argo/alpaca-api-key-production')
        print('   - argo-alpine/argo/alpaca-secret-key-production')
        print('   - argo-alpine/argo/alpaca-paper')
    else:
        print('\n⚠️  Some secrets failed to add. Check AWS permissions.')
    
    print('='*70 + '\n')
    
    return all_success

if __name__ == '__main__':
    success = add_alpaca_secrets()
    sys.exit(0 if success else 1)

