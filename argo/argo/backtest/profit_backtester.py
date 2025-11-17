#!/usr/bin/env python3
"""
Profit Backtester
Tests Argo trading profitability with full execution simulation
Focus: Returns, Sharpe ratio, drawdown, profit optimization (for Argo trading)
"""
import sys
import pandas as pd
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import logging
import copy

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from argo.backtest.base_backtester import BaseBacktester, Trade, BacktestMetrics
from argo.backtest.data_manager import DataManager
from argo.backtest.strategy_backtester import StrategyBacktester
from argo.backtest.constants import TransactionCostConstants, BacktestConstants

logger = logging.getLogger(__name__)

class ProfitBacktester(BaseBacktester):
    """
    Backtests Argo trading profitability
    Includes slippage, fees, risk management, position sizing
    Focus: Profitability, risk-adjusted returns, drawdown
    """
    
    def __init__(
        self,
        initial_capital: float = None,
        slippage_pct: float = TransactionCostConstants.DEFAULT_SLIPPAGE_PCT * 2,  # 0.1% slippage (higher for profit testing)
        commission_pct: float = TransactionCostConstants.DEFAULT_COMMISSION_PCT,
        position_size_pct: float = 10.0,
        max_position_size_pct: float = 15.0
    ):
        if initial_capital is None:
            initial_capital = BacktestConstants.DEFAULT_INITIAL_CAPITAL
        super().__init__(initial_capital)
        self.data_manager = DataManager()
        self.strategy_backtester = StrategyBacktester(initial_capital)
        self.slippage_pct = slippage_pct
        self.commission_pct = commission_pct
        self.position_size_pct = position_size_pct
        self.max_position_size_pct = max_position_size_pct
        
    async def run_backtest(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_confidence: float = 75.0
    ) -> Optional[BacktestMetrics]:
        """
        Run profit backtest with full execution simulation
        
        Args:
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            min_confidence: Minimum confidence threshold
        
        Returns:
            BacktestMetrics with profitability metrics
        """
        # Use strategy backtester to generate signals and trades
        # Then apply profit optimization and execution simulation
        strategy_metrics = await self.strategy_backtester.run_backtest(
            symbol, start_date, end_date, min_confidence
        )
        
        if strategy_metrics is None:
            return None
        
        # Copy trades from strategy backtester to this instance
        # This allows us to apply execution costs to the actual trades
        # Use deep copy to avoid modifying the original trades
        from copy import deepcopy
        self.trades = deepcopy(self.strategy_backtester.trades)
        self.positions = deepcopy(self.strategy_backtester.positions)
        self.capital = self.strategy_backtester.capital
        self.equity_curve = self.strategy_backtester.equity_curve.copy()
        self.dates = self.strategy_backtester.dates.copy()
        
        # Apply execution costs (slippage, fees) to trades
        self._apply_execution_costs()
        
        # Recalculate metrics with costs applied
        metrics = self.calculate_metrics()
        
        return metrics
    
    def _apply_execution_costs(self):
        """Apply execution costs using TransactionCostAnalyzer"""
        try:
            from argo.backtest.transaction_cost_analyzer import TransactionCostAnalyzer, Order, OrderType
            
            tca = TransactionCostAnalyzer({
                'commission_per_share': 0.0035,
                'min_commission': 0.35,
                'max_commission': 1.0
            })
            
            for trade in self.trades:
                # Get trade attributes (may vary by backtester)
                symbol = getattr(trade, 'symbol', 'UNKNOWN')
                shares = getattr(trade, 'shares', getattr(trade, 'quantity', 0))
                entry_price = getattr(trade, 'entry_price', 0)
                direction = getattr(trade, 'direction', getattr(trade, 'side', 'LONG'))
                
                if shares == 0 or entry_price == 0:
                    continue
                
                # Create order representation
                order = Order(
                    symbol=symbol,
                    shares=int(shares),
                    price=entry_price,
                    side='buy' if direction == 'LONG' else 'sell',
                    type=OrderType.MARKET
                )
                
                # Get market data for cost calculation
                market_data = {
                    'bid': entry_price * 0.9999,
                    'ask': entry_price * 1.0001,
                    'volatility': 0.02,  # Default
                    'avg_volume': 1000000  # Default
                }
                
                # Calculate costs
                costs = tca.calculate_costs(order, market_data)
                
                # Adjust trade entry price with costs
                cost_per_share = costs.total / shares if shares > 0 else 0
                if direction == 'LONG':
                    trade.entry_price = entry_price + cost_per_share
                else:
                    trade.entry_price = entry_price - cost_per_share
                    
                # Recalculate P&L if exit price exists
                if hasattr(trade, 'exit_price') and trade.exit_price:
                    if direction == 'LONG':
                        trade.pnl = (trade.exit_price - trade.entry_price) * shares
                    else:
                        trade.pnl = (trade.entry_price - trade.exit_price) * shares
        except Exception as e:
            logger.warning(f"Could not apply transaction costs: {e}, using simple cost model")
            # Fallback to simple cost model
            self._apply_simple_execution_costs()
    
    def _apply_simple_execution_costs(self):
        """Apply slippage and commission to all trades"""
        for trade in self.trades:
            if trade.exit_price is None or trade.pnl is None:
                continue
            
            # Apply slippage
            if trade.side == 'LONG':
                # Buy at slightly higher price, sell at slightly lower
                entry_with_slippage = trade.entry_price * (1 + self.slippage_pct)
                exit_with_slippage = trade.exit_price * (1 - self.slippage_pct)
            else:
                # Short: sell at slightly lower, buy back at slightly higher
                entry_with_slippage = trade.entry_price * (1 - self.slippage_pct)
                exit_with_slippage = trade.exit_price * (1 + self.slippage_pct)
            
            # Apply commission
            entry_cost = trade.quantity * entry_with_slippage
            exit_proceeds = trade.quantity * exit_with_slippage
            commission = (entry_cost + exit_proceeds) * self.commission_pct
            
            # Recalculate P&L with costs
            if trade.side == 'LONG':
                trade.pnl = exit_proceeds - entry_cost - commission
            else:
                trade.pnl = entry_cost - exit_proceeds - commission
            
            trade.pnl_pct = (trade.pnl / entry_cost) * 100
            
            # Update entry/exit prices
            trade.entry_price = entry_with_slippage
            trade.exit_price = exit_with_slippage

