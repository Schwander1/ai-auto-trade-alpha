#!/usr/bin/env python3
import boto3
import json
import sys

def store_alpaca_credentials():
    client = boto3.client('secretsmanager', region_name='us-west-2')

    secret_dict = {
        'alpaca_key_id': 'PKDVMUI62FMZPRBZBUEPUB2NFN',
        'alpaca_secret_key': '6z6zziHeoL1W9KeotxqzVVjmcaA1Sa79CNHRpFvK1PCc',
        'base_url': 'https://paper-api.alpaca.markets/v2'
    }

    try:
        response = client.create_secret(
            Name='alpaca-paper-trading',
            SecretString=json.dumps(secret_dict)
        )
        print(f"✓ Secret stored: {response['ARN']}")
        return True
    except client.exceptions.ResourceExistsException:
        client.update_secret(
            SecretId='alpaca-paper-trading',
            SecretString=json.dumps(secret_dict)
        )
        print("✓ Secret updated")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

if __name__ == '__main__':
    sys.exit(0 if store_alpaca_credentials() else 1)
