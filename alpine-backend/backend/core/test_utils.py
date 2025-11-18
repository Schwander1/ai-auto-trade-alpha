"""
Testing Utilities
Provides reusable test fixtures, helpers, and utilities for testing.
"""
from typing import Optional, Dict, Any, List
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
import json
from datetime import datetime, timedelta

from backend.core.database import Base, get_db
from backend.models.user import User, UserTier
from backend.models.signal import Signal
from backend.auth.security import get_password_hash, create_access_token


# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create test session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db():
    """Create a test database session"""
    # Create tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override"""
    from backend.main import app

    # Override database dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        tier=UserTier.STARTER,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_pro(db: Session) -> User:
    """Create a PRO tier test user"""
    user = User(
        email="pro@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Pro User",
        tier=UserTier.PRO,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_elite(db: Session) -> User:
    """Create an ELITE tier test user"""
    user = User(
        email="elite@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Elite User",
        tier=UserTier.ELITE,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db: Session) -> User:
    """Create an admin test user"""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        full_name="Admin User",
        tier=UserTier.ELITE,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Add admin role (if RBAC is implemented)
    # This would require role assignment logic

    return user


@pytest.fixture
def auth_headers(test_user: User) -> Dict[str, str]:
    """Create authentication headers for test user"""
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(admin_user: User) -> Dict[str, str]:
    """Create authentication headers for admin user"""
    token = create_access_token(data={"sub": admin_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_signal(db: Session, test_user: User) -> Signal:
    """Create a test signal"""
    from backend.models.signal import SignalAction
    
    signal = Signal(
        symbol="AAPL",
        action=SignalAction.BUY,
        price=175.50,
        confidence=0.855,  # Normalized to 0-1 range
        target_price=185.00,
        stop_loss=170.00,
        rationale="Test signal rationale for testing purposes",
        verification_hash="a" * 64,  # Valid SHA-256 hash format (64 hex chars)
        is_active=True
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


def create_test_user(
    db: Session,
    email: str = "test@example.com",
    password: str = "testpassword123",
    tier: UserTier = UserTier.STARTER,
    is_active: bool = True,
    is_verified: bool = True
) -> User:
    """Helper function to create a test user"""
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=f"Test User {email}",
        tier=tier,
        is_active=is_active,
        is_verified=is_verified
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_signal(
    db: Session,
    symbol: str = "AAPL",
    action: str = "BUY",
    price: float = 175.50,
    confidence: float = 0.855,  # Normalized to 0-1 range (85.5% = 0.855)
    is_active: bool = True
) -> Signal:
    """Helper function to create a test signal"""
    from backend.models.signal import SignalAction
    import hashlib
    
    # Convert action string to enum
    if isinstance(action, str):
        action_enum = SignalAction[action.upper()]
    else:
        action_enum = action
    
    # Normalize confidence if provided as 0-100
    if confidence > 1:
        confidence = confidence / 100.0
    
    # Generate valid SHA-256 hash
    hash_input = f"test_hash_{symbol}_{action}_{price}_{datetime.utcnow().timestamp()}"
    verification_hash = hashlib.sha256(hash_input.encode()).hexdigest()
    
    signal = Signal(
        symbol=symbol,
        action=action_enum,
        price=price,
        confidence=confidence,
        target_price=price * 1.05,
        stop_loss=price * 0.97,
        rationale=f"Test signal for {symbol} with sufficient reasoning to meet validation requirements",
        verification_hash=verification_hash,
        is_active=is_active
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


def assert_response_status(response, expected_status: int):
    """Assert response status code"""
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}. Response: {response.text}"


def assert_response_json(response, expected_keys: List[str]):
    """Assert response contains expected JSON keys"""
    data = response.json()
    for key in expected_keys:
        assert key in data, f"Response missing key: {key}. Response: {data}"


def assert_error_response(response, expected_error_code: str, expected_status: int = 400):
    """Assert error response format"""
    assert_response_status(response, expected_status)
    data = response.json()
    assert "error" in data, f"Response missing 'error' key. Response: {data}"
    assert data["error"]["code"] == expected_error_code, \
        f"Expected error code {expected_error_code}, got {data['error']['code']}"


def get_auth_token(user: User) -> str:
    """Get authentication token for user"""
    return create_access_token(data={"sub": user.email})


def get_auth_headers(user: User) -> Dict[str, str]:
    """Get authentication headers for user"""
    token = get_auth_token(user)
    return {"Authorization": f"Bearer {token}"}
