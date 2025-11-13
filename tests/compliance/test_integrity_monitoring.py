"""
Test suite for integrity monitoring
Tests integrity check functionality and failure detection
"""
import pytest
from unittest.mock import patch, MagicMock
from argo.compliance.integrity_monitor import IntegrityMonitor
import hashlib
import json


class TestIntegrityMonitoring:
    """Test integrity monitoring functionality"""
    
    @pytest.fixture
    def integrity_monitor(self):
        """Create integrity monitor instance"""
        return IntegrityMonitor()
    
    def test_hash_verification_valid(self, integrity_monitor):
        """Test hash verification for valid signal"""
        signal = {
            'signal_id': 'TEST-123',
            'symbol': 'AAPL',
            'action': 'BUY',
            'entry_price': 175.50,
            'target_price': 184.25,
            'stop_price': 171.00,
            'confidence': 95.5,
            'strategy': 'test',
            'timestamp': '2024-11-13T10:00:00Z'
        }
        
        # Calculate correct hash
        hash_fields = {
            'signal_id': signal['signal_id'],
            'symbol': signal['symbol'],
            'action': signal['action'],
            'entry_price': signal['entry_price'],
            'target_price': signal['target_price'],
            'stop_price': signal['stop_price'],
            'confidence': signal['confidence'],
            'strategy': signal['strategy'],
            'timestamp': signal['timestamp']
        }
        hash_string = json.dumps(hash_fields, sort_keys=True, default=str)
        correct_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
        
        signal['verification_hash'] = correct_hash
        
        # Verify hash
        is_valid = integrity_monitor._verify_signal_hash(signal)
        assert is_valid is True, "Valid hash should pass verification"
    
    def test_hash_verification_invalid(self, integrity_monitor):
        """Test hash verification for invalid signal"""
        signal = {
            'signal_id': 'TEST-123',
            'symbol': 'AAPL',
            'action': 'BUY',
            'entry_price': 175.50,
            'target_price': 184.25,
            'stop_price': 171.00,
            'confidence': 95.5,
            'strategy': 'test',
            'timestamp': '2024-11-13T10:00:00Z',
            'verification_hash': 'wrong_hash_12345'
        }
        
        # Verify hash (should fail)
        is_valid = integrity_monitor._verify_signal_hash(signal)
        assert is_valid is False, "Invalid hash should fail verification"
    
    def test_integrity_check_sample(self, integrity_monitor):
        """Test integrity check with sample size"""
        # Mock database query
        with patch.object(integrity_monitor, '_query_signals') as mock_query:
            mock_query.return_value = [
                {
                    'signal_id': 'TEST-1',
                    'symbol': 'AAPL',
                    'action': 'BUY',
                    'entry_price': 175.50,
                    'target_price': 184.25,
                    'stop_price': 171.00,
                    'confidence': 95.5,
                    'strategy': 'test',
                    'timestamp': '2024-11-13T10:00:00Z',
                    'verification_hash': 'valid_hash'
                }
            ]
            
            # Mock hash verification
            with patch.object(integrity_monitor, '_verify_signal_hash', return_value=True):
                result = integrity_monitor.run_integrity_check(sample_size=1)
                
                assert result['success'] is True, "Integrity check should pass"
                assert result['checked'] == 1, "Should check 1 signal"
                assert result['failed'] == 0, "Should have 0 failures"
    
    def test_integrity_check_failure_detection(self, integrity_monitor):
        """Test that integrity check detects failures"""
        # Mock database query
        with patch.object(integrity_monitor, '_query_signals') as mock_query:
            mock_query.return_value = [
                {
                    'signal_id': 'TEST-1',
                    'symbol': 'AAPL',
                    'action': 'BUY',
                    'entry_price': 175.50,
                    'target_price': 184.25,
                    'stop_price': 171.00,
                    'confidence': 95.5,
                    'strategy': 'test',
                    'timestamp': '2024-11-13T10:00:00Z',
                    'verification_hash': 'wrong_hash'
                }
            ]
            
            # Mock hash verification to return False
            with patch.object(integrity_monitor, '_verify_signal_hash', return_value=False):
                result = integrity_monitor.run_integrity_check(sample_size=1)
                
                assert result['success'] is False, "Integrity check should fail"
                assert result['failed'] == 1, "Should have 1 failure"
                assert len(result['failed_signals']) > 0, "Should list failed signals"
    
    def test_alert_triggered_on_failure(self, integrity_monitor):
        """Test that alert is triggered on integrity failure"""
        # Mock database query
        with patch.object(integrity_monitor, '_query_signals') as mock_query:
            mock_query.return_value = [
                {
                    'signal_id': 'TEST-1',
                    'symbol': 'AAPL',
                    'verification_hash': 'wrong_hash'
                }
            ]
            
            # Mock hash verification to return False
            with patch.object(integrity_monitor, '_verify_signal_hash', return_value=False):
                # Mock alert trigger
                with patch.object(integrity_monitor, '_trigger_alert') as mock_alert:
                    result = integrity_monitor.run_integrity_check(sample_size=1)
                    
                    # Verify alert was triggered
                    assert mock_alert.called, "Alert should be triggered on failure"
                    assert result['success'] is False, "Result should indicate failure"

