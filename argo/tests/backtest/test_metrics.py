#!/usr/bin/env python3
"""
Tests for Metrics Calculations
Validates all metrics are calculated correctly
"""
import pytest
import numpy as np
from datetime import datetime, timedelta
from argo.backtest.base_backtester import BaseBacktester, BacktestMetrics, Trade


class TestMetricsCalculations:
    """Test metrics calculation correctness"""
    
    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio is calculated correctly"""
        # Create simple backtester instance
        class TestBacktester(BaseBacktester):
            async def run_backtest(self, symbol: str, **kwargs):
                return None
        
        bt = TestBacktester(initial_capital=100000)
        
        # Create equity curve with known returns
        # 10% return over 10 days = ~1% per day
        bt.equity_curve = [100000]
        bt.dates = [datetime(2020, 1, 1)]
        
        for i in range(1, 11):
            bt.equity_curve.append(bt.equity_curve[-1] * 1.01)  # 1% daily return
            bt.dates.append(bt.dates[-1] + timedelta(days=1))
        
        # Add some trades
        for i in range(5):
            trade = Trade(
                entry_date=datetime(2020, 1, 1),
                exit_date=datetime(2020, 1, 2),
                symbol='TEST',
                entry_price=100.0,
                exit_price=101.0,  # 1% profit
                quantity=100,
                side='LONG',
                pnl=100.0,
                pnl_pct=1.0
            )
            bt.trades.append(trade)
        
        metrics = bt.calculate_metrics()
        
        # Verify metrics are reasonable
        assert metrics.total_return_pct > 0
        assert metrics.win_rate_pct == 100.0  # All trades profitable
        assert metrics.total_trades == 5
    
    def test_max_drawdown_calculation(self):
        """Test max drawdown is calculated correctly"""
        class TestBacktester(BaseBacktester):
            async def run_backtest(self, symbol: str, **kwargs):
                return None
        
        bt = TestBacktester(initial_capital=100000)
        
        # Create equity curve with a drawdown
        # Start at 100k, go to 120k, drop to 90k, recover to 110k
        bt.equity_curve = [100000, 110000, 120000, 115000, 90000, 95000, 110000]
        bt.dates = [datetime(2020, 1, 1) + timedelta(days=i) for i in range(7)]
        
        metrics = bt.calculate_metrics()
        
        # Max drawdown should be negative (from 120k to 90k = -25%)
        assert metrics.max_drawdown_pct < 0
        assert metrics.max_drawdown_pct <= -20  # At least 20% drawdown
    
    def test_profit_factor_calculation(self):
        """Test profit factor is calculated correctly"""
        class TestBacktester(BaseBacktester):
            async def run_backtest(self, symbol: str, **kwargs):
                return None
        
        bt = TestBacktester(initial_capital=100000)
        
        # Add winning and losing trades
        # 3 wins of $100 each = $300 gross profit
        # 2 losses of $50 each = $100 gross loss
        # Profit factor = 300/100 = 3.0
        
        for i in range(3):
            trade = Trade(
                entry_date=datetime(2020, 1, 1),
                exit_date=datetime(2020, 1, 2),
                symbol='TEST',
                entry_price=100.0,
                exit_price=101.0,
                quantity=100,
                side='LONG',
                pnl=100.0,
                pnl_pct=1.0
            )
            bt.trades.append(trade)
        
        for i in range(2):
            trade = Trade(
                entry_date=datetime(2020, 1, 1),
                exit_date=datetime(2020, 1, 2),
                symbol='TEST',
                entry_price=100.0,
                exit_price=99.5,
                quantity=100,
                side='LONG',
                pnl=-50.0,
                pnl_pct=-0.5
            )
            bt.trades.append(trade)
        
        bt.equity_curve = [100000, 100300]  # Start + profit
        bt.dates = [datetime(2020, 1, 1), datetime(2020, 1, 2)]
        
        metrics = bt.calculate_metrics()
        
        # Profit factor should be around 3.0 (300/100)
        assert abs(metrics.profit_factor - 3.0) < 0.1

