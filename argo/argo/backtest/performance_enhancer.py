#!/usr/bin/env python3
"""
Performance Enhancer
Implements improvements to increase win rate, return, and Sharpe ratio
"""
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple, TypedDict
from datetime import datetime, timedelta
import logging

from .constants import TradingConstants
from .symbol_classifier import SymbolClassifier
from .symbol_config import SymbolConfig

logger = logging.getLogger(__name__)


class IndicatorsDict(TypedDict, total=False):
    """Type definition for indicators dictionary"""
    current_price: float
    volatility: float
    volume_ratio: Optional[float]
    symbol: Optional[str]


class SignalDict(TypedDict, total=False):
    """Type definition for signal dictionary"""
    action: str
    confidence: float
    entry_price: float
    stop_price: Optional[float]
    target_price: Optional[float]
    symbol: Optional[str]


class PerformanceEnhancer:
    """
    Enhances backtest performance through:
    - Better signal quality (win rate)
    - Optimized risk/reward (returns)
    - Improved risk management (Sharpe ratio)
    """
    
    def __init__(
        self,
        min_confidence: float = 60.0,  # Slightly raised from 55.0 (more lenient)
        require_volume_confirmation: bool = False,  # Disabled by default (too strict)
        require_trend_filter: bool = False,  # Disabled by default (too strict)
        use_adaptive_stops: bool = True,
        use_trailing_stops: bool = True,
        use_position_sizing: bool = True
    ):
        """Initialize performance enhancer"""
        self.min_confidence = min_confidence
        self.require_volume_confirmation = require_volume_confirmation
        self.require_trend_filter = require_trend_filter
        self.use_adaptive_stops = use_adaptive_stops
        self.use_trailing_stops = use_trailing_stops
        self.use_position_sizing = use_position_sizing
        
    def calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = TradingConstants.ATR_PERIOD) -> pd.Series:
        """Calculate Average Directional Index (ADX) for trend strength"""
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate Directional Movement
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        # Smooth TR and DM
        atr = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        
        # Calculate DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()
        
        return adx
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = TradingConstants.ATR_PERIOD) -> pd.Series:
        """Calculate Average True Range (ATR) for volatility"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        return atr
    
    def filter_signal_by_trend(
        self,
        signal: Dict,
        indicators: Dict,
        df: pd.DataFrame,
        index: int
    ) -> Optional[Dict]:
        """Filter signal by trend strength (ADX)"""
        if not self.require_trend_filter:
            return signal
        
        try:
            # Calculate ADX
            if index < TradingConstants.MIN_DATA_POINTS_FOR_TREND:
                return signal
            
            historical_data = df.iloc[:index+1]
            adx = self.calculate_adx(
                historical_data['High'],
                historical_data['Low'],
                historical_data['Close']
            )
            
            current_adx = adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 0
            
            # Require ADX > threshold for strong trend
            if current_adx < TradingConstants.ADX_STRONG_TREND_THRESHOLD:
                logger.debug(f"Signal filtered: ADX {current_adx:.2f} < {TradingConstants.ADX_STRONG_TREND_THRESHOLD} (weak trend)")
                return None
            
            # Additional: Check 200-day MA for trend direction
            if len(historical_data) >= TradingConstants.SMA_200_PERIOD:
                sma_200 = historical_data['Close'].rolling(TradingConstants.SMA_200_PERIOD).mean().iloc[-1]
                current_price = indicators.get('current_price', historical_data['Close'].iloc[-1])
                
                action = signal.get('action')
                if action == 'BUY' and current_price < sma_200:
                    logger.debug(f"Signal filtered: BUY below {TradingConstants.SMA_200_PERIOD}-day MA (downtrend)")
                    return None
                elif action == 'SELL' and current_price > sma_200:
                    logger.debug(f"Signal filtered: SELL above {TradingConstants.SMA_200_PERIOD}-day MA (uptrend)")
                    return None
            
            return signal
        except Exception as e:
            logger.debug(f"Trend filter error: {e}, allowing signal")
            return signal
    
    def filter_signal_by_volume(
        self,
        signal: Dict,
        indicators: Dict
    ) -> Optional[Dict]:
        """Filter signal by volume confirmation"""
        if not self.require_volume_confirmation:
            return signal
        
        volume_ratio = indicators.get('volume_ratio')
        if volume_ratio is None:
            return signal  # Allow if volume data unavailable
        
        action = signal.get('action')
        # Require volume > threshold for confirmation
        if volume_ratio < TradingConstants.VOLUME_CONFIRMATION_RATIO:
            logger.debug(f"Signal filtered: volume ratio {volume_ratio:.2f} < {TradingConstants.VOLUME_CONFIRMATION_RATIO}")
            return None
        
        return signal
    
    def calculate_adaptive_stops(
        self,
        entry_price: float,
        action: str,
        indicators: Dict,
        df: pd.DataFrame,
        index: int,
        symbol: str = None
    ) -> Tuple[float, float]:
        """Calculate adaptive stop loss and take profit based on ATR with symbol-specific adjustments"""
        if not self.use_adaptive_stops or index < TradingConstants.ATR_MIN_INDEX:
            return self._get_fallback_stops(entry_price, action)
        
        try:
            atr_pct = self._calculate_atr_percentage(df, index, entry_price)
            config = SymbolConfig.get_config(symbol)
            multipliers = self._apply_volatility_adjustment(config, indicators)
            stop_loss, take_profit = self._calculate_stops_from_atr(
                entry_price, action, atr_pct, multipliers
            )
            return self._clamp_stops(entry_price, action, stop_loss, take_profit, symbol, config)
        except Exception as e:
            logger.debug(f"Adaptive stops error: {e}, using fixed stops")
            return self._get_fallback_stops(entry_price, action)
    
    def _get_fallback_stops(self, entry_price: float, action: str) -> Tuple[float, float]:
        """Get fallback stop loss and take profit when adaptive stops can't be calculated"""
        if action == 'BUY':
            return (
                entry_price * (1 - TradingConstants.FALLBACK_STOP_LOSS_PCT),
                entry_price * (1 + TradingConstants.FALLBACK_TAKE_PROFIT_PCT)
            )
        else:
            return (
                entry_price * (1 + TradingConstants.FALLBACK_STOP_LOSS_PCT),
                entry_price * (1 - TradingConstants.FALLBACK_TAKE_PROFIT_PCT)
            )
    
    def _calculate_atr_percentage(self, df: pd.DataFrame, index: int, entry_price: float) -> float:
        """Calculate ATR as a percentage of entry price"""
        historical_data = df.iloc[:index+1]
        atr = self.calculate_atr(
            historical_data['High'],
            historical_data['Low'],
            historical_data['Close']
        )
        current_atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else entry_price * TradingConstants.ATR_FALLBACK_PCT
        return (current_atr / entry_price) * 100
    
    def _apply_volatility_adjustment(self, config: Dict, indicators: Dict) -> Dict[str, float]:
        """Apply volatility-based adjustments to stop and profit multipliers"""
        stop_multiplier = config['stop_multiplier']
        profit_multiplier = config['profit_multiplier']
        
        volatility = indicators.get('volatility', TradingConstants.DEFAULT_VOLATILITY)
        
        if volatility > TradingConstants.HIGH_VOLATILITY_THRESHOLD:
            stop_multiplier *= TradingConstants.HIGH_VOLATILITY_STOP_MULTIPLIER
            profit_multiplier *= TradingConstants.HIGH_VOLATILITY_PROFIT_MULTIPLIER
        elif volatility < TradingConstants.LOW_VOLATILITY_THRESHOLD:
            stop_multiplier *= TradingConstants.LOW_VOLATILITY_STOP_MULTIPLIER
            profit_multiplier *= TradingConstants.LOW_VOLATILITY_PROFIT_MULTIPLIER
        
        return {'stop_multiplier': stop_multiplier, 'profit_multiplier': profit_multiplier}
    
    def _calculate_stops_from_atr(
        self,
        entry_price: float,
        action: str,
        atr_pct: float,
        multipliers: Dict[str, float]
    ) -> Tuple[float, float]:
        """Calculate stop loss and take profit from ATR percentage and multipliers"""
        stop_multiplier = multipliers['stop_multiplier']
        profit_multiplier = multipliers['profit_multiplier']
        
        if action == 'BUY':
            stop_loss = entry_price * (1 - (atr_pct * stop_multiplier / 100))
            take_profit = entry_price * (1 + (atr_pct * profit_multiplier / 100))
        else:  # SELL/SHORT
            stop_loss = entry_price * (1 + (atr_pct * stop_multiplier / 100))
            take_profit = entry_price * (1 - (atr_pct * profit_multiplier / 100))
        
        return stop_loss, take_profit
    
    def _clamp_stops(
        self,
        entry_price: float,
        action: str,
        stop_loss: float,
        take_profit: float,
        symbol: Optional[str],
        config: Dict
    ) -> Tuple[float, float]:
        """Clamp stop loss and take profit to reasonable ranges based on symbol configuration"""
        if action == 'BUY':
            max_stop_pct, max_profit_pct = SymbolConfig.get_stop_limits(symbol, action)
            stop_loss = max(entry_price * (1 - max_stop_pct), stop_loss)
            take_profit = min(entry_price * (1 + max_profit_pct), take_profit)
        else:  # SELL/SHORT
            max_stop_pct, min_profit_pct = SymbolConfig.get_stop_limits(symbol, action)
            stop_loss = min(entry_price * (1 + max_stop_pct), stop_loss)
            take_profit = max(entry_price * min_profit_pct, take_profit)
        
        return stop_loss, take_profit
    
    def calculate_position_size(
        self,
        base_capital: float,
        signal_confidence: float,
        volatility: float,
        symbol: str
    ) -> float:
        """Calculate optimal position size based on confidence and volatility"""
        if not self.use_position_sizing:
            return base_capital * TradingConstants.BASE_POSITION_SIZE_PCT
        
        # Confidence multiplier (0 to 1)
        confidence_multiplier = max(
            0,
            min(
                1,
                (signal_confidence - TradingConstants.CONFIDENCE_BASE) / TradingConstants.CONFIDENCE_RANGE
            )
        )
        
        # Volatility adjustment (reduce for high volatility)
        volatility_adjustment = 1.0 / (1.0 + volatility * TradingConstants.VOLATILITY_ADJUSTMENT_DIVISOR)
        
        # Symbol-specific position sizing adjustments
        config = SymbolConfig.get_config(symbol)
        volatility_adjustment *= config['position_size_adjustment']
        
        position_size_pct = (
            TradingConstants.BASE_POSITION_SIZE_PCT *
            (1 + confidence_multiplier * TradingConstants.CONFIDENCE_MULTIPLIER_MAX) *
            volatility_adjustment
        )
        position_size_pct = min(
            TradingConstants.MAX_POSITION_SIZE_PCT,
            max(TradingConstants.MIN_POSITION_SIZE_PCT, position_size_pct)
        )
        
        return base_capital * position_size_pct
    
    def update_trailing_stop(
        self,
        trade,
        current_price: float
    ) -> Optional[float]:
        """Update trailing stop loss"""
        if not self.use_trailing_stops:
            return None
        
        # Adaptive trailing stop based on symbol and volatility
        symbol = getattr(trade, 'symbol', None)
        volatility = getattr(
            trade,
            'volatility',
            TradingConstants.DEFAULT_VOLATILITY
        ) if hasattr(trade, 'volatility') else TradingConstants.DEFAULT_VOLATILITY
        
        # Get base trailing stop percentage from symbol configuration
        config = SymbolConfig.get_config(symbol)
        trailing_pct = config['trailing_stop_pct']
        
        # Adjust for volatility
        if volatility > TradingConstants.HIGH_VOLATILITY_THRESHOLD:
            trailing_pct *= TradingConstants.TRAILING_STOP_HIGH_VOL_MULTIPLIER
        elif volatility < TradingConstants.LOW_VOLATILITY_THRESHOLD:
            trailing_pct *= TradingConstants.TRAILING_STOP_LOW_VOL_MULTIPLIER
        
        if trade.side == 'LONG':
            highest_price = max(trade.entry_price, current_price)
            trailing_stop = highest_price * (1 - trailing_pct)
            
            # Update if trailing stop is higher than current stop
            if trailing_stop > trade.stop_loss:
                old_stop = trade.stop_loss
                trade.stop_loss = trailing_stop
                logger.debug(f"Trailing stop updated: ${old_stop:.2f} -> ${trailing_stop:.2f}")
                return trailing_stop
        else:  # SHORT
            lowest_price = min(trade.entry_price, current_price)
            trailing_stop = lowest_price * (1 + trailing_pct)
            
            # Update if trailing stop is lower than current stop
            if trailing_stop < trade.stop_loss:
                old_stop = trade.stop_loss
                trade.stop_loss = trailing_stop
                logger.debug(f"Trailing stop updated: ${old_stop:.2f} -> ${trailing_stop:.2f}")
                return trailing_stop
        
        return None
    
    def check_time_based_exit(
        self,
        trade,
        current_date: datetime,
        current_price: float
    ) -> bool:
        """Check if position should be exited based on time"""
        days_held = (current_date - trade.entry_date).days
        
        # Adaptive time-based exit based on symbol configuration
        symbol = getattr(trade, 'symbol', None)
        config = SymbolConfig.get_config(symbol)
        base_days = config['time_based_exit_days']
        
        if days_held > base_days:
            if trade.side == 'LONG' and current_price < trade.entry_price * TradingConstants.TIME_EXIT_PROGRESS_THRESHOLD_LONG:
                logger.info(f"Time-based exit: {days_held} days, no progress")
                return True
            elif trade.side == 'SHORT' and current_price > trade.entry_price * TradingConstants.TIME_EXIT_PROGRESS_THRESHOLD_SHORT:
                logger.info(f"Time-based exit: {days_held} days, no progress")
                return True
        
        return False
    
    def enhance_signal(
        self,
        signal: Dict,
        indicators: Dict,
        df: pd.DataFrame,
        index: int
    ) -> Optional[Dict]:
        """Apply all enhancements to signal"""
        if not signal:
            return None
        
        # Filter by volume (if enabled)
        if self.require_volume_confirmation:
            signal = self.filter_signal_by_volume(signal, indicators)
            if not signal:
                return None
        
        # Filter by trend (if enabled)
        if self.require_trend_filter:
            signal = self.filter_signal_by_trend(signal, indicators, df, index)
            if not signal:
                return None
        
        # Check confidence threshold
        confidence = signal.get('confidence', 0)
        if confidence < self.min_confidence:
            logger.debug(f"Signal filtered: confidence {confidence:.2f} < {self.min_confidence}")
            return None
        
        # Calculate adaptive stops (ALWAYS apply - this is the key improvement)
        entry_price = signal.get('entry_price', indicators.get('current_price', 0))
        action = signal.get('action')
        original_stop = signal.get('stop_price')
        original_target = signal.get('target_price')
        
        try:
            # Get symbol from signal if available
            symbol = signal.get('symbol', indicators.get('symbol', None))
            stop_loss, take_profit = self.calculate_adaptive_stops(
                entry_price, action, indicators, df, index, symbol=symbol
            )
            
            # Only update if adaptive stops are enabled and calculated successfully
            if self.use_adaptive_stops and stop_loss and take_profit:
                signal['stop_price'] = stop_loss
                signal['target_price'] = take_profit
                logger.info(f"[ENHANCEMENT] Adaptive stops calculated: entry=${entry_price:.2f}, stop=${stop_loss:.2f}, target=${take_profit:.2f}")
                if original_stop:
                    logger.info(f"[ENHANCEMENT] Stop override: ${original_stop:.2f} → ${stop_loss:.2f}")
                if original_target:
                    logger.info(f"[ENHANCEMENT] Target override: ${original_target:.2f} → ${take_profit:.2f}")
            else:
                logger.warning(f"[ENHANCEMENT] Adaptive stops NOT applied: use_adaptive_stops={self.use_adaptive_stops}, stop_loss={stop_loss}, take_profit={take_profit}")
        except Exception as e:
            logger.error(f"[ENHANCEMENT] Adaptive stops calculation failed: {e}, using original stops", exc_info=True)
            # Keep original stops if adaptive calculation fails
        
        return signal

