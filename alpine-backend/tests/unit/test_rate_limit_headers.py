"""Unit tests for rate limit header generation"""
import pytest
from fastapi import Response
from backend.core.response_formatter import add_rate_limit_headers
from backend.core.rate_limit import get_rate_limit_status


class TestRateLimitHeaders:
    """Test rate limit header generation"""
    
    def test_add_rate_limit_headers_basic(self):
        """Test basic rate limit header addition"""
        response = Response()
        result = add_rate_limit_headers(response, remaining=50, reset_at=1234567890)
        
        assert "X-RateLimit-Remaining" in result.headers
        assert result.headers["X-RateLimit-Remaining"] == "50"
        assert "X-RateLimit-Reset" in result.headers
        assert result.headers["X-RateLimit-Reset"] == "1234567890"
    
    def test_add_rate_limit_headers_without_reset(self):
        """Test rate limit headers without reset time"""
        response = Response()
        result = add_rate_limit_headers(response, remaining=25)
        
        assert "X-RateLimit-Remaining" in result.headers
        assert result.headers["X-RateLimit-Remaining"] == "25"
        assert "X-RateLimit-Reset" not in result.headers
    
    def test_add_rate_limit_headers_zero_remaining(self):
        """Test rate limit headers with zero remaining"""
        response = Response()
        result = add_rate_limit_headers(response, remaining=0, reset_at=1234567890)
        
        assert result.headers["X-RateLimit-Remaining"] == "0"
    
    def test_add_rate_limit_headers_negative_remaining(self):
        """Test rate limit headers with negative remaining (edge case)"""
        response = Response()
        result = add_rate_limit_headers(response, remaining=-1, reset_at=1234567890)
        
        assert result.headers["X-RateLimit-Remaining"] == "-1"
    
    def test_add_rate_limit_headers_max_remaining(self):
        """Test rate limit headers with max remaining"""
        response = Response()
        result = add_rate_limit_headers(response, remaining=100, reset_at=1234567890)
        
        assert result.headers["X-RateLimit-Remaining"] == "100"
    
    def test_add_rate_limit_headers_preserves_existing_headers(self):
        """Test that existing headers are preserved"""
        response = Response()
        response.headers["X-Custom-Header"] = "custom-value"
        result = add_rate_limit_headers(response, remaining=50, reset_at=1234567890)
        
        assert result.headers["X-Custom-Header"] == "custom-value"
        assert result.headers["X-RateLimit-Remaining"] == "50"
    
    def test_add_rate_limit_headers_string_conversion(self):
        """Test that numeric values are converted to strings"""
        response = Response()
        result = add_rate_limit_headers(response, remaining=50, reset_at=1234567890)
        
        assert isinstance(result.headers["X-RateLimit-Remaining"], str)
        assert isinstance(result.headers["X-RateLimit-Reset"], str)


class TestGetRateLimitStatus:
    """Test get_rate_limit_status function"""
    
    def test_get_rate_limit_status_structure(self):
        """Test that get_rate_limit_status returns correct structure"""
        # This will use the fallback when Redis is not available
        status = get_rate_limit_status("test-client")
        
        assert "current" in status
        assert "remaining" in status
        assert "reset_in" in status
        assert isinstance(status["remaining"], int)
        assert isinstance(status["reset_in"], int)

