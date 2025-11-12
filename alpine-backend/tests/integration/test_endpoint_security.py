"""Integration tests for endpoint security (XSS, SQL injection, path traversal)"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


class TestXSSPrevention:
    """Test XSS attack prevention"""
    
    def test_xss_in_email_field(self, auth_headers):
        """Test XSS prevention in email field"""
        xss_payload = "<script>alert('xss')</script>@example.com"
        response = client.put(
            "/api/users/profile",
            json={"email": xss_payload},
            headers=auth_headers
        )
        # Should fail validation, not execute script
        assert response.status_code in [400, 422]
    
    def test_xss_in_full_name_field(self, auth_headers):
        """Test XSS prevention in full name field"""
        xss_payload = "<script>alert('xss')</script>"
        response = client.put(
            "/api/users/profile",
            json={"full_name": xss_payload},
            headers=auth_headers
        )
        # HTML should be escaped
        if response.status_code == 200:
            assert "<script>" not in response.json()["full_name"]
    
    def test_xss_in_symbol_query_param(self):
        """Test XSS prevention in symbol query parameter"""
        xss_payload = "<script>alert('xss')</script>"
        response = client.get(f"/api/signals/subscribed?symbol={xss_payload}")
        # Should fail validation
        assert response.status_code in [400, 401, 422]
    
    def test_xss_in_notification_id(self, auth_headers):
        """Test XSS prevention in notification ID"""
        xss_payload = "<script>alert('xss')</script>"
        response = client.delete(
            f"/api/notifications/{xss_payload}",
            headers=auth_headers
        )
        # Should fail validation
        assert response.status_code in [400, 404]


class TestSQLInjectionPrevention:
    """Test SQL injection attack prevention"""
    
    def test_sql_injection_in_email(self):
        """Test SQL injection prevention in email field"""
        sql_payload = "admin' OR '1'='1"
        response = client.post(
            "/api/auth/login",
            data={"username": sql_payload, "password": "test"}
        )
        # Should fail authentication, not execute SQL
        assert response.status_code == 401
    
    def test_sql_injection_in_symbol(self, auth_headers):
        """Test SQL injection prevention in symbol parameter"""
        sql_payload = "'; DROP TABLE users; --"
        response = client.get(
            f"/api/signals/subscribed?symbol={sql_payload}",
            headers=auth_headers
        )
        # Should fail validation
        assert response.status_code in [400, 422]
    
    def test_sql_injection_in_tier_filter(self, admin_headers):
        """Test SQL injection prevention in tier filter"""
        sql_payload = "starter' OR '1'='1"
        response = client.get(
            f"/api/admin/users?tier={sql_payload}",
            headers=admin_headers
        )
        # Should fail validation
        assert response.status_code in [400, 422]


class TestPathTraversalPrevention:
    """Test path traversal attack prevention"""
    
    def test_path_traversal_in_signal_id(self):
        """Test path traversal prevention in signal ID"""
        path_traversal = "../../../etc/passwd"
        response = client.get(f"/api/signals/{path_traversal}")
        # Should fail validation
        assert response.status_code in [400, 404]
    
    def test_path_traversal_in_notification_id(self, auth_headers):
        """Test path traversal prevention in notification ID"""
        path_traversal = "../../../etc/passwd"
        response = client.delete(
            f"/api/notifications/{path_traversal}",
            headers=auth_headers
        )
        # Should fail validation
        assert response.status_code in [400, 404]
    
    def test_path_traversal_in_backtest_id(self):
        """Test path traversal prevention in backtest ID"""
        path_traversal = "../../../etc/passwd"
        response = client.get(f"/api/backtest/{path_traversal}")
        # Should fail validation
        assert response.status_code in [400, 404]


class TestCommandInjectionPrevention:
    """Test command injection attack prevention"""
    
    def test_command_injection_in_symbol(self, auth_headers):
        """Test command injection prevention in symbol"""
        cmd_payload = "AAPL; rm -rf /"
        response = client.get(
            f"/api/signals/subscribed?symbol={cmd_payload}",
            headers=auth_headers
        )
        # Should fail validation
        assert response.status_code in [400, 422]
    
    def test_command_injection_in_action(self, auth_headers):
        """Test command injection prevention in action"""
        cmd_payload = "BUY; cat /etc/passwd"
        response = client.get(
            f"/api/signals/subscribed?action={cmd_payload}",
            headers=auth_headers
        )
        # Should fail validation
        assert response.status_code in [400, 422]


class TestInputLengthLimits:
    """Test input length limit enforcement"""
    
    def test_very_long_email(self):
        """Test very long email is rejected"""
        long_email = "a" * 300 + "@example.com"
        response = client.post(
            "/api/auth/signup",
            json={
                "email": long_email,
                "password": "TestPassword123!",
                "full_name": "Test User"
            }
        )
        # Should fail validation
        assert response.status_code in [400, 422]
    
    def test_very_long_symbol(self, auth_headers):
        """Test very long symbol is rejected"""
        long_symbol = "A" * 100
        response = client.get(
            f"/api/signals/subscribed?symbol={long_symbol}",
            headers=auth_headers
        )
        # Should fail validation
        assert response.status_code in [400, 422]
    
    def test_very_long_notification_id(self, auth_headers):
        """Test very long notification ID is rejected"""
        long_id = "a" * 200
        response = client.delete(
            f"/api/notifications/{long_id}",
            headers=auth_headers
        )
        # Should fail validation
        assert response.status_code in [400, 404]

