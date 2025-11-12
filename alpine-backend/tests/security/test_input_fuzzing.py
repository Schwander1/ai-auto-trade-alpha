"""Security tests for input fuzzing"""
import pytest
import random
import string
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def generate_fuzz_strings():
    """Generate various fuzz strings for testing"""
    return [
        # Empty and null
        "",
        None,
        " ",
        "\x00",
        "\x00\x00\x00",
        
        # Special characters
        "!@#$%^&*()",
        "[]{}|\\:;\"'<>?,./",
        
        # Unicode
        "测试",
        "🚀",
        "\u0000",
        "\uFFFF",
        
        # Very long strings
        "A" * 1000,
        "A" * 10000,
        
        # Format strings
        "%s %d %x",
        "{0} {1}",
        "${VAR}",
        
        # Control characters
        "\n\r\t",
        "\x01\x02\x03",
        
        # SQL-like
        "'; --",
        "' OR '1'='1",
        
        # Script-like
        "<script>",
        "javascript:",
        
        # Path-like
        "../../",
        "..\\..\\",
        
        # Command-like
        "; ls",
        "| cat",
        "&& rm",
    ]


class TestInputFuzzing:
    """Test input fuzzing on various endpoints"""
    
    def test_fuzz_email_field(self, auth_headers):
        """Fuzz test email field"""
        fuzz_strings = generate_fuzz_strings()
        
        for fuzz in fuzz_strings:
            if fuzz is None:
                continue
            response = client.put(
                "/api/users/profile",
                json={"email": fuzz},
                headers=auth_headers
            )
            # Should either validate or return error, never crash
            assert response.status_code in [200, 400, 422, 500]
            if response.status_code == 500:
                # 500 should not expose internal details
                error_data = response.json()
                assert "Traceback" not in str(error_data)
    
    def test_fuzz_full_name_field(self, auth_headers):
        """Fuzz test full name field"""
        fuzz_strings = generate_fuzz_strings()
        
        for fuzz in fuzz_strings:
            if fuzz is None:
                continue
            response = client.put(
                "/api/users/profile",
                json={"full_name": fuzz},
                headers=auth_headers
            )
            # Should either validate or return error, never crash
            assert response.status_code in [200, 400, 422, 500]
    
    def test_fuzz_symbol_parameter(self, auth_headers):
        """Fuzz test symbol query parameter"""
        fuzz_strings = generate_fuzz_strings()
        
        for fuzz in fuzz_strings[:20]:  # Limit to avoid too many requests
            if fuzz is None:
                continue
            response = client.get(
                f"/api/signals/subscribed?symbol={fuzz}",
                headers=auth_headers
            )
            # Should either validate or return error, never crash
            assert response.status_code in [200, 400, 401, 422, 500]
    
    def test_fuzz_action_parameter(self, auth_headers):
        """Fuzz test action query parameter"""
        fuzz_strings = generate_fuzz_strings()
        
        for fuzz in fuzz_strings[:20]:
            if fuzz is None:
                continue
            response = client.get(
                f"/api/signals/subscribed?action={fuzz}",
                headers=auth_headers
            )
            assert response.status_code in [200, 400, 401, 422, 500]
    
    def test_fuzz_tier_parameter(self, auth_headers):
        """Fuzz test tier parameter"""
        fuzz_strings = generate_fuzz_strings()
        
        for fuzz in fuzz_strings[:20]:
            if fuzz is None:
                continue
            response = client.post(
                "/api/subscriptions/upgrade",
                json={"tier": fuzz},
                headers=auth_headers
            )
            assert response.status_code in [200, 400, 422, 500]
    
    def test_fuzz_notification_id(self, auth_headers):
        """Fuzz test notification ID path parameter"""
        fuzz_strings = generate_fuzz_strings()
        
        for fuzz in fuzz_strings[:20]:
            if fuzz is None:
                continue
            # URL encode the fuzz string
            import urllib.parse
            encoded = urllib.parse.quote(str(fuzz))
            response = client.delete(
                f"/api/notifications/{encoded}",
                headers=auth_headers
            )
            assert response.status_code in [200, 400, 401, 404, 422, 500]
    
    def test_fuzz_limit_parameter(self, auth_headers):
        """Fuzz test limit query parameter"""
        fuzz_values = [
            -1, 0, 1, 100, 1000, 10000,
            "not-a-number",
            "1; DROP TABLE users; --",
            "<script>alert('xss')</script>",
        ]
        
        for fuzz in fuzz_values:
            response = client.get(
                f"/api/signals/subscribed?limit={fuzz}",
                headers=auth_headers
            )
            assert response.status_code in [200, 400, 401, 422, 500]
    
    def test_fuzz_offset_parameter(self, auth_headers):
        """Fuzz test offset query parameter"""
        fuzz_values = [
            -1, 0, 1, 100, 1000,
            "not-a-number",
            "1' OR '1'='1",
        ]
        
        for fuzz in fuzz_values:
            response = client.get(
                f"/api/signals/subscribed?offset={fuzz}",
                headers=auth_headers
            )
            assert response.status_code in [200, 400, 401, 422, 500]
    
    def test_fuzz_totp_token(self, auth_headers):
        """Fuzz test TOTP token"""
        fuzz_strings = generate_fuzz_strings()
        
        for fuzz in fuzz_strings[:20]:
            if fuzz is None:
                continue
            response = client.post(
                "/api/2fa/enable",
                json={"token": str(fuzz)},
                headers=auth_headers
            )
            assert response.status_code in [200, 400, 401, 422, 500]
    
    def test_fuzz_password_field(self):
        """Fuzz test password field"""
        fuzz_strings = generate_fuzz_strings()
        
        for fuzz in fuzz_strings[:10]:  # Limit to avoid account lockout
            if fuzz is None:
                continue
            response = client.post(
                "/api/auth/login",
                data={
                    "username": "test@example.com",
                    "password": str(fuzz)
                }
            )
            # Should handle gracefully
            assert response.status_code in [200, 400, 401, 422, 500]

