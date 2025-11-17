"""
Unit tests for Performance Budget Monitoring
"""
import pytest
import time
from argo.core.performance_budget_monitor import (
    PerformanceMonitor,
    get_performance_monitor
)

def test_performance_measurement():
    """Test that performance is measured correctly"""
    monitor = PerformanceMonitor()
    
    with monitor.measure("signal_generation"):
        time.sleep(0.1)  # Simulate 100ms operation
    
    stats = monitor.get_statistics("signal_generation")
    assert stats['count'] == 1
    assert stats['mean_ms'] >= 100  # Should be at least 100ms

def test_budget_violation():
    """Test that budget violations are detected"""
    monitor = PerformanceMonitor()
    
    # Simulate slow operation (exceeds 500ms budget)
    with monitor.measure("signal_generation"):
        time.sleep(0.6)  # 600ms > 500ms budget
    
    stats = monitor.get_statistics("signal_generation")
    assert stats['budget_violations'] == 1
    assert stats['budget_violation_rate'] == 100.0

def test_percentile_calculation():
    """Test that percentiles are calculated correctly"""
    monitor = PerformanceMonitor()
    
    # Add multiple measurements
    for duration in [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]:
        monitor.record_measurement("signal_generation", duration)
    
    stats = monitor.get_statistics("signal_generation")
    assert stats['p95_ms'] >= stats['mean_ms']
    assert stats['p99_ms'] >= stats['p95_ms']
    assert stats['max_ms'] == 500

def test_global_instance():
    """Test that global instance works"""
    monitor1 = get_performance_monitor()
    monitor2 = get_performance_monitor()
    
    # Should be same instance
    assert monitor1 is monitor2

def test_reset():
    """Test that reset clears measurements"""
    monitor = PerformanceMonitor()
    
    monitor.record_measurement("signal_generation", 100)
    assert monitor.get_statistics("signal_generation")['count'] == 1
    
    monitor.reset()
    assert monitor.get_statistics("signal_generation")['count'] == 0

