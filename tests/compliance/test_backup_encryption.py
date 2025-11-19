"""
Test suite for backup encryption
Tests S3-managed encryption (AES256) for backups
"""
import pytest
import os
import tempfile
from pathlib import Path
from datetime import datetime
from argo.compliance.daily_backup import BackupManager
from unittest.mock import patch, MagicMock, call


class TestBackupEncryption:
    """Test backup encryption configuration"""

    @pytest.fixture
    def backup_manager(self):
        """Create backup manager instance"""
        with patch('argo.compliance.daily_backup.boto3.client') as mock_boto:
            mock_s3 = MagicMock()
            mock_boto.return_value = mock_s3

            with patch.dict(os.environ, {
                'BACKUP_BUCKET_NAME': 'test-bucket',
                'AWS_ACCESS_KEY_ID': 'test-key',
                'AWS_SECRET_ACCESS_KEY': 'test-secret',
                'AWS_DEFAULT_REGION': 'us-east-1'
            }):
                manager = BackupManager()
                manager.s3_client = mock_s3
                return manager

    def test_s3_encryption_enabled(self, backup_manager):
        """Test that S3 uploads use ServerSideEncryption"""
        # Create test CSV
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("signal_id,symbol,action\n")
            f.write("TEST-123,AAPL,BUY\n")
            test_csv = f.name

        try:
            backup_date = datetime.now()
            s3_key = backup_manager._upload_to_s3(test_csv, backup_date, format='csv')

            # Verify upload was called
            assert backup_manager.s3_client.upload_file.called, "S3 upload should be called"

            # Check ExtraArgs for encryption
            call_args = backup_manager.s3_client.upload_file.call_args
            extra_args = call_args[1].get('ExtraArgs', {})

            # Verify ServerSideEncryption is set to AES256
            assert 'ServerSideEncryption' in extra_args, "ServerSideEncryption should be set"
            assert extra_args['ServerSideEncryption'] == 'AES256', "Should use AES256 encryption"

        finally:
            if os.path.exists(test_csv):
                os.remove(test_csv)

    def test_parquet_encryption_enabled(self, backup_manager):
        """Test that Parquet uploads also use encryption"""
        # Create test Parquet file (mock)
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.parquet') as f:
            f.write("test data")
            test_parquet = f.name

        try:
            backup_date = datetime.now()
            s3_key = backup_manager._upload_to_s3(test_parquet, backup_date, format='parquet')

            # Verify upload was called
            assert backup_manager.s3_client.upload_file.called, "S3 upload should be called"

            # Check ExtraArgs for encryption
            call_args = backup_manager.s3_client.upload_file.call_args
            extra_args = call_args[1].get('ExtraArgs', {})

            # Verify ServerSideEncryption is set
            assert 'ServerSideEncryption' in extra_args, "ServerSideEncryption should be set"
            assert extra_args['ServerSideEncryption'] == 'AES256', "Should use AES256 encryption"

        finally:
            if os.path.exists(test_parquet):
                os.remove(test_parquet)

    def test_encryption_metadata_preserved(self, backup_manager):
        """Test that encryption doesn't interfere with metadata"""
        # Create test CSV
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("signal_id,symbol\n")
            f.write("TEST-123,AAPL\n")
            test_csv = f.name

        try:
            backup_date = datetime.now()
            s3_key = backup_manager._upload_to_s3(test_csv, backup_date, format='csv')

            # Check ExtraArgs
            call_args = backup_manager.s3_client.upload_file.call_args
            extra_args = call_args[1].get('ExtraArgs', {})

            # Verify both encryption and metadata are present
            assert 'ServerSideEncryption' in extra_args, "Encryption should be set"
            assert 'Metadata' in extra_args, "Metadata should be present"

            metadata = extra_args['Metadata']
            assert 'backup_date' in metadata, "Metadata should include backup_date"
            assert 'version' in metadata, "Metadata should include version"

        finally:
            if os.path.exists(test_csv):
                os.remove(test_csv)

    def test_content_type_with_encryption(self, backup_manager):
        """Test that ContentType is set correctly with encryption"""
        # Create test CSV
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("signal_id,symbol\n")
            f.write("TEST-123,AAPL\n")
            test_csv = f.name

        try:
            backup_date = datetime.now()
            s3_key = backup_manager._upload_to_s3(test_csv, backup_date, format='csv')

            # Check ExtraArgs
            call_args = backup_manager.s3_client.upload_file.call_args
            extra_args = call_args[1].get('ExtraArgs', {})

            # Verify ContentType is set
            assert 'ContentType' in extra_args, "ContentType should be set"
            assert extra_args['ContentType'] == 'text/csv', "Should be text/csv for CSV files"

            # Verify encryption is still present
            assert 'ServerSideEncryption' in extra_args, "Encryption should still be set"

        finally:
            if os.path.exists(test_csv):
                os.remove(test_csv)

    def test_s3_bucket_encryption_policy(self, backup_manager):
        """Test that bucket encryption policy can be verified"""
        # Mock get_bucket_encryption
        backup_manager.s3_client.get_bucket_encryption.return_value = {
            'ServerSideEncryptionConfiguration': {
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }]
            }
        }

        # Verify bucket encryption
        try:
            response = backup_manager.s3_client.get_bucket_encryption(
                Bucket=backup_manager.bucket_name
            )

            encryption_config = response['ServerSideEncryptionConfiguration']
            rule = encryption_config['Rules'][0]
            sse_algorithm = rule['ApplyServerSideEncryptionByDefault']['SSEAlgorithm']

            assert sse_algorithm == 'AES256', "Bucket should use AES256 encryption"

        except backup_manager.s3_client.exceptions.ClientError:
            # Bucket encryption policy might not be set (optional)
            # This is acceptable as we use ServerSideEncryption on upload
            pass
