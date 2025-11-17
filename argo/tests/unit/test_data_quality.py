"""
Unit tests for Data Quality Monitoring
"""
import pytest
from datetime import datetime, timedelta
from argo.validation.data_quality import DataQualityMonitor, DataQualityIssue

@pytest.mark.asyncio
async def test_freshness_check():
    """Test that stale signals are detected"""
    monitor = DataQualityMonitor()
    
    # Fresh signal
    fresh_signal = {
        'source': 'test',
        'symbol': 'AAPL',
        'direction': 'LONG',
        'confidence': 75.0,
        'timestamp': datetime.now().isoformat()
    }
    is_valid, issue = await monitor.validate_signal(fresh_signal, {})
    assert is_valid, "Fresh signal should be valid"
    
    # Stale signal
    stale_signal = {
        'source': 'test',
        'symbol': 'AAPL',
        'direction': 'LONG',
        'confidence': 75.0,
        'timestamp': (datetime.now() - timedelta(seconds=400)).isoformat()  # 400s > 300s limit
    }
    is_valid, issue = await monitor.validate_signal(stale_signal, {})
    assert not is_valid, "Stale signal should be invalid"
    assert issue.issue_type == "staleness"

@pytest.mark.asyncio
async def test_price_consistency_check():
    """Test that price anomalies are detected"""
    monitor = DataQualityMonitor()
    
    signal = {
        'source': 'test',
        'symbol': 'AAPL',
        'direction': 'LONG',
        'confidence': 75.0,
        'timestamp': datetime.now().isoformat(),
        'price': 175.0
    }
    
    # Consistent price
    market_data = {'price': 175.5}  # 0.3% deviation
    is_valid, issue = await monitor.validate_signal(signal, market_data)
    assert is_valid, "Consistent price should be valid"
    
    # Inconsistent price
    market_data = {'price': 200.0}  # 14% deviation > 5% limit
    is_valid, issue = await monitor.validate_signal(signal, market_data)
    assert not is_valid, "Inconsistent price should be invalid"
    assert issue.issue_type == "price_anomaly"

@pytest.mark.asyncio
async def test_confidence_check():
    """Test that low confidence signals are detected"""
    monitor = DataQualityMonitor()
    
    # High confidence
    signal = {
        'source': 'test',
        'symbol': 'AAPL',
        'direction': 'LONG',
        'confidence': 75.0,
        'timestamp': datetime.now().isoformat()
    }
    is_valid, issue = await monitor.validate_signal(signal, {})
    assert is_valid, "High confidence signal should be valid"
    
    # Low confidence
    signal['confidence'] = 50.0  # < 60.0 minimum
    is_valid, issue = await monitor.validate_signal(signal, {})
    assert not is_valid, "Low confidence signal should be invalid"
    assert issue.issue_type == "low_confidence"

@pytest.mark.asyncio
async def test_completeness_check():
    """Test that incomplete signals are detected"""
    monitor = DataQualityMonitor()
    
    # Complete signal
    signal = {
        'source': 'test',
        'symbol': 'AAPL',
        'direction': 'LONG',
        'confidence': 75.0,
        'timestamp': datetime.now().isoformat()
    }
    is_valid, issue = await monitor.validate_signal(signal, {})
    assert is_valid, "Complete signal should be valid"
    
    # Missing field
    del signal['direction']
    is_valid, issue = await monitor.validate_signal(signal, {})
    assert not is_valid, "Incomplete signal should be invalid"
    assert issue.issue_type == "incomplete_data"

@pytest.mark.asyncio
async def test_source_health_status():
    """Test that source health is calculated correctly"""
    monitor = DataQualityMonitor()
    
    # Add some issues
    for i in range(5):
        issue = DataQualityIssue(
            source='test_source',
            issue_type='test',
            severity='high',
            description='Test issue',
            timestamp=datetime.now()
        )
        monitor.quality_issues.append(issue)
    
    health = monitor.get_source_health_status()
    assert 'test_source' in health
    assert health['test_source']['high_issues'] == 5
    assert health['test_source']['health_score'] < 100

