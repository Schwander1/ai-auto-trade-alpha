#!/usr/bin/env python3
"""
Backup Verification and Restoration Testing
Tests backup integrity and restoration procedures
"""
import boto3
import os
import csv
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BackupVerification")

class BackupVerifier:
    """Verifies backup integrity and tests restoration"""

    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('BACKUP_BUCKET_NAME') or os.getenv('AWS_BUCKET_NAME')
        if not self.bucket_name:
            raise ValueError("BACKUP_BUCKET_NAME or AWS_BUCKET_NAME environment variable required")

    def get_latest_backup(self) -> Optional[str]:
        """Get the most recent backup S3 key"""
        try:
            # List all backups
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='signals/'
            )

            if 'Contents' not in response:
                logger.warning("No backups found")
                return None

            # Sort by last modified (most recent first)
            backups = sorted(
                response['Contents'],
                key=lambda x: x['LastModified'],
                reverse=True
            )

            if backups:
                latest = backups[0]
                logger.info(f"📦 Latest backup: {latest['Key']} (modified: {latest['LastModified']})")
                return latest['Key']

            return None
        except Exception as e:
            logger.error(f"❌ Failed to list backups: {e}")
            return None

    def test_restore(self, s3_key: Optional[str] = None) -> Dict:
        """
        Test restoring from backup

        Returns:
            Dictionary with restore test results
        """
        if s3_key is None:
            s3_key = self.get_latest_backup()
            if not s3_key:
                return {
                    'success': False,
                    'error': 'No backup found'
                }

        logger.info(f"🧪 Testing restore from: {s3_key}")

        try:
            # Download backup
            local_file = f'/tmp/restore_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            self.s3_client.download_file(self.bucket_name, s3_key, local_file)
            logger.info(f"📥 Downloaded backup to: {local_file}")

            # Parse CSV
            signals = []
            with open(local_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    signals.append(row)

            logger.info(f"📊 Parsed {len(signals)} signals from backup")

            # Validate structure
            validation_results = self._validate_backup(signals)

            # Verify hashes
            hash_verification = self._verify_hashes(signals)

            # Clean up
            os.remove(local_file)

            # Compile results
            results = {
                'success': validation_results['valid'] and hash_verification['all_valid'],
                's3_key': s3_key,
                'signal_count': len(signals),
                'validation': validation_results,
                'hash_verification': hash_verification,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            if results['success']:
                logger.info("✅ Restore test PASSED")
            else:
                logger.error("❌ Restore test FAILED")

            return results

        except Exception as e:
            logger.error(f"❌ Restore test failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    def _validate_backup(self, signals: List[Dict]) -> Dict:
        """Validate backup structure"""
        required_fields = ['signal_id', 'symbol', 'action', 'verification_hash']
        missing_fields = []
        invalid_records = []

        for idx, signal in enumerate(signals):
            for field in required_fields:
                if field not in signal or not signal[field]:
                    missing_fields.append(f"Record {idx}: missing {field}")
                    invalid_records.append(idx)

        return {
            'valid': len(missing_fields) == 0,
            'missing_fields': missing_fields,
            'invalid_records': len(invalid_records),
            'total_records': len(signals)
        }

    def _verify_hashes(self, signals: List[Dict]) -> Dict:
        """Verify SHA-256 hashes in backup"""
        import hashlib
        import json

        failed_verifications = []

        for idx, signal in enumerate(signals):
            stored_hash = signal.get('verification_hash', '')
            if not stored_hash:
                failed_verifications.append({
                    'record': idx,
                    'signal_id': signal.get('signal_id', 'unknown'),
                    'error': 'Missing verification_hash'
                })
                continue

            # Recalculate hash
            hash_fields = {
                'signal_id': signal.get('signal_id'),
                'symbol': signal.get('symbol'),
                'action': signal.get('action'),
                'entry_price': signal.get('entry_price'),
                'target_price': signal.get('target_price'),
                'stop_price': signal.get('stop_price'),
                'confidence': signal.get('confidence'),
                'strategy': signal.get('strategy'),
                'timestamp': signal.get('timestamp')
            }

            hash_string = json.dumps(hash_fields, sort_keys=True, default=str)
            calculated_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

            if calculated_hash != stored_hash:
                failed_verifications.append({
                    'record': idx,
                    'signal_id': signal.get('signal_id', 'unknown'),
                    'error': 'Hash mismatch',
                    'stored': stored_hash[:16],
                    'calculated': calculated_hash[:16]
                })

        return {
            'all_valid': len(failed_verifications) == 0,
            'failed_count': len(failed_verifications),
            'failed_verifications': failed_verifications[:10],  # Limit to first 10
            'total_verified': len(signals)
        }

    def continuous_verification(self, days: int = 7):
        """Run verification tests for recent backups"""
        logger.info(f"🔄 Running continuous verification for last {days} days")

        results = []
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # List backups in date range
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='signals/'
            )

            if 'Contents' not in response:
                logger.warning("No backups found")
                return results

            for obj in response['Contents']:
                if obj['LastModified'].replace(tzinfo=None) >= start_date:
                    logger.info(f"Testing backup: {obj['Key']}")
                    result = self.test_restore(obj['Key'])
                    results.append(result)

            # Summary
            passed = sum(1 for r in results if r.get('success', False))
            total = len(results)

            logger.info(f"\n📊 Verification Summary:")
            logger.info(f"   Total backups tested: {total}")
            logger.info(f"   Passed: {passed}")
            logger.info(f"   Failed: {total - passed}")

            if passed < total:
                logger.error("❌ Some backups failed verification!")
            else:
                logger.info("✅ All backups passed verification")

            return results

        except Exception as e:
            logger.error(f"❌ Continuous verification failed: {e}", exc_info=True)
            return []


def main():
    """Main execution"""
    import sys

    verifier = BackupVerifier()

    if len(sys.argv) > 1 and sys.argv[1] == 'continuous':
        # Continuous verification mode
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        verifier.continuous_verification(days)
    else:
        # Single restore test
        s3_key = sys.argv[1] if len(sys.argv) > 1 else None
        result = verifier.test_restore(s3_key)

        # Print results
        print(json.dumps(result, indent=2, default=str))

        exit(0 if result.get('success', False) else 1)

if __name__ == '__main__':
    main()
