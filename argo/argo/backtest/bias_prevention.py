#!/usr/bin/env python3
"""
Bias Prevention Utilities
Helper functions to detect and prevent look-ahead bias
"""
from datetime import datetime
from typing import List


class BiasPrevention:
    """Utilities for preventing look-ahead bias"""
    
    @staticmethod
    def validate_no_lookahead(signal_time: datetime, data_timestamps: List[datetime]) -> bool:
        """
        Validate that no future data is used
        
        Args:
            signal_time: Time when signal is generated
            data_timestamps: List of timestamps used in signal generation
        
        Returns:
            True if no look-ahead bias, False otherwise
        """
        for ts in data_timestamps:
            if ts > signal_time:
                return False
        return True
    
    @staticmethod
    def validate_data_slice(df_slice, current_index: int) -> bool:
        """
        Validate that data slice only contains historical data
        
        Args:
            df_slice: DataFrame slice
            current_index: Current index in full DataFrame
        
        Returns:
            True if valid, False if future data present
        """
        if df_slice is None or len(df_slice) == 0:
            return True
        
        # Check that all indices are <= current_index
        max_index = df_slice.index.max() if hasattr(df_slice.index, 'max') else len(df_slice) - 1
        if isinstance(max_index, int):
            return max_index <= current_index
        
        return True
