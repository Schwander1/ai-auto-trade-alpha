#!/usr/bin/env python3
"""
Backtest Utilities
Helper functions for backtesting operations
"""
from typing import List
from argo.backtest.constants import BacktestConstants


def to_percentage(value: float) -> float:
    """
    Convert decimal to percentage.
    
    Args:
        value: Decimal value (e.g., 0.05 for 5%)
    
    Returns:
        Percentage value (e.g., 5.0 for 5%)
    """
    return value * 100.0


def from_percentage(value: float) -> float:
    """
    Convert percentage to decimal.
    
    Args:
        value: Percentage value (e.g., 5.0 for 5%)
    
    Returns:
        Decimal value (e.g., 0.05 for 5%)
    """
    return value / 100.0


def generate_signal_indices(
    df_length: int,
    warmup_period: int = None,
    step: int = None
) -> List[int]:
    """
    Generate indices for signal generation.
    
    Args:
        df_length: Total length of DataFrame
        warmup_period: Number of bars to skip at start (default: WARMUP_PERIOD_BARS)
        step: Generate signal every N bars (default: SIGNAL_GENERATION_STEP)
    
    Returns:
        List of indices where signals should be generated
    """
    if warmup_period is None:
        warmup_period = BacktestConstants.WARMUP_PERIOD_BARS
    if step is None:
        step = BacktestConstants.SIGNAL_GENERATION_STEP
    
    indices = [
        i for i in range(warmup_period, df_length)
        if i % step == 0 or i == warmup_period
    ]
    return indices

