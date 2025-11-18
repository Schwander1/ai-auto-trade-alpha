"""
Integration tests for signal history endpoint
Tests the /api/v1/signals/history endpoint with real database queries
"""
import pytest
import hashlib
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from backend.models.signal import Signal, SignalAction


class TestSignalHistoryEndpoint:
    """Test signal history endpoint functionality"""

    def test_signal_history_requires_authentication(self, client):
        """Test that signal history endpoint requires authentication"""
        response = client.get("/api/v1/signals/history")
        assert response.status_code == 401

    def test_signal_history_returns_empty_list_when_no_signals(self, client, auth_headers, db):
        """Test that signal history returns empty list when no signals exist"""
        response = client.get("/api/v1/signals/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_signal_history_returns_signals(self, client, auth_headers, db):
        """Test that signal history returns signals from database"""
        # Create test signals
        now = datetime.now(timezone.utc)
        signals = [
            Signal(
                symbol="AAPL",
                action=SignalAction.BUY,
                price=175.50,
                confidence=0.85,
                rationale="Test signal rationale for AAPL buy signal with sufficient length",
                verification_hash=hashlib.sha256(f"hash_{i}_{now.timestamp()}".encode()).hexdigest(),
                is_active=True,
                created_at=now - timedelta(days=i)
            )
            for i in range(5)
        ]
        for signal in signals:
            db.add(signal)
        db.commit()

        response = client.get("/api/v1/signals/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert data[0]["symbol"] == "AAPL"
        assert data[0]["action"] == "BUY"
        assert data[0]["entry_price"] == 175.50
        assert data[0]["status"] == "active"
        assert "SIG-" in data[0]["signal_id"]

    def test_signal_history_respects_limit(self, client, auth_headers, db):
        """Test that signal history respects the limit parameter"""
        # Create 10 test signals
        now = datetime.now(timezone.utc)
        signals = [
            Signal(
                symbol="AAPL",
                action=SignalAction.BUY,
                price=175.50,
                confidence=0.85,
                rationale="Test signal rationale for AAPL buy signal with sufficient length",
                verification_hash=hashlib.sha256(f"hash_{i}_{now.timestamp()}".encode()).hexdigest(),
                is_active=True,
                created_at=now - timedelta(days=i)
            )
            for i in range(10)
        ]
        for signal in signals:
            db.add(signal)
        db.commit()

        # Request only 5 signals
        response = client.get("/api/v1/signals/history?limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_signal_history_respects_days_parameter(self, client, auth_headers, db):
        """Test that signal history respects the days parameter"""
        now = datetime.now(timezone.utc)

        # Create signals: 2 within 7 days, 2 older than 7 days
        recent_signals = [
            Signal(
                symbol="AAPL",
                action=SignalAction.BUY,
                price=175.50,
                confidence=0.85,
                rationale="Test signal rationale for AAPL buy signal with sufficient length",
                verification_hash=hashlib.sha256(f"recent_hash_{i}_{now.timestamp()}".encode()).hexdigest(),
                is_active=True,
                created_at=now - timedelta(days=i)
            )
            for i in range(2)
        ]

        old_signals = [
            Signal(
                symbol="NVDA",
                action=SignalAction.SELL,
                price=500.00,
                confidence=0.90,
                rationale="Test signal rationale for NVDA sell signal with sufficient length",
                verification_hash=hashlib.sha256(f"old_hash_{i}_{now.timestamp()}".encode()).hexdigest(),
                is_active=False,
                created_at=now - timedelta(days=10 + i)
            )
            for i in range(2)
        ]

        for signal in recent_signals + old_signals:
            db.add(signal)
        db.commit()

        # Request signals from last 7 days
        response = client.get("/api/v1/signals/history?days=7", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(s["symbol"] == "AAPL" for s in data)

    def test_signal_history_orders_by_newest_first(self, client, auth_headers, db):
        """Test that signal history orders signals by newest first"""
        now = datetime.now(timezone.utc)
        signals = [
            Signal(
                symbol="AAPL",
                action=SignalAction.BUY,
                price=175.50 + i,
                confidence=0.85,
                rationale="Test signal rationale for AAPL buy signal with sufficient length",
                verification_hash=hashlib.sha256(f"hash_{i}_{now.timestamp()}".encode()).hexdigest(),
                is_active=True,
                created_at=now - timedelta(days=5 - i)  # Newest first
            )
            for i in range(5)
        ]
        for signal in signals:
            db.add(signal)
        db.commit()

        response = client.get("/api/v1/signals/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Verify ordering (newest first)
        for i in range(len(data) - 1):
            current_time = datetime.fromisoformat(data[i]["created_at"].replace('Z', '+00:00'))
            next_time = datetime.fromisoformat(data[i + 1]["created_at"].replace('Z', '+00:00'))
            assert current_time >= next_time

    def test_signal_history_includes_status(self, client, auth_headers, db):
        """Test that signal history includes correct status based on is_active"""
        now = datetime.now(timezone.utc)

        active_signal = Signal(
            symbol="AAPL",
            action=SignalAction.BUY,
            price=175.50,
            confidence=0.85,
            rationale="Test signal rationale for AAPL buy signal with sufficient length",
            verification_hash=hashlib.sha256("active_hash".encode()).hexdigest(),
            is_active=True,
            created_at=now
        )

        inactive_signal = Signal(
            symbol="NVDA",
            action=SignalAction.SELL,
            price=500.00,
            confidence=0.90,
            rationale="Test signal rationale for NVDA sell signal with sufficient length",
            verification_hash=hashlib.sha256("inactive_hash".encode()).hexdigest(),
            is_active=False,
            created_at=now - timedelta(days=1)
        )

        db.add(active_signal)
        db.add(inactive_signal)
        db.commit()

        response = client.get("/api/v1/signals/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Find signals by symbol
        aapl_signal = next(s for s in data if s["symbol"] == "AAPL")
        nvda_signal = next(s for s in data if s["symbol"] == "NVDA")

        assert aapl_signal["status"] == "active"
        assert nvda_signal["status"] == "closed"

    def test_signal_history_includes_null_fields(self, client, auth_headers, db):
        """Test that signal history includes null fields for exit_price, pnl_pct, closed_at"""
        signal = Signal(
            symbol="AAPL",
            action="BUY",
            price=175.50,
            confidence=0.85,
            rationale="Test signal rationale for AAPL buy signal with sufficient length",
            verification_hash="test_hash",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(signal)
        db.commit()

        response = client.get("/api/v1/signals/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        signal_data = data[0]
        assert signal_data["exit_price"] is None
        assert signal_data["pnl_pct"] is None
        assert signal_data["closed_at"] is None

    def test_signal_history_rate_limiting(self, client, auth_headers, db):
        """Test that signal history endpoint enforces rate limiting"""
        # Create a signal
        signal = Signal(
            symbol="AAPL",
            action="BUY",
            price=175.50,
            confidence=0.85,
            rationale="Test signal rationale for AAPL buy signal with sufficient length",
            verification_hash="test_hash",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(signal)
        db.commit()

        # Make requests up to the limit (100 requests)
        for i in range(100):
            response = client.get("/api/v1/signals/history", headers=auth_headers)
            assert response.status_code == 200

        # 101st request should be rate limited
        response = client.get("/api/v1/signals/history", headers=auth_headers)
        assert response.status_code == 429

    def test_signal_history_includes_cache_headers(self, client, auth_headers, db):
        """Test that signal history endpoint includes cache headers"""
        signal = Signal(
            symbol="AAPL",
            action="BUY",
            price=175.50,
            confidence=0.85,
            rationale="Test signal rationale for AAPL buy signal with sufficient length",
            verification_hash="test_hash",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(signal)
        db.commit()

        response = client.get("/api/v1/signals/history", headers=auth_headers)
        assert response.status_code == 200
        # Check for cache headers
        assert "Cache-Control" in response.headers or "cache-control" in response.headers

    def test_signal_history_includes_rate_limit_headers(self, client, auth_headers, db):
        """Test that signal history endpoint includes rate limit headers"""
        signal = Signal(
            symbol="AAPL",
            action="BUY",
            price=175.50,
            confidence=0.85,
            rationale="Test signal rationale for AAPL buy signal with sufficient length",
            verification_hash="test_hash",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(signal)
        db.commit()

        response = client.get("/api/v1/signals/history", headers=auth_headers)
        assert response.status_code == 200
        # Check for rate limit headers
        assert "X-RateLimit-Remaining" in response.headers or "x-ratelimit-remaining" in response.headers.lower()

    def test_signal_history_validates_limit_parameter(self, client, auth_headers):
        """Test that signal history validates limit parameter"""
        # Test limit too high
        response = client.get("/api/v1/signals/history?limit=1000", headers=auth_headers)
        assert response.status_code == 422  # Validation error

        # Test limit too low
        response = client.get("/api/v1/signals/history?limit=0", headers=auth_headers)
        assert response.status_code == 422  # Validation error

    def test_signal_history_validates_days_parameter(self, client, auth_headers):
        """Test that signal history validates days parameter"""
        # Test days too high
        response = client.get("/api/v1/signals/history?days=1000", headers=auth_headers)
        assert response.status_code == 422  # Validation error

        # Test days too low
        response = client.get("/api/v1/signals/history?days=0", headers=auth_headers)
        assert response.status_code == 422  # Validation error

    def test_signal_history_handles_different_actions(self, client, auth_headers, db):
        """Test that signal history handles different action types"""
        now = datetime.now(timezone.utc)
        actions_list = [SignalAction.BUY, SignalAction.SELL, SignalAction.BUY, SignalAction.SELL]
        signals = [
            Signal(
                symbol="AAPL",
                action=action,
                price=175.50,
                confidence=0.85,
                rationale=f"Test signal rationale for {action.value} signal with sufficient length",
                verification_hash=hashlib.sha256(f"hash_{action.value}_{i}_{now.timestamp()}".encode()).hexdigest(),
                is_active=True,
                created_at=now - timedelta(days=i)
            )
            for i, action in enumerate(actions_list)
        ]
        for signal in signals:
            db.add(signal)
        db.commit()

        response = client.get("/api/v1/signals/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

        actions = [s["action"] for s in data]
        assert "BUY" in actions
        assert "SELL" in actions

    def test_signal_history_handles_multiple_symbols(self, client, auth_headers, db):
        """Test that signal history handles multiple symbols"""
        now = datetime.now(timezone.utc)
        symbols = ["AAPL", "NVDA", "BTC-USD", "ETH-USD"]
        signals = [
            Signal(
                symbol=symbol,
                action=SignalAction.BUY,
                price=175.50,
                confidence=0.85,
                rationale=f"Test signal rationale for {symbol} buy signal with sufficient length",
                verification_hash=hashlib.sha256(f"hash_{symbol}_{i}_{now.timestamp()}".encode()).hexdigest(),
                is_active=True,
                created_at=now - timedelta(days=i)
            )
            for i, symbol in enumerate(symbols)
        ]
        for signal in signals:
            db.add(signal)
        db.commit()

        response = client.get("/api/v1/signals/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

        returned_symbols = [s["symbol"] for s in data]
        for symbol in symbols:
            assert symbol in returned_symbols
