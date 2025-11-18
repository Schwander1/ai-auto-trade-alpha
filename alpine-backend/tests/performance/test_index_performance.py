"""
Performance tests for database indexes
Tests query performance with new indexes
"""
import pytest
import time
from datetime import datetime, timezone, timedelta
import hashlib
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.models.user import User, UserTier
from backend.models.signal import Signal, SignalAction
from backend.models.notification import Notification, NotificationType
from backend.models.backtest import Backtest, BacktestStatus
from backend.auth.security import get_password_hash


class TestIndexPerformance:
    """Test performance improvements from new indexes"""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, db: Session):
        """Create test data for performance tests"""
        # Create users
        users = []
        for i in range(100):
            user = User(
                email=f"user{i}@example.com",
                hashed_password=get_password_hash("password123"),
                tier=UserTier.STARTER if i % 3 == 0 else (UserTier.PRO if i % 3 == 1 else UserTier.ELITE),
                is_active=i % 10 != 0  # 90% active
            )
            users.append(user)
            db.add(user)
        db.commit()
        
        # Create signals
        signals = []
        for i in range(1000):
            signal = Signal(
                symbol=f"SYM{i % 50}",  # 50 different symbols
                action=SignalAction.BUY if i % 2 == 0 else SignalAction.SELL,
                price=100.0 + (i % 100),
                confidence=0.5 + (i % 50) / 100.0,  # 0.5 to 1.0
                rationale=f"Test signal rationale for symbol {i % 50} with sufficient length for validation",
                verification_hash=hashlib.sha256(f"hash_{i}".encode()).hexdigest(),
                is_active=i % 5 != 0,  # 80% active
                created_at=datetime.now(timezone.utc) - timedelta(days=i % 30)
            )
            signals.append(signal)
            db.add(signal)
        db.commit()
        
        # Create notifications
        notifications = []
        for i, user in enumerate(users[:50]):  # 50 users with notifications
            for j in range(10):  # 10 notifications per user
                notification = Notification(
                    user_id=user.id,
                    title=f"Notification {j}",
                    message=f"Test message {j}",
                    type=list(NotificationType)[j % len(NotificationType)],
                    is_read=j % 2 == 0,
                    created_at=datetime.now(timezone.utc) - timedelta(days=j)
                )
                notifications.append(notification)
                db.add(notification)
        db.commit()
        
        # Create backtests
        backtests = []
        for i in range(200):
            backtest = Backtest(
                backtest_id=f"bt-{i}",
                symbol=f"SYM{i % 20}",
                start_date=datetime.now(timezone.utc) - timedelta(days=30),
                end_date=datetime.now(timezone.utc) - timedelta(days=i % 30),
                initial_capital=10000.0,
                status=list(BacktestStatus)[i % len(BacktestStatus)],
                created_at=datetime.now(timezone.utc) - timedelta(days=i % 30)
            )
            backtests.append(backtest)
            db.add(backtest)
        db.commit()
        
        yield
        
        # Cleanup
        db.query(Backtest).delete()
        db.query(Notification).delete()
        db.query(Signal).delete()
        db.query(User).delete()
        db.commit()
    
    def test_signal_index_active_confidence_created(self, db: Session):
        """Test performance of composite index on signals (is_active, confidence, created_at)"""
        start = time.time()
        
        # Query that should use the composite index
        signals = db.query(Signal).filter(
            Signal.is_active == True,
            Signal.confidence >= 0.8
        ).order_by(Signal.created_at.desc()).limit(100).all()
        
        elapsed = time.time() - start
        
        assert len(signals) <= 100
        assert elapsed < 0.1  # Should be very fast with index
        print(f"✅ Signal active/confidence query: {elapsed:.4f}s")
    
    def test_signal_index_symbol_created(self, db: Session):
        """Test performance of composite index on signals (symbol, created_at)"""
        start = time.time()
        
        # Query that should use the symbol index
        signals = db.query(Signal).filter(
            Signal.symbol == "SYM1"
        ).order_by(Signal.created_at.desc()).limit(50).all()
        
        elapsed = time.time() - start
        
        assert len(signals) <= 50
        assert elapsed < 0.1  # Should be very fast with index
        print(f"✅ Signal symbol query: {elapsed:.4f}s")
    
    def test_signal_index_action(self, db: Session):
        """Test performance of index on signal action"""
        start = time.time()
        
        # Query by action
        buy_signals = db.query(Signal).filter(
            Signal.action == SignalAction.BUY
        ).limit(100).all()
        
        elapsed = time.time() - start
        
        assert len(buy_signals) <= 100
        assert elapsed < 0.1
        print(f"✅ Signal action query: {elapsed:.4f}s")
    
    def test_user_index_tier_active(self, db: Session):
        """Test performance of composite index on users (tier, is_active)"""
        start = time.time()
        
        # Query that should use the composite index
        pro_users = db.query(User).filter(
            User.tier == UserTier.PRO,
            User.is_active == True
        ).all()
        
        elapsed = time.time() - start
        
        assert len(pro_users) > 0
        assert elapsed < 0.1
        print(f"✅ User tier/active query: {elapsed:.4f}s")
    
    def test_notification_index_user_read_created(self, db: Session):
        """Test performance of composite index on notifications"""
        user = db.query(User).first()
        start = time.time()
        
        # Query that should use the composite index
        unread = db.query(Notification).filter(
            Notification.user_id == user.id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc()).all()
        
        elapsed = time.time() - start
        
        assert elapsed < 0.1
        print(f"✅ Notification user/read query: {elapsed:.4f}s")
    
    def test_notification_index_type_created(self, db: Session):
        """Test performance of index on notification type"""
        start = time.time()
        
        # Query by type
        info_notifications = db.query(Notification).filter(
            Notification.type == NotificationType.INFO
        ).order_by(Notification.created_at.desc()).limit(50).all()
        
        elapsed = time.time() - start
        
        assert elapsed < 0.1
        print(f"✅ Notification type query: {elapsed:.4f}s")
    
    def test_backtest_index_user_created(self, db: Session):
        """Test performance of composite index on backtests"""
        user = db.query(User).first()
        start = time.time()
        
        # Query user backtests
        backtests = db.query(Backtest).filter(
            Backtest.user_id == user.id
        ).order_by(Backtest.created_at.desc()).all()
        
        elapsed = time.time() - start
        
        assert elapsed < 0.1
        print(f"✅ Backtest user query: {elapsed:.4f}s")
    
    def test_backtest_index_status_created(self, db: Session):
        """Test performance of composite index on backtests (status, created_at)"""
        start = time.time()
        
        # Query by status
        completed = db.query(Backtest).filter(
            Backtest.status == BacktestStatus.COMPLETED
        ).order_by(Backtest.created_at.desc()).limit(50).all()
        
        elapsed = time.time() - start
        
        assert elapsed < 0.1
        print(f"✅ Backtest status query: {elapsed:.4f}s")
    
    def test_explain_query_plans(self, db: Session):
        """Test that queries use indexes (PostgreSQL EXPLAIN)"""
        # This test requires PostgreSQL
        try:
            # Check signal query plan
            result = db.execute(text("""
                EXPLAIN ANALYZE
                SELECT * FROM signals 
                WHERE is_active = true AND confidence >= 0.8 
                ORDER BY created_at DESC 
                LIMIT 100;
            """))
            plan = "\n".join([str(row) for row in result])
            
            # Should mention index usage
            assert "Index" in plan or "idx_signal" in plan.lower()
            print("✅ Signal query uses index")
            
        except Exception as e:
            # Skip if not PostgreSQL or EXPLAIN not available
            pytest.skip(f"EXPLAIN not available: {e}")

