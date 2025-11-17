#!/usr/bin/env python3
"""
Test Alpine Sync Service
Tests signal sync from Argo to Alpine backend
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add argo to path
workspace_root = Path(__file__).parent.parent.parent
argo_path = workspace_root / "argo"
sys.path.insert(0, str(argo_path))

from argo.core.alpine_sync import get_alpine_sync_service

async def test_alpine_sync():
    """Test Alpine sync service"""
    print("🧪 Testing Alpine Sync Service")
    print("=" * 50)
    
    # Get sync service
    sync_service = get_alpine_sync_service()
    
    # Check if enabled
    if not sync_service._sync_enabled:
        print("⚠️  Alpine sync is disabled (missing configuration)")
        print("\nRequired configuration:")
        print("  - ALPINE_API_URL (or in config.json)")
        print("  - ARGO_API_KEY (or in config.json)")
        return False
    
    print(f"✅ Sync service initialized")
    print(f"   Alpine URL: {sync_service.alpine_url}")
    print(f"   Endpoint: {sync_service.endpoint}")
    print()
    
    # Test health check
    print("🏥 Testing Alpine backend health...")
    health_ok = await sync_service.check_health()
    if health_ok:
        print("✅ Alpine backend is reachable")
    else:
        print("❌ Alpine backend health check failed")
        print("   Check that Alpine backend is running and reachable")
        return False
    print()
    
    # Create test signal
    test_signal = {
        'signal_id': f'TEST-{int(datetime.utcnow().timestamp())}',
        'symbol': 'AAPL',
        'action': 'BUY',
        'entry_price': 175.50,
        'target_price': 184.25,
        'stop_price': 171.00,
        'confidence': 95.5,
        'strategy': 'weighted_consensus_v6',
        'asset_type': 'stock',
        'data_source': 'weighted_consensus',
        'timestamp': datetime.utcnow().isoformat(),
        'sha256': 'test_hash_1234567890abcdef',
        'reasoning': 'Test signal for Alpine sync verification'
    }
    
    # Calculate proper hash
    import json
    import hashlib
    hash_fields = {
        'signal_id': test_signal['signal_id'],
        'symbol': test_signal['symbol'],
        'action': test_signal['action'],
        'entry_price': test_signal['entry_price'],
        'target_price': test_signal['target_price'],
        'stop_price': test_signal['stop_price'],
        'confidence': test_signal['confidence'],
        'strategy': test_signal['strategy'],
        'timestamp': test_signal['timestamp']
    }
    hash_string = json.dumps(hash_fields, sort_keys=True, default=str)
    test_signal['sha256'] = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
    
    # Test sync
    print("📤 Testing signal sync...")
    print(f"   Signal ID: {test_signal['signal_id']}")
    print(f"   Symbol: {test_signal['symbol']}")
    print(f"   Action: {test_signal['action']}")
    print()
    
    success = await sync_service.sync_signal(test_signal)
    
    if success:
        print("✅ Signal synced successfully!")
        print()
        print("📊 Verification:")
        print("   1. Check Alpine backend logs for confirmation")
        print("   2. Query Alpine database:")
        print(f"      SELECT * FROM signals WHERE verification_hash = '{test_signal['sha256'][:16]}...';")
        return True
    else:
        print("❌ Signal sync failed")
        print("   Check logs for error details")
        return False

async def main():
    """Main test function"""
    try:
        success = await test_alpine_sync()
        
        # Cleanup
        sync_service = get_alpine_sync_service()
        await sync_service.close()
        
        if success:
            print()
            print("=" * 50)
            print("✅ All tests passed!")
            sys.exit(0)
        else:
            print()
            print("=" * 50)
            print("❌ Tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())

