"""Penetration tests for all endpoints"""
import pytest
import random
import string
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


class TestPenetrationTesting:
    """Penetration tests for endpoint security"""
    
    def test_unauthorized_access_attempts(self):
        """Test unauthorized access attempts"""
        protected_endpoints = [
            "/api/users/profile",
            "/api/subscriptions/plan",
            "/api/signals/subscribed",
            "/api/admin/analytics",
            "/api/2fa/status"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"{endpoint} should require authentication"
    
    def test_invalid_token_attempts(self):
        """Test invalid token attempts"""
        invalid_tokens = [
            "invalid-token",
            "Bearer invalid",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "",
            "Bearer ",
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": token}
            response = client.get("/api/users/profile", headers=headers)
            assert response.status_code == 401, f"Invalid token should be rejected: {token[:20]}"
    
    def test_admin_endpoint_protection(self, auth_headers):
        """Test admin endpoints are protected"""
        admin_endpoints = [
            "/api/admin/analytics",
            "/api/admin/users",
            "/api/admin/revenue"
        ]
        
        for endpoint in admin_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            # Should be 403 (forbidden) for non-admin users
            assert response.status_code in [403, 401], f"{endpoint} should require admin access"
    
    def test_sql_injection_attempts(self, auth_headers):
        """Test SQL injection attempts"""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "1' OR '1'='1",
            "admin'--",
            "' OR 1=1--",
        ]
        
        for payload in sql_payloads:
            # Test in email field
            response = client.put(
                "/api/users/profile",
                json={"email": payload},
                headers=auth_headers
            )
            assert response.status_code in [400, 422], f"SQL injection should be blocked: {payload[:20]}"
            
            # Test in symbol parameter
            response = client.get(
                f"/api/signals/subscribed?symbol={payload}",
                headers=auth_headers
            )
            assert response.status_code in [400, 422], f"SQL injection should be blocked in symbol: {payload[:20]}"
    
    def test_xss_attempts(self, auth_headers):
        """Test XSS attack attempts"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "'\"><script>alert('xss')</script>",
        ]
        
        for payload in xss_payloads:
            # Test in full_name field
            response = client.put(
                "/api/users/profile",
                json={"full_name": payload},
                headers=auth_headers
            )
            if response.status_code == 200:
                # If accepted, should be escaped
                data = response.json()
                assert "<script>" not in data.get("full_name", ""), "XSS should be escaped"
    
    def test_path_traversal_attempts(self):
        """Test path traversal attempts"""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//etc/passwd",
            "/etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",  # URL encoded
        ]
        
        for payload in traversal_payloads:
            # Test in signal ID
            response = client.get(f"/api/signals/{payload}")
            assert response.status_code in [400, 404], f"Path traversal should be blocked: {payload[:20]}"
            
            # Test in notification ID (requires auth, but we test the path)
            response = client.delete(f"/api/notifications/{payload}")
            assert response.status_code in [400, 401, 404], f"Path traversal should be blocked: {payload[:20]}"
    
    def test_command_injection_attempts(self, auth_headers):
        """Test command injection attempts"""
        command_payloads = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "&& ls -la",
            "`whoami`",
            "$(id)",
        ]
        
        for payload in command_payloads:
            # Test in symbol parameter
            response = client.get(
                f"/api/signals/subscribed?symbol=AAPL{payload}",
                headers=auth_headers
            )
            assert response.status_code in [400, 422], f"Command injection should be blocked: {payload[:20]}"
    
    def test_ldap_injection_attempts(self, auth_headers):
        """Test LDAP injection attempts"""
        ldap_payloads = [
            "*)(&",
            "*))%00",
            "admin)(&(password=*",
        ]
        
        for payload in ldap_payloads:
            # Test in email field
            response = client.put(
                "/api/users/profile",
                json={"email": f"test{payload}@example.com"},
                headers=auth_headers
            )
            assert response.status_code in [400, 422], f"LDAP injection should be blocked: {payload[:20]}"
    
    def test_xml_injection_attempts(self, auth_headers):
        """Test XML injection attempts"""
        xml_payloads = [
            "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><foo>&xxe;</foo>",
            "<!ENTITY xxe SYSTEM 'file:///etc/passwd'>",
        ]
        
        for payload in xml_payloads:
            # Test in full_name field
            response = client.put(
                "/api/users/profile",
                json={"full_name": payload},
                headers=auth_headers
            )
            # Should be sanitized or rejected
            assert response.status_code in [200, 400, 422]
            if response.status_code == 200:
                data = response.json()
                assert "<!ENTITY" not in data.get("full_name", ""), "XML injection should be blocked"

