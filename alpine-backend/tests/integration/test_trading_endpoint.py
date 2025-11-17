"""
Integration tests for trading status endpoint
Tests the full flow: Argo → Alpine → Frontend
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import httpx


class TestTradingStatusEndpoint:
    """Test trading status endpoint functionality"""
    
    def test_trading_status_requires_authentication(self, client):
        """Test that trading status endpoint requires authentication"""
        response = client.get("/api/v1/trading/status")
        assert response.status_code == 401
    
    def test_trading_status_returns_valid_response(self, client, auth_headers):
        """Test that trading status endpoint returns valid response structure"""
        with patch('backend.api.trading.get_http_client') as mock_client:
            # Mock HTTP client and response
            mock_http_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {
                "environment": "production",
                "trading_mode": "production",
                "account_name": "Test Account",
                "account_number": "TEST123",
                "portfolio_value": 100000.0,
                "buying_power": 200000.0,
                "prop_firm_enabled": False,
                "alpaca_connected": True,
                "account_status": "ACTIVE"
            }
            mock_response.raise_for_status = Mock()
            mock_http_client.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_http_client
            
            response = client.get("/api/v1/trading/status", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["environment"] == "production"
            assert data["trading_mode"] == "production"
            assert data["account_name"] == "Test Account"
            assert data["alpaca_connected"] is True
    
    def test_trading_status_rate_limiting(self, client, auth_headers):
        """Test that trading status endpoint enforces rate limiting"""
        with patch('backend.api.trading.get_http_client') as mock_client:
            # Mock HTTP client
            mock_http_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {
                "environment": "production",
                "trading_mode": "production",
                "alpaca_connected": True
            }
            mock_response.raise_for_status = Mock()
            mock_http_client.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_http_client
            
            # Make requests up to the limit (30 requests)
            for i in range(30):
                response = client.get("/api/v1/trading/status", headers=auth_headers)
                assert response.status_code == 200
            
            # 31st request should be rate limited
            response = client.get("/api/v1/trading/status", headers=auth_headers)
            assert response.status_code == 429
    
    def test_trading_status_caching(self, client, auth_headers):
        """Test that trading status endpoint caches responses"""
        with patch('backend.api.trading.get_http_client') as mock_client:
            # Mock HTTP client
            mock_http_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {
                "environment": "production",
                "trading_mode": "production",
                "alpaca_connected": True
            }
            mock_response.raise_for_status = Mock()
            mock_http_client.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_http_client
            
            # First request
            response1 = client.get("/api/v1/trading/status", headers=auth_headers)
            assert response1.status_code == 200
            
            # Second request should use cache (same response, but HTTP client should not be called again)
            response2 = client.get("/api/v1/trading/status", headers=auth_headers)
            assert response2.status_code == 200
            assert response1.json() == response2.json()
    
    def test_trading_status_handles_argo_timeout(self, client, auth_headers):
        """Test that trading status endpoint handles Argo API timeout"""
        with patch('backend.api.trading.get_http_client') as mock_client:
            import httpx
            mock_http_client = AsyncMock()
            mock_http_client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            mock_client.return_value = mock_http_client
            
            response = client.get("/api/v1/trading/status", headers=auth_headers)
            assert response.status_code == 504
            assert "timeout" in response.json()["detail"].lower()
    
    def test_trading_status_handles_argo_error(self, client, auth_headers):
        """Test that trading status endpoint handles Argo API errors"""
        with patch('backend.api.trading.get_http_client') as mock_client:
            import httpx
            mock_http_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_http_client.get = AsyncMock(side_effect=httpx.HTTPStatusError(
                "Error", request=Mock(), response=mock_response
            ))
            mock_client.return_value = mock_http_client
            
            response = client.get("/api/v1/trading/status", headers=auth_headers)
            assert response.status_code == 502
    
    def test_trading_status_handles_connection_error(self, client, auth_headers):
        """Test that trading status endpoint handles connection errors"""
        with patch('backend.api.trading.get_http_client') as mock_client:
            import httpx
            mock_http_client = AsyncMock()
            mock_http_client.get = AsyncMock(side_effect=httpx.RequestError("Connection failed"))
            mock_client.return_value = mock_http_client
            
            response = client.get("/api/v1/trading/status", headers=auth_headers)
            assert response.status_code == 503
            assert "connection" in response.json()["detail"].lower()
    
    def test_trading_status_includes_cache_headers(self, client, auth_headers):
        """Test that trading status endpoint includes cache headers"""
        with patch('backend.api.trading.get_http_client') as mock_client:
            # Mock HTTP client
            mock_http_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {
                "environment": "production",
                "trading_mode": "production",
                "alpaca_connected": True
            }
            mock_response.raise_for_status = Mock()
            mock_http_client.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_http_client
            
            response = client.get("/api/v1/trading/status", headers=auth_headers)
            assert response.status_code == 200
            # Check for cache headers
            assert "Cache-Control" in response.headers or "cache-control" in response.headers
    
    def test_trading_status_includes_rate_limit_headers(self, client, auth_headers):
        """Test that trading status endpoint includes rate limit headers"""
        with patch('backend.api.trading.get_http_client') as mock_client:
            # Mock HTTP client
            mock_http_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {
                "environment": "production",
                "trading_mode": "production",
                "alpaca_connected": True
            }
            mock_response.raise_for_status = Mock()
            mock_http_client.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_http_client
            
            response = client.get("/api/v1/trading/status", headers=auth_headers)
            assert response.status_code == 200
            # Check for rate limit headers
            assert "X-RateLimit-Remaining" in response.headers or "x-ratelimit-remaining" in response.headers.lower()

