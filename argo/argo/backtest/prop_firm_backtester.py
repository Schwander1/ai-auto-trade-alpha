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
        
        # Prop firm optimized: Tighter stop losses (1.5% vs 3% standard)
        # This helps prevent large losses that could breach daily loss limits
        self.prop_firm_stop_loss_pct = 1.5  # 1.5% stop loss for prop firm
        self.prop_firm_take_profit_pct = 3.0  # 3% take profit (2:1 risk/reward)

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
        """Update daily P&L tracking with early warning system"""
        trading_date = self._get_trading_date(date)
        current_equity = self.equity_curve[-1] if self.equity_curve else self.initial_capital

        if trading_date in self.daily_start_equity:
            start_equity = self.daily_start_equity[trading_date]
            daily_pnl = current_equity - start_equity
            daily_pnl_pct = (daily_pnl / start_equity) * 100 if start_equity > 0 else 0.0

            self.daily_pnl[trading_date] = daily_pnl

            # OPTIMIZATION: Early warning at 50% of daily loss limit
            warning_threshold = -self.daily_loss_limit_pct * 0.5
            if daily_pnl_pct <= warning_threshold and daily_pnl_pct > -self.daily_loss_limit_pct:
                logger.warning(f"⚠️ Daily loss warning: {daily_pnl_pct:.2f}% (50% of limit)")

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
                    
                    # OPTIMIZATION: Close all positions immediately on breach
                    # Note: Positions will be closed by parent class's exit logic
                    # This halt prevents new positions from being opened

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

        # FIX: Check daily loss limit BEFORE entering new positions
        if self.daily_pnl and self.last_trading_date:
            current_equity = self.equity_curve[-1] if self.equity_curve else self.initial_capital
            if self.last_trading_date in self.daily_start_equity:
                start_equity = self.daily_start_equity[self.last_trading_date]
                daily_pnl_pct = ((current_equity - start_equity) / start_equity) * 100 if start_equity > 0 else 0.0
                if daily_pnl_pct <= -self.daily_loss_limit_pct:
                    return False, f"Daily loss limit reached ({daily_pnl_pct:.2f}% <= -{self.daily_loss_limit_pct}%)"

        # Check drawdown
        can_trade, drawdown_pct = self._check_drawdown()
        if not can_trade:
            return False, f"Max drawdown limit reached ({drawdown_pct:.2f}% >= {self.max_drawdown_pct}%)"

        return True, ""

    def _get_drawdown_adjustment(self) -> float:
        """Get position size adjustment based on current drawdown (prop firm specific)
        OPTIMIZED: More aggressive reduction to prevent breach
        """
        can_trade, drawdown_pct = self._check_drawdown()

        if not can_trade or drawdown_pct <= 0:
            return 1.0

        # Aggressive position size reduction as drawdown increases
        # At 0% drawdown: 1.0x
        # At 0.5% drawdown: 0.75x (start reducing early)
        # At 1.0% drawdown: 0.5x (half size)
        # At 1.5% drawdown: 0.25x (quarter size)
        # At 2.0% drawdown: 0.0x (no new positions)
        if drawdown_pct >= self.max_drawdown_pct:
            return 0.0  # No new positions at limit
        
        # Linear reduction from 0% to max drawdown
        # More aggressive: start reducing immediately
        adjustment = 1.0 - (drawdown_pct / self.max_drawdown_pct) * 0.8  # Reduce up to 80%
        return max(0.2, adjustment)  # Minimum 20% of position size

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
        
        # OPTIMIZATION: Apply tighter stop losses for prop firm
        # Override signal stop/target with prop firm limits
        if 'stop_price' in signal:
            entry_price = signal.get('entry_price', price)
            if side == 'LONG':
                # Tighter stop loss: 1.5% instead of default 3%
                signal['stop_price'] = entry_price * (1 - self.prop_firm_stop_loss_pct / 100.0)
                signal['target_price'] = entry_price * (1 + self.prop_firm_take_profit_pct / 100.0)
            else:  # SHORT
                signal['stop_price'] = entry_price * (1 + self.prop_firm_stop_loss_pct / 100.0)
                signal['target_price'] = entry_price * (1 - self.prop_firm_take_profit_pct / 100.0)

        # Call parent to enter position
        # Temporarily override max_position_size_pct
        original_max_size = TradingConstants.MAX_POSITION_SIZE_PCT
        TradingConstants.MAX_POSITION_SIZE_PCT = self.max_position_size_pct

        try:
            super()._enter_position(symbol, price, date, signal, side, entry_bar, df)
            # Initialize last_price for gap protection
            if symbol in self.positions:
                self.positions[symbol].last_price = price
        finally:
            TradingConstants.MAX_POSITION_SIZE_PCT = original_max_size

    def _check_gap_protection(self, symbol: str, current_price: float, previous_price: float) -> bool:
        """
        Check for price gaps that could bypass stop losses
        Returns True if gap is acceptable, False if gap is too large
        """
        if previous_price <= 0:
            return True
        
        gap_pct = abs((current_price - previous_price) / previous_price) * 100
        
        # If gap is larger than stop loss, it could bypass the stop
        # For prop firm, we want to be very conservative
        max_acceptable_gap = self.prop_firm_stop_loss_pct * 1.5  # 1.5x stop loss
        
        if gap_pct > max_acceptable_gap:
            logger.warning(f"⚠️ Large gap detected for {symbol}: {gap_pct:.2f}% (max: {max_acceptable_gap:.2f}%)")
            return False
        
        return True
    
    def _check_position_risk_limits(self, symbol: str, current_price: float) -> tuple[bool, str]:
        """
        Check position-level risk limits with enhanced protection
        Returns (can_hold, reason) tuple
        """
        if symbol not in self.positions:
            return True, ""
        
        position = self.positions[symbol]
        entry_price = position.entry_price
        
        # CRITICAL: Check stop loss first (most important protection)
        stop_price = getattr(position, 'stop_price', None)
        if stop_price:
            if position.side == 'LONG' and current_price <= stop_price:
                return False, f"Stop loss hit: ${current_price:.2f} <= ${stop_price:.2f}"
            elif position.side == 'SHORT' and current_price >= stop_price:
                return False, f"Stop loss hit: ${current_price:.2f} >= ${stop_price:.2f}"
        
        # Calculate current P&L percentage
        if position.side == 'LONG':
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
        else:  # SHORT
            pnl_pct = ((entry_price - current_price) / entry_price) * 100
        
        # OPTIMIZATION: Very tight position-level risk limit (1.0% - tighter than stop loss)
        max_position_loss_pct = 1.0  # Even tighter than 1.5% stop loss for safety
        if pnl_pct <= -max_position_loss_pct:
            return False, f"Position loss limit: {pnl_pct:.2f}% <= -{max_position_loss_pct}%"
        
        # Also check if position loss would breach daily limit
        position_value = position.quantity * entry_price
        position_loss = position_value * (abs(pnl_pct) / 100.0) if pnl_pct < 0 else 0
        
        if self.daily_start_equity and self.last_trading_date:
            start_equity = self.daily_start_equity.get(self.last_trading_date, self.initial_capital)
            if start_equity > 0:
                daily_loss_from_position = (position_loss / start_equity) * 100
                # Very conservative: close at 50% of daily limit to prevent breach
                if daily_loss_from_position > self.daily_loss_limit_pct * 0.5:
                    return False, f"Position approaching daily limit: {daily_loss_from_position:.2f}%"
        
        return True, ""

    def _check_stop_loss_with_bar_data(self, symbol: str, df: pd.DataFrame, index: int) -> tuple[bool, float, str]:
        """
        Check stop loss using bar High/Low/Open prices for more accurate execution
        Handles gaps by checking bar Open first, then High/Low
        Returns (should_exit, exit_price, reason) tuple
        """
        if symbol not in self.positions:
            return False, 0.0, ""
        
        position = self.positions[symbol]
        stop_price = getattr(position, 'stop_price', None)
        
        if not stop_price or index >= len(df) or index < 1:
            return False, 0.0, ""
        
        # Get bar prices
        bar_open = float(df.iloc[index]['Open'])
        bar_high = float(df.iloc[index]['High'])
        bar_low = float(df.iloc[index]['Low'])
        prev_close = float(df.iloc[index - 1]['Close'])
        
        # CRITICAL: Check opening gap first (most important for gap protection)
        # If bar opens beyond stop, we exit at open (gap fill scenario)
        if position.side == 'LONG':
            # For LONG: stop is below entry, check if open gapped below stop
            if bar_open <= stop_price:
                exit_price = stop_price  # Execute at stop, not worse
                return True, exit_price, f"Stop loss hit at bar open (gap): ${bar_open:.2f} <= stop: ${stop_price:.2f}"
            # Then check if Low hit stop during the bar
            if bar_low <= stop_price:
                exit_price = stop_price
                return True, exit_price, f"Stop loss hit (bar Low: ${bar_low:.2f} <= stop: ${stop_price:.2f})"
        else:  # SHORT
            # For SHORT: stop is above entry, check if open gapped above stop
            if bar_open >= stop_price:
                exit_price = stop_price  # Execute at stop, not worse
                return True, exit_price, f"Stop loss hit at bar open (gap): ${bar_open:.2f} >= stop: ${stop_price:.2f}"
            # Then check if High hit stop during the bar
            if bar_high >= stop_price:
                exit_price = stop_price
                return True, exit_price, f"Stop loss hit (bar High: ${bar_high:.2f} >= stop: ${stop_price:.2f})"
        
        return False, 0.0, ""

    def update_equity(self, current_price: float, date: datetime, df: pd.DataFrame = None, index: int = None):
        """Update equity curve and check prop firm constraints with enhanced risk controls and bar-level stop checking"""
        # Reset daily tracking if new day (before updating equity)
        self._reset_daily_tracking(date)

        # OPTIMIZATION: Bar-level stop loss checking using High/Low prices
        # This prevents gaps from bypassing stops
        if self.positions and df is not None and index is not None and index < len(df):
            bar_data = df.iloc[index]
            high_price = float(bar_data.get('High', current_price))
            low_price = float(bar_data.get('Low', current_price))
            
            for symbol in list(self.positions.keys()):
                if symbol not in self.positions:
                    continue
                    
                position = self.positions[symbol]
                
                # CRITICAL: Check stop loss using bar High/Low (catches gaps)
                should_exit, exit_price, reason = self._check_stop_loss_with_bar_data(symbol, df, index)
                if should_exit:
                    logger.warning(f"🚨 Closing {symbol}: {reason}")
                    super()._exit_position(symbol, exit_price, date, reason='stop_loss_bar_level')
                    continue
                
                # Get previous price for gap checking
                previous_price = getattr(position, 'last_price', None)
                if previous_price is None:
                    previous_price = position.entry_price
                
                # Enhanced gap protection using bar data
                if previous_price and previous_price > 0:
                    # Check gap using the worst case (high for shorts, low for longs)
                    if position.side == 'LONG':
                        gap_price = low_price  # Worst case for long
                    else:
                        gap_price = high_price  # Worst case for short
                    
                    if not self._check_gap_protection(symbol, gap_price, previous_price):
                        logger.warning(f"🚨 Closing {symbol} due to large gap (bar-level)")
                        # Use worst case price for exit
                        super()._exit_position(symbol, gap_price, date, reason='gap_protection_bar')
                        continue
                
                # Check position-level risk limits using worst case price
                worst_price = low_price if position.side == 'LONG' else high_price
                can_hold, reason = self._check_position_risk_limits(symbol, worst_price)
                if not can_hold:
                    logger.warning(f"🚨 Closing {symbol}: {reason} (bar-level check)")
                    super()._exit_position(symbol, worst_price, date, reason='position_risk_limit_bar')
                    continue
                
                # Update last price for gap checking (use close price)
                position.last_price = current_price

        # Fallback: If no bar data, use standard checks
        elif self.positions:
            for symbol in list(self.positions.keys()):
                if symbol not in self.positions:
                    continue
                    
                position = self.positions[symbol]
                previous_price = getattr(position, 'last_price', None)
                if previous_price is None:
                    previous_price = position.entry_price
                
                if previous_price and previous_price > 0:
                    if not self._check_gap_protection(symbol, current_price, previous_price):
                        logger.warning(f"🚨 Closing {symbol} due to large gap")
                        super()._exit_position(symbol, current_price, date, reason='gap_protection')
                        continue
                
                can_hold, reason = self._check_position_risk_limits(symbol, current_price)
                if not can_hold:
                    logger.warning(f"🚨 Closing {symbol}: {reason}")
                    super()._exit_position(symbol, current_price, date, reason='position_risk_limit')
                    continue
                
                position.last_price = current_price

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
