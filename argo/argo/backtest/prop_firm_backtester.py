#!/usr/bin/env python3
"""
Prop Firm Backtester
Specialized backtester for prop firm trading accounts
Enforces prop firm constraints: 2.0% max drawdown, 4.5% daily loss limit
"""
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from argo.backtest.strategy_backtester import StrategyBacktester
from argo.backtest.base_backtester import BacktestMetrics, Trade
from argo.backtest.constants import TransactionCostConstants, BacktestConstants, TradingConstants

logger = logging.getLogger(__name__)


class PropFirmBacktester(StrategyBacktester):
    """
    Prop firm-specific backtester
    Enforces strict risk limits: 2.0% max drawdown, 4.5% daily loss limit
    Conservative position sizing: 5-10% (vs 10-20% standard)
    Higher confidence threshold: 80%+ (vs 60-75% standard)
    """
    
    def __init__(
        self,
        initial_capital: float = 25000.0,  # Typical prop firm account
        max_drawdown_pct: float = 2.0,  # Conservative: 2.0% vs 2.5% limit
        daily_loss_limit_pct: float = 4.5,  # Conservative: 4.5% vs 5.0% limit
        max_position_size_pct: float = 10.0,  # Conservative: 10% vs 20% standard
        min_confidence: float = 80.0,  # Higher threshold: 80%+ vs 60-75%
        max_positions: int = 5,  # Limit concurrent positions
        slippage_pct: float = TransactionCostConstants.DEFAULT_SLIPPAGE_PCT,
        spread_pct: float = TransactionCostConstants.DEFAULT_SPREAD_PCT,
        commission_pct: float = TransactionCostConstants.DEFAULT_COMMISSION_PCT,
        use_cost_modeling: bool = True,
        use_enhanced_cost_model: bool = True
    ):
        # Initialize parent with prop firm capital
        super().__init__(
            initial_capital=initial_capital,
            slippage_pct=slippage_pct,
            spread_pct=spread_pct,
            commission_pct=commission_pct,
            use_cost_modeling=use_cost_modeling,
            use_enhanced_cost_model=use_enhanced_cost_model,
            min_holding_bars=5
        )
        
        # Prop firm-specific constraints
        self.max_drawdown_pct = max_drawdown_pct
        self.daily_loss_limit_pct = daily_loss_limit_pct
        self.max_position_size_pct = max_position_size_pct
        self.min_confidence = min_confidence
        self.max_positions = max_positions
        
        # Daily P&L tracking
        self.daily_pnl: Dict[str, float] = {}  # Date -> P&L
        self.daily_start_equity: Dict[str, float] = {}  # Date -> Starting equity
        self.last_trading_date: Optional[datetime] = None
        
        # Breach tracking
        self.drawdown_breaches: List[Dict] = []
        self.daily_loss_breaches: List[Dict] = []
        self.trading_halted: bool = False
        self.halt_reason: Optional[str] = None
        
        # Override portfolio limits
        self.max_portfolio_drawdown = max_drawdown_pct / 100.0  # Convert to decimal
        self.max_positions = max_positions
        
        logger.info(f"✅ PropFirmBacktester initialized:")
        logger.info(f"   Max Drawdown: {max_drawdown_pct}%")
        logger.info(f"   Daily Loss Limit: {daily_loss_limit_pct}%")
        logger.info(f"   Max Position Size: {max_position_size_pct}%")
        logger.info(f"   Min Confidence: {min_confidence}%")
        logger.info(f"   Max Positions: {max_positions}")
        logger.info(f"   Initial Capital: ${initial_capital:,.2f}")
    
    def _get_trading_date(self, date: datetime) -> str:
        """Get trading date string (YYYY-MM-DD)"""
        if isinstance(date, pd.Timestamp):
            return date.date().isoformat()
        elif hasattr(date, 'date'):
            return date.date().isoformat()
        else:
            return str(date)[:10]  # Extract YYYY-MM-DD
    
    def _reset_daily_tracking(self, date: datetime):
        """Reset daily tracking for new trading day"""
        trading_date = self._get_trading_date(date)
        
        if self.last_trading_date != trading_date:
            # New trading day
            current_equity = self.equity_curve[-1] if self.equity_curve else self.initial_capital
            self.daily_start_equity[trading_date] = current_equity
            self.daily_pnl[trading_date] = 0.0
            self.last_trading_date = trading_date
            
            # Reset trading halt if new day (prop firms may reset daily)
            if self.trading_halted:
                logger.info(f"📅 New trading day {trading_date}: Resetting trading halt")
                self.trading_halted = False
                self.halt_reason = None
    
    def _update_daily_pnl(self, date: datetime):
        """Update daily P&L tracking"""
        trading_date = self._get_trading_date(date)
        current_equity = self.equity_curve[-1] if self.equity_curve else self.initial_capital
        
        if trading_date in self.daily_start_equity:
            start_equity = self.daily_start_equity[trading_date]
            daily_pnl = current_equity - start_equity
            daily_pnl_pct = (daily_pnl / start_equity) * 100 if start_equity > 0 else 0.0
            
            self.daily_pnl[trading_date] = daily_pnl
            
            # Check daily loss limit
            if daily_pnl_pct <= -self.daily_loss_limit_pct:
                if not self.trading_halted:
                    self.trading_halted = True
                    self.halt_reason = f"Daily loss limit breached: {daily_pnl_pct:.2f}% <= -{self.daily_loss_limit_pct}%"
                    self.daily_loss_breaches.append({
                        'date': trading_date,
                        'daily_pnl_pct': daily_pnl_pct,
                        'limit': -self.daily_loss_limit_pct
                    })
                    logger.critical(f"🚨 DAILY LOSS LIMIT BREACH: {self.halt_reason}")
    
    def _check_drawdown(self) -> tuple[bool, float]:
        """Check current drawdown against limit"""
        if not self.equity_curve:
            return True, 0.0
        
        current_equity = self.equity_curve[-1]
        
        # Update peak equity
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
        
        # Calculate drawdown
        if self.peak_equity > 0:
            drawdown_pct = ((self.peak_equity - current_equity) / self.peak_equity) * 100
        else:
            drawdown_pct = 0.0
        
        # Check limit
        if drawdown_pct >= self.max_drawdown_pct:
            if not self.trading_halted:
                self.trading_halted = True
                self.halt_reason = f"Max drawdown breached: {drawdown_pct:.2f}% >= {self.max_drawdown_pct}%"
                self.drawdown_breaches.append({
                    'date': self.last_trading_date,
                    'drawdown_pct': drawdown_pct,
                    'limit': self.max_drawdown_pct,
                    'peak_equity': self.peak_equity,
                    'current_equity': current_equity
                })
                logger.critical(f"🚨 MAX DRAWDOWN BREACH: {self.halt_reason}")
            return False, drawdown_pct
        
        return True, drawdown_pct
    
    def _check_portfolio_risk_limits(self) -> tuple[bool, str]:
        """Check portfolio-level risk limits (prop firm specific)"""
        # Check if trading is halted
        if self.trading_halted:
            return False, f"Trading halted: {self.halt_reason}"
        
        # Check maximum positions
        if len(self.positions) >= self.max_positions:
            return False, f"Maximum positions reached ({self.max_positions})"
        
        # Check drawdown
        can_trade, drawdown_pct = self._check_drawdown()
        if not can_trade:
            return False, f"Max drawdown limit reached ({drawdown_pct:.2f}% >= {self.max_drawdown_pct}%)"
        
        return True, ""
    
    def _get_drawdown_adjustment(self) -> float:
        """Get position size adjustment based on current drawdown (prop firm specific)"""
        can_trade, drawdown_pct = self._check_drawdown()
        
        if not can_trade or drawdown_pct <= 0:
            return 1.0
        
        # Reduce position size as drawdown increases
        # At 0% drawdown: 1.0x
        # At 1.0% drawdown: 0.75x
        # At 2.0% drawdown: 0.5x (at limit)
        max_drawdown_decimal = self.max_drawdown_pct / 100.0
        if drawdown_pct / 100.0 > max_drawdown_decimal * 0.5:  # If > 50% of limit
            adjustment = max(0.5, 1.0 - (drawdown_pct / self.max_drawdown_pct) * 0.5)
            return adjustment
        
        return 1.0
    
    async def run_backtest(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_confidence: Optional[float] = None
    ) -> Optional[BacktestMetrics]:
        """
        Run prop firm backtest with strict constraints
        
        Args:
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            min_confidence: Minimum confidence (default: self.min_confidence = 80%)
        
        Returns:
            BacktestMetrics with prop firm-specific metrics
        """
        # Use prop firm minimum confidence if not specified
        if min_confidence is None:
            min_confidence = self.min_confidence
        
        logger.info(f"🚀 Starting prop firm backtest for {symbol}")
        logger.info(f"   Confidence threshold: {min_confidence}%")
        logger.info(f"   Date range: {start_date} to {end_date}")
        
        # Reset state
        self.reset()
        self.peak_equity = self.initial_capital
        self.daily_pnl.clear()
        self.daily_start_equity.clear()
        self.drawdown_breaches.clear()
        self.daily_loss_breaches.clear()
        self.trading_halted = False
        self.halt_reason = None
        self.last_trading_date = None
        
        # Run parent backtest
        metrics = await super().run_backtest(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            min_confidence=min_confidence
        )
        
        if metrics is None:
            return None
        
        # Add prop firm-specific metrics
        prop_firm_metrics = self._calculate_prop_firm_metrics(metrics)
        
        return prop_firm_metrics
    
    def _calculate_prop_firm_metrics(self, base_metrics: BacktestMetrics) -> BacktestMetrics:
        """Calculate prop firm-specific metrics"""
        # Calculate final drawdown
        final_drawdown_pct = 0.0
        if self.peak_equity > 0 and self.equity_curve:
            final_equity = self.equity_curve[-1]
            final_drawdown_pct = ((self.peak_equity - final_equity) / self.peak_equity) * 100
        
        # Calculate daily P&L statistics
        daily_returns = []
        profitable_days = 0
        losing_days = 0
        
        for date, pnl in self.daily_pnl.items():
            if date in self.daily_start_equity:
                start_equity = self.daily_start_equity[date]
                if start_equity > 0:
                    daily_return_pct = (pnl / start_equity) * 100
                    daily_returns.append(daily_return_pct)
                    if daily_return_pct > 0:
                        profitable_days += 1
                    elif daily_return_pct < 0:
                        losing_days += 1
        
        avg_daily_return = np.mean(daily_returns) if daily_returns else 0.0
        daily_win_rate = (profitable_days / len(daily_returns) * 100) if daily_returns else 0.0
        
        # Log prop firm metrics
        logger.info(f"📊 Prop Firm Metrics:")
        logger.info(f"   Final Drawdown: {final_drawdown_pct:.2f}% (limit: {self.max_drawdown_pct}%)")
        logger.info(f"   Drawdown Breaches: {len(self.drawdown_breaches)}")
        logger.info(f"   Daily Loss Breaches: {len(self.daily_loss_breaches)}")
        logger.info(f"   Trading Halted: {self.trading_halted}")
        logger.info(f"   Daily Win Rate: {daily_win_rate:.2f}%")
        logger.info(f"   Avg Daily Return: {avg_daily_return:.2f}%")
        
        # Return base metrics (drawdown already calculated)
        # Note: base_metrics.max_drawdown_pct is already calculated by parent
        return base_metrics
    
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
        """Enter position with prop firm constraints"""
        # Reset daily tracking if new day
        self._reset_daily_tracking(date)
        
        # Check if trading is halted
        if self.trading_halted:
            logger.warning(f"[{symbol}] Cannot enter position: Trading halted - {self.halt_reason}")
            return
        
        # Check portfolio risk limits
        can_trade, reason = self._check_portfolio_risk_limits()
        if not can_trade:
            logger.warning(f"[{symbol}] Cannot enter position: {reason}")
            return
        
        # Override position size to use prop firm limit
        # Calculate base position size
        try:
            if hasattr(self, '_performance_enhancer') and self._performance_enhancer:
                volatility = signal.get('volatility', 0.2)
                drawdown_adjustment = self._get_drawdown_adjustment()
                base_position_value = self._performance_enhancer.calculate_position_size(
                    self.capital,
                    signal.get('confidence', self.min_confidence),
                    volatility,
                    symbol
                )
                position_value = base_position_value * drawdown_adjustment
            else:
                position_value = self.capital * (self.max_position_size_pct / 100.0)
        except:
            position_value = self.capital * (self.max_position_size_pct / 100.0)
        
        # Apply prop firm position size limit
        max_position_value = self.capital * (self.max_position_size_pct / 100.0)
        position_value = min(position_value, max_position_value)
        
        # Call parent to enter position
        # Temporarily override max_position_size_pct
        original_max_size = TradingConstants.MAX_POSITION_SIZE_PCT
        TradingConstants.MAX_POSITION_SIZE_PCT = self.max_position_size_pct
        
        try:
            super()._enter_position(symbol, price, date, signal, side, entry_bar, df)
        finally:
            TradingConstants.MAX_POSITION_SIZE_PCT = original_max_size
    
    def update_equity(self, current_price: float, date: datetime):
        """Update equity curve and check prop firm constraints"""
        # Reset daily tracking if new day (before updating equity)
        self._reset_daily_tracking(date)
        
        # Update equity (parent method)
        super().update_equity(current_price, date)
        
        # Update daily P&L (after equity update)
        self._update_daily_pnl(date)
        
        # Check drawdown
        self._check_drawdown()
    
    def get_prop_firm_report(self) -> Dict:
        """Generate prop firm-specific report"""
        final_equity = self.equity_curve[-1] if self.equity_curve else self.initial_capital
        final_drawdown_pct = 0.0
        if self.peak_equity > 0:
            final_drawdown_pct = ((self.peak_equity - final_equity) / self.peak_equity) * 100
        
        # Calculate daily statistics
        daily_returns = []
        for date, pnl in self.daily_pnl.items():
            if date in self.daily_start_equity:
                start_equity = self.daily_start_equity[date]
                if start_equity > 0:
                    daily_returns.append((pnl / start_equity) * 100)
        
        return {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return_pct': ((final_equity - self.initial_capital) / self.initial_capital) * 100,
            'peak_equity': self.peak_equity,
            'final_drawdown_pct': final_drawdown_pct,
            'max_drawdown_limit': self.max_drawdown_pct,
            'drawdown_compliant': final_drawdown_pct < self.max_drawdown_pct,
            'drawdown_breaches': len(self.drawdown_breaches),
            'daily_loss_breaches': len(self.daily_loss_breaches),
            'trading_halted': self.trading_halted,
            'halt_reason': self.halt_reason,
            'total_trading_days': len(self.daily_pnl),
            'profitable_days': sum(1 for pnl in self.daily_pnl.values() if pnl > 0),
            'losing_days': sum(1 for pnl in self.daily_pnl.values() if pnl < 0),
            'avg_daily_return_pct': np.mean(daily_returns) if daily_returns else 0.0,
            'max_daily_loss_pct': min(daily_returns) if daily_returns else 0.0,
            'daily_loss_limit': -self.daily_loss_limit_pct,
            'daily_loss_compliant': min(daily_returns) > -self.daily_loss_limit_pct if daily_returns else True,
            'total_trades': len(self.trades),
            'max_positions': self.max_positions,
            'max_position_size_pct': self.max_position_size_pct,
            'min_confidence': self.min_confidence
        }

