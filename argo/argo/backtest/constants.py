#!/usr/bin/env python3
"""
Trading Constants
Centralized constants for trading and backtesting operations
"""
from typing import Final


class TradingConstants:
    """Constants for trading operations"""
    
    # Fallback stops (tighter for drawdown reduction)
    FALLBACK_STOP_LOSS_PCT: Final[float] = 0.025  # 2.5% (tighter from 3%)
    FALLBACK_TAKE_PROFIT_PCT: Final[float] = 0.05  # 5%
    
    # Tighter stops for drawdown reduction
    TIGHT_STOP_LOSS_PCT: Final[float] = 0.02  # 2% for high volatility symbols
    
    # ATR (Average True Range)
    ATR_FALLBACK_PCT: Final[float] = 0.02  # 2%
    ATR_PERIOD: Final[int] = 14
    ATR_MIN_INDEX: Final[int] = 14  # Minimum index required for ATR calculation
    
    # Volatility thresholds
    DEFAULT_VOLATILITY: Final[float] = 0.2
    HIGH_VOLATILITY_THRESHOLD: Final[float] = 0.3
    LOW_VOLATILITY_THRESHOLD: Final[float] = 0.15
    
    # Volatility adjustment multipliers (tighter for drawdown reduction)
    HIGH_VOLATILITY_STOP_MULTIPLIER: Final[float] = 0.85  # Tighter stops (was 0.95)
    HIGH_VOLATILITY_PROFIT_MULTIPLIER: Final[float] = 1.05  # Higher profit target
    LOW_VOLATILITY_STOP_MULTIPLIER: Final[float] = 1.0  # Same stops (was 1.05)
    LOW_VOLATILITY_PROFIT_MULTIPLIER: Final[float] = 0.95  # Lower profit target
    
    # Volume confirmation
    VOLUME_CONFIRMATION_RATIO: Final[float] = 1.2  # 1.2x average volume
    
    # Trend indicators
    ADX_STRONG_TREND_THRESHOLD: Final[float] = 25.0
    SMA_200_PERIOD: Final[int] = 200
    MIN_DATA_POINTS_FOR_TREND: Final[int] = 200
    
    # Position sizing (optimized for better returns while maintaining risk)
    BASE_POSITION_SIZE_PCT: Final[float] = 0.09  # 9% (slightly increased from 8% for better returns)
    MIN_POSITION_SIZE_PCT: Final[float] = 0.05  # 5% (increased from 4%)
    MAX_POSITION_SIZE_PCT: Final[float] = 0.16  # 16% (slightly increased from 15%)
    
    # Portfolio-level risk limits
    MAX_PORTFOLIO_DRAWDOWN_PCT: Final[float] = 0.20  # 20% max portfolio drawdown
    MAX_POSITIONS_AT_ONCE: Final[int] = 5  # Maximum concurrent positions
    REDUCE_SIZE_ON_DRAWDOWN: Final[bool] = True  # Reduce position size during drawdowns
    CONFIDENCE_BASE: Final[float] = 50.0  # Base confidence for multiplier calculation
    CONFIDENCE_RANGE: Final[float] = 50.0  # Range for confidence multiplier (50-100)
    CONFIDENCE_MULTIPLIER_MAX: Final[float] = 0.5  # Max multiplier from confidence
    VOLATILITY_ADJUSTMENT_DIVISOR: Final[float] = 2.0  # Divisor for volatility adjustment
    
    # Time-based exit
    DEFAULT_TIME_BASED_EXIT_DAYS: Final[int] = 30
    TIME_EXIT_PROGRESS_THRESHOLD_LONG: Final[float] = 1.02  # 2% gain required
    TIME_EXIT_PROGRESS_THRESHOLD_SHORT: Final[float] = 0.98  # 2% loss allowed
    
    # Trailing stop volatility adjustments
    TRAILING_STOP_HIGH_VOL_MULTIPLIER: Final[float] = 1.1  # Looser for high volatility
    TRAILING_STOP_LOW_VOL_MULTIPLIER: Final[float] = 0.9  # Tighter for low volatility


class TransactionCostConstants:
    """Constants for transaction cost modeling"""
    
    # Default slippage (0.05%)
    DEFAULT_SLIPPAGE_PCT: Final[float] = 0.0005
    
    # Default spread (0.02%)
    DEFAULT_SPREAD_PCT: Final[float] = 0.0002
    
    # Default commission (0.1%)
    DEFAULT_COMMISSION_PCT: Final[float] = 0.001
    
    # Market-specific adjustments
    CRYPTO_SLIPPAGE_MULTIPLIER: Final[float] = 1.5  # Higher slippage for crypto
    CRYPTO_SPREAD_MULTIPLIER: Final[float] = 2.0    # Higher spread for crypto


class BacktestConstants:
    """Constants for backtesting operations"""
    
    # Initial capital
    DEFAULT_INITIAL_CAPITAL: Final[float] = 100000.0
    MIN_INITIAL_CAPITAL: Final[float] = 10000.0
    MAX_INITIAL_CAPITAL: Final[float] = 10000000.0
    
    # Warmup periods
    WARMUP_PERIOD_BARS: Final[int] = 200  # Bars needed before signal generation
    PARALLEL_PROCESSING_THRESHOLD: Final[int] = 500  # Min bars for parallel processing
    ML_THRESHOLD_MIN_DATA: Final[int] = 200  # Min data for ML threshold optimization
    MIN_DATA_FOR_BACKTEST: Final[int] = 100  # Minimum data points required
    
    # Data splitting
    DEFAULT_TRAIN_PCT: Final[float] = 0.6
    DEFAULT_VAL_PCT: Final[float] = 0.2
    DEFAULT_TEST_PCT: Final[float] = 0.2
    
    # Signal generation
    SIGNAL_GENERATION_STEP: Final[int] = 2  # Generate signal every N bars
    MIN_LOOKBACK_BARS: Final[int] = 50  # Minimum lookback for indicators
    DEFAULT_LOOKBACK_BARS: Final[int] = 20  # Default lookback period
    
    # Default confidence threshold (raised from 55% to 60% for better win rate)
    DEFAULT_MIN_CONFIDENCE: Final[float] = 60.0
    PREVIOUS_MIN_CONFIDENCE: Final[float] = 55.0  # For comparison
    
    # Position size defaults
    DEFAULT_POSITION_SIZE_PCT: Final[float] = 0.10  # 10% of capital
    MIN_POSITION_SIZE_PCT: Final[float] = 0.05  # 5% minimum
    MAX_POSITION_SIZE_PCT: Final[float] = 0.20  # 20% maximum
    
    # Stop loss and take profit defaults
    DEFAULT_STOP_LOSS_PCT: Final[float] = 0.03  # 3% stop loss
    DEFAULT_TAKE_PROFIT_PCT: Final[float] = 0.05  # 5% take profit
    
    # Validation thresholds
    MAX_REASONABLE_PNL_PCT: Final[float] = 1000.0  # 1000% max reasonable P&L
    MIN_REASONABLE_PNL_PCT: Final[float] = -100.0  # -100% max reasonable loss
    MAX_OPEN_POSITIONS: Final[int] = 10  # Maximum reasonable open positions


class IndicatorConstants:
    """Constants for technical indicators"""
    
    # SMA periods
    SMA_SHORT_PERIOD: Final[int] = 20
    SMA_LONG_PERIOD: Final[int] = 50
    
    # RSI period
    RSI_PERIOD: Final[int] = 14
    
    # MACD periods
    MACD_FAST_PERIOD: Final[int] = 12
    MACD_SLOW_PERIOD: Final[int] = 26
    MACD_SIGNAL_PERIOD: Final[int] = 9
    
    # Volatility
    VOLATILITY_PERIOD: Final[int] = 20
    TRADING_DAYS_PER_YEAR: Final[int] = 252
    ANNUALIZATION_FACTOR: Final[float] = 15.874507866387544  # sqrt(252)
    
    # Volume
    VOLUME_SMA_PERIOD: Final[int] = 20


class DatabaseConstants:
    """Database configuration constants"""
    
    # SQLite settings
    SQLITE_SYNCHRONOUS: Final[str] = 'NORMAL'
    SQLITE_CACHE_SIZE_KB: Final[int] = 64000  # 64MB
    SQLITE_TEMP_STORE: Final[str] = 'MEMORY'
    SQLITE_MMAP_SIZE_BYTES: Final[int] = 268435456  # 256MB
    SQLITE_CONNECTION_TIMEOUT: Final[float] = 10.0
    SQLITE_MAX_POOL_SIZE: Final[int] = 5

