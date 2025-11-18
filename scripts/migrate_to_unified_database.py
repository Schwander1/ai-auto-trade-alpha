#!/usr/bin/env python3
"""
Database Migration Script
Migrates all existing signals to unified database
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from typing import Tuple

# Add argo to path
sys.path.insert(0, str(Path(__file__).parent.parent / "argo"))

def get_column_names(cursor, table_name: str) -> list:
    """Get column names from table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [col[1] for col in cursor.fetchall()]

def migrate_database(source_db: Path, unified_db: Path, service_type: str) -> Tuple[int, int]:
    """Migrate signals from source to unified database"""
    if not source_db.exists():
        print(f"⚠️  Source database not found: {source_db}")
        return 0, 0
    
    print(f"\n📦 Migrating {service_type} signals from {source_db.name}...")
    
    try:
        source_conn = sqlite3.connect(str(source_db))
        unified_conn = sqlite3.connect(str(unified_db))
        
        source_cursor = source_conn.cursor()
        unified_cursor = unified_conn.cursor()
        
        # Get column names
        source_columns = get_column_names(source_cursor, 'signals')
        
        # Get all signals
        source_cursor.execute("SELECT * FROM signals")
        signals = source_cursor.fetchall()
        
        migrated = 0
        skipped = 0
        errors = 0
        
        for signal_row in signals:
            try:
                signal_dict = dict(zip(source_columns, signal_row))
                
                # Check if signal already exists (by signal_id)
                unified_cursor.execute(
                    "SELECT id FROM signals WHERE signal_id = ?",
                    (signal_dict.get('signal_id'),)
                )
                if unified_cursor.fetchone():
                    skipped += 1
                    continue
                
                # Insert with service type
                unified_cursor.execute('''
                    INSERT INTO signals (
                        signal_id, symbol, action, entry_price, target_price, stop_price,
                        confidence, strategy, asset_type, data_source, timestamp,
                        outcome, exit_price, profit_loss_pct, sha256, order_id, created_at,
                        service_type, generated_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    signal_dict.get('signal_id'),
                    signal_dict.get('symbol'),
                    signal_dict.get('action'),
                    signal_dict.get('entry_price'),
                    signal_dict.get('target_price'),
                    signal_dict.get('stop_price'),
                    signal_dict.get('confidence'),
                    signal_dict.get('strategy', 'weighted_consensus_v6'),
                    signal_dict.get('asset_type', 'stock'),
                    signal_dict.get('data_source', 'weighted_consensus'),
                    signal_dict.get('timestamp'),
                    signal_dict.get('outcome'),
                    signal_dict.get('exit_price'),
                    signal_dict.get('profit_loss_pct'),
                    signal_dict.get('sha256'),
                    signal_dict.get('order_id'),
                    signal_dict.get('created_at', datetime.now().isoformat()),
                    service_type,
                    'migration'
                ))
                migrated += 1
                
            except sqlite3.IntegrityError:
                skipped += 1
            except Exception as e:
                errors += 1
                print(f"  ⚠️  Error migrating signal: {e}")
        
        unified_conn.commit()
        source_conn.close()
        unified_conn.close()
        
        print(f"  ✅ Migrated: {migrated:,}, Skipped: {skipped:,}, Errors: {errors:,}")
        return migrated, skipped
        
    except Exception as e:
        print(f"  ❌ Error migrating {service_type}: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0

def create_backup(db_path: Path, backup_dir: Path) -> Path:
    """Create backup of database"""
    if not db_path.exists():
        return None
    
    backup_path = backup_dir / f"{db_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"  💾 Backup created: {backup_path}")
    return backup_path

def main():
    """Run migration for all databases"""
    print("="*70)
    print("📊 DATABASE MIGRATION TO UNIFIED ARCHITECTURE")
    print("="*70)
    
    # Create backup directory
    backup_dir = Path(__file__).parent.parent / "backups" / datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n💾 Backup directory: {backup_dir}")
    
    # Determine unified database path
    if Path("/root/argo-production-unified").exists():
        unified_db = Path("/root/argo-production-unified/data/signals_unified.db")
        unified_db.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Use local path for development
        unified_db = Path(__file__).parent.parent / "argo" / "data" / "signals_unified.db"
        unified_db.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Unified database: {unified_db}")
    
    # Initialize unified database
    print("\n🔧 Initializing unified database...")
    try:
        from argo.core.unified_signal_tracker import UnifiedSignalTracker
        tracker = UnifiedSignalTracker(unified_db)
        print("  ✅ Unified database initialized")
    except Exception as e:
        print(f"  ❌ Error initializing unified database: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Create backups of source databases
    print("\n💾 Creating backups...")
    source_dbs = [
        (Path("/root/argo-production-green/data/signals.db"), "argo"),
        (Path("/root/argo-production-prop-firm/data/signals.db"), "prop_firm"),
        (Path("/root/argo-production/data/signals.db"), "legacy"),
        (Path("/root/argo-production-blue/data/signals.db"), "argo"),
    ]
    
    # Also check local paths
    local_dbs = [
        (Path(__file__).parent.parent / "argo" / "data" / "signals.db", "local_argo"),
        (Path(__file__).parent.parent / "data" / "signals.db", "local_root"),
    ]
    
    all_dbs = source_dbs + local_dbs
    
    backups_created = []
    for db_path, _ in all_dbs:
        if db_path.exists():
            backup = create_backup(db_path, backup_dir)
            if backup:
                backups_created.append(backup)
    
    # Migrate from all sources
    print("\n📦 Starting migration...")
    migrations = [
        (Path("/root/argo-production-green/data/signals.db"), "argo"),
        (Path("/root/argo-production-prop-firm/data/signals.db"), "prop_firm"),
        (Path("/root/argo-production/data/signals.db"), "legacy"),
        (Path("/root/argo-production-blue/data/signals.db"), "argo"),
        (Path(__file__).parent.parent / "argo" / "data" / "signals.db", "local_argo"),
        (Path(__file__).parent.parent / "data" / "signals.db", "local_root"),
    ]
    
    total_migrated = 0
    total_skipped = 0
    
    for source_db, service_type in migrations:
        if source_db.exists():
            migrated, skipped = migrate_database(source_db, unified_db, service_type)
            total_migrated += migrated
            total_skipped += skipped
        else:
            print(f"⚠️  Source database not found: {source_db}")
    
    # Verify migration
    print("\n🔍 Verifying migration...")
    try:
        conn = sqlite3.connect(str(unified_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM signals")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT service_type) FROM signals")
        service_types = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"  ✅ Total signals in unified database: {total:,}")
        print(f"  ✅ Service types: {service_types}")
    except Exception as e:
        print(f"  ❌ Error verifying: {e}")
    
    print(f"\n{'='*70}")
    print(f"📊 MIGRATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total Migrated: {total_migrated:,}")
    print(f"Total Skipped: {total_skipped:,}")
    print(f"Backups Created: {len(backups_created)}")
    print(f"Unified Database: {unified_db}")
    print(f"\n✅ Migration complete!")

if __name__ == "__main__":
    main()

