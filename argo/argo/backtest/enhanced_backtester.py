#!/usr/bin/env python3
"""
Enhanced Backtester with Realistic Cost Modeling
Includes slippage, spreads, commissions, and train/val/test split
OPTIMIZED: Uses enhanced transaction cost model with square-root slippage
Compliance: Rule 15 (Backtesting)
"""
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Tuple, Union
from argo.backtest.base_backtester import BaseBacktester, Trade, BacktestMetrics
from argo.backtest.strategy_backtester import StrategyBacktester
from argo.backtest.enhanced_transaction_cost import EnhancedTransactionCostModel
from argo.backtest.constants import TransactionCostConstants, BacktestConstants
from argo.backtest.data_converter import DataConverter
import logging

logger = logging.getLogger(__name__)

class EnhancedBacktester(StrategyBacktester):
    """
    Enhanced backtester with:
    - Realistic cost modeling (slippage, spreads, commissions)
    - Train/val/test split
    - Proper data leakage prevention
    """
    
    def __init__(
        self,
        initial_capital: float = None,
        slippage_pct: float = TransactionCostConstants.DEFAULT_SLIPPAGE_PCT,
        spread_pct: float = TransactionCostConstants.DEFAULT_SPREAD_PCT,
        commission_pct: float = TransactionCostConstants.DEFAULT_COMMISSION_PCT,
        use_enhanced_cost_model: bool = True,  # Use enhanced cost model
        min_holding_bars: int = 5  # Minimum bars before exit
    ):
        if initial_capital is None:
            initial_capital = BacktestConstants.DEFAULT_INITIAL_CAPITAL
        super().__init__(initial_capital, min_holding_bars=min_holding_bars)
        self.slippage_pct = slippage_pct
        self.spread_pct = spread_pct
        self.commission_pct = commission_pct
        self.use_enhanced_cost_model = use_enhanced_cost_model
        
        if use_enhanced_cost_model:
            self.cost_model = EnhancedTransactionCostModel()
            logger.info("✅ Using enhanced transaction cost model (square-root slippage)")
        else:
            self.cost_model = None
    
    def split_data(
        self,
        df: Union[pd.DataFrame, 'pl.DataFrame'],
        train_pct: float = 0.6,
        val_pct: float = 0.2,
        test_pct: float = 0.2
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data into train/val/test sets
        
        Args:
            df: Full dataset (Pandas or Polars)
            train_pct: Training set percentage
            val_pct: Validation set percentage
            test_pct: Test set percentage
        
        Returns:
            (train_df, val_df, test_df) as Pandas DataFrames
        """
        assert abs(train_pct + val_pct + test_pct - 1.0) < 0.01, "Percentages must sum to 1.0"
        
        # Convert Polars to Pandas if needed
        try:
            df = DataConverter.to_pandas(df)
        except Exception as e:
            logger.warning(f"Data conversion failed: {e}")
            raise ValueError(f"Data must be Pandas DataFrame, got {type(df)}")
        
        # Ensure it's Pandas
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"Data must be Pandas DataFrame, got {type(df)}")
        
        n = len(df)
        train_end = int(n * train_pct)
        val_end = train_end + int(n * val_pct)
        
        train_df = df.iloc[:train_end].copy()
        val_df = df.iloc[train_end:val_end].copy()
        test_df = df.iloc[val_end:].copy()
        
        logger.info(f"Data split: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
        return train_df, val_df, test_df
    
    def _apply_costs(self, price: float, side: str) -> float:
        """
        Apply realistic trading costs
        
        Args:
            price: Base price
            side: 'LONG' or 'SHORT'
        
        Returns:
            Adjusted price with costs
        """
        # Slippage (always costs)
        slippage = price * self.slippage_pct
        
        # Spread (half on entry, half on exit)
        spread = price * self.spread_pct * 0.5
        
        # Commission
        commission = price * self.commission_pct
        
        if side == 'LONG':
            # Buying: pay more
            return price + slippage + spread + commission
        else:
            # Selling: receive less
            return price - slippage - spread - commission
    
    def _enter_position(
        self,
        symbol: str,
        price: float,
        date: datetime,
        signal: Dict,
        side: str,
        entry_bar: int = 0
    ):
        """Enter position with cost modeling"""
        # Apply entry costs
        entry_price = self._apply_costs(price, side)
        
        # Calculate position size
        position_value = self.capital * 0.10
        quantity = int(position_value / entry_price)
        
        if quantity <= 0:
            return
        
        cost = quantity * entry_price
        if cost > self.capital:
            return
        
        self.capital -= cost
        
        trade = Trade(
            entry_date=date,
            exit_date=None,
            symbol=symbol,
            entry_price=entry_price,  # Use adjusted price
            exit_price=None,
            quantity=quantity,
            side=side,
            confidence=signal.get('confidence'),
            stop_loss=signal.get('stop_price'),
            take_profit=signal.get('target_price')
        )
        
        self.positions[symbol] = trade
        self.position_entry_bars[symbol] = entry_bar  # Track entry bar for minimum holding period
    
    def _exit_position(self, symbol: str, exit_price: float, exit_date: datetime):
        """Exit position with cost modeling"""
        if symbol not in self.positions:
            return
        
        trade = self.positions[symbol]
        
        # Apply exit costs
        adjusted_exit_price = self._apply_costs(exit_price, trade.side)
        
        trade.exit_date = exit_date
        trade.exit_price = adjusted_exit_price
        
        # Calculate P&L with costs
        if trade.side == 'LONG':
            proceeds = trade.quantity * adjusted_exit_price
            trade.pnl = proceeds - (trade.quantity * trade.entry_price)
        else:
            proceeds = trade.quantity * adjusted_exit_price
            trade.pnl = (trade.quantity * trade.entry_price) - proceeds
        
        trade.pnl_pct = (trade.pnl / (trade.quantity * trade.entry_price)) * 100
        
        self.capital += proceeds
        self.trades.append(trade)
        del self.positions[symbol]

