"""
Unit tests for Chinese Models Rate Limiting
"""
import pytest
import asyncio
from argo.core.data_sources.chinese_models_source import (
    ChineseModelsDataSource,
    APIRateLimiter,
    APICostConfig
)

@pytest.mark.asyncio
async def test_rate_limiting_enforced():
    """Test that rate limiting prevents excessive API calls"""
    config = APICostConfig(requests_per_minute=5, cost_per_request=0.001)
    limiter = APIRateLimiter(config)
    
    # Make 5 requests (should all succeed)
    for i in range(5):
        allowed, _ = await limiter.acquire()
        assert allowed, f"Request {i+1} should be allowed"
        
    # 6th request should be rate limited
    allowed, wait_time = await limiter.acquire()
    assert not allowed, "6th request should be rate limited"
    assert wait_time is not None, "Should provide wait time"
    
@pytest.mark.asyncio
async def test_daily_budget_enforced():
    """Test that daily budget prevents overspending"""
    config = APICostConfig(
        requests_per_minute=100,
        cost_per_request=10.0,  # High cost for testing
        daily_budget=50.0
    )
    limiter = APIRateLimiter(config)
    
    # Make 5 requests (should succeed, $50 total)
    for i in range(5):
        allowed, _ = await limiter.acquire()
        assert allowed, f"Request {i+1} should be allowed"
        
    # 6th request should exceed budget
    allowed, _ = await limiter.acquire()
    assert not allowed, "Request should be blocked by budget"
    
@pytest.mark.asyncio
async def test_cost_tracking():
    """Test that costs are tracked correctly"""
    config = APICostConfig(
        requests_per_minute=100,
        cost_per_request=0.50,
        daily_budget=100.0
    )
    limiter = APIRateLimiter(config)
    
    # Make 10 requests
    for i in range(10):
        await limiter.acquire()
        
    stats = limiter.get_cost_stats()
    assert stats['total_requests'] == 10
    assert stats['total_cost'] == 5.0  # 10 * 0.50
    assert stats['daily_cost'] == 5.0

@pytest.mark.asyncio
async def test_fallback_mechanism():
    """Test that system falls back to next model when rate limited"""
    source = ChineseModelsDataSource({
        'qwen_rpm': 0,  # Force rate limit on Qwen
        'glm_rpm': 10,
        'baichuan_rpm': 10
    })
    
    # Should fall back to GLM or Baichuan
    signal = await source.get_signal("AAPL", {})
    # Signal should be returned from fallback model
    assert signal is not None

@pytest.mark.asyncio
async def test_cache_functionality():
    """Test that caching works correctly"""
    source = ChineseModelsDataSource()
    
    # First call should hit API
    signal1 = await source.get_signal("AAPL", {})
    assert signal1 is not None
    
    # Second call should use cache (within TTL)
    signal2 = await source.get_signal("AAPL", {})
    assert signal2 is not None
    # Should be same signal (cached)
    assert signal1['source'] == signal2['source']

