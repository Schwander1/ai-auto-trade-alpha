#!/usr/bin/env python3
"""
Signal Archive Utility
Archives old signals to a separate archive database to keep main database small
"""
import sqlite3
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

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

def create_archive_database(archive_path: Path):
    """Create archive database with same schema"""
    conn = sqlite3.connect(str(archive_path))
    cursor = conn.cursor()
    
    # Create signals table with same schema
    cursor.execute('''CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        signal_id TEXT UNIQUE NOT NULL,
        symbol TEXT NOT NULL,
        action TEXT NOT NULL,
        entry_price REAL NOT NULL,
        target_price REAL NOT NULL,
        stop_price REAL NOT NULL,
        confidence REAL NOT NULL,
        strategy TEXT NOT NULL,
        asset_type TEXT NOT NULL,
        data_source TEXT DEFAULT 'weighted_consensus',
        timestamp TEXT NOT NULL,
        outcome TEXT DEFAULT NULL,
        exit_price REAL DEFAULT NULL,
        profit_loss_pct REAL DEFAULT NULL,
        sha256 TEXT NOT NULL,
        order_id TEXT DEFAULT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        exit_timestamp TEXT DEFAULT NULL
    )''')
    
    # Create indexes
    from argo.core.database_indexes import DatabaseIndexes
    DatabaseIndexes.create_all_indexes(cursor)
    
    conn.commit()
    conn.close()

def archive_signals(
    db_path: Path,
    archive_path: Path,
    months: int = 12,
    dry_run: bool = False
) -> tuple[int, int]:
    """
    Archive signals older than specified months
    
    Returns:
        (archived_count, remaining_count)
    """
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)
    
    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d')
    
    print(f"📦 Archiving signals older than {cutoff_str} ({months} months)")
    
    # Connect to main database
    main_conn = sqlite3.connect(str(db_path))
    main_cursor = main_conn.cursor()
    
    # Count signals to archive
    main_cursor.execute('''
        SELECT COUNT(*) FROM signals
        WHERE DATE(created_at) < ?
    ''', (cutoff_str,))
    to_archive = main_cursor.fetchone()[0]
    
    # Count remaining signals
    main_cursor.execute('''
        SELECT COUNT(*) FROM signals
        WHERE DATE(created_at) >= ?
    ''', (cutoff_str,))
    remaining = main_cursor.fetchone()[0]
    
    print(f"  Signals to archive: {to_archive:,}")
    print(f"  Signals to keep: {remaining:,}")
    
    if to_archive == 0:
        print("✅ No signals to archive")
        main_conn.close()
        return (0, remaining)
    
    if dry_run:
        print("🔍 DRY RUN - No changes made")
        main_conn.close()
        return (to_archive, remaining)
    
    # Create archive database if it doesn't exist
    if not archive_path.exists():
        print(f"📁 Creating archive database: {archive_path}")
        create_archive_database(archive_path)
    
    # Connect to archive database
    archive_conn = sqlite3.connect(str(archive_path))
    archive_cursor = archive_conn.cursor()
    
    try:
        # Copy signals to archive
        print("📤 Copying signals to archive...")
        main_cursor.execute('''
            SELECT 
                signal_id, symbol, action, entry_price, target_price, stop_price,
                confidence, strategy, asset_type, data_source, timestamp,
                outcome, exit_price, profit_loss_pct, sha256, order_id,
                created_at, exit_timestamp
            FROM signals
            WHERE DATE(created_at) < ?
        ''', (cutoff_str,))
        
        signals = main_cursor.fetchall()
        
        archive_cursor.executemany('''
            INSERT OR IGNORE INTO signals (
                signal_id, symbol, action, entry_price, target_price, stop_price,
                confidence, strategy, asset_type, data_source, timestamp,
                outcome, exit_price, profit_loss_pct, sha256, order_id,
                created_at, exit_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', signals)
        
        archive_conn.commit()
        archived_count = archive_cursor.rowcount
        
        # Delete archived signals from main database
        print("🗑️  Removing archived signals from main database...")
        main_cursor.execute('''
            DELETE FROM signals
            WHERE DATE(created_at) < ?
        ''', (cutoff_str,))
        
        main_conn.commit()
        deleted_count = main_cursor.rowcount
        
        print(f"✅ Archived {archived_count:,} signals")
        print(f"✅ Deleted {deleted_count:,} signals from main database")
        
        # Vacuum database to reclaim space
        print("🧹 Vacuuming main database...")
        main_cursor.execute('VACUUM')
        main_conn.commit()
        
        # Get new database size
        new_size = db_path.stat().st_size / (1024 * 1024)
        print(f"✅ Database size after vacuum: {new_size:.2f} MB")
        
        archive_conn.close()
        main_conn.close()
        
        return (archived_count, remaining - deleted_count)
        
    except Exception as e:
        print(f"❌ Error during archiving: {e}")
        archive_conn.rollback()
        main_conn.rollback()
        archive_conn.close()
        main_conn.close()
        raise

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Archive old signals to separate database')
    parser.add_argument(
        '--months',
        type=int,
        default=12,
        help='Archive signals older than this many months (default: 12)'
    )
    parser.add_argument(
        '--archive-path',
        type=str,
        help='Path to archive database (default: signals_archive.db in same directory)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be archived without making changes'
    )
    
    args = parser.parse_args()
    
    db_path = get_db_path()
    
    if args.archive_path:
        archive_path = Path(args.archive_path)
    else:
        archive_path = db_path.parent / "signals_archive.db"
    
    print("=" * 60)
    print("Signal Archive Utility")
    print("=" * 60)
    print(f"Main Database: {db_path}")
    print(f"Archive Database: {archive_path}")
    print()
    
    try:
        archived, remaining = archive_signals(
            db_path,
            archive_path,
            months=args.months,
            dry_run=args.dry_run
        )
        
        print()
        print("=" * 60)
        print(f"✅ Archive complete: {archived:,} archived, {remaining:,} remaining")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Archive failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

