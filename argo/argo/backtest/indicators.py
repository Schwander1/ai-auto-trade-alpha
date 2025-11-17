#!/usr/bin/env python3
"""
Indicator Calculator
Calculates technical indicators for backtesting
"""
import pandas as pd
import numpy as np
import logging
from argo.backtest.constants import IndicatorConstants

logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """Calculates technical indicators"""
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all indicators.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with indicator columns added
        """
        df = df.copy()
        
        # Ensure numeric types
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate indicators by category
        df = IndicatorCalculator.calculate_sma_indicators(df)
        df = IndicatorCalculator.calculate_momentum_indicators(df)
        df = IndicatorCalculator.calculate_volume_indicators(df)
        df = IndicatorCalculator.calculate_volatility_indicators(df)
        
        logger.info(f"✅ Indicators calculated: sma_20, sma_50, rsi, macd, macd_signal, volume_ratio, volatility")
        return df
    
    @staticmethod
    def calculate_sma_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate SMA-based indicators"""
        df['sma_20'] = df['Close'].rolling(window=IndicatorConstants.SMA_SHORT_PERIOD, min_periods=1).mean()
        df['sma_50'] = df['Close'].rolling(window=IndicatorConstants.SMA_LONG_PERIOD, min_periods=1).mean()
        return df
    
    @staticmethod
    def calculate_momentum_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate momentum indicators (RSI, MACD)"""
        # RSI calculation (vectorized)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=IndicatorConstants.RSI_PERIOD, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=IndicatorConstants.RSI_PERIOD, min_periods=1).mean()
        rs = gain / loss.replace(0, np.nan)
        df['rsi'] = 100 - (100 / (1 + rs))
        df['rsi'] = df['rsi'].fillna(50.0)  # Fill NaN with neutral RSI
        
        # MACD calculation
        ema_12 = df['Close'].ewm(span=IndicatorConstants.MACD_FAST_PERIOD, adjust=False).mean()
        ema_26 = df['Close'].ewm(span=IndicatorConstants.MACD_SLOW_PERIOD, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=IndicatorConstants.MACD_SIGNAL_PERIOD, adjust=False).mean()
        
        return df
    
    @staticmethod
    def calculate_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume-based indicators"""
        if 'Volume' in df.columns:
            volume = df['Volume'].values
            df['volume_sma_20'] = df['Volume'].rolling(window=IndicatorConstants.VOLUME_SMA_PERIOD, min_periods=1).mean()
            df['volume_ratio'] = df['Volume'] / df['volume_sma_20'].replace(0, np.nan)
            df['volume_ratio'] = df['volume_ratio'].fillna(1.0)
        else:
            df['volume_ratio'] = 1.0
        
        return df
    
    @staticmethod
    def calculate_volatility_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volatility indicators"""
        # Volatility (rolling standard deviation of returns)
        returns = df['Close'].pct_change()
        df['volatility'] = returns.rolling(window=IndicatorConstants.VOLATILITY_PERIOD, min_periods=1).std() * IndicatorConstants.ANNUALIZATION_FACTOR
        df['volatility'] = df['volatility'].fillna(0.0)
        return df

