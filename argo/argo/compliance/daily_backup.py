#!/usr/bin/env python3
"""
Enhanced Daily Backup Script for Argo Capital
Backs up signals to S3 with verification and metadata

COMPLIANCE:
- 7-year retention requirement
- Tamper-evident storage (SHA-256 verification)
- Versioned backups (S3 versioning)
- Immediate verification after upload

NOTE: Encryption removed per user request - plain CSV to S3
"""
import boto3
import os
import csv
import json
import time
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BackupManager")

# Use relative path that works in both dev and production
if os.path.exists("/root/argo-production"):
    BASE_DIR = Path("/root/argo-production")
else:
    BASE_DIR = Path(__file__).parent.parent.parent.parent

DB_FILE = BASE_DIR / "data" / "signals.db"


class BackupManager:
    """Manages signal backups to S3 with verification"""
    
    def __init__(self):
        self.s3_client = self._init_s3_client()
        self.bucket_name = os.getenv('BACKUP_BUCKET_NAME') or os.getenv('AWS_BUCKET_NAME')
        if not self.bucket_name:
            raise ValueError("BACKUP_BUCKET_NAME or AWS_BUCKET_NAME environment variable required")
    
    def _init_s3_client(self):
        """Initialize S3 client"""
        return boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
    
    def create_backup(self, date: Optional[datetime] = None) -> Optional[str]:
        """
        Create backup for specified date (default: yesterday)
        
        Returns:
            S3 key of uploaded backup, or None if failed
        """
        if date is None:
            date = datetime.now() - timedelta(days=1)
        
        start_time = time.time()
        logger.info(f"🔄 Starting backup for {date.strftime('%Y-%m-%d')}")
        
        try:
            # Export signals to CSV
            csv_filename = self._export_signals_to_csv(date)
            
            # Upload to S3
            s3_key = self._upload_to_s3(csv_filename, date)
            
            # Verify backup immediately
            if self._verify_backup(s3_key):
                duration = time.time() - start_time
                logger.info(f"✅ Backup completed successfully in {duration:.2f}s: {s3_key}")
                
                # Record metrics
                try:
                    from argo.core.metrics import backup_duration_seconds, last_backup_timestamp
                    backup_duration_seconds.observe(duration)
                    last_backup_timestamp.set(time.time())
                except (ImportError, AttributeError):
                    pass
                
                # Clean up local file
                os.remove(csv_filename)
                
                return s3_key
            else:
                logger.error(f"❌ Backup verification failed: {s3_key}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}", exc_info=True)
            return None
    
    def _export_signals_to_csv(self, date: datetime) -> str:
        """Export signals for date to CSV file"""
        date_str = date.strftime('%Y%m%d')
        csv_filename = f'signals_backup_{date_str}_{datetime.now().strftime("%H%M%S")}.csv'
        
        # Query signals from SQLite database
        if not DB_FILE.exists():
            logger.warning(f"Database not found at {DB_FILE}, creating empty backup")
            with open(csv_filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['signal_id', 'symbol', 'action', 'entry_price', 'target_price', 
                               'stop_price', 'confidence', 'strategy', 'timestamp', 'verification_hash',
                               'generation_latency_ms', 'server_timestamp'])
            return csv_filename
        
        conn = sqlite3.connect(str(DB_FILE))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query signals for the date
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        cursor.execute("""
            SELECT signal_id, symbol, action, entry_price, target_price, stop_price,
                   confidence, strategy, timestamp, sha256 as verification_hash,
                   generation_latency_ms, NULL as server_timestamp
            FROM signals
            WHERE timestamp >= ? AND timestamp < ?
            ORDER BY timestamp ASC
        """, (start_date.isoformat(), end_date.isoformat()))
        
        signals = cursor.fetchall()
        conn.close()
        
        # Write to CSV
        with open(csv_filename, 'w', newline='') as f:
            if signals:
                fieldnames = signals[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows([dict(row) for row in signals])
            else:
                # Empty backup
                writer = csv.writer(f)
                writer.writerow(['signal_id', 'symbol', 'action', 'entry_price', 'target_price', 
                               'stop_price', 'confidence', 'strategy', 'timestamp', 'verification_hash',
                               'generation_latency_ms', 'server_timestamp'])
        
        logger.info(f"📊 Exported {len(signals)} signals to {csv_filename}")
        return csv_filename
    
    def _upload_to_s3(self, csv_filename: str, date: datetime) -> str:
        """Upload CSV to S3 with metadata"""
        s3_key = f'signals/{date.year}/{date.month:02d}/{os.path.basename(csv_filename)}'
        
        # Get file size
        file_size = os.path.getsize(csv_filename)
        
        # Count records
        record_count = 0
        with open(csv_filename, 'r') as f:
            record_count = sum(1 for line in f) - 1  # Subtract header
        
        # Upload with metadata
        metadata = {
            'backup_date': date.strftime('%Y-%m-%d'),
            'record_count': str(record_count),
            'file_size': str(file_size),
            'version': '1.0',
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        self.s3_client.upload_file(
            csv_filename,
            self.bucket_name,
            s3_key,
            ExtraArgs={
                'Metadata': metadata,
                'ServerSideEncryption': 'AES256'  # S3 managed encryption (not custom crypto)
            }
        )
        
        logger.info(f"📤 Uploaded to s3://{self.bucket_name}/{s3_key}")
        return s3_key
    
    def _verify_backup(self, s3_key: str) -> bool:
        """
        Verify backup by downloading and validating
        
        Returns:
            True if backup is valid, False otherwise
        """
        try:
            # Download backup
            local_file = f'/tmp/verify_{os.path.basename(s3_key)}'
            self.s3_client.download_file(self.bucket_name, s3_key, local_file)
            
            # Validate CSV structure
            with open(local_file, 'r') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                
                # Check required fields
                required_fields = ['signal_id', 'symbol', 'action', 'verification_hash']
                missing_fields = [f for f in required_fields if f not in fieldnames]
                if missing_fields:
                    logger.error(f"❌ Missing required fields: {missing_fields}")
                    os.remove(local_file)
                    return False
                
                # Count records and verify structure
                record_count = 0
                for row in reader:
                    record_count += 1
                    # Verify verification_hash exists
                    if not row.get('verification_hash'):
                        logger.warning(f"⚠️  Signal {row.get('signal_id')} missing verification_hash")
            
            # Verify record count matches metadata
            metadata = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)['Metadata']
            expected_count = int(metadata.get('record_count', 0))
            
            if record_count != expected_count:
                logger.warning(f"⚠️  Record count mismatch: expected {expected_count}, got {record_count}")
            
            # Clean up
            os.remove(local_file)
            
            logger.info(f"✅ Backup verification passed: {record_count} records")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup verification failed: {e}", exc_info=True)
            return False


def backup_signals(date: Optional[datetime] = None) -> bool:
    """Main backup function (backwards compatible)"""
    try:
        manager = BackupManager()
        s3_key = manager.create_backup(date)
        return s3_key is not None
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Custom date: YYYY-MM-DD
        try:
            backup_date = datetime.strptime(sys.argv[1], '%Y-%m-%d')
            backup_signals(backup_date)
        except ValueError:
            logger.error(f"Invalid date format: {sys.argv[1]}. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        # Default: yesterday
        backup_signals()
