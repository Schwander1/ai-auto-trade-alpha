#!/usr/bin/env python3
"""yfinance Data Source - Technical Indicators (supplements Alpha Vantage)"""
import logging
import pandas as pd
import numpy as np
from typing import Optional, Dict, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("YFinance")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("⚠️  yfinance not available - install yfinance")

class YFinanceDataSource:
    """
    yfinance integration for technical indicators
    Free, high-quality data source
    Supplements Alpha Vantage with additional indicators
    """
    
    def __init__(self):
        self.enabled = YFINANCE_AVAILABLE
        if not self.enabled:
            logger.warning("⚠️  yfinance not available")
        else:
            logger.info("✅ yfinance data source initialized")
    
    def fetch_technical_indicators(self, symbol: str) -> Optional[Dict]:
        """Fetch technical indicators using yfinance (synchronous - wrapped in async)"""
        if not self.enabled:
            return None
        
        try:
            hist = self._get_historical_data(symbol)
            if hist is None:
                return None
            
            # Calculate all indicators
            indicators = self._calculate_all_indicators(hist)
            
            logger.info(f"✅ yfinance: {symbol} indicators retrieved")
            return indicators
            
        except Exception as e:
            logger.error(f"yfinance error for {symbol}: {e}")
            return None
    
    def _get_historical_data(self, symbol: str) -> Optional:
        """Get historical data from yfinance"""
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="6mo", interval="1d")
        
        if hist.empty or len(hist) < 50:
            logger.warning(f"⚠️  yfinance: Insufficient data for {symbol}")
            return None
        
        return hist
    
    def _calculate_all_indicators(self, hist) -> Dict:
        """Calculate all technical indicators"""
        close = hist['Close']
        
        # Calculate RSI
        rsi = self._calculate_rsi(close)
        
        # Calculate SMAs
        sma_20, sma_50 = self._calculate_smas(close)
        
        # Calculate MACD
        macd, macd_signal = self._calculate_macd(close)
        
        # Extract current values
        return self._extract_current_values(close, rsi, sma_20, sma_50, macd, macd_signal)
    
    def _calculate_rsi(self, close) -> pd.Series:
        """Calculate RSI indicator"""
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_smas(self, close) -> Tuple[pd.Series, pd.Series]:
        """Calculate SMA indicators"""
        sma_20 = close.rolling(window=20).mean()
        sma_50 = close.rolling(window=50).mean()
        return sma_20, sma_50
    
    def _calculate_macd(self, close) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        return macd, macd_signal
    
    def _extract_current_values(self, close, rsi, sma_20, sma_50, macd, macd_signal) -> Dict:
        """Extract current indicator values"""
        return {
            'rsi': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
            'sma_20': float(sma_20.iloc[-1]) if not pd.isna(sma_20.iloc[-1]) else None,
            'sma_50': float(sma_50.iloc[-1]) if not pd.isna(sma_50.iloc[-1]) else None,
            'macd': float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
            'macd_signal': float(macd_signal.iloc[-1]) if not pd.isna(macd_signal.iloc[-1]) else None,
            'current_price': float(close.iloc[-1])
        }
    
    def generate_signal(self, indicators: Dict, symbol: str) -> Optional[dict]:
        """Generate signal from yfinance technical indicators"""
        if not indicators:
            return None
        
        try:
            # Validate required indicators
            if not self._validate_indicators(indicators):
                return None
            
            # Determine signal direction and confidence
            direction, confidence = self._determine_signal(indicators)
            
            if confidence < 60:
                return None
            
            return self._build_signal_dict(direction, confidence, indicators)
            
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return None
    
    def _validate_indicators(self, indicators: Dict) -> bool:
        """Validate that required indicators are present"""
        rsi = indicators.get('rsi')
        sma_20 = indicators.get('sma_20')
        current_price = indicators.get('current_price')
        return all([rsi, sma_20, current_price])
    
    def _determine_signal(self, indicators: Dict) -> Tuple[str, float]:
        """Determine signal direction and confidence"""
        rsi = indicators.get('rsi')
        sma_20 = indicators.get('sma_20')
        sma_50 = indicators.get('sma_50')
        macd = indicators.get('macd')
        macd_signal = indicators.get('macd_signal')
        current_price = indicators.get('current_price')
        
        confidence = 50.0
        direction = 'NEUTRAL'
        
        # RSI-based signals
        direction, confidence = self._apply_rsi_signals(rsi, direction, confidence)
        
        # MACD confirmation
        confidence = self._apply_macd_confirmation(macd, macd_signal, direction, confidence)
        
        # Price vs SMA trend
        confidence = self._apply_sma_trend(current_price, sma_20, direction, confidence)
        
        # SMA trend confirmation
        confidence = self._apply_sma_trend_confirmation(sma_20, sma_50, direction, confidence)
        
        confidence = min(confidence, 95.0)
        return direction, confidence
    
    def _apply_rsi_signals(self, rsi: float, direction: str, confidence: float) -> Tuple[str, float]:
        """Apply RSI-based signal logic"""
        if rsi < 30:  # Oversold
            direction = 'LONG'
            confidence += 20.0
        elif rsi > 70:  # Overbought
            direction = 'SHORT'
            confidence += 20.0
        elif rsi < 45:  # Moderately oversold
            direction = 'LONG'
            confidence += 10.0
        elif rsi > 60:  # Moderately overbought
            direction = 'SHORT'
            confidence += 10.0
        return direction, confidence
    
    def _apply_macd_confirmation(self, macd: Optional[float], macd_signal: Optional[float], 
                                 direction: str, confidence: float) -> float:
        """Apply MACD confirmation"""
        if macd and macd_signal:
            if macd > macd_signal and direction == 'LONG':
                confidence += 10.0
            elif macd < macd_signal and direction == 'SHORT':
                confidence += 10.0
            elif macd > macd_signal and direction == 'SHORT':
                confidence -= 5.0
            elif macd < macd_signal and direction == 'LONG':
                confidence -= 5.0
        return confidence
    
    def _apply_sma_trend(self, current_price: float, sma_20: float, 
                        direction: str, confidence: float) -> float:
        """Apply price vs SMA trend logic"""
        if current_price > sma_20:
            if direction == 'LONG':
                confidence += 15.0
            elif direction == 'SHORT':
                confidence -= 10.0
        else:
            if direction == 'SHORT':
                confidence += 15.0
            elif direction == 'LONG':
                confidence -= 10.0
        return confidence
    
    def _apply_sma_trend_confirmation(self, sma_20: float, sma_50: Optional[float],
                                     direction: str, confidence: float) -> float:
        """Apply SMA trend confirmation"""
        if sma_50:
            if sma_20 > sma_50 and direction == 'LONG':
                confidence += 5.0
            elif sma_20 < sma_50 and direction == 'SHORT':
                confidence += 5.0
        return confidence
    
    def _build_signal_dict(self, direction: str, confidence: float, indicators: Dict) -> Dict:
        """Build signal dictionary"""
        return {
            'direction': direction,
            'confidence': round(confidence, 2),
            'source': 'yfinance',
            'weight': 0.25,  # Same weight as Alpha Vantage
            'indicators': {
                'rsi': round(indicators['rsi'], 2),
                'sma_20': round(indicators['sma_20'], 2),
                'sma_50': round(indicators['sma_50'], 2) if indicators.get('sma_50') else None,
                'macd': round(indicators['macd'], 4) if indicators.get('macd') else None,
                'current_price': round(indicators['current_price'], 2)
            }
        }

