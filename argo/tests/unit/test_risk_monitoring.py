"""
Unit tests for Prop Firm Risk Monitoring
"""
import pytest
import asyncio
from argo.risk.prop_firm_risk_monitor import (
    PropFirmRiskMonitor,
    RiskLevel,
    RiskMetrics
)
from datetime import datetime

@pytest.mark.asyncio
async def test_risk_level_assessment():
    """Test that risk levels are assessed correctly"""
    config = {
        "max_drawdown_pct": 2.0,
        "daily_loss_limit_pct": 4.5,
        "initial_capital": 25000.0
    }
    monitor = PropFirmRiskMonitor(config)
    
    # Normal risk
    metrics = RiskMetrics(
        timestamp=datetime.now(),
        current_drawdown=0.5,
        daily_pnl_pct=-1.0,
        open_positions=2,
        correlated_positions=0,
        largest_position_size=5.0,
        portfolio_correlation=0.2,
        risk_level=RiskLevel.NORMAL
    )
    level = monitor._assess_risk_level(metrics)
    assert level == RiskLevel.NORMAL
    
    # Warning level (70% of max)
    metrics.current_drawdown = 1.4  # 70% of 2.0
    level = monitor._assess_risk_level(metrics)
    assert level == RiskLevel.WARNING
    
    # Critical level (90% of max)
    metrics.current_drawdown = 1.8  # 90% of 2.0
    level = monitor._assess_risk_level(metrics)
    assert level == RiskLevel.CRITICAL
    
    # Breach level
    metrics.current_drawdown = 2.1  # Exceeds 2.0
    level = monitor._assess_risk_level(metrics)
    assert level == RiskLevel.BREACH

@pytest.mark.asyncio
async def test_equity_tracking():
    """Test that equity is tracked correctly"""
    config = {
        "max_drawdown_pct": 2.0,
        "daily_loss_limit_pct": 4.5,
        "initial_capital": 25000.0
    }
    monitor = PropFirmRiskMonitor(config)
    
    assert monitor.current_equity == 25000.0
    assert monitor.peak_equity == 25000.0
    
    # Update equity
    monitor.update_equity(26000.0)
    assert monitor.current_equity == 26000.0
    assert monitor.peak_equity == 26000.0
    
    # Drawdown scenario
    monitor.update_equity(24500.0)
    assert monitor.current_equity == 24500.0
    assert monitor.peak_equity == 26000.0  # Peak should remain

@pytest.mark.asyncio
async def test_monitoring_start_stop():
    """Test that monitoring can be started and stopped"""
    config = {
        "max_drawdown_pct": 2.0,
        "daily_loss_limit_pct": 4.5,
        "initial_capital": 25000.0
    }
    monitor = PropFirmRiskMonitor(config)
    
    assert not monitor.monitoring_active
    
    # Start monitoring
    await monitor.start_monitoring()
    assert monitor.monitoring_active
    
    # Wait a bit
    await asyncio.sleep(0.5)
    
    # Stop monitoring
    await monitor.stop_monitoring()
    assert not monitor.monitoring_active

@pytest.mark.asyncio
async def test_metrics_collection():
    """Test that metrics are collected correctly"""
    config = {
        "max_drawdown_pct": 2.0,
        "daily_loss_limit_pct": 4.5,
        "initial_capital": 25000.0
    }
    monitor = PropFirmRiskMonitor(config)
    
    monitor.update_equity(25000.0)
    metrics = await monitor._collect_metrics()
    
    assert metrics.current_drawdown == 0.0
    assert metrics.daily_pnl_pct == 0.0
    assert metrics.account_equity == 25000.0

