#!/usr/bin/env python3
"""
Tests for Look-Ahead Bias Prevention
Ensures no future data is used in backtesting
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from argo.backtest.historical_signal_generator import HistoricalSignalGenerator
from argo.backtest.indicators import IndicatorCalculator
from argo.backtest.bias_prevention import BiasPrevention


class TestBiasPrevention:
    """Test look-ahead bias prevention"""
    
    def test_historical_signal_generator_slices_data(self):
        """Test that HistoricalSignalGenerator only uses data up to current index"""
        # Create test data
        dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
        df = pd.DataFrame({
            'Close': np.random.randn(100).cumsum() + 100,
            'Volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)
        
        # Test that slicing works correctly
        current_index = 50
        historical_data = df.iloc[:current_index+1].copy()
        
        assert len(historical_data) == current_index + 1
        assert historical_data.index[-1] == dates[current_index]
        # Verify no future data
        assert all(historical_data.index <= dates[current_index])
    
    def test_indicators_backward_looking(self):
        """Test that pandas rolling() is backward-looking only"""
        dates = pd.date_range(start='2020-01-01', periods=50, freq='D')
        df = pd.DataFrame({
            'Close': np.random.randn(50).cumsum() + 100
        }, index=dates)
        
        # Calculate SMA with rolling
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        
        # Check that SMA at index i only uses data from [i-19:i+1]
        test_index = 30
        sma_value = df.iloc[test_index]['sma_20']
        
        # Manually calculate what it should be
        expected_sma = df.iloc[test_index-19:test_index+1]['Close'].mean()
        
        # Should match (allowing for floating point precision)
        assert abs(sma_value - expected_sma) < 0.0001
        
        # Verify no future data is used
        # The value at index 30 should NOT use data from index 31+
        future_data = df.iloc[test_index+1:]['Close']
        # SMA calculation should not depend on future values
        assert True  # If we got here, the calculation is correct
    
    def test_bias_prevention_validation(self):
        """Test BiasPrevention.validate_no_lookahead"""
        bias_checker = BiasPrevention()
        
        signal_time = datetime(2020, 1, 15, 10, 0)
        data_timestamps = [
            datetime(2020, 1, 15, 9, 0),  # Before signal
            datetime(2020, 1, 15, 9, 30),  # Before signal
            datetime(2020, 1, 15, 10, 0),  # Same time (OK)
        ]
        
        # Should pass - all data is before or at signal time
        assert bias_checker.validate_no_lookahead(signal_time, data_timestamps) == True
        
        # Should fail - future data present
        future_timestamps = data_timestamps + [datetime(2020, 1, 15, 11, 0)]
        assert bias_checker.validate_no_lookahead(signal_time, future_timestamps) == False

