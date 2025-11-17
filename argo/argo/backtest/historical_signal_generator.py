#!/usr/bin/env python3
"""
Historical Signal Generator
Generates signals using historical data (for backtesting)
Uses data up to the current date in the backtest to prevent look-ahead bias
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Import tracer for advanced debugging
try:
    from argo.backtest.signal_tracer import get_tracer
    TRACER_AVAILABLE = True
except ImportError:
    TRACER_AVAILABLE = False
    def get_tracer():
        return None

class HistoricalSignalGenerator:
    """
    Generates signals using historical data for backtesting
    Prevents look-ahead bias by only using data available up to the current date
    """
    
    def __init__(self, signal_service, data_manager):
        """
        Initialize historical signal generator
        
        Args:
            signal_service: SignalGenerationService instance
            data_manager: DataManager instance for historical data
        """
        self.signal_service = signal_service
        self.data_manager = data_manager
        
    async def generate_signal_for_date(
        self,
        symbol: str,
        current_date: datetime,
        historical_df: pd.DataFrame,
        current_index: int
    ) -> Optional[Dict]:
        """
        Generate signal for a specific historical date
        
        Args:
            symbol: Trading symbol
            current_date: Current date in the backtest
            historical_df: Full historical dataframe
            current_index: Current index in the dataframe
            
        Returns:
            Signal dictionary or None
        """
        try:
            # Get data up to current date (prevent look-ahead bias)
            historical_data = historical_df.iloc[:current_index+1].copy()
            
            if len(historical_data) < 50:
                return None  # Need minimum data
            
            # Use the signal service's consensus engine with historical data
            # We'll simulate what the signal would have been at that point
            
            # Get current price from historical data
            current_price = float(historical_data.iloc[-1]['Close'])
            
            # Calculate technical indicators from historical data
            indicators = self._calculate_indicators(historical_data)
            
            # Trace indicator calculation
            if TRACER_AVAILABLE:
                tracer = get_tracer()
                if tracer:
                    tracer.trace_indicator_calculation(symbol, len(historical_data), indicators, bool(indicators))
            
            # DEBUG: Log if no indicators
            if not indicators:
                logger.debug(f"No indicators calculated for {symbol} at {current_date}, data_len={len(historical_data)}")
                return None
            
            # Generate signal based on indicators (simplified version of consensus)
            signal = self._generate_signal_from_indicators(
                symbol,
                current_price,
                indicators,
                historical_data
            )
            
            # DEBUG: Log if no signal generated
            if not signal:
                logger.debug(f"No signal generated for {symbol} at {current_date} despite having indicators: {list(indicators.keys())}")
            
            if signal:
                signal['entry_price'] = current_price
                signal['timestamp'] = current_date.isoformat()
            
            return signal
            
        except Exception as e:
            logger.debug(f"Error generating historical signal for {symbol} at {current_date}: {e}")
            return None
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators from historical data"""
        if len(df) < 20:
            logger.debug(f"Insufficient data for indicators: {len(df)} < 20")
            return {}
        
        try:
            # Ensure we have numeric data
            close = pd.to_numeric(df['Close'], errors='coerce').values
            volume = pd.to_numeric(df['Volume'], errors='coerce').values if 'Volume' in df.columns else None
            
            # Remove any NaN values
            close = close[~np.isnan(close)]
            if volume is not None:
                volume = volume[~np.isnan(volume)]
            
            if len(close) < 20:
                logger.debug(f"Insufficient valid close prices: {len(close)} < 20")
                return {}
            
            # Moving averages - ALWAYS calculate if we have enough data
            sma_20 = np.mean(close[-20:]) if len(close) >= 20 else None
            sma_50 = np.mean(close[-50:]) if len(close) >= 50 else None
            
            # RSI - calculate if we have enough data
            rsi = self._calculate_rsi(close) if len(close) >= 15 else None
            
            # MACD - calculate if we have enough data
            macd, signal_line = self._calculate_macd(close) if len(close) >= 26 else (None, None)
            
            # Volume
            avg_volume = np.mean(volume[-20:]) if volume is not None and len(volume) >= 20 else None
            current_volume = volume[-1] if volume is not None else None
            volume_ratio = current_volume / avg_volume if avg_volume and avg_volume > 0 else None
            
            # Volatility
            returns = np.diff(close) / close[:-1] if len(close) > 1 else np.array([])
            volatility = np.std(returns[-20:]) * np.sqrt(252) if len(returns) >= 20 else None
            
            indicators = {
                'sma_20': sma_20,
                'sma_50': sma_50,
                'rsi': rsi,
                'macd': macd,
                'macd_signal': signal_line,
                'volume_ratio': volume_ratio,
                'volatility': volatility,
                'current_price': close[-1]
            }
            
            # Log if we don't have key indicators
            if not sma_20 or not sma_50:
                logger.debug(f"Missing SMA indicators: sma_20={sma_20}, sma_50={sma_50}, data_len={len(df)}")
            
            return indicators
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}", exc_info=True)
            return {}
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> Optional[float]:
        """Calculate RSI (optimized with Numba if available)"""
        try:
            from argo.backtest.performance_optimizer import calculate_rsi_fast
            return float(calculate_rsi_fast(prices, period))
        except ImportError:
            # Fallback to standard calculation
            if len(prices) < period + 1:
                return None
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi)
    
    def _calculate_macd(self, prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """Calculate MACD"""
        if len(prices) < slow + signal:
            return None, None
        
        # EMA calculations
        ema_fast = self._ema(prices, fast)
        ema_slow = self._ema(prices, slow)
        
        if ema_fast is None or ema_slow is None:
            return None, None
        
        macd_line = ema_fast - ema_slow
        
        # Signal line (EMA of MACD)
        macd_values = macd_line[-signal:]
        signal_line = self._ema(macd_values, signal)
        
        macd_value = float(macd_line[-1]) if len(macd_line) > 0 else None
        signal_value = float(signal_line[-1]) if signal_line is not None and len(signal_line) > 0 else None
        return macd_value, signal_value
    
    def _ema(self, prices: np.ndarray, period: int) -> Optional[np.ndarray]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return None
        
        multiplier = 2 / (period + 1)
        ema = np.zeros_like(prices)
        ema[0] = prices[0]
        
        for i in range(1, len(prices)):
            ema[i] = (prices[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        
        return ema
    
    def _generate_signal_from_indicators(
        self,
        symbol: str,
        current_price: float,
        indicators: Dict,
        historical_df: pd.DataFrame
    ) -> Optional[Dict]:
        """Generate signal from technical indicators"""
        if not indicators:
            logger.debug("_generate_signal_from_indicators: No indicators provided")
            return None
        
        # Get consensus engine weights
        try:
            consensus_engine = self.signal_service.consensus_engine
            weights = consensus_engine.source_weights
        except:
            weights = {'massive': 0.4, 'alpha_vantage': 0.25, 'x_sentiment': 0.2, 'sonar': 0.15}
        
        # Calculate signal strength based on indicators
        signals = []
        confidences = []
        
        # Trace: Log initial state
        if TRACER_AVAILABLE:
            tracer = get_tracer()
            if tracer:
                tracer.trace('signal_generation_start', symbol, {
                    'indicators_available': list(indicators.keys()),
                    'current_price': current_price
                })
        
        # Trend signals (from moving averages) - ALWAYS GENERATE SIGNAL
        if indicators.get('sma_20') and indicators.get('sma_50'):
            # Always generate a signal based on trend direction
            if indicators['sma_20'] > indicators['sma_50']:
                signals.append('BUY')
                # Strength based on separation - more lenient
                separation = (indicators['sma_20'] - indicators['sma_50']) / indicators['sma_50']
                # Lower base confidence, accept even small separations
                base_confidence = 55.0 if separation > 0.0001 else 52.0  # Even smaller threshold
                confidences.append(base_confidence + min(30.0, separation * 2500))
            else:
                signals.append('SELL')
                separation = (indicators['sma_50'] - indicators['sma_20']) / indicators['sma_50']
                base_confidence = 55.0 if separation > 0.0001 else 52.0
                confidences.append(base_confidence + min(30.0, separation * 2500))
        
        # RSI signals - VERY LENIENT THRESHOLDS (always generate signal)
        if indicators.get('rsi'):
            rsi = indicators['rsi']
            if rsi < 50:  # Oversold - always generate BUY
                signals.append('BUY')
                confidences.append(55.0 + (50 - rsi) * 0.6)  # Lower base, higher multiplier
            else:  # Overbought or neutral - always generate SELL
                signals.append('SELL')
                confidences.append(55.0 + (rsi - 50) * 0.6)
        
        # MACD signals - ALWAYS GENERATE SIGNAL
        if indicators.get('macd') is not None and indicators.get('macd_signal') is not None:
            if indicators['macd'] > indicators['macd_signal']:
                signals.append('BUY')
                confidences.append(56.0)  # Lowered from 62.0
            else:
                signals.append('SELL')
                confidences.append(56.0)
        
        # Volume confirmation
        volume_boost = 0
        if indicators.get('volume_ratio'):
            if indicators['volume_ratio'] > 1.5:  # High volume
                volume_boost = 3.0
            elif indicators['volume_ratio'] < 0.5:  # Low volume
                volume_boost = -2.0
        
        # CRITICAL FIX: Generate fallback signal BEFORE checking if signals list is empty
        # This ensures we always generate a signal when indicators exist
        if not signals and indicators:
            # Generate fallback signal based on trend
            if indicators.get('sma_20') and indicators.get('sma_50'):
                if indicators['sma_20'] > indicators['sma_50']:
                    signals.append('BUY')
                    confidences.append(58.0)  # Lowered for more signals
                else:
                    signals.append('SELL')
                    confidences.append(58.0)
            elif indicators.get('rsi'):
                # Use RSI for fallback
                rsi = indicators['rsi']
                if rsi < 50:
                    signals.append('BUY')
                    confidences.append(56.0)  # Lowered
                else:
                    signals.append('SELL')
                    confidences.append(56.0)
        
        # Now check if we have signals (after fallback generation)
        if not signals:
            logger.debug(f"_generate_signal_from_indicators: No signals generated despite indicators: {list(indicators.keys())}")
            return None  # No indicators or signals possible
        
        # Weighted consensus
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count:
            action = 'BUY'
            direction = 'LONG'
            avg_confidence = np.mean([c for s, c in zip(signals, confidences) if s == 'BUY'])
        elif sell_count > buy_count:
            action = 'SELL'
            direction = 'SHORT'
            avg_confidence = np.mean([c for s, c in zip(signals, confidences) if s == 'SELL'])
        else:
            # Tie - use strongest signal
            max_idx = np.argmax(confidences)
            action = signals[max_idx]
            direction = 'LONG' if action == 'BUY' else 'SHORT'
            avg_confidence = confidences[max_idx]
        
        # Apply volume boost
        avg_confidence += volume_boost
        # LOWERED MINIMUM CONFIDENCE for more signals (was 55.0, now 50.0)
        avg_confidence = min(95.0, max(50.0, avg_confidence))
        
        # Trace signal generation result
        if TRACER_AVAILABLE:
            tracer = get_tracer()
            if tracer:
                tracer.trace_signal_generation(
                    symbol,
                    indicators,
                    signals,
                    confidences,
                    {
                        'action': action,
                        'direction': direction,
                        'confidence': avg_confidence
                    } if signals else None,
                    55.0  # min_confidence threshold
                )
        
        # Get trading config
        try:
            trading_config = self.signal_service.trading_config
            profit_target = trading_config.get('profit_target', 0.05)
            stop_loss = trading_config.get('stop_loss', 0.03)
        except:
            profit_target = 0.05
            stop_loss = 0.03
        
        return {
            'action': action,
            'direction': direction,
            'confidence': float(avg_confidence),
            'target_price': current_price * (1 + profit_target) if action == 'BUY' else current_price * (1 - profit_target),
            'stop_price': current_price * (1 - stop_loss) if action == 'BUY' else current_price * (1 + stop_loss),
            'indicators': indicators
        }

