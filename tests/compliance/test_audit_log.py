"""
Test suite for audit log functionality
Tests that all operations are logged correctly
"""
import pytest
from sqlalchemy import text
from backend.core.database import get_engine
from datetime import datetime
import hashlib
import json


@pytest.fixture
def db_connection():
    """Get database connection"""
    engine = get_engine()
    return engine.connect()


class TestAuditLogging:
    """Test audit log functionality"""
    
    def test_insert_logged_automatically(self, db_connection):
        """Test that INSERT operations are automatically logged"""
        signal_data = {
            'signal_id': f'TEST-{int(datetime.now().timestamp())}',
            'symbol': 'TEST',
            'action': 'BUY',
            'entry_price': 100.0,
            'target_price': 110.0,
            'stop_price': 95.0,
            'confidence': 95.5,
            'strategy': 'test',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        hash_string = json.dumps(signal_data, sort_keys=True, default=str)
        verification_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
        
        # Insert signal
        with db_connection.begin():
            result = db_connection.execute(text("""
                INSERT INTO signals (
                    symbol, action, price, confidence, target_price, stop_loss,
                    rationale, verification_hash, created_at, retention_expires_at
                ) VALUES (
                    :symbol, :action, :price, :confidence, :target_price, :stop_loss,
                    :rationale, :verification_hash, NOW(), NOW() + INTERVAL '7 years'
                ) RETURNING id
            """), {
                'symbol': signal_data['symbol'],
                'action': signal_data['action'],
                'price': signal_data['entry_price'],
                'confidence': signal_data['confidence'] / 100.0,
                'target_price': signal_data['target_price'],
                'stop_loss': signal_data['stop_price'],
                'rationale': 'Test signal for audit log testing',
                'verification_hash': verification_hash
            })
            signal_id = result.scalar()
        
        # Verify audit log entry was created
        result = db_connection.execute(text("""
            SELECT action, new_data, verification_hash 
            FROM signal_audit_log 
            WHERE signal_id = :signal_id AND action = 'INSERT'
        """), {'signal_id': signal_id})
        
        audit_entry = result.fetchone()
        assert audit_entry is not None, "INSERT should be logged in audit log"
        assert audit_entry[0] == 'INSERT', "Action should be INSERT"
        assert audit_entry[2] == verification_hash, "Verification hash should match"
    
    def test_update_attempt_logged(self, db_connection):
        """Test that UPDATE attempts are logged"""
        signal_data = {
            'signal_id': f'TEST-{int(datetime.now().timestamp())}',
            'symbol': 'TEST',
            'action': 'BUY',
            'entry_price': 100.0,
            'confidence': 95.5,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        hash_string = json.dumps(signal_data, sort_keys=True, default=str)
        verification_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
        
        # Insert signal
        with db_connection.begin():
            result = db_connection.execute(text("""
                INSERT INTO signals (
                    symbol, action, price, confidence, target_price, stop_loss,
                    rationale, verification_hash, created_at, retention_expires_at
                ) VALUES (
                    :symbol, :action, :price, :confidence, 110.0, 95.0,
                    :rationale, :verification_hash, NOW(), NOW() + INTERVAL '7 years'
                ) RETURNING id
            """), {
                'symbol': signal_data['symbol'],
                'action': signal_data['action'],
                'price': signal_data['entry_price'],
                'confidence': signal_data['confidence'] / 100.0,
                'rationale': 'Test signal',
                'verification_hash': verification_hash
            })
            signal_id = result.scalar()
        
        # Attempt UPDATE (will fail but should log)
        try:
            with db_connection.begin():
                db_connection.execute(text("""
                    UPDATE signals SET confidence = 99.9 WHERE id = :signal_id
                """), {'signal_id': signal_id})
        except Exception:
            pass  # Expected to fail
        
        # Verify UPDATE_ATTEMPT was logged
        result = db_connection.execute(text("""
            SELECT action, old_data, new_data 
            FROM signal_audit_log 
            WHERE signal_id = :signal_id AND action = 'UPDATE_ATTEMPT'
        """), {'signal_id': signal_id})
        
        audit_entry = result.fetchone()
        assert audit_entry is not None, "UPDATE_ATTEMPT should be logged"
        assert audit_entry[0] == 'UPDATE_ATTEMPT', "Action should be UPDATE_ATTEMPT"
        assert audit_entry[1] is not None, "old_data should be present"
        assert audit_entry[2] is not None, "new_data should be present"
    
    def test_delete_attempt_logged(self, db_connection):
        """Test that DELETE attempts are logged"""
        signal_data = {
            'signal_id': f'TEST-{int(datetime.now().timestamp())}',
            'symbol': 'TEST',
            'action': 'BUY',
            'entry_price': 100.0,
            'confidence': 95.5,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        hash_string = json.dumps(signal_data, sort_keys=True, default=str)
        verification_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
        
        # Insert signal
        with db_connection.begin():
            result = db_connection.execute(text("""
                INSERT INTO signals (
                    symbol, action, price, confidence, target_price, stop_loss,
                    rationale, verification_hash, created_at, retention_expires_at
                ) VALUES (
                    :symbol, :action, :price, :confidence, 110.0, 95.0,
                    :rationale, :verification_hash, NOW(), NOW() + INTERVAL '7 years'
                ) RETURNING id
            """), {
                'symbol': signal_data['symbol'],
                'action': signal_data['action'],
                'price': signal_data['entry_price'],
                'confidence': signal_data['confidence'] / 100.0,
                'rationale': 'Test signal',
                'verification_hash': verification_hash
            })
            signal_id = result.scalar()
        
        # Attempt DELETE (will fail but should log)
        try:
            with db_connection.begin():
                db_connection.execute(text("""
                    DELETE FROM signals WHERE id = :signal_id
                """), {'signal_id': signal_id})
        except Exception:
            pass  # Expected to fail
        
        # Verify DELETE_ATTEMPT was logged
        result = db_connection.execute(text("""
            SELECT action, old_data 
            FROM signal_audit_log 
            WHERE signal_id = :signal_id AND action = 'DELETE_ATTEMPT'
        """), {'signal_id': signal_id})
        
        audit_entry = result.fetchone()
        assert audit_entry is not None, "DELETE_ATTEMPT should be logged"
        assert audit_entry[0] == 'DELETE_ATTEMPT', "Action should be DELETE_ATTEMPT"
        assert audit_entry[1] is not None, "old_data should be present"
    
    def test_audit_log_queryable(self, db_connection):
        """Test that audit log entries can be queried"""
        # Query recent audit log entries
        result = db_connection.execute(text("""
            SELECT action, COUNT(*) as count
            FROM signal_audit_log
            WHERE timestamp > NOW() - INTERVAL '1 hour'
            GROUP BY action
            ORDER BY action
        """))
        
        entries = result.fetchall()
        assert len(entries) >= 0, "Should be able to query audit log"
        
        # Verify structure
        for entry in entries:
            assert entry[0] in ['INSERT', 'UPDATE_ATTEMPT', 'DELETE_ATTEMPT', 'VERIFICATION']
            assert entry[1] >= 0

