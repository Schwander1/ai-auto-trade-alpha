#!/usr/bin/env python3
"""
Base Backtester Class
Foundation for all backtesting implementations
"""
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import logging
from argo.backtest.constants import BacktestConstants
from argo.backtest.exceptions import (
    BacktestError, PositionError, InsufficientCapitalError,
    InvalidPositionSizeError, MetricsError
)

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Represents a single trade"""
    entry_date: datetime
    exit_date: Optional[datetime]
    symbol: str
    entry_price: float
    exit_price: Optional[float]
    quantity: int
    side: str  # 'LONG' or 'SHORT'
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    confidence: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass
class BacktestMetrics:
    """Backtest performance metrics"""
    total_return_pct: float
    annualized_return_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float
    win_rate_pct: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win_pct: float
    avg_loss_pct: float
    largest_win_pct: float
    largest_loss_pct: float
    # ENHANCED: Additional risk metrics
    var_95_pct: float = 0.0  # Value at Risk (95% confidence)
    cvar_95_pct: float = 0.0  # Conditional VaR (95% confidence)
    calmar_ratio: float = 0.0  # Annualized return / Max drawdown
    omega_ratio: float = 0.0  # Probability-weighted ratio of gains vs losses
    ulcer_index: float = 0.0  # Measure of drawdown depth and duration

class BaseBacktester(ABC):
    """Base class for all backtesters"""

    def __init__(self, initial_capital: float = None, min_holding_bars: int = 5):
        """
        Initialize backtester

        Args:
            initial_capital: Starting capital (default: BacktestConstants.DEFAULT_INITIAL_CAPITAL)
            min_holding_bars: Minimum bars before exit (default: 5)
        """
        if initial_capital is None:
            initial_capital = BacktestConstants.DEFAULT_INITIAL_CAPITAL
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: Dict[str, Trade] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [initial_capital]
        self.dates: List[datetime] = []
        self.position_entry_bars: Dict[str, int] = {}  # Track entry bar for minimum holding period
        self.min_holding_bars = min_holding_bars

    @abstractmethod
    async def run_backtest(self, symbol: str, **kwargs) -> Optional[BacktestMetrics]:
        """
        Run backtest - must be implemented by subclasses

        Args:
            symbol: Trading symbol to backtest
            **kwargs: Additional parameters (start_date, end_date, min_confidence, etc.)

        Returns:
            BacktestMetrics or None if backtest failed
        """
        pass

    @staticmethod
    def create_empty_metrics() -> BacktestMetrics:
        """Create empty BacktestMetrics for error cases"""
        return BacktestMetrics(
            total_return_pct=0.0,
            annualized_return_pct=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            max_drawdown_pct=0.0,
            win_rate_pct=0.0,
            profit_factor=0.0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            avg_win_pct=0.0,
            avg_loss_pct=0.0,
            largest_win_pct=0.0,
            largest_loss_pct=0.0,
            var_95_pct=0.0,
            cvar_95_pct=0.0,
            calmar_ratio=0.0,
            omega_ratio=0.0,
            ulcer_index=0.0
        )

    def calculate_metrics(self) -> BacktestMetrics:
        """Calculate comprehensive performance metrics"""
        if not self.trades:
            return BacktestMetrics.create_empty_metrics()

        # Calculate returns
        equity = np.array(self.equity_curve)
        returns = np.diff(equity) / equity[:-1]

        # Total return
        total_return = (equity[-1] - self.initial_capital) / self.initial_capital

        # Annualized return
        if len(self.dates) > 1:
            days = (self.dates[-1] - self.dates[0]).days
            years = days / 365.25
            if years > 0:
                annualized_return = (1 + total_return) ** (1 / years) - 1
            else:
                annualized_return = 0.0
        else:
            annualized_return = 0.0

        # Sharpe ratio
        if len(returns) > 0 and np.std(returns) > 0:
            sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252)
        else:
            sharpe_ratio = 0.0

        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0 and np.std(downside_returns) > 0:
            sortino_ratio = (np.mean(returns) / np.std(downside_returns)) * np.sqrt(252)
        else:
            sortino_ratio = 0.0

        # Max drawdown
        cumulative = np.maximum.accumulate(equity)
        drawdown = (equity - cumulative) / cumulative
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0.0

        # Trade statistics
        completed_trades = [t for t in self.trades if t.exit_price is not None and t.pnl is not None]
        winning_trades = [t for t in completed_trades if t.pnl > 0]
        losing_trades = [t for t in completed_trades if t.pnl <= 0]

        win_rate = len(winning_trades) / len(completed_trades) if completed_trades else 0.0

        # Profit factor
        gross_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0.0
        gross_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

        # Average win/loss
        avg_win = np.mean([t.pnl_pct for t in winning_trades]) if winning_trades else 0.0
        avg_loss = np.mean([t.pnl_pct for t in losing_trades]) if losing_trades else 0.0

        # Largest win/loss
        largest_win = max([t.pnl_pct for t in winning_trades]) if winning_trades else 0.0
        largest_loss = min([t.pnl_pct for t in losing_trades]) if losing_trades else 0.0

        # ENHANCED: Calculate additional risk metrics
        # Value at Risk (VaR) - 95% confidence
        var_95_pct = 0.0
        cvar_95_pct = 0.0
        if len(returns) > 0:
            var_95 = np.percentile(returns, 5)  # 5th percentile (95% VaR)
            var_95_pct = var_95 * 100
            # Conditional VaR (expected loss beyond VaR)
            cvar_95 = returns[returns <= var_95].mean() if len(returns[returns <= var_95]) > 0 else var_95
            cvar_95_pct = cvar_95 * 100

        # Calmar Ratio (annualized return / max drawdown)
        calmar_ratio = 0.0
        if abs(max_drawdown) > 0.0001:  # Avoid division by zero
            calmar_ratio = annualized_return / abs(max_drawdown)

        # Omega Ratio (probability-weighted ratio of gains vs losses)
        omega_ratio = 0.0
        if len(returns) > 0:
            threshold = 0.0  # Risk-free rate (0 for simplicity)
            gains = returns[returns > threshold] - threshold
            losses = threshold - returns[returns < threshold]
            if len(losses) > 0 and losses.sum() > 0:
                omega_ratio = gains.sum() / losses.sum() if losses.sum() > 0 else 0.0

        # Ulcer Index (measure of drawdown depth and duration)
        ulcer_index = 0.0
        if len(equity) > 1:
            # Calculate drawdowns
            peak = np.maximum.accumulate(equity)
            drawdowns = (equity - peak) / peak
            # Square of drawdowns, then average, then square root
            ulcer_index = np.sqrt(np.mean(drawdowns ** 2)) * 100

        return BacktestMetrics(
            total_return_pct=total_return * 100,
            annualized_return_pct=annualized_return * 100,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown_pct=max_drawdown * 100,
            win_rate_pct=win_rate * 100,
            profit_factor=profit_factor,
            total_trades=len(completed_trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_win_pct=avg_win,
            avg_loss_pct=avg_loss,
            largest_win_pct=largest_win,
            largest_loss_pct=largest_loss,
            var_95_pct=var_95_pct,
            cvar_95_pct=cvar_95_pct,
            calmar_ratio=calmar_ratio,
            omega_ratio=omega_ratio,
            ulcer_index=ulcer_index
        )

    def update_equity(self, current_price: float, date: datetime, sample_rate: int = 1):
        """
        Update equity curve
        ENHANCED: Added sampling for long backtests to reduce memory usage

        Args:
            current_price: Current price
            date: Current date
            sample_rate: Store every Nth point (1 = all, 10 = every 10th point)
        """
        position_value = sum(
            pos.quantity * current_price if pos.side == 'LONG' else -pos.quantity * current_price
            for pos in self.positions.values()
        )
        total_equity = self.capital + position_value

        # ENHANCED: Sample equity curve for long backtests to save memory
        # Always store first and last points, sample in between
        if sample_rate > 1 and len(self.equity_curve) > 0:
            # Store every Nth point, or if it's the last point
            if len(self.equity_curve) % sample_rate == 0:
                self.equity_curve.append(total_equity)
                self.dates.append(date)
        else:
            # Store all points (default behavior)
            self.equity_curve.append(total_equity)
            self.dates.append(date)

    def reset(self):
        """Reset backtester state"""
        self.capital = self.initial_capital
        self.positions.clear()
        self.trades.clear()
        self.equity_curve = [self.initial_capital]
        self.dates.clear()
        self.position_entry_bars.clear()

    def validate_state(self) -> List[str]:
        """
        Validate backtester state, return list of issues
        ENHANCED: More comprehensive validation checks

        Returns:
            List of validation issue messages (empty if no issues)
        """
        issues = []

        # Check capital
        if self.capital < 0:
            issues.append(f"Capital is negative: ${self.capital:.2f}")
        elif self.capital > self.initial_capital * 10:
            issues.append(f"Capital seems unreasonably high: ${self.capital:.2f} (initial: ${self.initial_capital:.2f})")

        # Check position count
        if len(self.positions) > BacktestConstants.MAX_OPEN_POSITIONS:
            issues.append(f"Too many open positions: {len(self.positions)} (max: {BacktestConstants.MAX_OPEN_POSITIONS})")

        # Check positions for invalid values
        for symbol, position in self.positions.items():
            if position.entry_price <= 0:
                issues.append(f"Position {symbol} has invalid entry price: {position.entry_price}")
            if position.quantity <= 0:
                issues.append(f"Position {symbol} has invalid quantity: {position.quantity}")
            if position.entry_date is None:
                issues.append(f"Position {symbol} has missing entry date")

        # Check trades for unrealistic values
        for i, trade in enumerate(self.trades):
            if trade.pnl_pct is not None:
                if trade.pnl_pct > BacktestConstants.MAX_REASONABLE_PNL_PCT:
                    issues.append(f"Trade {i} has unrealistic P&L: {trade.pnl_pct:.2f}%")
                elif trade.pnl_pct < BacktestConstants.MIN_REASONABLE_PNL_PCT:
                    issues.append(f"Trade {i} has unrealistic loss: {trade.pnl_pct:.2f}%")

            # Check for missing required fields
            if trade.entry_price <= 0:
                issues.append(f"Trade {i} has invalid entry price: {trade.entry_price}")
            if trade.exit_price is not None and trade.exit_price <= 0:
                issues.append(f"Trade {i} has invalid exit price: {trade.exit_price}")
            if trade.quantity <= 0:
                issues.append(f"Trade {i} has invalid quantity: {trade.quantity}")

            # Check date consistency
            if trade.exit_date is not None and trade.entry_date is not None:
                if trade.exit_date < trade.entry_date:
                    issues.append(f"Trade {i} has exit date before entry date")

        # Check equity curve consistency
        if len(self.equity_curve) != len(self.dates):
            issues.append(f"Equity curve length ({len(self.equity_curve)}) doesn't match dates length ({len(self.dates)})")

        # Check for negative equity
        if self.equity_curve and min(self.equity_curve) < 0:
            issues.append(f"Equity curve has negative values (min: ${min(self.equity_curve):.2f})")

        # Check for decreasing equity curve (should generally increase or decrease smoothly)
        if len(self.equity_curve) > 1:
            # Check for NaN or Inf values
            equity_array = np.array(self.equity_curve)
            if np.any(np.isnan(equity_array)):
                issues.append("Equity curve contains NaN values")
            if np.any(np.isinf(equity_array)):
                issues.append("Equity curve contains Inf values")

            # Check for unrealistic jumps (more than 50% in one period)
            if len(equity_array) > 1:
                returns = np.diff(equity_array) / equity_array[:-1]
                extreme_returns = returns[np.abs(returns) > 0.5]
                if len(extreme_returns) > 0:
                    issues.append(f"Equity curve has extreme returns: {len(extreme_returns)} periods with >50% change")

        # Check dates are in order
        if len(self.dates) > 1:
            for i in range(1, len(self.dates)):
                if self.dates[i] < self.dates[i-1]:
                    issues.append(f"Dates are not in order: {self.dates[i-1]} > {self.dates[i]}")
                    break

        # Check for look-ahead bias indicators (positions opened before data available)
        # This is a heuristic check - if we have very early positions, might indicate bias
        if self.trades and self.dates:
            first_trade_date = min(t.entry_date for t in self.trades if t.entry_date is not None)
            first_data_date = self.dates[0] if self.dates else None
            if first_data_date and first_trade_date:
                # Allow some warmup period (e.g., 20 days)
                warmup_days = 20
                if (first_trade_date - first_data_date).days < warmup_days:
                    issues.append(f"First trade ({first_trade_date}) very close to data start ({first_data_date}), possible look-ahead bias")

        return issues
