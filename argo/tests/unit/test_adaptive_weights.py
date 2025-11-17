"""
Unit tests for Adaptive Weight Management
"""
import pytest
from argo.core.adaptive_weight_manager import AdaptiveWeightManager

def test_initial_weights():
    """Test that initial weights are set correctly"""
    initial_weights = {
        'source1': 0.4,
        'source2': 0.3,
        'source3': 0.3
    }
    manager = AdaptiveWeightManager(initial_weights)
    
    assert manager.get_weight('source1') == 0.4
    assert manager.get_weight('source2') == 0.3
    assert manager.get_weight('source3') == 0.3

def test_performance_update():
    """Test that performance updates are recorded"""
    initial_weights = {
        'source1': 0.5,
        'source2': 0.5
    }
    manager = AdaptiveWeightManager(initial_weights)
    
    # Update performance
    manager.update_performance('source1', was_correct=True, confidence=80.0)
    manager.update_performance('source2', was_correct=False, confidence=70.0)
    
    # Check that performance was recorded
    assert len(manager.performance_history['source1']) == 1
    assert len(manager.performance_history['source2']) == 1

def test_weight_adjustment():
    """Test that weights adjust based on performance"""
    initial_weights = {
        'source1': 0.5,
        'source2': 0.5
    }
    manager = AdaptiveWeightManager(initial_weights)
    
    # Make source1 perform well
    for _ in range(20):
        manager.update_performance('source1', was_correct=True, confidence=80.0)
        manager.update_performance('source2', was_correct=False, confidence=70.0)
    
    # Adjust weights
    new_weights = manager.adjust_weights()
    
    # Source1 should have higher weight
    assert new_weights['source1'] > new_weights['source2']
    # Weights should still sum to ~1.0
    assert abs(sum(new_weights.values()) - 1.0) < 0.01

def test_weight_bounds():
    """Test that weights stay within bounds"""
    initial_weights = {
        'source1': 0.1,
        'source2': 0.9
    }
    manager = AdaptiveWeightManager(initial_weights)
    
    # Make source2 perform extremely poorly
    for _ in range(50):
        manager.update_performance('source1', was_correct=True, confidence=90.0)
        manager.update_performance('source2', was_correct=False, confidence=50.0)
    
    new_weights = manager.adjust_weights()
    
    # Source2 should not go below min_weight
    assert new_weights['source2'] >= manager.min_weight
    # Source1 should not exceed max_weight
    assert new_weights['source1'] <= manager.max_weight

def test_performance_report():
    """Test that performance report is generated correctly"""
    initial_weights = {
        'source1': 0.5,
        'source2': 0.5
    }
    manager = AdaptiveWeightManager(initial_weights)
    
    # Add some performance data
    for _ in range(10):
        manager.update_performance('source1', was_correct=True, confidence=80.0)
    
    report = manager.get_performance_report()
    
    assert 'source1' in report
    assert report['source1']['sample_size'] == 10
    assert report['source1']['accuracy'] > 0

