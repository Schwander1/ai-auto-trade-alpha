#!/usr/bin/env python3
"""
Signal Storage Monitoring Script
Monitors signal storage health, database size, and performance metrics
"""
import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def get_db_path() -> Path:
    """Get database path"""
    # Check for production paths first
    if os.path.exists("/root/argo-production-prop-firm"):
        return Path("/root/argo-production-prop-firm") / "data" / "signals.db"
    elif os.path.exists("/root/argo-production-green"):
        return Path("/root/argo-production-green") / "data" / "signals.db"
    elif os.path.exists("/root/argo-production"):
        return Path("/root/argo-production") / "data" / "signals.db"
    else:
        # Development path
        return Path(__file__).parent.parent.parent / "data" / "signals.db"

def get_database_stats(db_path: Path) -> Dict[str, Any]:
    """Get database statistics"""
    if not db_path.exists():
        return {"error": "Database file does not exist"}
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    stats = {}
    
    # Database size
    db_size = db_path.stat().st_size
    stats['database_size_bytes'] = db_size
    stats['database_size_mb'] = round(db_size / (1024 * 1024), 2)
    
    # Total signals
    cursor.execute('SELECT COUNT(*) FROM signals')
    stats['total_signals'] = cursor.fetchone()[0]
    
    # Signals by date
    cursor.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM signals
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        LIMIT 7
    ''')
    stats['signals_by_date'] = dict(cursor.fetchall())
    
    # Signals by symbol
    cursor.execute('''
        SELECT symbol, COUNT(*) as count
        FROM signals
        GROUP BY symbol
        ORDER BY count DESC
    ''')
    stats['signals_by_symbol'] = dict(cursor.fetchall())
    
    # Signals by outcome
    cursor.execute('''
        SELECT 
            CASE WHEN outcome IS NULL THEN 'pending' ELSE outcome END as status,
            COUNT(*) as count
        FROM signals
        GROUP BY status
    ''')
    stats['signals_by_outcome'] = dict(cursor.fetchall())
    
    # Average confidence
    cursor.execute('SELECT AVG(confidence) FROM signals')
    avg_confidence = cursor.fetchone()[0]
    stats['avg_confidence'] = round(avg_confidence, 2) if avg_confidence else 0
    
    # Latest signal
    cursor.execute('''
        SELECT created_at, symbol, action, confidence
        FROM signals
        ORDER BY created_at DESC
        LIMIT 1
    ''')
    latest = cursor.fetchone()
    if latest:
        stats['latest_signal'] = {
            'created_at': latest[0],
            'symbol': latest[1],
            'action': latest[2],
            'confidence': latest[3]
        }
    
    # Signals in last 24 hours
    cursor.execute('''
        SELECT COUNT(*) FROM signals
        WHERE created_at >= datetime('now', '-24 hours')
    ''')
    stats['signals_last_24h'] = cursor.fetchone()[0]
    
    # Signals in last hour
    cursor.execute('''
        SELECT COUNT(*) FROM signals
        WHERE created_at >= datetime('now', '-1 hour')
    ''')
    stats['signals_last_hour'] = cursor.fetchone()[0]
    
    # Check for WAL file
    wal_path = db_path.parent / f"{db_path.name}-wal"
    shm_path = db_path.parent / f"{db_path.name}-shm"
    stats['wal_file_size'] = wal_path.stat().st_size if wal_path.exists() else 0
    stats['shm_file_size'] = shm_path.stat().st_size if shm_path.exists() else 0
    
    # Index information
    cursor.execute('''
        SELECT name, sql FROM sqlite_master
        WHERE type='index' AND tbl_name='signals'
    ''')
    indexes = cursor.fetchall()
    stats['index_count'] = len(indexes)
    stats['indexes'] = [name for name, _ in indexes]
    
    conn.close()
    
    return stats

def check_database_health(stats: Dict[str, Any]) -> Dict[str, Any]:
    """Check database health and return warnings"""
    warnings = []
    errors = []
    
    # Check database size
    if stats.get('database_size_mb', 0) > 1000:  # > 1GB
        warnings.append(f"Database size is large: {stats['database_size_mb']} MB - consider archiving old signals")
    
    # Check WAL file size
    if stats.get('wal_file_size', 0) > 100 * 1024 * 1024:  # > 100MB
        warnings.append(f"WAL file is large: {stats['wal_file_size'] / (1024*1024):.2f} MB - may need checkpoint")
    
    # Check signal generation rate
    signals_last_hour = stats.get('signals_last_hour', 0)
    if signals_last_hour == 0:
        warnings.append("No signals generated in the last hour - check signal generation service")
    elif signals_last_hour < 10:
        warnings.append(f"Low signal generation rate: {signals_last_hour} signals/hour")
    
    # Check for old signals
    if stats.get('total_signals', 0) > 100000:
        warnings.append(f"Large number of signals: {stats['total_signals']} - consider archiving old signals")
    
    # Check indexes
    if stats.get('index_count', 0) < 10:
        warnings.append(f"Low index count: {stats['index_count']} - ensure all indexes are created")
    
    return {
        'warnings': warnings,
        'errors': errors,
        'healthy': len(errors) == 0
    }

def print_report(stats: Dict[str, Any], health: Dict[str, Any]):
    """Print monitoring report"""
    print("=" * 60)
    print("Signal Storage Monitoring Report")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if 'error' in stats:
        print(f"❌ Error: {stats['error']}")
        return
    
    # Database Info
    print("📊 Database Information")
    print("-" * 60)
    print(f"  Database Size: {stats.get('database_size_mb', 0)} MB")
    print(f"  Total Signals: {stats.get('total_signals', 0):,}")
    print(f"  Indexes: {stats.get('index_count', 0)}")
    print(f"  WAL File Size: {stats.get('wal_file_size', 0) / (1024*1024):.2f} MB")
    print()
    
    # Recent Activity
    print("📈 Recent Activity")
    print("-" * 60)
    print(f"  Signals (last hour): {stats.get('signals_last_hour', 0)}")
    print(f"  Signals (last 24h): {stats.get('signals_last_24h', 0)}")
    if stats.get('latest_signal'):
        latest = stats['latest_signal']
        print(f"  Latest Signal: {latest['symbol']} {latest['action']} @ {latest['confidence']}% ({latest['created_at']})")
    print()
    
    # Statistics
    print("📊 Statistics")
    print("-" * 60)
    print(f"  Average Confidence: {stats.get('avg_confidence', 0)}%")
    print()
    
    # Signals by Symbol
    if stats.get('signals_by_symbol'):
        print("  Signals by Symbol:")
        for symbol, count in list(stats['signals_by_symbol'].items())[:10]:
            print(f"    {symbol}: {count:,}")
        print()
    
    # Signals by Outcome
    if stats.get('signals_by_outcome'):
        print("  Signals by Outcome:")
        for outcome, count in stats['signals_by_outcome'].items():
            print(f"    {outcome}: {count:,}")
        print()
    
    # Health Status
    print("🏥 Health Status")
    print("-" * 60)
    if health['healthy']:
        print("  ✅ Database is healthy")
    else:
        print("  ❌ Database has errors")
        for error in health['errors']:
            print(f"    ❌ {error}")
    
    if health['warnings']:
        print("  ⚠️  Warnings:")
        for warning in health['warnings']:
            print(f"    ⚠️  {warning}")
    else:
        print("  ✅ No warnings")
    
    print()
    print("=" * 60)

def main():
    """Main function"""
    db_path = get_db_path()
    
    print(f"Monitoring signal storage: {db_path}")
    print()
    
    stats = get_database_stats(db_path)
    health = check_database_health(stats)
    
    print_report(stats, health)
    
    # Exit with error code if unhealthy
    if not health['healthy']:
        sys.exit(1)
    elif health['warnings']:
        sys.exit(2)  # Warning exit code
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()

