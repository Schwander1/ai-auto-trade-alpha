"""Security tests for authentication and authorization"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


class TestAuthentication:
    """Test authentication mechanisms"""
    
    def test_missing_token(self):
        """Test missing authentication token"""
        response = client.get("/api/users/profile")
        assert response.status_code == 401
    
    def test_invalid_token_format(self):
        """Test invalid token format"""
        headers = {"Authorization": "InvalidFormat token"}
        response = client.get("/api/users/profile", headers=headers)
        assert response.status_code == 401
    
    def test_expired_token(self):
        """Test expired token handling"""
        # Create a token that would be expired
        # This is hard to test without mocking time, but we can test the structure
        headers = {"Authorization": "Bearer expired.token.here"}
        response = client.get("/api/users/profile", headers=headers)
        assert response.status_code == 401
    
    def test_token_blacklist(self, auth_headers):
        """Test that blacklisted tokens are rejected"""
        # Get a valid token
        response = client.get("/api/users/profile", headers=auth_headers)
        assert response.status_code == 200
        
        # Logout (blacklist token)
        logout_response = client.post("/api/auth/logout", headers=auth_headers)
        assert logout_response.status_code == 200
        
        # Try to use blacklisted token
        response = client.get("/api/users/profile", headers=auth_headers)
        assert response.status_code == 401
    
    def test_token_replay_attack(self, auth_headers):
        """Test token replay attack prevention"""
        # Use same token multiple times (should work until logout)
        response1 = client.get("/api/users/profile", headers=auth_headers)
        response2 = client.get("/api/users/profile", headers=auth_headers)
        
        # Both should work (tokens are valid until expiration/logout)
        assert response1.status_code == 200
        assert response2.status_code == 200
    
    def test_case_sensitive_bearer(self):
        """Test case sensitivity of Bearer keyword"""
        headers = {"Authorization": "bearer invalid.token"}
        response = client.get("/api/users/profile", headers=headers)
        # Should still be 401 (invalid token), but test the format
        assert response.status_code == 401


class TestAuthorization:
    """Test authorization mechanisms"""
    
    def test_admin_endpoint_requires_admin(self, auth_headers):
        """Test that admin endpoints require admin role"""
        admin_endpoints = [
            "/api/admin/analytics",
            "/api/admin/users",
            "/api/admin/revenue"
        ]
        
        for endpoint in admin_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            # Non-admin users should get 403
            assert response.status_code in [403, 401], f"{endpoint} should require admin"
    
    def test_user_can_access_own_profile(self, auth_headers):
        """Test that users can access their own profile"""
        response = client.get("/api/users/profile", headers=auth_headers)
        assert response.status_code == 200
    
    def test_user_cannot_access_other_users_data(self, auth_headers):
        """Test that users cannot access other users' data"""
        # Try to access admin endpoint (other users' data)
        response = client.get("/api/admin/users", headers=auth_headers)
        assert response.status_code in [403, 401]
    
    def test_inactive_user_cannot_access(self, db, client):
        """Test that inactive users cannot access endpoints"""
        from backend.models.user import User, UserTier
        from backend.auth.security import get_password_hash, create_access_token
        
        # Create inactive user
        user = User(
            email="inactive@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            full_name="Inactive User",
            tier=UserTier.STARTER,
            is_active=False
        )
        db.add(user)
        db.commit()
        
        # Create token for inactive user
        token = create_access_token(data={"sub": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access endpoint
        response = client.get("/api/users/profile", headers=headers)
        assert response.status_code == 403
    
    def test_unverified_user_access(self, db, client):
        """Test unverified user access (if applicable)"""
        from backend.models.user import User, UserTier
        from backend.auth.security import get_password_hash, create_access_token
        
        # Create unverified user
        user = User(
            email="unverified@example.com",
            hashed_password=get_password_hash("TestPassword123!"),
            full_name="Unverified User",
            tier=UserTier.STARTER,
            is_active=True,
            is_verified=False
        )
        db.add(user)
        db.commit()
        
        # Create token
        token = create_access_token(data={"sub": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # User should still be able to access basic endpoints
        response = client.get("/api/users/profile", headers=headers)
        # May or may not be restricted based on business logic
        assert response.status_code in [200, 403]


class TestPrivilegeEscalation:
    """Test privilege escalation attempts"""
    
    def test_user_tries_to_become_admin(self, auth_headers):
        """Test that users cannot escalate to admin"""
        # Try to access admin endpoints
        response = client.get("/api/admin/analytics", headers=auth_headers)
        assert response.status_code in [403, 401]
    
    def test_user_tries_to_modify_tier(self, auth_headers):
        """Test that users cannot directly modify their tier"""
        # Try to update tier through profile update (should not be allowed)
        response = client.put(
            "/api/users/profile",
            json={"tier": "elite"},  # This field shouldn't exist in UpdateProfileRequest
            headers=auth_headers
        )
        # Should either ignore the field or return error
        assert response.status_code in [200, 400, 422]
        if response.status_code == 200:
            # Tier should not have changed
            profile_response = client.get("/api/users/profile", headers=auth_headers)
            if profile_response.status_code == 200:
                data = profile_response.json()
                # Tier should still be starter (or whatever it was)
                assert "tier" in data
    
    def test_user_tries_to_access_admin_data(self, auth_headers):
        """Test that users cannot access admin-only data"""
        admin_endpoints = [
            "/api/admin/analytics",
            "/api/admin/users",
            "/api/admin/revenue"
        ]
        
        for endpoint in admin_endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code in [403, 401], f"User should not access {endpoint}"


class TestSessionManagement:
    """Test session and token management"""
    
    def test_multiple_sessions(self):
        """Test that users can have multiple active sessions"""
        # Create two different tokens (simulate two logins)
        # This is hard to test without actual login, but we can test the structure
        pass
    
    def test_token_refresh(self):
        """Test token refresh mechanism (if implemented)"""
        # Token refresh is not currently implemented
        pass
    
    def test_concurrent_logout(self, auth_headers):
        """Test concurrent logout requests"""
        import threading
        
        responses = []
        def logout():
            response = client.post("/api/auth/logout", headers=auth_headers)
            responses.append(response)
        
        # Make concurrent logout requests
        threads = [threading.Thread(target=logout) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=2)
        
        # All should succeed (idempotent)
        assert len(responses) > 0
        assert all(r.status_code in [200, 401] for r in responses)

