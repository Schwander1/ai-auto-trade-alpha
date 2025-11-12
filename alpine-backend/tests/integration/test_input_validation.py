"""Integration tests for input validation"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


class TestInputValidation:
    """Test input validation across endpoints"""
    
    def test_email_validation_on_signup(self):
        """Test email validation on signup"""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "invalid-email",
                "password": "TestPassword123!",
                "full_name": "Test User"
            }
        )
        assert response.status_code in [400, 422]
    
    def test_password_validation_on_signup(self):
        """Test password validation on signup"""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "short",  # Too short
                "full_name": "Test User"
            }
        )
        assert response.status_code in [400, 422]
    
    def test_password_complexity_validation(self):
        """Test password complexity requirements"""
        # Test password without uppercase
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "testpassword123!",
                "full_name": "Test User"
            }
        )
        assert response.status_code in [400, 422]
    
    def test_tier_validation_on_upgrade(self, auth_headers):
        """Test tier validation on subscription upgrade"""
        response = client.post(
            "/api/subscriptions/upgrade",
            json={"tier": "invalid-tier"},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
    
    def test_limit_validation_on_pagination(self, auth_headers):
        """Test limit validation on paginated endpoints"""
        # Test negative limit
        response = client.get(
            "/api/signals/subscribed?limit=-1",
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # Test limit too high
        response = client.get(
            "/api/signals/subscribed?limit=1000",
            headers=auth_headers
        )
        # Should either cap at max or return 400
        assert response.status_code in [200, 400, 422]
    
    def test_offset_validation_on_pagination(self, auth_headers):
        """Test offset validation on paginated endpoints"""
        # Test negative offset
        response = client.get(
            "/api/signals/subscribed?offset=-1",
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
    
    def test_symbol_validation(self, auth_headers):
        """Test symbol validation"""
        # Test invalid symbol format
        response = client.get(
            "/api/signals/subscribed?symbol=INVALID@SYMBOL",
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
    
    def test_action_validation(self, auth_headers):
        """Test action validation"""
        # Test invalid action
        response = client.get(
            "/api/signals/subscribed?action=HOLD",
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
    
    def test_totp_token_validation(self, auth_headers):
        """Test TOTP token validation"""
        # Test invalid token format
        response = client.post(
            "/api/2fa/enable",
            json={"token": "12345"},  # Too short
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # Test token with letters
        response = client.post(
            "/api/2fa/enable",
            json={"token": "12345a"},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
    
    def test_notification_ids_validation(self, auth_headers):
        """Test notification IDs validation"""
        # Test empty list
        response = client.post(
            "/api/notifications/read",
            json={"notification_ids": []},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
        
        # Test too many IDs
        ids = [f"notif-{i}" for i in range(101)]
        response = client.post(
            "/api/notifications/read",
            json={"notification_ids": ids},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]

