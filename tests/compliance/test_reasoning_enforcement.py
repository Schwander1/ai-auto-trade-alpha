"""
Test suite for reasoning enforcement
Tests that all signals have meaningful reasoning
"""
import pytest
from backend.models.signal import Signal
from sqlalchemy.exc import StatementError


class TestReasoningEnforcement:
    """Test reasoning validation and enforcement"""
    
    def test_reasoning_required(self):
        """Test that reasoning is required (not nullable)"""
        # This test verifies the database constraint
        # In practice, this would be tested with actual database operations
        signal = Signal(
            symbol='TEST',
            action='BUY',
            price=100.0,
            confidence=0.95,
            rationale=None  # Should fail validation
        )
        
        # Validate should raise error
        with pytest.raises((ValueError, StatementError)):
            signal.validate_reasoning('rationale', None)
    
    def test_reasoning_minimum_length(self):
        """Test that reasoning must be at least 20 characters"""
        signal = Signal(
            symbol='TEST',
            action='BUY',
            price=100.0,
            confidence=0.95,
            rationale='Short'  # Too short
        )
        
        # Validate should raise error
        with pytest.raises(ValueError) as exc_info:
            signal.validate_reasoning('rationale', 'Short')
        
        assert '20 characters' in str(exc_info.value).lower()
    
    def test_reasoning_valid(self):
        """Test that valid reasoning passes validation"""
        signal = Signal(
            symbol='TEST',
            action='BUY',
            price=100.0,
            confidence=0.95,
            rationale='This is a valid reasoning that is longer than 20 characters and explains the signal.'
        )
        
        # Validate should pass
        result = signal.validate_reasoning('rationale', signal.rationale)
        assert len(result) >= 20, "Reasoning should be at least 20 characters"
        assert result == signal.rationale.strip(), "Reasoning should be trimmed"
    
    def test_explainer_always_returns_reasoning(self):
        """Test that explainer always returns meaningful reasoning"""
        from argo.ai.explainer import SignalExplainer
        
        explainer = SignalExplainer()
        
        signal = {
            'symbol': 'AAPL',
            'action': 'BUY',
            'entry': 175.50,
            'stop_loss': 171.00,
            'take_profit': 184.25,
            'confidence': 95.5
        }
        
        reasoning = explainer.explain_signal(signal)
        
        # Verify reasoning is not empty
        assert reasoning is not None, "Reasoning should not be None"
        assert len(reasoning.strip()) >= 20, "Reasoning should be at least 20 characters"
        assert 'AAPL' in reasoning or 'BUY' in reasoning, "Reasoning should mention signal details"
    
    def test_explainer_fallback_reasoning(self):
        """Test that fallback reasoning is used when LLM fails"""
        from argo.ai.explainer import SignalExplainer
        
        explainer = SignalExplainer()
        explainer.enabled = False  # Disable LLM to force fallback
        
        signal = {
            'symbol': 'NVDA',
            'action': 'SELL',
            'entry': 460.0,
            'stop_loss': 480.0,
            'take_profit': 440.0,
            'confidence': 92.5,
            'data_source': 'weighted_consensus',
            'sources_count': 4
        }
        
        reasoning = explainer._generate_fallback_reasoning(signal)
        
        # Verify fallback reasoning is meaningful
        assert len(reasoning) >= 20, "Fallback reasoning should be at least 20 characters"
        assert 'NVDA' in reasoning, "Should mention symbol"
        assert 'SELL' in reasoning, "Should mention action"
        assert '92.5' in reasoning or '92' in reasoning, "Should mention confidence"
        assert 'weighted' in reasoning.lower() or 'consensus' in reasoning.lower(), \
            "Should mention data source"

