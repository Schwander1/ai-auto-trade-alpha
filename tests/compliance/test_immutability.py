"""
Test suite for signal immutability
Tests that UPDATE/DELETE operations are blocked by database triggers
"""
import pytest
from sqlalchemy import text
from backend.core.database import get_engine
from backend.models.signal import Signal
from datetime import datetime
import hashlib
import json


@pytest.fixture
def test_signal_data():
    """Create test signal data"""
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
    signal_data['verification_hash'] = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
    
    return signal_data


@pytest.fixture
def db_connection():
    """Get database connection"""
    engine = get_engine()
    return engine.connect()


class TestSignalImmutability:
    """Test that signals cannot be modified or deleted"""
    
    def test_update_blocked(self, db_connection, test_signal_data):
        """Test that UPDATE operation is blocked"""
        # Insert a test signal
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
                'symbol': test_signal_data['symbol'],
                'action': test_signal_data['action'],
                'price': test_signal_data['entry_price'],
                'confidence': test_signal_data['confidence'] / 100.0,
                'target_price': test_signal_data['target_price'],
                'stop_loss': test_signal_data['stop_price'],
                'rationale': 'Test signal for immutability testing',
                'verification_hash': test_signal_data['verification_hash']
            })
            signal_id = result.scalar()
        
        # Attempt UPDATE - should fail
        with pytest.raises(Exception) as exc_info:
            with db_connection.begin():
                db_connection.execute(text("""
                    UPDATE signals 
                    SET confidence = 99.9 
                    WHERE id = :signal_id
                """), {'signal_id': signal_id})
        
        # Verify error message mentions immutability
        error_msg = str(exc_info.value).lower()
        assert 'immutable' in error_msg or 'P0001' in str(exc_info.value)
        
        # Verify signal was not modified
        result = db_connection.execute(text("""
            SELECT confidence FROM signals WHERE id = :signal_id
        """), {'signal_id': signal_id})
        confidence = result.scalar()
        assert confidence == pytest.approx(test_signal_data['confidence'] / 100.0, rel=0.01)
    
    def test_delete_blocked(self, db_connection, test_signal_data):
        """Test that DELETE operation is blocked"""
        # Insert a test signal
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
                'symbol': test_signal_data['symbol'],
                'action': test_signal_data['action'],
                'price': test_signal_data['entry_price'],
                'confidence': test_signal_data['confidence'] / 100.0,
                'target_price': test_signal_data['target_price'],
                'stop_loss': test_signal_data['stop_price'],
                'rationale': 'Test signal for immutability testing',
                'verification_hash': test_signal_data['verification_hash']
            })
            signal_id = result.scalar()
        
        # Attempt DELETE - should fail
        with pytest.raises(Exception) as exc_info:
            with db_connection.begin():
                db_connection.execute(text("""
                    DELETE FROM signals WHERE id = :signal_id
                """), {'signal_id': signal_id})
        
        # Verify error message mentions immutability
        error_msg = str(exc_info.value).lower()
        assert 'immutable' in error_msg or 'P0001' in str(exc_info.value)
        
        # Verify signal still exists
        result = db_connection.execute(text("""
            SELECT COUNT(*) FROM signals WHERE id = :signal_id
        """), {'signal_id': signal_id})
        count = result.scalar()
        assert count == 1
    
    def test_audit_log_created_on_update_attempt(self, db_connection, test_signal_data):
        """Test that UPDATE attempt is logged in audit log"""
        # Insert a test signal
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
                'symbol': test_signal_data['symbol'],
                'action': test_signal_data['action'],
                'price': test_signal_data['entry_price'],
                'confidence': test_signal_data['confidence'] / 100.0,
                'target_price': test_signal_data['target_price'],
                'stop_loss': test_signal_data['stop_price'],
                'rationale': 'Test signal for audit log testing',
                'verification_hash': test_signal_data['verification_hash']
            })
            signal_id = result.scalar()
        
        # Get initial audit log count
        result = db_connection.execute(text("""
            SELECT COUNT(*) FROM signal_audit_log WHERE signal_id = :signal_id
        """), {'signal_id': signal_id})
        initial_count = result.scalar()
        
        # Attempt UPDATE (will fail but should log)
        try:
            with db_connection.begin():
                db_connection.execute(text("""
                    UPDATE signals SET confidence = 99.9 WHERE id = :signal_id
                """), {'signal_id': signal_id})
        except Exception:
            pass  # Expected to fail
        
        # Verify audit log entry was created
        result = db_connection.execute(text("""
            SELECT COUNT(*) FROM signal_audit_log 
            WHERE signal_id = :signal_id AND action = 'UPDATE_ATTEMPT'
        """), {'signal_id': signal_id})
        update_attempts = result.scalar()
        
        assert update_attempts > 0, "UPDATE_ATTEMPT should be logged in audit log"
    
    def test_audit_log_immutable(self, db_connection):
        """Test that audit log itself is immutable"""
        # Get an audit log entry
        result = db_connection.execute(text("""
            SELECT id FROM signal_audit_log LIMIT 1
        """))
        row = result.fetchone()
        
        if row:
            audit_id = row[0]
            
            # Attempt UPDATE - should fail
            with pytest.raises(Exception) as exc_info:
                with db_connection.begin():
                    db_connection.execute(text("""
                        UPDATE signal_audit_log 
                        SET action = 'MODIFIED' 
                        WHERE id = :audit_id
                    """), {'audit_id': audit_id})
            
            # Verify error
            error_msg = str(exc_info.value).lower()
            assert 'append-only' in error_msg or 'immutable' in error_msg or 'P0001' in str(exc_info.value)
            
            # Attempt DELETE - should fail
            with pytest.raises(Exception) as exc_info:
                with db_connection.begin():
                    db_connection.execute(text("""
                        DELETE FROM signal_audit_log WHERE id = :audit_id
                    """), {'audit_id': audit_id})
            
            # Verify error
            error_msg = str(exc_info.value).lower()
            assert 'append-only' in error_msg or 'immutable' in error_msg or 'P0001' in str(exc_info.value)

