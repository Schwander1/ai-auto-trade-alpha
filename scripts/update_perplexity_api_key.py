#!/usr/bin/env python3
"""
Update Perplexity API key in AWS Secrets Manager

Usage:
    python scripts/update_perplexity_api_key.py <new_api_key>
    
Or set as environment variable:
    export PERPLEXITY_API_KEY="pplx-..."
    python scripts/update_perplexity_api_key.py
"""
import sys
import os
from pathlib import Path

# Add argo to path
script_dir = Path(__file__).parent
workspace_root = script_dir.parent
sys.path.insert(0, str(workspace_root / "argo"))

from argo.utils.secrets_manager import get_secrets_manager


def update_perplexity_key(api_key: str) -> bool:
    """Update Perplexity API key in AWS Secrets Manager"""
    if not api_key:
        print("❌ Error: API key is required")
        return False
    
    if not api_key.startswith("pplx-"):
        print("⚠️  Warning: API key doesn't start with 'pplx-' - are you sure it's correct?")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    
    sm = get_secrets_manager()
    
    print(f"Updating Perplexity API key in AWS Secrets Manager...")
    print(f"Key: {api_key[:15]}...")
    
    success = sm.set_secret(
        'perplexity-api-key',
        api_key,
        service='argo',
        description='Perplexity Sonar API key for news research',
        force_create=True
    )
    
    if success:
        print("✅ Perplexity API key updated successfully!")
        
        # Verify it
        verify_key = sm.get_secret('perplexity-api-key', service='argo')
        if verify_key == api_key:
            print("✅ Verification: Key retrieved correctly")
            return True
        else:
            print("⚠️  Warning: Key updated but verification failed")
            return False
    else:
        print("❌ Failed to update Perplexity API key")
        return False


def test_api_key(api_key: str) -> bool:
    """Test if the API key works"""
    import requests
    
    print(f"\nTesting API key: {api_key[:15]}...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'sonar',
        'messages': [
            {'role': 'user', 'content': 'What is Bitcoin?'}
        ],
        'max_tokens': 50
    }
    
    try:
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ API key is valid and working!")
            return True
        elif response.status_code == 401:
            print("❌ API key is invalid or expired (401 Unauthorized)")
            return False
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return False


def main():
    # Get API key from command line or environment variable
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if not api_key:
            print("Usage: python scripts/update_perplexity_api_key.py <api_key>")
            print("   Or: export PERPLEXITY_API_KEY='pplx-...' && python scripts/update_perplexity_api_key.py")
            sys.exit(1)
    
    # Test the key first
    if not test_api_key(api_key):
        print("\n⚠️  API key test failed. Do you want to update it anyway? (y/n): ", end='')
        response = input()
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(1)
    
    # Update the key
    if update_perplexity_key(api_key):
        print("\n✅ Success! Perplexity API key has been updated.")
        print("   Restart the signal generator service to use the new key:")
        print("   systemctl restart argo-signal-generator.service")
        sys.exit(0)
    else:
        print("\n❌ Failed to update Perplexity API key")
        sys.exit(1)


if __name__ == '__main__':
    main()

