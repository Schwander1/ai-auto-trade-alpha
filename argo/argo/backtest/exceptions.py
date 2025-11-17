#!/usr/bin/env python3
"""
Backtesting Exceptions
Custom exception classes for backtesting operations
"""
from typing import Optional


class BacktestError(Exception):
    """Base exception for backtesting errors"""
    pass


class DataError(BacktestError):
    """Exception for data-related errors"""
    def __init__(self, message: str, symbol: Optional[str] = None):
        super().__init__(message)
        self.symbol = symbol


class InsufficientDataError(DataError):
    """Exception when insufficient data is available"""
    pass


class InvalidDataError(DataError):
    """Exception when data is invalid or corrupted"""
    pass


class CostModelError(BacktestError):
    """Exception for cost model errors"""
    pass


class PositionError(BacktestError):
    """Exception for position-related errors"""
    def __init__(self, message: str, symbol: Optional[str] = None):
        super().__init__(message)
        self.symbol = symbol


class InsufficientCapitalError(PositionError):
    """Exception when insufficient capital for position"""
    pass


class InvalidPositionSizeError(PositionError):
    """Exception when position size is invalid"""
    pass


class MetricsError(BacktestError):
    """Exception for metrics calculation errors"""
    pass

