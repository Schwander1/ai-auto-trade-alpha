#!/usr/bin/env python3
"""
Alpine Sync Verification Script
Verifies that signals are being synced from Argo to Alpine backend in production

Usage:
    python scripts/verify_alpine_sync.py [--hours 24] [--verbose]
"""
import sys
import argparse
import sqlite3
import httpx
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from argo.core.alpine_sync import AlpineSyncService
    from argo.core.config_loader import ConfigLoader
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("   Make sure you're running from the argo directory")
    sys.exit(1)

def get_argo_signals(hours: int = 24) -> List[Dict]:
    """Get signals from Argo database"""
    db_path = Path(__file__).parent.parent / "data" / "signals.db"

    if not db_path.exists():
        print(f"❌ Argo signal database not found: {db_path}")
        return []

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

    cursor.execute("""
        SELECT signal_id, symbol, action, entry_price, confidence,
               sha256, timestamp, created_at
        FROM signals
        WHERE created_at >= ?
        ORDER BY created_at DESC
        LIMIT 100
    """, (cutoff_time,))

    signals = []
    for row in cursor.fetchall():
        signals.append({
            'signal_id': row['signal_id'],
            'symbol': row['symbol'],
            'action': row['action'],
            'entry_price': row['entry_price'],
            'confidence': row['confidence'],
            'sha256': row['sha256'],
            'timestamp': row['timestamp'],
            'created_at': row['created_at']
        })

    conn.close()
    return signals

async def check_alpine_signal(api_url: str, api_key: str, signal_hash: str) -> Optional[Dict]:
    """Check if signal exists in Alpine backend"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{api_url}/api/v1/external-signals/verify/{signal_hash}",
                headers={"X-API-Key": api_key}
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                print(f"⚠️  Alpine API returned {response.status_code}")
                return None
    except Exception as e:
        print(f"⚠️  Error checking Alpine: {e}")
        return None

async def verify_sync_status(hours: int = 24, verbose: bool = False) -> Dict:
    """Verify sync status between Argo and Alpine"""
    print("=" * 70)
    print("🔍 ALPINE SYNC VERIFICATION")
    print("=" * 70)
    print(f"⏰ Checking signals from last {hours} hours")
    print()

    # Get Argo signals
    print("📊 Fetching signals from Argo database...")
    argo_signals = get_argo_signals(hours)

    if not argo_signals:
        print("❌ No signals found in Argo database")
        return {
            'total_signals': 0,
            'synced': 0,
            'missing': 0,
            'sync_rate': 0.0
        }

    print(f"✅ Found {len(argo_signals)} signals in Argo")
    print()

    # Get Alpine configuration
    try:
        config, _ = ConfigLoader.load_config()
        alpine_url = os.getenv('ALPINE_API_URL') or config.get('alpine', {}).get('api_url', 'http://91.98.153.49:8001')
        api_key = os.getenv('ARGO_API_KEY') or config.get('alpine', {}).get('api_key', '')

        if not api_key:
            # Try secrets manager
            try:
                from argo.utils.secrets_manager import get_secret
                api_key = get_secret('argo-api-key', service='argo') or ''
            except:
                pass
    except Exception as e:
        print(f"⚠️  Error loading config: {e}")
        alpine_url = 'http://91.98.153.49:8001'
        api_key = os.getenv('ARGO_API_KEY', '')

    if not api_key:
        print("❌ API key not found. Set ARGO_API_KEY environment variable or configure in config.json")
        return {
            'total_signals': len(argo_signals),
            'synced': 0,
            'missing': len(argo_signals),
            'sync_rate': 0.0
        }

    print(f"🌐 Alpine URL: {alpine_url}")
    print(f"🔑 API Key: {'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else '***'}")
    print()

    # Check health first
    print("🏥 Checking Alpine backend health...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            health_response = await client.get(f"{alpine_url}/api/v1/external-signals/sync/health")
            if health_response.status_code == 200:
                print("✅ Alpine backend is healthy")
            else:
                print(f"⚠️  Alpine backend health check returned {health_response.status_code}")
    except Exception as e:
        print(f"❌ Alpine backend health check failed: {e}")
        print("   Cannot verify sync status")
        return {
            'total_signals': len(argo_signals),
            'synced': 0,
            'missing': len(argo_signals),
            'sync_rate': 0.0,
            'error': 'Alpine backend unreachable'
        }

    print()
    print("🔄 Verifying signal sync status...")

    # Check each signal (sample first 20 for speed)
    check_count = min(20, len(argo_signals))
    synced_count = 0
    missing_signals = []

    import asyncio
    for i, signal in enumerate(argo_signals[:check_count]):
        if verbose:
            print(f"   Checking {i+1}/{check_count}: {signal['symbol']} {signal['action']} (hash: {signal['sha256'][:8]}...)")

        result = await check_alpine_signal(alpine_url, api_key, signal['sha256'])
        if result:
            synced_count += 1
        else:
            missing_signals.append(signal)

    # Calculate sync rate
    sync_rate = (synced_count / check_count * 100) if check_count > 0 else 0.0

    print()
    print("=" * 70)
    print("📊 VERIFICATION RESULTS")
    print("=" * 70)
    print(f"Total signals checked: {check_count}")
    print(f"✅ Synced: {synced_count}")
    print(f"❌ Missing: {len(missing_signals)}")
    print(f"📈 Sync rate: {sync_rate:.1f}%")
    print()

    if missing_signals and verbose:
        print("Missing signals:")
        for signal in missing_signals[:5]:
            print(f"  - {signal['symbol']} {signal['action']} @ ${signal['entry_price']:.2f} ({signal['confidence']:.1f}%) - {signal['created_at']}")
        if len(missing_signals) > 5:
            print(f"  ... and {len(missing_signals) - 5} more")
        print()

    # Recommendations
    if sync_rate < 90:
        print("⚠️  WARNING: Sync rate is below 90%")
        print("   Recommendations:")
        print("   1. Check Alpine sync service logs: tail -f argo/logs/service_*.log")
        print("   2. Verify API key is correct")
        print("   3. Check network connectivity to Alpine backend")
        print("   4. Verify Alpine backend is running and accessible")
    elif sync_rate == 100:
        print("✅ Perfect sync rate! All signals are being synced successfully.")
    else:
        print("✅ Good sync rate. Minor issues may exist.")

    return {
        'total_signals': check_count,
        'synced': synced_count,
        'missing': len(missing_signals),
        'sync_rate': sync_rate,
        'missing_signals': missing_signals[:10] if verbose else []
    }

def main():
    parser = argparse.ArgumentParser(description='Verify Alpine sync status')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back (default: 24)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    import asyncio
    result = asyncio.run(verify_sync_status(args.hours, args.verbose))

    # Exit with error code if sync rate is too low
    if result.get('sync_rate', 0) < 90:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
