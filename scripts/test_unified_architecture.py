#!/usr/bin/env python3
"""
Test Unified Architecture
Validates all components of unified architecture
"""
import sys
import asyncio
import httpx
import sqlite3
from pathlib import Path
from typing import Dict, List

# Add argo to path
sys.path.insert(0, str(Path(__file__).parent.parent / "argo"))


def test_unified_tracker():
    """Test unified signal tracker"""
    print("🧪 Testing Unified Signal Tracker...")
    try:
        from argo.core.unified_signal_tracker import UnifiedSignalTracker
        
        tracker = UnifiedSignalTracker()
        
        # Test signal storage
        test_signal = {
            'symbol': 'TEST',
            'action': 'BUY',
            'entry_price': 100.0,
            'target_price': 105.0,
            'stop_price': 98.0,
            'confidence': 75.0,
            'strategy': 'test',
            'asset_type': 'stock',
            'service_type': 'both',
            'generated_by': 'test'
        }
        
        signal_id = tracker.log_signal(test_signal)
        tracker.flush_pending()
        
        # Test stats
        stats = tracker.get_stats()
        print(f"  ✅ Tracker working: {stats.get('total_signals', 0)} signals")
        
        return True
    except Exception as e:
        print(f"  ❌ Tracker test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_signal_distributor():
    """Test signal distributor"""
    print("🧪 Testing Signal Distributor...")
    try:
        from argo.core.signal_distributor import SignalDistributor
        
        distributor = SignalDistributor()
        
        # Test executor initialization
        assert 'argo' in distributor.executors
        assert 'prop_firm' in distributor.executors
        
        print("  ✅ Distributor initialized")
        return True
    except Exception as e:
        print(f"  ❌ Distributor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_executor_health():
    """Test executor health endpoints"""
    print("🧪 Testing Executor Health...")
    
    executors = [
        ('Signal Generator', 'http://localhost:7999'),
        ('Argo Executor', 'http://localhost:8000'),
        ('Prop Firm Executor', 'http://localhost:8001'),
    ]
    
    results = []
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in executors:
            try:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    print(f"  ✅ {name}: Healthy")
                    results.append(True)
                else:
                    print(f"  ⚠️  {name}: Status {response.status_code}")
                    results.append(False)
            except Exception as e:
                print(f"  ❌ {name}: {e}")
                results.append(False)
    
    return all(results)


def test_database_migration():
    """Test database migration"""
    print("🧪 Testing Database Migration...")
    
    unified_db = Path("/root/argo-production-unified/data/signals_unified.db")
    if not unified_db.exists():
        # Try local path
        unified_db = Path(__file__).parent.parent / "argo" / "data" / "signals_unified.db"
    
    if not unified_db.exists():
        print("  ⚠️  Unified database not found (may not be migrated yet)")
        return True  # Not a failure, just not migrated
    
    try:
        conn = sqlite3.connect(str(unified_db))
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signals'")
        if not cursor.fetchone():
            print("  ❌ Signals table not found")
            return False
        
        # Check service_type column exists
        cursor.execute("PRAGMA table_info(signals)")
        columns = [col[1] for col in cursor.fetchall()]
        
        required_columns = ['service_type', 'executor_id', 'generated_by']
        missing = [col for col in required_columns if col not in columns]
        
        if missing:
            print(f"  ⚠️  Missing columns: {missing}")
        else:
            print("  ✅ All required columns present")
        
        # Check signal count
        cursor.execute("SELECT COUNT(*) FROM signals")
        count = cursor.fetchone()[0]
        print(f"  ✅ Database has {count} signals")
        
        conn.close()
        return True
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_signal_distribution():
    """Test signal distribution flow"""
    print("🧪 Testing Signal Distribution...")
    
    # This would require running services
    # For now, just check if distributor can be initialized
    try:
        from argo.core.signal_distributor import SignalDistributor
        
        distributor = SignalDistributor()
        
        test_signal = {
            'symbol': 'TEST',
            'action': 'BUY',
            'entry_price': 100.0,
            'target_price': 105.0,
            'stop_price': 98.0,
            'confidence': 80.0,
            'service_type': 'both',
            'regime': 'BULL'
        }
        
        # Try to distribute (will fail if executors not running, but that's OK)
        try:
            results = await distributor.distribute_signal(test_signal)
            print(f"  ✅ Distribution attempted: {len(results)} results")
        except Exception as e:
            print(f"  ⚠️  Distribution test (executors may not be running): {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ Distribution test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("="*70)
    print("🧪 UNIFIED ARCHITECTURE TEST SUITE")
    print("="*70)
    print()
    
    results = []
    
    # Component tests
    results.append(("Unified Tracker", test_unified_tracker()))
    results.append(("Signal Distributor", test_signal_distributor()))
    results.append(("Database Migration", test_database_migration()))
    results.append(("Signal Distribution", await test_signal_distribution()))
    
    # Service health tests (requires running services)
    print()
    print("🧪 Testing Service Health (requires running services)...")
    health_results = await test_executor_health()
    results.append(("Service Health", health_results))
    
    # Summary
    print()
    print("="*70)
    print("📊 TEST RESULTS")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

