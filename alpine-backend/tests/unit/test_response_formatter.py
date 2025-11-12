"""Unit tests for response formatter functions"""
import pytest
from fastapi import Response, Request
from unittest.mock import Mock, MagicMock
from backend.core.response_formatter import (
    format_error_response,
    add_rate_limit_headers,
    format_paginated_response
)


class TestFormatErrorResponse:
    """Test format_error_response function"""
    
    def test_basic_error_response(self):
        """Test basic error response formatting"""
        result = format_error_response(400, "Bad Request")
        assert result["error"]["code"] == 400
        assert result["error"]["message"] == "Bad Request"
        assert "timestamp" in result["error"]
    
    def test_error_response_with_details(self):
        """Test error response with details"""
        details = {"field": "email", "reason": "invalid format"}
        result = format_error_response(400, "Validation Error", details=details)
        assert result["error"]["details"] == details
    
    def test_error_response_with_request(self):
        """Test error response with request ID"""
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-Request-ID": "req-123"}
        
        # Mock get_request_id to return the request ID from headers
        from unittest.mock import patch
        with patch('backend.core.response_formatter.get_request_id', return_value="req-123"):
            result = format_error_response(400, "Error", request=mock_request)
            assert result["error"]["request_id"] == "req-123"
    
    def test_error_response_timestamp_format(self):
        """Test error response timestamp format"""
        result = format_error_response(400, "Error")
        timestamp = result["error"]["timestamp"]
        assert timestamp.endswith("Z")
        assert "T" in timestamp


class TestAddRateLimitHeaders:
    """Test add_rate_limit_headers function"""
    
    def test_add_rate_limit_headers(self):
        """Test adding rate limit headers"""
        response = Response()
        result = add_rate_limit_headers(response, remaining=50, reset_at=1234567890)
        
        assert result.headers["X-RateLimit-Remaining"] == "50"
        assert result.headers["X-RateLimit-Reset"] == "1234567890"
    
    def test_add_rate_limit_headers_without_reset(self):
        """Test adding rate limit headers without reset time"""
        response = Response()
        result = add_rate_limit_headers(response, remaining=50)
        
        assert result.headers["X-RateLimit-Remaining"] == "50"
        assert "X-RateLimit-Reset" not in result.headers
    
    def test_add_rate_limit_headers_zero_remaining(self):
        """Test adding rate limit headers with zero remaining"""
        response = Response()
        result = add_rate_limit_headers(response, remaining=0, reset_at=1234567890)
        
        assert result.headers["X-RateLimit-Remaining"] == "0"
    
    def test_add_rate_limit_headers_negative_remaining(self):
        """Test adding rate limit headers with negative remaining"""
        response = Response()
        result = add_rate_limit_headers(response, remaining=-1, reset_at=1234567890)
        
        assert result.headers["X-RateLimit-Remaining"] == "-1"


class TestFormatPaginatedResponse:
    """Test format_paginated_response function"""
    
    def test_basic_paginated_response(self):
        """Test basic paginated response formatting"""
        items = [{"id": 1}, {"id": 2}]
        result = format_paginated_response(items, total=10, limit=2, offset=0)
        
        assert result["items"] == items
        assert result["pagination"]["total"] == 10
        assert result["pagination"]["limit"] == 2
        assert result["pagination"]["offset"] == 0
        assert result["pagination"]["has_more"] is True
        assert "timestamp" in result
    
    def test_paginated_response_has_more_false(self):
        """Test paginated response with has_more=False"""
        items = [{"id": 1}, {"id": 2}]
        result = format_paginated_response(items, total=2, limit=2, offset=0)
        
        assert result["pagination"]["has_more"] is False
    
    def test_paginated_response_page_calculation(self):
        """Test paginated response page calculation"""
        items = [{"id": 1}]
        result = format_paginated_response(items, total=10, limit=2, offset=4)
        
        assert result["pagination"]["page"] == 3  # (4 // 2) + 1
        assert result["pagination"]["total_pages"] == 5  # (10 + 2 - 1) // 2
    
    def test_paginated_response_with_request(self):
        """Test paginated response with request ID"""
        mock_request = Mock(spec=Request)
        
        # Mock get_request_id
        from unittest.mock import patch
        with patch('backend.core.response_formatter.get_request_id', return_value="req-456"):
            items = [{"id": 1}]
            result = format_paginated_response(items, total=10, limit=2, offset=0, request=mock_request)
            assert result["request_id"] == "req-456"
    
    def test_paginated_response_zero_limit(self):
        """Test paginated response with zero limit"""
        items = []
        result = format_paginated_response(items, total=10, limit=0, offset=0)
        
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["total_pages"] == 1
    
    def test_paginated_response_empty_items(self):
        """Test paginated response with empty items"""
        items = []
        result = format_paginated_response(items, total=0, limit=10, offset=0)
        
        assert result["items"] == []
        assert result["pagination"]["total"] == 0
        assert result["pagination"]["has_more"] is False

