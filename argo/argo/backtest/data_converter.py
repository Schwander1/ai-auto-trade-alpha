#!/usr/bin/env python3
"""
Data Converter
Utility for converting between Polars and Pandas DataFrames
"""
from typing import Union, TYPE_CHECKING
import pandas as pd
import logging

if TYPE_CHECKING:
    import polars as pl

logger = logging.getLogger(__name__)


class DataConverter:
    """Utility for converting between Polars and Pandas DataFrames"""

    @staticmethod
    def to_pandas(df: Union['pl.DataFrame', pd.DataFrame]) -> pd.DataFrame:
        """
        Convert Polars DataFrame to Pandas, handling all edge cases.

        Args:
            df: Polars or Pandas DataFrame

        Returns:
            Pandas DataFrame with normalized date index and numeric columns

        Raises:
            ValueError: If DataFrame type is unsupported
        """
        try:
            import polars as pl
        except ImportError:
            pl = None

        if isinstance(df, pd.DataFrame):
            return DataConverter._normalize_pandas_df(df)

        if pl and isinstance(df, pl.DataFrame):
            # Convert to Pandas
            pandas_df = df.to_pandas()
            return DataConverter._normalize_pandas_df(pandas_df)

        raise ValueError(f"Unsupported DataFrame type: {type(df)}")

    @staticmethod
    def _normalize_pandas_df(df: pd.DataFrame) -> pd.DataFrame:
        """Normalize Pandas DataFrame: date index, numeric columns"""
        df = df.copy()

        # Handle date column/index
        df = DataConverter._normalize_date_index(df)

        # Ensure numeric columns
        df = DataConverter._ensure_numeric_columns(df)

        return df

    @staticmethod
    def _normalize_date_index(df: pd.DataFrame) -> pd.DataFrame:
        """Normalize date index/column"""
        # Try Date column first
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.set_index('Date')
        elif 'Datetime' in df.columns:
            df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
            df = df.set_index('Datetime')

        # Ensure index is DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index, errors='coerce')
            except Exception:
                pass

        return df.sort_index()

    @staticmethod
    def _ensure_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Ensure OHLCV columns are numeric"""
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
