"""Integration tests for endpoint input validation"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


class TestEndpointInputValidation:
    """Test input validation across all endpoints"""
    
    def test_auth_signup_validation(self):
        """Test signup endpoint validation"""
        # Missing required fields
        response = client.post("/api/auth/signup", json={})
        assert response.status_code in [400, 422]
        
        # Invalid email
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "invalid",
                "password": "TestPassword123!",
                "full_name": "Test User"
            }
        )
        assert response.status_code in [400, 422]
        
        # Weak password
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "weak",
                "full_name": "Test User"
            }
        )
        assert response.status_code in [400, 422]
    
    def test_users_profile_validation(self, auth_headers):
        """Test user profile endpoint validation"""
        # Invalid email format
        response = client.put(
            "/api/users/profile",
            json={"email": "not-an-email"},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # Empty full name
        response = client.put(
            "/api/users/profile",
            json={"full_name": ""},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
    
    def test_subscriptions_upgrade_validation(self, auth_headers):
        """Test subscription upgrade validation"""
        # Invalid tier
        response = client.post(
            "/api/subscriptions/upgrade",
            json={"tier": "invalid"},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # Missing tier
        response = client.post(
            "/api/subscriptions/upgrade",
            json={},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
    
    def test_signals_subscribed_validation(self, auth_headers):
        """Test signals subscribed endpoint validation"""
        # Invalid limit
        response = client.get(
            "/api/signals/subscribed?limit=-1",
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # Invalid offset
        response = client.get(
            "/api/signals/subscribed?offset=-1",
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # Invalid symbol
        response = client.get(
            "/api/signals/subscribed?symbol=INVALID@SYMBOL",
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # Invalid action
        response = client.get(
            "/api/signals/subscribed?action=HOLD",
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
    
    def test_notifications_read_validation(self, auth_headers):
        """Test notifications read endpoint validation"""
        # Empty notification IDs
        response = client.post(
            "/api/notifications/read",
            json={"notification_ids": []},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # Too many notification IDs
        ids = [f"notif-{i}" for i in range(101)]
        response = client.post(
            "/api/notifications/read",
            json={"notification_ids": ids},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
    
    def test_2fa_enable_validation(self, auth_headers):
        """Test 2FA enable endpoint validation"""
        # Invalid token format
        response = client.post(
            "/api/2fa/enable",
            json={"token": "12345"},  # Too short
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # Token with letters
        response = client.post(
            "/api/2fa/enable",
            json={"token": "12345a"},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
    
    def test_admin_users_validation(self, admin_headers):
        """Test admin users endpoint validation"""
        # Invalid tier filter
        response = client.get(
            "/api/admin/users?tier=invalid",
            headers=admin_headers
        )
        assert response.status_code in [400, 422]
        
        # Invalid limit
        response = client.get(
            "/api/admin/users?limit=-1",
            headers=admin_headers
        )
        assert response.status_code in [400, 422]

