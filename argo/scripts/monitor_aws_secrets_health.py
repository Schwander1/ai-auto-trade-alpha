#!/usr/bin/env python3
"""
Monitor AWS Secrets Manager Health
Checks access, secret availability, and alerts on issues
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from argo.utils.secrets_manager import get_secrets_manager
    SECRETS_AVAILABLE = True
except ImportError:
    SECRETS_AVAILABLE = False

def check_secrets_health():
    """Check health of AWS Secrets Manager"""
    print('\n' + '='*70)
    print('🔍 AWS SECRETS MANAGER HEALTH CHECK')
    print('='*70)
    print(f'Timestamp: {datetime.now().isoformat()}')
    print('')
    
    if not SECRETS_AVAILABLE:
        print('❌ Secrets manager not available')
        return False
    
    try:
        secrets = get_secrets_manager()
        service = "argo"
        
        # Required secrets for Argo
        required_secrets = [
            'alpaca-api-key-dev',
            'alpaca-secret-key-dev',
            'alpaca-api-key-production',
            'alpaca-secret-key-production',
            'alpaca-paper'
        ]
        
        results = []
        all_healthy = True
        
        print('📋 Checking required secrets...')
        print('')
        
        for secret_key in required_secrets:
            try:
                secret_value = secrets.get_secret(secret_key, service=service)
                if secret_value:
                    print(f'   ✅ {secret_key}')
                    results.append({
                        'secret': secret_key,
                        'status': 'healthy',
                        'accessible': True
                    })
                else:
                    print(f'   ❌ {secret_key} - Not found')
                    results.append({
                        'secret': secret_key,
                        'status': 'missing',
                        'accessible': False
                    })
                    all_healthy = False
            except Exception as e:
                print(f'   ⚠️  {secret_key} - Error: {str(e)[:50]}')
                results.append({
                    'secret': secret_key,
                    'status': 'error',
                    'accessible': False,
                    'error': str(e)
                })
                all_healthy = False
        
        print('')
        print('='*70)
        print('📊 SUMMARY')
        print('='*70)
        
        healthy_count = sum(1 for r in results if r['status'] == 'healthy')
        print(f'   Healthy: {healthy_count}/{len(required_secrets)}')
        print(f'   Missing: {sum(1 for r in results if r["status"] == "missing")}')
        print(f'   Errors: {sum(1 for r in results if r["status"] == "error")}')
        
        if all_healthy:
            print('')
            print('✅ All secrets are healthy and accessible')
        else:
            print('')
            print('⚠️  Some secrets have issues - check above')
        
        print('='*70 + '\n')
        
        return all_healthy
        
    except Exception as e:
        print(f'❌ Health check failed: {e}')
        return False

if __name__ == '__main__':
    healthy = check_secrets_health()
    sys.exit(0 if healthy else 1)

