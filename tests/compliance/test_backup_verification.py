"""
Test suite for backup and verification
Tests backup creation, encryption, and verification
"""
import pytest
import os
import csv
import tempfile
from pathlib import Path
from datetime import datetime
from argo.compliance.daily_backup import BackupManager
from unittest.mock import patch, MagicMock, mock_open


class TestBackupManager:
    """Test backup manager functionality"""
    
    @pytest.fixture
    def backup_manager(self):
        """Create backup manager instance"""
        with patch('argo.compliance.daily_backup.boto3.client'):
            manager = BackupManager()
            return manager
    
    def test_csv_export_structure(self, backup_manager):
        """Test that CSV export has correct structure"""
        # Mock database query
        with patch('argo.compliance.daily_backup.sqlite3') as mock_sqlite:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_row = MagicMock()
            
            mock_row.keys.return_value = ['signal_id', 'symbol', 'action', 'verification_hash']
            mock_row.__getitem__.side_effect = lambda key: {
                'signal_id': 'TEST-123',
                'symbol': 'AAPL',
                'action': 'BUY',
                'verification_hash': 'abc123'
            }[key]
            
            mock_cursor.fetchall.return_value = [mock_row]
            mock_conn.cursor.return_value = mock_cursor
            mock_sqlite.connect.return_value = mock_conn
            mock_sqlite.Row = MagicMock()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
                temp_file = f.name
            
            try:
                # Export to CSV
                csv_file = backup_manager._export_signals_to_csv(datetime.now())
                
                # Verify CSV structure
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    fieldnames = reader.fieldnames
                    
                    required_fields = ['signal_id', 'symbol', 'action', 'verification_hash']
                    for field in required_fields:
                        assert field in fieldnames, f"Required field {field} missing from CSV"
                
                # Clean up
                if os.path.exists(csv_file):
                    os.remove(csv_file)
            finally:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
    
    def test_backup_verification(self, backup_manager):
        """Test backup verification"""
        # Create test CSV
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            writer = csv.DictWriter(f, fieldnames=['signal_id', 'symbol', 'action', 'verification_hash'])
            writer.writeheader()
            writer.writerow({
                'signal_id': 'TEST-123',
                'symbol': 'AAPL',
                'action': 'BUY',
                'verification_hash': 'abc123def456'
            })
            test_csv = f.name
        
        try:
            # Mock S3 operations
            with patch.object(backup_manager.s3_client, 'download_file'), \
                 patch.object(backup_manager.s3_client, 'head_object', return_value={
                     'Metadata': {'record_count': '1'}
                 }):
                
                # Verify backup
                result = backup_manager._verify_backup('test-key')
                
                # Should pass verification
                assert result is True, "Backup verification should pass"
        finally:
            if os.path.exists(test_csv):
                os.remove(test_csv)
    
    def test_backup_metadata(self, backup_manager):
        """Test that backup includes correct metadata"""
        # Create test CSV
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            writer = csv.writer(f)
            writer.writerow(['signal_id', 'symbol'])
            writer.writerow(['TEST-123', 'AAPL'])
            test_csv = f.name
        
        try:
            # Mock S3 upload
            with patch.object(backup_manager.s3_client, 'upload_file') as mock_upload:
                backup_date = datetime.now()
                s3_key = backup_manager._upload_to_s3(test_csv, backup_date)
                
                # Verify upload was called with metadata
                assert mock_upload.called, "S3 upload should be called"
                
                # Check ExtraArgs for metadata
                call_args = mock_upload.call_args
                extra_args = call_args[1].get('ExtraArgs', {})
                metadata = extra_args.get('Metadata', {})
                
                assert 'backup_date' in metadata, "Metadata should include backup_date"
                assert 'record_count' in metadata, "Metadata should include record_count"
                assert 'version' in metadata, "Metadata should include version"
        finally:
            if os.path.exists(test_csv):
                os.remove(test_csv)

