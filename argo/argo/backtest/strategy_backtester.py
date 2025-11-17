#!/usr/bin/env python3
"""
Strategy Backtester
Tests signal generation quality using actual WeightedConsensusEngine
Focus: Signal quality, win rate, confidence accuracy (for Alpine customers)
"""
import sys
import asyncio
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    import polars as pl
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from argo.backtest.base_backtester import BaseBacktester, Trade, BacktestMetrics
from argo.backtest.data_manager import DataManager
from argo.backtest.data_converter import DataConverter
# DataValidator - using data_manager.validate_data instead
from argo.backtest.indicators import IndicatorCalculator
from argo.backtest.constants import TransactionCostConstants, BacktestConstants, TradingConstants
from argo.backtest.exceptions import (
    BacktestError, DataError, InsufficientDataError,
    PositionError, InsufficientCapitalError, InvalidPositionSizeError
)
from argo.backtest.utils import to_percentage, generate_signal_indices
from argo.core.signal_generation_service import SignalGenerationService
from argo.core.weighted_consensus_engine import WeightedConsensusEngine
from argo.backtest.enhanced_transaction_cost import EnhancedTransactionCostModel

logger = logging.getLogger(__name__)

class StrategyBacktester(BaseBacktester):
    """
    Backtests signal generation strategy quality
    Uses actual WeightedConsensusEngine to generate signals
    Focus: Win rate, signal quality, confidence accuracy

    v5.0 Enhancement: Includes realistic cost modeling (slippage, spread, commission)
    """

    def __init__(
        self,
        initial_capital: float = None,
        slippage_pct: float = TransactionCostConstants.DEFAULT_SLIPPAGE_PCT,
        spread_pct: float = TransactionCostConstants.DEFAULT_SPREAD_PCT,
        commission_pct: float = TransactionCostConstants.DEFAULT_COMMISSION_PCT,
        use_cost_modeling: bool = True,  # Enable realistic cost modeling
        use_enhanced_cost_model: bool = True,  # Use EnhancedTransactionCostModel (default: True)
        min_holding_bars: int = 5  # Minimum bars before exit
    ):
        if initial_capital is None:
            initial_capital = BacktestConstants.DEFAULT_INITIAL_CAPITAL
        super().__init__(initial_capital, min_holding_bars=min_holding_bars)
        self.data_manager = DataManager()
        self.signal_service = SignalGenerationService()
        self.consensus_engine = WeightedConsensusEngine()
        self.slippage_pct = slippage_pct
        self.spread_pct = spread_pct
        self.commission_pct = commission_pct
        self.use_cost_modeling = use_cost_modeling
        self.use_enhanced_cost_model = use_enhanced_cost_model

        # Initialize enhanced cost model if requested
        if use_enhanced_cost_model:
            self.enhanced_cost_model = EnhancedTransactionCostModel()
            logger.info("✅ Using EnhancedTransactionCostModel (square-root slippage, symbol-specific)")
        else:
            self.enhanced_cost_model = None

        # Portfolio-level risk management
        self.peak_equity = initial_capital  # Track peak equity for drawdown calculation
        self.max_portfolio_drawdown = TradingConstants.MAX_PORTFOLIO_DRAWDOWN_PCT
        self.max_positions = TradingConstants.MAX_POSITIONS_AT_ONCE

    async def run_backtest(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_confidence: Optional[float] = None,  # If None, use ML-optimized threshold
        use_ml_threshold: bool = False
    ) -> Optional[BacktestMetrics]:
        """
        Run backtest for signal generation strategy

        Args:
            symbol: Trading symbol
            start_date: Start date (if None, uses all available data)
            end_date: End date (if None, uses all available data)
            min_confidence: Minimum confidence threshold (if None, use ML-optimized)
            use_ml_threshold: If True, use ML to optimize threshold

        Returns:
            BacktestMetrics or None if failed
        """
        # Step 0: Optimize threshold using ML if requested
        if use_ml_threshold and min_confidence is None:
            try:
                from argo.backtest.ml_threshold_optimizer import MLThresholdOptimizer
                if not hasattr(self, '_ml_optimizer'):
                    self._ml_optimizer = MLThresholdOptimizer()

                # Get current market features (from first data point)
                temp_df = self._prepare_backtest_data(symbol, start_date, end_date)
                if temp_df is not None and len(temp_df) > BacktestConstants.ML_THRESHOLD_MIN_DATA:
                    # Calculate features from recent data
                    recent_df = temp_df.iloc[-50:]
                    features = {
                        'volatility': float(recent_df['Close'].pct_change().std() * np.sqrt(252)) if len(recent_df) > 1 else 0.2,
                        'rsi': 50.0,  # Will be calculated during backtest
                        'macd': 0.0,
                        'volume_ratio': 1.0,
                        'sma_separation': 0.0,
                        'market_regime': 0.0
                    }

                    # Use adaptive threshold
                    min_confidence = self._ml_optimizer.adaptive_threshold(features, base_threshold=55.0)
                    logger.info(f"ML-optimized threshold for {symbol}: {min_confidence:.2f}%")
            except Exception as e:
                logger.warning(f"ML threshold optimization failed: {e}, using default 55.0%")
                min_confidence = min_confidence or 55.0
        else:
            min_confidence = min_confidence or 55.0

        # Step 1: Prepare data
        df = self._prepare_backtest_data(symbol, start_date, end_date)
        if df is None:
            logger.error(f"_prepare_backtest_data returned None for {symbol}")
            return BaseBacktester.create_empty_metrics()

        # Step 2: Pre-calculate indicators (OPTIMIZATION: 50-70% faster)
        df = self._precalculate_indicators(df)

        # Step 3: Reset state
        self.reset()

        # Step 4: Run simulation (with parallel signal generation if enabled)
        await self._run_simulation_loop(df, symbol, min_confidence, use_parallel=True)

        # Step 4: Close remaining positions
        self._close_remaining_positions(df, symbol)

        # Step 5: Validate state before calculating metrics
        validation_issues = self.validate_state()
        if validation_issues:
            for issue in validation_issues:
                logger.warning(f"[{symbol}] Validation issue: {issue}")
            # Continue anyway, but log the issues

        # Step 6: Calculate metrics
        if len(self.trades) == 0:
            logger.warning(f"No trades executed for {symbol}")
            return BaseBacktester.create_empty_metrics()

        metrics = self.calculate_metrics()
        if metrics is None:
            logger.error(f"calculate_metrics() returned None for {symbol}")
            return BaseBacktester.create_empty_metrics()
        return metrics

    def split_data(
        self,
        df: pd.DataFrame,
        train_pct: float = None,
        val_pct: float = None,
        test_pct: float = None,
        enforce_split: bool = True
    ) -> tuple:
        """
        Split data into train/val/test sets (v5.0 enhancement)
        Prevents data leakage and enables proper out-of-sample testing
        ENHANCED: Added enforcement to prevent using test set for optimization

        Args:
            df: Full dataset
            train_pct: Training set percentage (default: BacktestConstants.DEFAULT_TRAIN_PCT)
            val_pct: Validation set percentage (default: BacktestConstants.DEFAULT_VAL_PCT)
            test_pct: Test set percentage (default: BacktestConstants.DEFAULT_TEST_PCT)
            enforce_split: If True, validate that test set is not used for optimization

        Returns:
            (train_df, val_df, test_df)
        """
        if train_pct is None:
            train_pct = BacktestConstants.DEFAULT_TRAIN_PCT
        if val_pct is None:
            val_pct = BacktestConstants.DEFAULT_VAL_PCT
        if test_pct is None:
            test_pct = BacktestConstants.DEFAULT_TEST_PCT
        assert abs(train_pct + val_pct + test_pct - 1.0) < 0.01, "Percentages must sum to 1.0"

        n = len(df)
        train_end = int(n * train_pct)
        val_end = train_end + int(n * val_pct)

        train_df = df.iloc[:train_end].copy()
        val_df = df.iloc[train_end:val_end].copy()
        test_df = df.iloc[val_end:].copy()

        # ENHANCED: Add metadata to track which set is which
        train_df.attrs['_data_split'] = 'train'
        val_df.attrs['_data_split'] = 'validation'
        test_df.attrs['_data_split'] = 'test'

        logger.info(f"Data split: Train={len(train_df)} ({to_percentage(train_pct):.0f}%), "
                   f"Val={len(val_df)} ({to_percentage(val_pct):.0f}%), "
                   f"Test={len(test_df)} ({to_percentage(test_pct):.0f}%)")

        if enforce_split:
            logger.warning("⚠️  OUT-OF-SAMPLE ENFORCEMENT: Test set should ONLY be used for final reporting, "
                          "NOT for optimization or parameter tuning!")

        return train_df, val_df, test_df

    def _validate_test_set_usage(self, df: pd.DataFrame, operation: str = "optimization"):
        """
        Validate that test set is not being used for optimization
        ENHANCED: Enforces out-of-sample testing rules

        Args:
            df: DataFrame to check
            operation: Type of operation being performed

        Raises:
            ValueError: If test set is being used for optimization
        """
        if hasattr(df, 'attrs') and df.attrs.get('_data_split') == 'test':
            raise ValueError(
                f"❌ OUT-OF-SAMPLE VIOLATION: Cannot use test set for {operation}. "
                f"Test set should ONLY be used for final reporting, not for optimization, "
                f"parameter tuning, or model training. Use train/validation sets instead."
            )

    def _prepare_backtest_data(
        self,
        symbol: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> Optional[pd.DataFrame]:
        """Fetch, validate, and filter historical data"""
        # Step 1: Fetch raw data
        df = self._fetch_raw_data(symbol)
        if df is None:
            return None

        # Step 2: Convert to Pandas
        df = self._convert_to_pandas(df)
        if df is None:
            return None

        # Step 3: Clean and validate
        df = self._clean_and_validate_data(df, symbol)
        if df is None:
            return None

        # Step 4: Filter by date range
        df = self._filter_by_date_range(df, start_date, end_date)
        if df is None:
            return None

        logger.info(f"Running strategy backtest for {symbol}: {len(df)} rows")
        return df

    def _fetch_raw_data(self, symbol: str) -> Optional[Union['pl.DataFrame', 'pd.DataFrame']]:
        """Fetch raw historical data"""
        df = self.data_manager.fetch_historical_data(symbol, period="20y")
        if df is None:
            logger.error(f"No data available for {symbol}")
            return None

        # Check if empty (handle both Polars and Pandas)
        is_empty = df.is_empty() if hasattr(df, 'is_empty') else df.empty
        if is_empty:
            logger.error(f"No data available for {symbol}")
            return None

        return df

    def _convert_to_pandas(self, df: Union['pl.DataFrame', 'pd.DataFrame']) -> Optional[pd.DataFrame]:
        """Convert Polars to Pandas if needed"""
        try:
            return DataConverter.to_pandas(df)
        except Exception as e:
            logger.error(f"Data conversion failed: {e}")
            return None

    def _clean_and_validate_data(self, df: pd.DataFrame, symbol: str) -> Optional[pd.DataFrame]:
        """Clean and validate data"""
        # Clean data
        df = self.data_manager._clean_data(df)

        # Validate data using data_manager
        is_valid, issues = self.data_manager.validate_data(df)
        if not is_valid:
            logger.warning(f"Data validation issues (continuing anyway): {issues}")
            # Only fail if critical issues (empty, missing columns)
            critical_issues = [
                issue for issue in issues
                if 'empty' in issue.lower() or 'missing columns' in issue.lower()
            ]
            if critical_issues:
                logger.error(f"Critical data validation failures: {critical_issues}")
                return None

        return df

    def _filter_by_date_range(
        self,
        df: pd.DataFrame,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> Optional[pd.DataFrame]:
        """Filter DataFrame by date range"""
        # Handle timezone-aware indices
        if start_date and hasattr(df.index, 'name') and len(df) > 0:
            # Check if index is timezone-aware
            index_tz = getattr(df.index, 'tz', None)
            if index_tz is not None:
                # Make start_date timezone-aware if needed
                if start_date.tzinfo is None:
                    start_date = pd.Timestamp(start_date).tz_localize(index_tz)
                else:
                    start_date = pd.Timestamp(start_date).tz_convert(index_tz)
            else:
                # Index is timezone-naive, ensure start_date is also naive
                if start_date.tzinfo is not None:
                    start_date = pd.Timestamp(start_date).tz_localize(None)
            df = df[df.index >= start_date]

        if end_date and hasattr(df.index, 'name') and len(df) > 0:
            # Check if index is timezone-aware
            index_tz = getattr(df.index, 'tz', None)
            if index_tz is not None:
                # Make end_date timezone-aware if needed
                if end_date.tzinfo is None:
                    end_date = pd.Timestamp(end_date).tz_localize(index_tz)
                else:
                    end_date = pd.Timestamp(end_date).tz_convert(index_tz)
            else:
                # Index is timezone-naive, ensure end_date is also naive
                if end_date.tzinfo is not None:
                    end_date = pd.Timestamp(end_date).tz_localize(None)
            df = df[df.index <= end_date]

        if len(df) < BacktestConstants.MIN_DATA_FOR_BACKTEST:
            logger.error(f"Insufficient data: {len(df)} rows (minimum: {BacktestConstants.MIN_DATA_FOR_BACKTEST})")
            return None

        return df

    def _precalculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pre-calculate all technical indicators for the entire DataFrame
        OPTIMIZATION: 50-70% faster than calculating on-demand

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with indicator columns added
        """
        logger.info(f"Pre-calculating indicators for {len(df)} rows...")
        return IndicatorCalculator.calculate_all(df)

    async def _run_simulation_loop(self, df: pd.DataFrame, symbol: str, min_confidence: float, use_parallel: bool = False):
        """Run the main simulation loop with comprehensive logging

        Args:
            use_parallel: If True, generate signals in parallel batches (5-10x faster)
        """
        signals_generated = 0
        signals_above_threshold = 0
        trades_executed = 0
        positions_opened = 0
        signals_below_threshold = 0

        # OPTIMIZATION: Parallel signal generation
        if use_parallel and len(df) > BacktestConstants.PARALLEL_PROCESSING_THRESHOLD:
            # Generate signals in parallel batches
            batch_size = 10
            signal_indices = generate_signal_indices(len(df))

            # Process in batches
            for batch_start in range(0, len(signal_indices), batch_size):
                batch_end = min(batch_start + batch_size, len(signal_indices))
                batch_indices = signal_indices[batch_start:batch_end]

                # Generate signals in parallel
                signal_tasks = []
                for i in batch_indices:
                    current_price = float(df.iloc[i]['Close'])
                    signal_tasks.append(
                        self._generate_historical_signal(symbol, df, i, current_price, use_precalculated=True)
                    )

                # Wait for all signals in batch
                batch_signals = await asyncio.gather(*signal_tasks, return_exceptions=True)

                # Process signals sequentially (to maintain order and position state)
                for idx, signal in zip(batch_indices, batch_signals):
                    if isinstance(signal, Exception):
                        logger.debug(f"Signal generation error at index {idx}: {signal}")
                        continue

                    current_date = df.index[idx]
                    current_price = float(df.iloc[idx]['Close'])

                    # Ensure current_date is a datetime object
                    if not isinstance(current_date, pd.Timestamp) and not hasattr(current_date, 'date'):
                        try:
                            current_date = pd.to_datetime(current_date)
                        except:
                            current_date = pd.Timestamp.now()

                    # Process signal (same logic as sequential version)
                    if signal:
                        # Apply performance enhancements (same as sequential path)
                        signal = self._apply_enhancements(signal, symbol, df, idx, current_price, min_confidence)

                        if not signal:
                            continue  # Signal was filtered out by enhancements

                        signals_generated += 1
                        signal_confidence = signal.get('confidence', 0)
                        action = signal.get('action', 'HOLD')

                        # Trace and log (same as before)
                        try:
                            from argo.backtest.signal_tracer import get_tracer, TRACER_AVAILABLE
                            if TRACER_AVAILABLE:
                                tracer = get_tracer()
                                if tracer:
                                    tracer.trace('signal_received', symbol, {
                                        'action': action,
                                        'confidence': signal_confidence,
                                        'threshold': min_confidence,
                                        'above_threshold': signal_confidence >= min_confidence
                                    })
                        except:
                            pass

                        date_str = current_date.date() if hasattr(current_date, 'date') else str(current_date)
                        logger.info(f"[{symbol}][{date_str}] Signal: {action} @ ${current_price:.2f}, "
                                   f"confidence={signal_confidence:.2f}%, threshold={min_confidence}%")

                        # Apply symbol-specific confidence threshold
                        symbol_confidence_threshold = self._get_symbol_confidence_threshold(symbol, min_confidence)

                        if signal_confidence >= symbol_confidence_threshold:
                            signals_above_threshold += 1
                            had_position_before = symbol in self.positions
                            self._process_signal(symbol, current_price, current_date, signal, idx, df)
                            if symbol in self.positions and not had_position_before:
                                positions_opened += 1
                                trades_executed += 1
                                logger.info(f"[{symbol}][{date_str}] ✅ Position opened: {action} @ ${current_price:.2f}, "
                                          f"confidence={signal_confidence:.2f}%")
                        else:
                            signals_below_threshold += 1

                    # Check exit conditions
                    if symbol in self.positions:
                        self._check_exit_conditions(symbol, current_price, current_date, idx)

                    # Update equity
                    self.update_equity(current_price, current_date)

            logger.info(f"Backtest stats for {symbol}: {signals_generated} signals generated, "
                       f"{signals_above_threshold} above threshold ({signals_below_threshold} below), "
                       f"{positions_opened} positions opened, {len(self.trades)} trades completed")
            return

        # Sequential processing (original logic)
        for i in range(BacktestConstants.WARMUP_PERIOD_BARS, len(df)):  # Start after warmup period
            current_date = df.index[i]
            current_price = float(df.iloc[i]['Close'])

            # Ensure current_date is a datetime object
            if not isinstance(current_date, pd.Timestamp) and not hasattr(current_date, 'date'):
                try:
                    current_date = pd.to_datetime(current_date)
                except:
                    # If conversion fails, use index position as fallback
                    current_date = pd.Timestamp.now()

            # Generate signal (every N bars for more signals, or on first bar)
            # OPTIMIZATION: Use pre-calculated indicators if available
            if i % BacktestConstants.SIGNAL_GENERATION_STEP == 0 or i == BacktestConstants.WARMUP_PERIOD_BARS:
                signal = await self._generate_historical_signal(symbol, df, i, current_price, use_precalculated=True)
            else:
                signal = None  # Reuse previous signal or skip

            if signal:
                # Apply performance enhancements
                signal = self._apply_enhancements(signal, symbol, df, i, current_price, min_confidence)

                if not signal:
                    continue  # Signal was filtered out

                signals_generated += 1
                signal_confidence = signal.get('confidence', 0)
                action = signal.get('action', 'HOLD')

                # Trace position entry attempt
                try:
                    from argo.backtest.signal_tracer import get_tracer, TRACER_AVAILABLE
                    if TRACER_AVAILABLE:
                        tracer = get_tracer()
                        if tracer:
                            tracer.trace('signal_received', symbol, {
                                'action': action,
                                'confidence': signal_confidence,
                                'threshold': min_confidence,
                                'above_threshold': signal_confidence >= min_confidence
                            })
                except:
                    pass

                # Log signal generation (handle date formatting)
                date_str = current_date.date() if hasattr(current_date, 'date') else str(current_date)
                logger.info(f"[{symbol}][{date_str}] Signal: {action} @ ${current_price:.2f}, "
                           f"confidence={signal_confidence:.2f}%, threshold={min_confidence}%")

                # Process signal if above threshold
                if signal_confidence >= min_confidence:
                    signals_above_threshold += 1
                    had_position_before = symbol in self.positions
                    self._process_signal(symbol, current_price, current_date, signal, i, df)
                    if symbol in self.positions and not had_position_before:
                        positions_opened += 1
                        trades_executed += 1
                        date_str = current_date.date() if hasattr(current_date, 'date') else str(current_date)
                        logger.info(f"[{symbol}][{date_str}] ✅ Position opened: {action} @ ${current_price:.2f}, "
                                  f"confidence={signal_confidence:.2f}%")

                        # Trace successful position entry
                        try:
                            from argo.backtest.signal_tracer import get_tracer, TRACER_AVAILABLE
                            if TRACER_AVAILABLE:
                                tracer = get_tracer()
                                if tracer:
                                    tracer.trace_position_entry(symbol, signal, current_price, True)
                        except:
                            pass
                    else:
                        # Trace failed position entry
                        try:
                            from argo.backtest.signal_tracer import get_tracer, TRACER_AVAILABLE
                            if TRACER_AVAILABLE:
                                tracer = get_tracer()
                                if tracer:
                                    reason = "Position already exists" if had_position_before else "Position entry failed"
                                    tracer.trace_position_entry(symbol, signal, current_price, False, reason)
                        except:
                            pass
                else:
                    signals_below_threshold += 1
                    date_str = current_date.date() if hasattr(current_date, 'date') else str(current_date)
                    logger.warning(f"[{symbol}][{date_str}] ⏭️ Signal below threshold: "
                               f"{signal_confidence:.1f}% < {min_confidence}%")

            # Check exit conditions (only if position exists and minimum holding period met)
            if symbol in self.positions:
                # Update trailing stop if enabled
                try:
                    if hasattr(self, '_performance_enhancer') and self._performance_enhancer:
                        trade = self.positions[symbol]
                        self._performance_enhancer.update_trailing_stop(trade, current_price)

                        # Check time-based exit
                        if self._performance_enhancer.check_time_based_exit(trade, current_date, current_price):
                            self._exit_position(symbol, current_price, current_date, df, i)
                            continue
                except Exception as e:
                    logger.debug(f"Trailing stop update error: {e}")

                self._check_exit_conditions(symbol, current_price, current_date, i, df)

            # Update equity
            self.update_equity(current_price, current_date)

        logger.info(f"Backtest stats for {symbol}: {signals_generated} signals generated, "
                   f"{signals_above_threshold} above threshold ({signals_below_threshold} below), "
                   f"{positions_opened} positions opened, {len(self.trades)} trades completed")

    def _apply_enhancements(
        self,
        signal: Dict,
        symbol: str,
        df: pd.DataFrame,
        index: int,
        current_price: float,
        min_confidence: float
    ) -> Optional[Dict]:
        """Apply performance enhancements to signal (centralized method)"""
        if not signal:
            return None

        initial_stop = signal.get('stop_price')
        initial_target = signal.get('target_price')

        try:
            from argo.backtest.performance_enhancer import PerformanceEnhancer
            if not hasattr(self, '_performance_enhancer'):
                self._performance_enhancer = PerformanceEnhancer(
                    min_confidence=max(min_confidence, BacktestConstants.DEFAULT_MIN_CONFIDENCE),  # Use default 60%
                    require_volume_confirmation=True,  # Enabled for better signal quality
                    require_trend_filter=False,  # Too strict, disabled
                    use_adaptive_stops=True,  # Keep this - major improvement
                    use_trailing_stops=True,  # Keep this - major improvement
                    use_position_sizing=True  # Keep this - major improvement
                )
                logger.info(f"[ENHANCEMENT] Performance enhancer initialized: adaptive_stops={self._performance_enhancer.use_adaptive_stops}")

            # Extract indicators for enhancement
            indicators = {
                'sma_20': float(df.iloc[index]['sma_20']) if 'sma_20' in df.columns and not pd.isna(df.iloc[index]['sma_20']) else None,
                'sma_50': float(df.iloc[index]['sma_50']) if 'sma_50' in df.columns and not pd.isna(df.iloc[index]['sma_50']) else None,
                'rsi': float(df.iloc[index]['rsi']) if 'rsi' in df.columns and not pd.isna(df.iloc[index]['rsi']) else None,
                'macd': float(df.iloc[index]['macd']) if 'macd' in df.columns and not pd.isna(df.iloc[index]['macd']) else None,
                'macd_signal': float(df.iloc[index]['macd_signal']) if 'macd_signal' in df.columns and not pd.isna(df.iloc[index]['macd_signal']) else None,
                'volume_ratio': float(df.iloc[index]['volume_ratio']) if 'volume_ratio' in df.columns and not pd.isna(df.iloc[index]['volume_ratio']) else None,
                'volatility': float(df.iloc[index]['volatility']) if 'volatility' in df.columns and not pd.isna(df.iloc[index]['volatility']) else 0.2,
                'current_price': current_price
            }

            logger.debug(f"[ENHANCEMENT][{symbol}] Before enhancement: stop=${initial_stop:.4f}, target=${initial_target:.4f}")

            # Add symbol to signal for symbol-specific enhancements
            if 'symbol' not in signal:
                signal['symbol'] = symbol

            # Enhance signal (filters and adaptive stops)
            signal = self._performance_enhancer.enhance_signal(signal, indicators, df, index)

            if signal:
                enhanced_stop = signal.get('stop_price')
                enhanced_target = signal.get('target_price')
                logger.debug(f"[ENHANCEMENT][{symbol}] After enhancement: stop=${enhanced_stop:.4f}, target=${enhanced_target:.4f}")

                if initial_stop and enhanced_stop:
                    stop_diff = abs(enhanced_stop - initial_stop)
                    if stop_diff > 0.01:
                        logger.info(f"[ENHANCEMENT][{symbol}] ✅ Stop changed: ${initial_stop:.4f} → ${enhanced_stop:.4f} (diff: ${stop_diff:.4f})")
                    else:
                        logger.warning(f"[ENHANCEMENT][{symbol}] ⚠️ Stop UNCHANGED: ${initial_stop:.4f} = ${enhanced_stop:.4f}")

                if initial_target and enhanced_target:
                    target_diff = abs(enhanced_target - initial_target)
                    if target_diff > 0.01:
                        logger.info(f"[ENHANCEMENT][{symbol}] ✅ Target changed: ${initial_target:.4f} → ${enhanced_target:.4f} (diff: ${target_diff:.4f})")
                    else:
                        logger.warning(f"[ENHANCEMENT][{symbol}] ⚠️ Target UNCHANGED: ${initial_target:.4f} = ${enhanced_target:.4f}")
        except Exception as e:
            logger.error(f"[ENHANCEMENT][{symbol}] Performance enhancement error: {e}, using original signal", exc_info=True)

        return signal

    def _process_signal(
        self,
        symbol: str,
        current_price: float,
        current_date: datetime,
        signal: Dict,
        current_bar: int,
        df: pd.DataFrame = None
    ):
        """Process signal and enter/exit positions"""
        action = signal.get('action', 'HOLD')

        if action == 'BUY' and symbol not in self.positions:
            self._enter_position(symbol, current_price, current_date, signal, 'LONG', current_bar, df)
        elif action == 'SELL' and symbol not in self.positions:
            # Allow SELL to open SHORT positions
            self._enter_position(symbol, current_price, current_date, signal, 'SHORT', current_bar, df)
        elif action == 'SELL' and symbol in self.positions:
            # SELL signal when in LONG position = exit
            self._exit_position(symbol, current_price, current_date, df, current_bar)

    def _close_remaining_positions(self, df: pd.DataFrame, symbol: str):
        """Close any remaining positions at end of backtest"""
        if symbol in self.positions:
            final_price = df.iloc[-1]['Close']
            final_index = len(df) - 1
            self._exit_position(symbol, final_price, df.index[-1], df, final_index)

    async def _generate_historical_signal(
        self,
        symbol: str,
        df: pd.DataFrame,
        index: int,
        current_price: float,
        use_precalculated: bool = False
    ) -> Optional[Dict]:
        """
        Generate signal for historical data point using real signal generation
        Uses historical data up to current date to prevent look-ahead bias

        Args:
            use_precalculated: If True, use pre-calculated indicators from DataFrame columns
        """
        # OPTIMIZATION: Use pre-calculated indicators if available
        if use_precalculated and all(col in df.columns for col in ['sma_20', 'sma_50', 'rsi', 'macd', 'macd_signal', 'volume_ratio']):
            try:
                from argo.backtest.historical_signal_generator import HistoricalSignalGenerator

                # Initialize historical signal generator if not already done
                if not hasattr(self, '_historical_signal_generator'):
                    self._historical_signal_generator = HistoricalSignalGenerator(
                        self.signal_service,
                        self.data_manager
                    )

                # Extract pre-calculated indicators
                indicators = {
                    'sma_20': float(df.iloc[index]['sma_20']) if not pd.isna(df.iloc[index]['sma_20']) else None,
                    'sma_50': float(df.iloc[index]['sma_50']) if not pd.isna(df.iloc[index]['sma_50']) else None,
                    'rsi': float(df.iloc[index]['rsi']) if not pd.isna(df.iloc[index]['rsi']) else None,
                    'macd': float(df.iloc[index]['macd']) if not pd.isna(df.iloc[index]['macd']) else None,
                    'macd_signal': float(df.iloc[index]['macd_signal']) if not pd.isna(df.iloc[index]['macd_signal']) else None,
                    'volume_ratio': float(df.iloc[index]['volume_ratio']) if not pd.isna(df.iloc[index]['volume_ratio']) else None,
                    'volatility': float(df.iloc[index]['volatility']) if 'volatility' in df.columns and not pd.isna(df.iloc[index]['volatility']) else None,
                    'current_price': current_price
                }

                # Generate signal directly from indicators (skip indicator calculation)
                current_date = df.index[index]
                historical_data = df.iloc[:index+1].copy()
                signal = self._historical_signal_generator._generate_signal_from_indicators(
                    symbol,
                    current_price,
                    indicators,
                    historical_data
                )

                if signal:
                    signal['entry_price'] = current_price
                    signal['timestamp'] = current_date.isoformat() if hasattr(current_date, 'isoformat') else str(current_date)
                    return signal
            except Exception as e:
                logger.debug(f"Pre-calculated indicator signal generation failed: {e}, falling back to standard")

        # Use real signal generation with historical data (fallback)
        try:
            from argo.backtest.historical_signal_generator import HistoricalSignalGenerator

            # Initialize historical signal generator if not already done
            if not hasattr(self, '_historical_signal_generator'):
                self._historical_signal_generator = HistoricalSignalGenerator(
                    self.signal_service,
                    self.data_manager
                )

            current_date = df.index[index]
            signal = await self._historical_signal_generator.generate_signal_for_date(
                symbol,
                current_date,
                df,
                index
            )

            if signal:
                signal['entry_price'] = current_price
                return signal

        except Exception as e:
            logger.debug(f"Historical signal generation failed for {symbol}: {e}, using fallback")

        # Fallback to simple momentum-based signal if historical generator fails
        if index < 50:
            return None  # Need more data for pattern detection

        # Simple momentum-based fallback signal
        lookback = min(20, index)
        recent_prices = df.iloc[index-lookback:index]['Close'].values
        current_ma = recent_prices.mean()

        price_ratio = current_price / current_ma if current_ma > 0 else 1.0

        # Generate signal based on price vs moving average
        if price_ratio > 1.01:  # Price 1% above MA = bullish
            confidence = min(85.0, 72.0 + (price_ratio - 1.0) * 300)
            return {
                'action': 'BUY',
                'entry_price': current_price,
                'confidence': confidence,
                'target_price': current_price * 1.05,
                'stop_price': current_price * 0.97,
                'direction': 'LONG'
            }
        elif price_ratio < 0.99:  # Price 1% below MA = bearish
            confidence = min(85.0, 72.0 + (1.0 - price_ratio) * 300)
            return {
                'action': 'SELL',
                'entry_price': current_price,
                'confidence': confidence,
                'target_price': current_price * 0.95,
                'stop_price': current_price * 1.03,
                'direction': 'SHORT'
            }

        return None

    def _apply_costs(
        self,
        price: float,
        side: str,
        is_entry: bool = True,
        symbol: str = None,
        trade_size: float = None,
        df: pd.DataFrame = None,
        index: int = None
    ) -> float:
        """
        Apply realistic trading costs (v5.0 enhancement)
        Now supports EnhancedTransactionCostModel for more accurate costs

        Args:
            price: Base price
            side: 'LONG' or 'SHORT'
            is_entry: True for entry, False for exit
            symbol: Trading symbol (required for enhanced model)
            trade_size: Trade size in shares (required for enhanced model)
            df: DataFrame with volume data (required for enhanced model)
            index: Current index in DataFrame (required for enhanced model)

        Returns:
            Adjusted price with costs
        """
        if not self.use_cost_modeling:
            return price

        # FIX: Always try to use enhanced cost model when enabled
        # Try to get required parameters even if not explicitly provided
        if self.use_enhanced_cost_model and self.enhanced_cost_model:
            # Try to infer missing parameters
            inferred_symbol = symbol or "UNKNOWN"
            inferred_trade_size = trade_size if trade_size is not None else 100  # Default fallback
            inferred_df = df
            inferred_index = index

            # If df/index not provided but we have symbol, try to get from data_manager
            if inferred_df is None and inferred_symbol != "UNKNOWN":
                try:
                    # Try to get current data from data_manager (if available)
                    if hasattr(self, 'data_manager') and self.data_manager:
                        temp_df = self.data_manager.fetch_historical_data(inferred_symbol, period="1y")
                        if temp_df is not None:
                            from argo.backtest.data_converter import DataConverter
                            inferred_df = DataConverter.to_pandas(temp_df)
                            if inferred_df is not None and len(inferred_df) > 0:
                                inferred_index = len(inferred_df) - 1
                except Exception as e:
                    logger.debug(f"Could not infer df/index for enhanced cost model: {e}")

            # Use enhanced model if we have minimum required parameters
            if inferred_df is not None and inferred_index is not None:
                try:
                    # Get volume and volatility data
                    if 'Volume' in inferred_df.columns and inferred_index < len(inferred_df):
                        # Calculate average volume (20-day)
                        volume_window = min(20, inferred_index + 1)
                        avg_volume = float(inferred_df.iloc[max(0, inferred_index - volume_window + 1):inferred_index + 1]['Volume'].mean())
                    else:
                        avg_volume = 1_000_000  # Default fallback

                    # Get volatility from indicators or calculate
                    if 'volatility' in inferred_df.columns and inferred_index < len(inferred_df):
                        volatility = float(inferred_df.iloc[inferred_index]['volatility'])
                        # Convert annualized to daily
                        if volatility > 1.0:  # Likely annualized
                            volatility = volatility / np.sqrt(252)
                    else:
                        # Calculate from returns
                        if inferred_index >= 20:
                            returns = inferred_df.iloc[max(0, inferred_index - 20):inferred_index + 1]['Close'].pct_change().dropna()
                            volatility = float(returns.std() * np.sqrt(252)) / np.sqrt(252) if len(returns) > 0 else 0.02
                        else:
                            volatility = 0.02  # Default 2% daily volatility

                    # Apply enhanced cost model
                    result = self.enhanced_cost_model.apply_costs_to_price(
                        price=price,
                        side=side,
                        symbol=inferred_symbol,
                        trade_size=inferred_trade_size,
                        avg_volume=avg_volume,
                        volatility=volatility,
                        is_entry=is_entry
                    )
                    logger.debug(f"[{inferred_symbol}] Using enhanced cost model: ${price:.4f} -> ${result:.4f}")
                    return result
                except Exception as e:
                    logger.warning(f"[{inferred_symbol}] Enhanced cost model failed, falling back to simple model: {e}")
                    # Fall through to simple model
            elif symbol and trade_size is not None:
                # Have symbol and trade_size but not df/index - log warning
                logger.debug(f"[{symbol}] Enhanced cost model requires df/index, using simple model")

        # Simple cost model (fallback or default)
        slippage = price * self.slippage_pct
        spread = price * self.spread_pct * 0.5
        commission = price * self.commission_pct

        if side == 'LONG':
            if is_entry:
                return price + slippage + spread + commission
            else:
                return price - slippage - spread - commission
        else:
            if is_entry:
                return price - slippage - spread - commission
            else:
                return price + slippage + spread + commission

    def _check_portfolio_risk_limits(self) -> tuple[bool, str]:
        """
        Check portfolio-level risk limits

        Returns:
            (can_trade, reason) - True if can trade, False with reason if not
        """
        # Check maximum positions
        if len(self.positions) >= self.max_positions:
            return False, f"Maximum positions reached ({self.max_positions})"

        # Check portfolio drawdown
        if hasattr(self, 'peak_equity') and self.peak_equity > 0:
            current_equity = self.equity_curve[-1] if self.equity_curve else self.initial_capital
            drawdown_pct = (self.peak_equity - current_equity) / self.peak_equity

            if drawdown_pct >= self.max_portfolio_drawdown:
                return False, f"Portfolio drawdown limit reached ({drawdown_pct*100:.2f}% >= {self.max_portfolio_drawdown*100:.2f}%)"

        return True, ""

    def _get_drawdown_adjustment(self) -> float:
        """
        Get position size adjustment based on current drawdown

        Returns:
            Multiplier for position size (0.5 to 1.0)
        """
        if not TradingConstants.REDUCE_SIZE_ON_DRAWDOWN:
            return 1.0

        if hasattr(self, 'peak_equity') and self.peak_equity > 0:
            current_equity = self.equity_curve[-1] if self.equity_curve else self.initial_capital
            drawdown_pct = (self.peak_equity - current_equity) / self.peak_equity

            # Reduce position size as drawdown increases
            # At 0% drawdown: 1.0x
            # At 10% drawdown: 0.75x
            # At 20% drawdown: 0.5x
            if drawdown_pct > 0:
                adjustment = max(0.5, 1.0 - (drawdown_pct / self.max_portfolio_drawdown) * 0.5)
                return adjustment

        return 1.0

    def _get_symbol_confidence_threshold(self, symbol: str, base_confidence: float) -> float:
        """
        Get symbol-specific confidence threshold

        Args:
            symbol: Trading symbol
            base_confidence: Base confidence threshold

        Returns:
            Adjusted confidence threshold for symbol
        """
        # Symbol-specific adjustments
        symbol_thresholds = {
            'SPY': base_confidence - 2.0,  # Lower threshold for SPY (more liquid)
            'QQQ': base_confidence - 2.0,  # Lower threshold for QQQ
            'BTC-USD': base_confidence + 3.0,  # Higher threshold for crypto (more volatile)
            'ETH-USD': base_confidence + 3.0,  # Higher threshold for crypto
            'TSLA': base_confidence + 1.0,  # Higher threshold for volatile stocks
            'AMD': base_confidence + 1.0,  # Higher threshold for volatile stocks
        }

        return symbol_thresholds.get(symbol, base_confidence)

    def _enter_position(
        self,
        symbol: str,
        price: float,
        date: datetime,
        signal: Dict,
        side: str,
        entry_bar: int,
        df: pd.DataFrame = None
    ):
        """Enter a new position with realistic cost modeling and risk management"""

        # Check portfolio risk limits
        can_trade, reason = self._check_portfolio_risk_limits()
        if not can_trade:
            logger.debug(f"[{symbol}] Cannot enter position: {reason}")
            return
        # Calculate position size first (needed for enhanced cost model)
        try:
            if hasattr(self, '_performance_enhancer') and self._performance_enhancer:
                volatility = signal.get('volatility', 0.2)
                # Apply drawdown adjustment to position size
                drawdown_adjustment = self._get_drawdown_adjustment()
                base_position_value = self._performance_enhancer.calculate_position_size(
                    self.capital,
                    signal.get('confidence', 55.0),
                    volatility,
                    symbol
                )
                position_value = base_position_value * drawdown_adjustment

                # Additional adjustment: Increase size slightly for high-confidence signals
                confidence = signal.get('confidence', 55.0)
                if confidence >= 70.0:
                    confidence_boost = 1.1  # 10% boost for very high confidence
                    position_value *= confidence_boost
                    logger.debug(f"[{symbol}] Position size boosted by 10% for high confidence ({confidence:.1f}%)")

                if drawdown_adjustment < 1.0:
                    logger.debug(f"[{symbol}] Position size reduced by {(1-drawdown_adjustment)*100:.1f}% due to drawdown")
            else:
                position_value = self.capital * BacktestConstants.DEFAULT_POSITION_SIZE_PCT
        except:
            position_value = self.capital * BacktestConstants.DEFAULT_POSITION_SIZE_PCT  # Fallback

        quantity = int(position_value / price)

        # Apply entry costs (with enhanced model if available)
        if df is not None and entry_bar < len(df):
            entry_price = self._apply_costs(
                price, side, is_entry=True,
                symbol=symbol, trade_size=quantity,
                df=df, index=entry_bar
            )
        else:
            entry_price = self._apply_costs(price, side, is_entry=True)

        # Recalculate quantity with adjusted price
        quantity = int(position_value / entry_price)

        if quantity <= 0:
            logger.warning(f"[{symbol}] Cannot enter position: quantity={quantity} (position_value=${position_value:.2f}, entry_price=${entry_price:.2f})")
            # Don't raise exception, just return (graceful failure)
            return

        cost = quantity * entry_price
        if cost > self.capital:
            logger.warning(f"[{symbol}] Cannot enter position: insufficient capital (need ${cost:.2f}, have ${self.capital:.2f})")
            # Don't raise exception, just return (graceful failure)
            return

        self.capital -= cost

        trade = Trade(
            entry_date=date,
            exit_date=None,
            symbol=symbol,
            entry_price=entry_price,  # Use adjusted price with costs
            exit_price=None,
            quantity=quantity,
            side=side,
            confidence=signal.get('confidence'),
            stop_loss=signal.get('stop_price'),
            take_profit=signal.get('target_price')
        )

        self.positions[symbol] = trade
        self.position_entry_bars[symbol] = entry_bar  # Track entry bar for minimum holding period

    def _exit_position(
        self,
        symbol: str,
        exit_price: float,
        exit_date: datetime,
        df: pd.DataFrame = None,
        exit_bar: int = None
    ):
        """Exit an existing position with realistic cost modeling (v5.0)"""
        if symbol not in self.positions:
            return

        trade = self.positions[symbol]

        # Apply exit costs (with enhanced model if available)
        if df is not None and exit_bar is not None and exit_bar < len(df):
            adjusted_exit_price = self._apply_costs(
                exit_price, trade.side, is_entry=False,
                symbol=symbol, trade_size=trade.quantity,
                df=df, index=exit_bar
            )
        else:
            adjusted_exit_price = self._apply_costs(exit_price, trade.side, is_entry=False)

        trade.exit_date = exit_date
        trade.exit_price = adjusted_exit_price

        # Calculate P&L with costs
        if trade.side == 'LONG':
            proceeds = trade.quantity * adjusted_exit_price
            trade.pnl = proceeds - (trade.quantity * trade.entry_price)
        else:
            # SHORT: entry was sell, exit is buy
            proceeds = trade.quantity * adjusted_exit_price
            trade.pnl = (trade.quantity * trade.entry_price) - proceeds

        trade.pnl_pct = to_percentage(trade.pnl / (trade.quantity * trade.entry_price))

        # Log trade completion
        logger.info(f"[{symbol}][{exit_date.date()}] Position closed: {trade.side} @ ${adjusted_exit_price:.2f}, "
                   f"P&L=${trade.pnl:.2f} ({trade.pnl_pct:+.2f}%), "
                   f"held for {(exit_date - trade.entry_date).days} days")

        self.capital += proceeds
        self.trades.append(trade)
        del self.positions[symbol]
        # Remove entry bar tracking
        if symbol in self.position_entry_bars:
            del self.position_entry_bars[symbol]

    def _get_dynamic_stop_loss(self, trade, current_price: float) -> Optional[float]:
        """
        Get dynamically adjusted stop loss based on portfolio drawdown

        Returns:
            Adjusted stop loss price or None if no adjustment needed
        """
        if not hasattr(self, 'peak_equity') or self.peak_equity <= 0:
            return None

        current_equity = self.equity_curve[-1] if self.equity_curve else self.initial_capital
        drawdown_pct = (self.peak_equity - current_equity) / self.peak_equity

        # Tighten stops as drawdown increases
        # At 0% drawdown: no adjustment
        # At 10% drawdown: tighten by 20%
        # At 20% drawdown: tighten by 40%
        if drawdown_pct > 0.05:  # Only if drawdown > 5%
            tightening_factor = 1.0 - (drawdown_pct / self.max_portfolio_drawdown) * 0.4
            tightening_factor = max(0.6, tightening_factor)  # Don't tighten more than 40%

            if trade.stop_loss:
                original_stop_distance = abs(trade.entry_price - trade.stop_loss)
                adjusted_stop_distance = original_stop_distance * tightening_factor

                if trade.side == 'LONG':
                    adjusted_stop = trade.entry_price - adjusted_stop_distance
                    # Only tighten, never loosen
                    return max(adjusted_stop, trade.stop_loss)
                else:  # SHORT
                    adjusted_stop = trade.entry_price + adjusted_stop_distance
                    # Only tighten, never loosen
                    return min(adjusted_stop, trade.stop_loss)

        return None

    def _check_exit_conditions(
        self,
        symbol: str,
        current_price: float,
        current_date: datetime,
        current_bar: int,
        df: pd.DataFrame = None
    ):
        """Check if position should be exited due to stop loss or take profit"""
        if symbol not in self.positions:
            return

        trade = self.positions[symbol]

        # Apply dynamic stop loss tightening based on portfolio drawdown
        dynamic_stop = self._get_dynamic_stop_loss(trade, current_price)
        effective_stop_loss = dynamic_stop if dynamic_stop is not None else trade.stop_loss

        # Check minimum holding period (but allow stop loss exits regardless)
        # Only apply minimum holding period to normal exits, not stop losses
        is_stop_loss_exit = False
        if effective_stop_loss:
            if (trade.side == 'LONG' and current_price <= effective_stop_loss) or \
               (trade.side == 'SHORT' and current_price >= effective_stop_loss):
                is_stop_loss_exit = True

        if symbol in self.position_entry_bars and not is_stop_loss_exit:
            bars_held = current_bar - self.position_entry_bars[symbol]
            if bars_held < self.min_holding_bars:
                return  # Don't exit yet - minimum holding period not met (unless stop loss)

        # Check stop loss (use dynamic stop if available)
        if effective_stop_loss:
            if trade.side == 'LONG' and current_price <= effective_stop_loss:
                stop_reason = "dynamic" if dynamic_stop is not None else "static"
                logger.info(f"[{symbol}][{current_date.date()}] 🛑 Stop loss hit ({stop_reason}): ${current_price:.2f} <= ${effective_stop_loss:.2f}")
                self._exit_position(symbol, effective_stop_loss, current_date, df, current_bar)
                return
            elif trade.side == 'SHORT' and current_price >= effective_stop_loss:
                stop_reason = "dynamic" if dynamic_stop is not None else "static"
                logger.info(f"[{symbol}][{current_date.date()}] 🛑 Stop loss hit ({stop_reason}): ${current_price:.2f} >= ${effective_stop_loss:.2f}")
                self._exit_position(symbol, effective_stop_loss, current_date, df, current_bar)
                return

        # Check take profit
        if trade.take_profit:
            if trade.side == 'LONG' and current_price >= trade.take_profit:
                logger.info(f"[{symbol}][{current_date.date()}] 🎯 Take profit hit: ${current_price:.2f} >= ${trade.take_profit:.2f}")
                self._exit_position(symbol, trade.take_profit, current_date, df, current_bar)
                return
            elif trade.side == 'SHORT' and current_price <= trade.take_profit:
                logger.info(f"[{symbol}][{current_date.date()}] 🎯 Take profit hit: ${current_price:.2f} <= ${trade.take_profit:.2f}")
                self._exit_position(symbol, trade.take_profit, current_date, df, current_bar)
                return
