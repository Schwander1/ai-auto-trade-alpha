"""
Unit tests for model validations
Tests all the new validation logic added to models
"""
import pytest
from datetime import datetime, timezone, timedelta
import hashlib
from sqlalchemy.exc import IntegrityError

from backend.models.user import User, UserTier
from backend.models.signal import Signal, SignalAction
from backend.models.notification import Notification, NotificationType
from backend.models.backtest import Backtest, BacktestStatus
from backend.models.role import Role, Permission, PermissionEnum
from backend.auth.security import get_password_hash


class TestUserModelValidations:
    """Test User model validations"""
    
    def test_email_validation_valid(self, db):
        """Test valid email formats"""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test User"
        )
        db.add(user)
        db.commit()
        assert user.email == "test@example.com"
    
    def test_email_validation_invalid_format(self, db):
        """Test invalid email format raises error"""
        user = User(
            email="invalid-email",
            hashed_password=get_password_hash("password123")
        )
        db.add(user)
        with pytest.raises(ValueError, match="Invalid email format"):
            db.commit()
    
    def test_email_validation_too_long(self, db):
        """Test email too long raises error"""
        long_email = "a" * 250 + "@example.com"
        user = User(
            email=long_email,
            hashed_password=get_password_hash("password123")
        )
        db.add(user)
        with pytest.raises(ValueError, match="Email must be 255 characters or less"):
            db.commit()
    
    def test_email_normalization(self, db):
        """Test email is normalized to lowercase"""
        user = User(
            email="Test@Example.COM",
            hashed_password=get_password_hash("password123")
        )
        db.add(user)
        db.commit()
        assert user.email == "test@example.com"
    
    def test_full_name_validation(self, db):
        """Test full name validation"""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="A" * 300  # Too long
        )
        db.add(user)
        with pytest.raises(ValueError, match="Full name must be 255 characters or less"):
            db.commit()
    
    def test_user_repr(self, db):
        """Test User __repr__ method"""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            tier=UserTier.PRO,
            is_active=True
        )
        db.add(user)
        db.commit()
        repr_str = repr(user)
        assert "User" in repr_str
        assert "test@example.com" in repr_str
        assert "pro" in repr_str.lower()


class TestSignalModelValidations:
    """Test Signal model validations"""
    
    def test_action_enum_required(self, db):
        """Test that action must be SignalAction enum"""
        signal = Signal(
            symbol="AAPL",
            action=SignalAction.BUY,
            price=175.50,
            confidence=0.85,
            rationale="Test signal rationale with sufficient length for validation",
            verification_hash=hashlib.sha256(b"test").hexdigest()
        )
        db.add(signal)
        db.commit()
        assert signal.action == SignalAction.BUY
    
    def test_confidence_range_validation(self, db):
        """Test confidence must be between 0 and 1"""
        # Valid confidence
        signal = Signal(
            symbol="AAPL",
            action=SignalAction.BUY,
            price=175.50,
            confidence=0.85,
            rationale="Test signal rationale with sufficient length for validation",
            verification_hash=hashlib.sha256(b"test1").hexdigest()
        )
        db.add(signal)
        db.commit()
        assert signal.confidence == 0.85
        
        # Invalid confidence (too high)
        signal2 = Signal(
            symbol="NVDA",
            action=SignalAction.SELL,
            price=500.00,
            confidence=1.5,  # Invalid
            rationale="Test signal rationale with sufficient length for validation",
            verification_hash=hashlib.sha256(b"test2").hexdigest()
        )
        db.add(signal2)
        with pytest.raises(ValueError, match="Confidence must be between 0 and 1"):
            db.commit()
    
    def test_price_positive_validation(self, db):
        """Test price must be positive"""
        signal = Signal(
            symbol="AAPL",
            action=SignalAction.BUY,
            price=-100.0,  # Invalid
            confidence=0.85,
            rationale="Test signal rationale with sufficient length for validation",
            verification_hash=hashlib.sha256(b"test3").hexdigest()
        )
        db.add(signal)
        with pytest.raises(ValueError, match="must be greater than 0"):
            db.commit()
    
    def test_symbol_validation(self, db):
        """Test symbol validation"""
        # Valid symbol
        signal = Signal(
            symbol="AAPL",
            action=SignalAction.BUY,
            price=175.50,
            confidence=0.85,
            rationale="Test signal rationale with sufficient length for validation",
            verification_hash=hashlib.sha256(b"test4").hexdigest()
        )
        db.add(signal)
        db.commit()
        assert signal.symbol == "AAPL"  # Should be uppercase
        
        # Symbol too long
        signal2 = Signal(
            symbol="A" * 25,  # Too long
            action=SignalAction.BUY,
            price=175.50,
            confidence=0.85,
            rationale="Test signal rationale with sufficient length for validation",
            verification_hash=hashlib.sha256(b"test5").hexdigest()
        )
        db.add(signal2)
        with pytest.raises(ValueError, match="Symbol must be 20 characters or less"):
            db.commit()
    
    def test_rationale_validation(self, db):
        """Test rationale must be meaningful (>20 chars)"""
        # Too short
        signal = Signal(
            symbol="AAPL",
            action=SignalAction.BUY,
            price=175.50,
            confidence=0.85,
            rationale="Short",  # Too short
            verification_hash=hashlib.sha256(b"test6").hexdigest()
        )
        db.add(signal)
        with pytest.raises(ValueError, match="must be meaningful"):
            db.commit()
    
    def test_verification_hash_validation(self, db):
        """Test verification hash must be valid SHA-256"""
        # Invalid length
        signal = Signal(
            symbol="AAPL",
            action=SignalAction.BUY,
            price=175.50,
            confidence=0.85,
            rationale="Test signal rationale with sufficient length for validation",
            verification_hash="short_hash"  # Invalid
        )
        db.add(signal)
        with pytest.raises(ValueError, match="must be 64 characters"):
            db.commit()
        
        # Invalid hex format
        signal2 = Signal(
            symbol="AAPL",
            action=SignalAction.BUY,
            price=175.50,
            confidence=0.85,
            rationale="Test signal rationale with sufficient length for validation",
            verification_hash="x" * 64  # Invalid hex
        )
        db.add(signal2)
        with pytest.raises(ValueError, match="valid hexadecimal string"):
            db.commit()
    
    def test_signal_repr(self, db):
        """Test Signal __repr__ method"""
        signal = Signal(
            symbol="AAPL",
            action=SignalAction.BUY,
            price=175.50,
            confidence=0.85,
            rationale="Test signal rationale with sufficient length for validation",
            verification_hash=hashlib.sha256(b"test7").hexdigest(),
            is_active=True
        )
        db.add(signal)
        db.commit()
        repr_str = repr(signal)
        assert "Signal" in repr_str
        assert "AAPL" in repr_str
        assert "BUY" in repr_str


class TestNotificationModelValidations:
    """Test Notification model validations"""
    
    def test_notification_type_enum(self, db, test_user):
        """Test notification type must be enum"""
        notification = Notification(
            user_id=test_user.id,
            title="Test Notification",
            message="Test message",
            type=NotificationType.INFO
        )
        db.add(notification)
        db.commit()
        assert notification.type == NotificationType.INFO
    
    def test_title_validation(self, db, test_user):
        """Test title validation"""
        # Title too long
        notification = Notification(
            user_id=test_user.id,
            title="A" * 300,  # Too long
            message="Test message",
            type=NotificationType.INFO
        )
        db.add(notification)
        with pytest.raises(ValueError, match="Title must be 255 characters or less"):
            db.commit()
    
    def test_message_validation(self, db, test_user):
        """Test message cannot be empty"""
        notification = Notification(
            user_id=test_user.id,
            title="Test",
            message="",  # Empty
            type=NotificationType.INFO
        )
        db.add(notification)
        with pytest.raises(ValueError, match="Message cannot be empty"):
            db.commit()
    
    def test_mark_as_read(self, db, test_user):
        """Test mark_as_read helper method"""
        notification = Notification(
            user_id=test_user.id,
            title="Test",
            message="Test message",
            type=NotificationType.INFO
        )
        db.add(notification)
        db.commit()
        
        assert notification.is_read == False
        notification.mark_as_read()
        assert notification.is_read == True
        assert notification.read_at is not None
    
    def test_notification_repr(self, db, test_user):
        """Test Notification __repr__ method"""
        notification = Notification(
            user_id=test_user.id,
            title="Test",
            message="Test message",
            type=NotificationType.INFO
        )
        db.add(notification)
        db.commit()
        repr_str = repr(notification)
        assert "Notification" in repr_str
        assert str(test_user.id) in repr_str


class TestBacktestModelValidations:
    """Test Backtest model validations"""
    
    def test_backtest_status_enum(self, db):
        """Test backtest status must be enum"""
        backtest = Backtest(
            backtest_id="test-123",
            symbol="AAPL",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=1),
            initial_capital=10000.0,
            status=BacktestStatus.RUNNING
        )
        db.add(backtest)
        db.commit()
        assert backtest.status == BacktestStatus.RUNNING
    
    def test_date_range_validation(self, db):
        """Test end_date must be after start_date"""
        backtest = Backtest(
            backtest_id="test-124",
            symbol="AAPL",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) - timedelta(days=1),  # Before start
            initial_capital=10000.0
        )
        db.add(backtest)
        with pytest.raises(ValueError, match="End date must be after start date"):
            db.commit()
    
    def test_initial_capital_validation(self, db):
        """Test initial capital must be positive"""
        backtest = Backtest(
            backtest_id="test-125",
            symbol="AAPL",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=1),
            initial_capital=-1000.0  # Invalid
        )
        db.add(backtest)
        with pytest.raises(ValueError, match="Initial capital must be greater than 0"):
            db.commit()
    
    def test_risk_per_trade_validation(self, db):
        """Test risk per trade must be between 0 and 1"""
        # Valid risk
        backtest = Backtest(
            backtest_id="test-126",
            symbol="AAPL",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=1),
            initial_capital=10000.0,
            risk_per_trade=0.02
        )
        db.add(backtest)
        db.commit()
        assert backtest.risk_per_trade == 0.02
        
        # Invalid risk (too high)
        backtest2 = Backtest(
            backtest_id="test-127",
            symbol="NVDA",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=1),
            initial_capital=10000.0,
            risk_per_trade=1.5  # Invalid
        )
        db.add(backtest2)
        with pytest.raises(ValueError, match="Risk per trade must be between 0 and 1"):
            db.commit()
    
    def test_mark_completed(self, db):
        """Test mark_completed helper method"""
        backtest = Backtest(
            backtest_id="test-128",
            symbol="AAPL",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=1),
            initial_capital=10000.0
        )
        db.add(backtest)
        db.commit()
        
        assert backtest.status == BacktestStatus.RUNNING
        backtest.mark_completed({"total_return": 0.15})
        assert backtest.status == BacktestStatus.COMPLETED
        assert backtest.results == {"total_return": 0.15}
        assert backtest.completed_at is not None
    
    def test_mark_failed(self, db):
        """Test mark_failed helper method"""
        backtest = Backtest(
            backtest_id="test-129",
            symbol="AAPL",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=1),
            initial_capital=10000.0
        )
        db.add(backtest)
        db.commit()
        
        backtest.mark_failed("Test error")
        assert backtest.status == BacktestStatus.FAILED
        assert backtest.error == "Test error"
        assert backtest.completed_at is not None
    
    def test_backtest_repr(self, db):
        """Test Backtest __repr__ method"""
        backtest = Backtest(
            backtest_id="test-130",
            symbol="AAPL",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=1),
            initial_capital=10000.0,
            status=BacktestStatus.RUNNING
        )
        db.add(backtest)
        db.commit()
        repr_str = repr(backtest)
        assert "Backtest" in repr_str
        assert "test-130" in repr_str
        assert "AAPL" in repr_str


class TestRoleModelValidations:
    """Test Role and Permission model validations"""
    
    def test_role_name_validation(self, db):
        """Test role name validation"""
        # Valid role name
        role = Role(
            name="test_role",
            description="Test role"
        )
        db.add(role)
        db.commit()
        assert role.name == "test_role"  # Should be lowercase
        
        # Invalid characters
        role2 = Role(
            name="test role!",  # Invalid characters
            description="Test"
        )
        db.add(role2)
        with pytest.raises(ValueError, match="can only contain alphanumeric"):
            db.commit()
    
    def test_permission_name_validation(self, db):
        """Test permission name must be in resource:action format"""
        # Valid permission
        permission = Permission(
            name="user:read",
            description="Read users"
        )
        db.add(permission)
        db.commit()
        
        # Invalid format (no colon)
        permission2 = Permission(
            name="userread",  # Missing colon
            description="Test"
        )
        db.add(permission2)
        with pytest.raises(ValueError, match="must be in format 'resource:action'"):
            db.commit()
    
    def test_role_repr(self, db):
        """Test Role __repr__ method"""
        role = Role(
            name="admin",
            is_system=True
        )
        db.add(role)
        db.commit()
        repr_str = repr(role)
        assert "Role" in repr_str
        assert "admin" in repr_str
    
    def test_permission_repr(self, db):
        """Test Permission __repr__ method"""
        permission = Permission(
            name="user:read"
        )
        db.add(permission)
        db.commit()
        repr_str = repr(permission)
        assert "Permission" in repr_str
        assert "user:read" in repr_str

