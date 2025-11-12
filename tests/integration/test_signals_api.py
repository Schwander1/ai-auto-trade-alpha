"""
Integration tests for signals API
Tests end-to-end flow from Argo to Alpine
"""

import pytest
import httpx
from typing import Dict, Any


@pytest.mark.integration
@pytest.mark.requires_network
class TestSignalsAPI:
    """Integration tests for signals API endpoints"""
    
    ARGO_URL = "http://178.156.194.174:8000"
    ALPINE_BACKEND_URL = "http://91.98.153.49:8001"
    
    @pytest.fixture
    def argo_client(self):
        """HTTP client for Argo API"""
        return httpx.AsyncClient(base_url=self.ARGO_URL, timeout=10.0)
    
    @pytest.fixture
    def alpine_client(self):
        """HTTP client for Alpine Backend API"""
        return httpx.AsyncClient(base_url=self.ALPINE_BACKEND_URL, timeout=10.0)
    
    @pytest.mark.asyncio
    async def test_argo_health(self, argo_client):
        """Test Argo health endpoint"""
        response = await argo_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
    
    @pytest.mark.asyncio
    async def test_argo_signals_latest(self, argo_client):
        """Test Argo /api/signals/latest endpoint returns array"""
        response = await argo_client.get("/api/signals/latest", params={"limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Response should be an array"
        if len(data) > 0:
            signal = data[0]
            assert "id" in signal
            assert "symbol" in signal
            assert "action" in signal
            assert "confidence" in signal
    
    @pytest.mark.asyncio
    async def test_argo_signals_premium_filter(self, argo_client):
        """Test Argo premium signals filter"""
        response = await argo_client.get(
            "/api/signals/latest",
            params={"limit": 10, "premium_only": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All signals should have confidence >= 95
        for signal in data:
            assert signal.get("confidence", 0) >= 95
    
    @pytest.mark.asyncio
    async def test_alpine_backend_health(self, alpine_client):
        """Test Alpine Backend health endpoint"""
        response = await alpine_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
    
    @pytest.mark.asyncio
    async def test_signal_verification(self, argo_client):
        """Test signal hash verification"""
        response = await argo_client.get("/api/signals/latest", params={"limit": 1})
        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            signal = data[0]
            assert "hash" in signal, "Signal should have hash field"
            # Hash should be 64 characters (SHA-256 hex)
            assert len(signal["hash"]) == 64

