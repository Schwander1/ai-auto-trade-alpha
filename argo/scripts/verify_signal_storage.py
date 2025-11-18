#!/usr/bin/env python3
"""
Comprehensive Signal Storage Verification Script
Verifies signal storage is working correctly and all components are healthy
"""
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_database():
    """Check database exists and is accessible"""
    print("1️⃣  Database Check")
    print("-" * 60)
    
    try:
        from argo.core.signal_tracker import SignalTracker
        tracker = SignalTracker()
        
        db_path = tracker.db_file
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"  ✅ Database exists: {db_path}")
            print(f"  ✅ Database size: {size_mb:.2f} MB")
        else:
            print(f"  ⚠️  Database file not found: {db_path}")
            return False
        
        # Check if we can query
        try:
            stats = tracker.get_stats()
            print(f"  ✅ Database accessible")
            print(f"  ✅ Total signals: {stats.get('total_signals', 0):,}")
            return True
        except Exception as e:
            print(f"  ❌ Database query failed: {e}")
            return False
            
    except Exception as e:
        print(f"  ❌ Database check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_signal_tracker():
    """Check SignalTracker functionality"""
    print("\n2️⃣  Signal Tracker Check")
    print("-" * 60)
    
    try:
        from argo.core.signal_tracker import SignalTracker
        tracker = SignalTracker()
        
        # Check methods exist
        methods = [
            'log_signal',
            'log_signal_async',
            'flush_pending',
            'flush_pending_async',
            '_periodic_flush_loop',
            '_ensure_periodic_flush'
        ]
        
        for method in methods:
            if hasattr(tracker, method):
                print(f"  ✅ Method exists: {method}")
            else:
                print(f"  ❌ Method missing: {method}")
                return False
        
        # Check configuration
        print(f"  ✅ Batch size: {tracker._batch_size}")
        print(f"  ✅ Batch timeout: {tracker._batch_timeout}s")
        print(f"  ✅ Periodic flush interval: {tracker._periodic_flush_interval}s")
        
        return True
        
    except Exception as e:
        print(f"  ❌ SignalTracker check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_alpine_sync():
    """Check Alpine sync service"""
    print("\n3️⃣  Alpine Sync Check")
    print("-" * 60)
    
    try:
        from argo.core.alpine_sync import get_alpine_sync_service
        sync_service = get_alpine_sync_service()
        
        if sync_service._sync_enabled:
            print(f"  ✅ Alpine sync enabled")
            print(f"  ✅ Alpine URL: {sync_service.alpine_url}")
            print(f"  ✅ API key configured: {'Yes' if sync_service.api_key else 'No'}")
        else:
            print(f"  ⚠️  Alpine sync disabled (missing configuration)")
            print(f"     Set ALPINE_API_URL and ARGO_API_KEY to enable")
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Alpine sync check failed: {e}")
        return False

async def check_signal_generation_service():
    """Check signal generation service"""
    print("\n4️⃣  Signal Generation Service Check")
    print("-" * 60)
    
    try:
        from argo.core.signal_generation_service import SignalGenerationService
        service = SignalGenerationService()
        
        # Check components
        components = {
            'tracker': service.tracker,
            'alpine_sync': service.alpine_sync,
            'consensus_engine': service.consensus_engine,
        }
        
        for name, component in components.items():
            if component:
                print(f"  ✅ {name}: initialized")
            else:
                print(f"  ⚠️  {name}: not initialized")
        
        # Check methods
        if hasattr(service, '_sync_signal_to_alpine'):
            print(f"  ✅ _sync_signal_to_alpine: exists")
        else:
            print(f"  ❌ _sync_signal_to_alpine: missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Signal generation service check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_indexes():
    """Check database indexes"""
    print("\n5️⃣  Database Indexes Check")
    print("-" * 60)
    
    try:
        from argo.core.signal_tracker import SignalTracker
        import sqlite3
        
        tracker = SignalTracker()
        conn = sqlite3.connect(str(tracker.db_file))
        cursor = conn.cursor()
        
        # Get all indexes
        cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type='index' AND tbl_name='signals'
        ''')
        indexes = [row[0] for row in cursor.fetchall()]
        
        # Expected indexes
        expected_indexes = [
            'idx_symbol',
            'idx_confidence',
            'idx_created_at',
            'idx_symbol_confidence',
            'idx_created_outcome',
            'idx_confidence_outcome',
        ]
        
        print(f"  ✅ Found {len(indexes)} indexes")
        
        missing = [idx for idx in expected_indexes if idx not in indexes]
        if missing:
            print(f"  ⚠️  Missing indexes: {', '.join(missing)}")
        else:
            print(f"  ✅ All expected indexes present")
        
        conn.close()
        return len(missing) == 0
        
    except Exception as e:
        print(f"  ❌ Index check failed: {e}")
        return False

def check_recent_signals():
    """Check for recent signal activity"""
    print("\n6️⃣  Recent Signal Activity Check")
    print("-" * 60)
    
    try:
        from argo.core.signal_tracker import SignalTracker
        import sqlite3
        from datetime import datetime, timedelta
        
        tracker = SignalTracker()
        conn = sqlite3.connect(str(tracker.db_file))
        cursor = conn.cursor()
        
        # Check signals in last hour
        cursor.execute('''
            SELECT COUNT(*) FROM signals
            WHERE created_at >= datetime('now', '-1 hour')
        ''')
        last_hour = cursor.fetchone()[0]
        
        # Check signals in last 24 hours
        cursor.execute('''
            SELECT COUNT(*) FROM signals
            WHERE created_at >= datetime('now', '-24 hours')
        ''')
        last_24h = cursor.fetchone()[0]
        
        # Get latest signal
        cursor.execute('''
            SELECT created_at, symbol, action, confidence
            FROM signals
            ORDER BY created_at DESC
            LIMIT 1
        ''')
        latest = cursor.fetchone()
        
        print(f"  Signals (last hour): {last_hour}")
        print(f"  Signals (last 24h): {last_24h}")
        
        if latest:
            print(f"  Latest signal: {latest[1]} {latest[2]} @ {latest[3]}% ({latest[0]})")
            
            # Check if signal is recent (within last hour)
            try:
                latest_time = datetime.fromisoformat(latest[0].replace('Z', '+00:00'))
                if latest_time.tzinfo is None:
                    latest_time = datetime.strptime(latest[0], '%Y-%m-%d %H:%M:%S')
                
                age = datetime.now() - latest_time.replace(tzinfo=None)
                if age < timedelta(hours=1):
                    print(f"  ✅ Recent signal activity detected")
                else:
                    print(f"  ⚠️  No recent signals (latest is {age})")
            except:
                pass
        else:
            print(f"  ⚠️  No signals found in database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Recent activity check failed: {e}")
        return False

async def main():
    """Main verification function"""
    print("=" * 60)
    print("Signal Storage Verification")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    # Run checks
    results.append(("Database", check_database()))
    results.append(("Signal Tracker", check_signal_tracker()))
    results.append(("Alpine Sync", check_alpine_sync()))
    results.append(("Signal Generation Service", await check_signal_generation_service()))
    results.append(("Database Indexes", check_indexes()))
    results.append(("Recent Activity", check_recent_signals()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ All checks passed!")
        return 0
    else:
        print("⚠️  Some checks failed - review output above")
        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

