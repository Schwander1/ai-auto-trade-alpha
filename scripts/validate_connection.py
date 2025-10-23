#!/usr/bin/env python3
"""
Day 1 Checkpoint: Validate Alpaca Paper Trading connectivity
Run: python scripts/validate_connection.py
"""

import sys
import json
from config.alpaca_config import AlpacaConfig
from services.alpaca_client import AlpacaClient

def validate_alpaca():
    """Test full Alpaca connection pipeline"""

    print("=" * 60)
    print("CHECKPOINT: Alpaca Paper Trading Connection Validation")
    print("=" * 60)

    print("\n[1/4] Loading credentials from AWS Secrets Manager...")
    try:
        client = AlpacaClient()
        print("✓ Credentials loaded")
    except Exception as e:
        print(f"✗ Failed to load credentials: {e}")
        return False

    print("\n[2/4] Connecting to Alpaca Paper Trading API...")
    try:
        if not client.connect():
            print("✗ Connection failed")
            return False
        print("✓ Connected to API")
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

    print("\n[3/4] Retrieving account details...")
    try:
        account = client.get_account_details()
        print("✓ Account details retrieved:")
        print(json.dumps(account, indent=2))
    except Exception as e:
        print(f"✗ Failed to fetch account: {e}")
        return False

    print("\n[4/4] Checking positions...")
    try:
        positions = client.list_positions()
        print(f"✓ {len(positions)} position(s) found")
        if positions:
            print(json.dumps(positions, indent=2))
        else:
            print("  (No open positions)")
    except Exception as e:
        print(f"✗ Failed to fetch positions: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ ALL CHECKPOINTS PASSED - Ready for Day 2")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = validate_alpaca()
    sys.exit(0 if success else 1)
