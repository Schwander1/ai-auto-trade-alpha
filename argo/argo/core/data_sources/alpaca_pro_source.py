#!/usr/bin/env python3
"""Alpaca Pro Data Source - Real-time Market Data (supplements Massive.com)"""
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlpacaPro")

class AlpacaProDataSource:
    """
    Alpaca Pro integration for real-time market data
    Used to supplement Massive.com with real-time data
    High quality, already paid for with Alpaca Pro subscription
    """
    
    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://data.alpaca.markets"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.enabled = bool(api_key and secret_key)
        
        if not self.enabled:
            logger.warning("⚠️  Alpaca Pro credentials not configured")
        else:
            logger.info("✅ Alpaca Pro data source initialized")
    
    def _get_headers(self):
        """Get authentication headers"""
        return {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret_key
        }
    
    async def fetch_price_data(self, symbol: str, days: int = 90) -> Optional[pd.DataFrame]:
        """
        Fetch historical price data from Alpaca Pro
        High quality real-time data
        """
        if not self.enabled:
            return None
        
        try:
            is_crypto = self._is_crypto_symbol(symbol)
            alpaca_symbol = self._convert_symbol_format(symbol, is_crypto)
            client = self._create_client(is_crypto)
            
            start, end = self._get_date_range(days)
            request = self._create_request(alpaca_symbol, is_crypto, start, end)
            
            bars = await self._fetch_bars(client, request)
            
            if not bars or alpaca_symbol not in bars:
                logger.debug(f"⚠️  Alpaca Pro: No data for {symbol}")
                return None
            
            return self._convert_to_dataframe(bars[alpaca_symbol], symbol)
            
        except ImportError:
            logger.warning("⚠️  Alpaca data library not available - install alpaca-py")
            return None
        except Exception as e:
            logger.debug(f"Alpaca Pro error for {symbol}: {e}")
            return None
    
    def _is_crypto_symbol(self, symbol: str) -> bool:
        """Determine if symbol is crypto"""
        return '-USD' in symbol or symbol.startswith('BTC') or symbol.startswith('ETH')
    
    def _convert_symbol_format(self, symbol: str, is_crypto: bool) -> str:
        """Convert symbol format for Alpaca API"""
        if is_crypto:
            return symbol.replace('-USD', 'USD')
        return symbol
    
    def _create_client(self, is_crypto: bool):
        """Create appropriate Alpaca client"""
        from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
        
        if is_crypto:
            return CryptoHistoricalDataClient(self.api_key, self.secret_key)
        else:
            return StockHistoricalDataClient(self.api_key, self.secret_key)
    
    def _get_date_range(self, days: int) -> Tuple[datetime, datetime]:
        """Get start and end dates"""
        end = datetime.now()
        start = end - timedelta(days=days)
        return start, end
    
    def _create_request(self, alpaca_symbol: str, is_crypto: bool, start: datetime, end: datetime):
        """Create Alpaca bars request"""
        from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
        from alpaca.data.timeframe import TimeFrame
        
        if is_crypto:
            return CryptoBarsRequest(
                symbol_or_symbols=[alpaca_symbol],
                timeframe=TimeFrame.Day,
                start=start,
                end=end
            )
        else:
            return StockBarsRequest(
                symbol_or_symbols=[alpaca_symbol],
                timeframe=TimeFrame.Day,
                start=start,
                end=end
            )
    
    async def _fetch_bars(self, client, request):
        """Fetch bars from Alpaca API"""
        try:
            return await asyncio.to_thread(client.get_bars, request)
        except AttributeError:
            # Fallback for Python < 3.9
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: client.get_bars(request))
    
    def _convert_to_dataframe(self, symbol_bars, symbol: str) -> Optional[pd.DataFrame]:
        """Convert Alpaca bars to DataFrame"""
        data = []
        for bar in symbol_bars:
            data.append({
                'Open': float(bar.open),
                'High': float(bar.high),
                'Low': float(bar.low),
                'Close': float(bar.close),
                'Volume': float(bar.volume),
                'Date': bar.timestamp
            })
        
        if not data:
            return None
        
        df = pd.DataFrame(data)
        df = df.set_index('Date')
        df = df.sort_index()
        
        logger.info(f"✅ Alpaca Pro: {symbol} - {len(df)} bars")
        return df
    
    def generate_signal(self, df: pd.DataFrame, symbol: str) -> Optional[dict]:
        """Generate signal from Alpaca Pro price data"""
        if df is None or len(df) < 50:
            return None
        
        try:
            # Calculate indicators (same logic as Massive.com for consistency)
            indicators = self._calculate_indicators(df)
            
            # Determine signal direction and confidence
            direction, confidence = self._determine_signal(indicators, df)
            
            if confidence < 65:
                return None
            
            return self._build_signal_dict(direction, confidence, indicators)
            
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return None
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators"""
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['Volume_SMA'] = df['Volume'].rolling(20).mean()
        
        latest = df.iloc[-1]
        return {
            'current_price': latest['Close'],
            'sma_20': latest['SMA_20'],
            'sma_50': latest['SMA_50'],
            'volume_ratio': latest['Volume'] / latest['Volume_SMA']
        }
    
    def _determine_signal(self, indicators: Dict, df: pd.DataFrame) -> Tuple[str, float]:
        """Determine signal direction and confidence"""
        current_price = indicators['current_price']
        sma_20 = indicators['sma_20']
        sma_50 = indicators['sma_50']
        volume_ratio = indicators['volume_ratio']
        
        confidence = 60.0
        direction = 'NEUTRAL'
        
        # Trend-based
        if current_price > sma_20 > sma_50:
            direction = 'LONG'
            confidence += 15.0
        elif current_price < sma_20 < sma_50:
            direction = 'SHORT'
            confidence += 15.0
        
        # Volume confirmation
        if volume_ratio > 1.2:
            confidence += 10.0
        
        # Price momentum
        price_change_pct = ((current_price - df.iloc[-5]['Close']) / df.iloc[-5]['Close']) * 100
        if abs(price_change_pct) > 2:
            confidence += 10.0
        
        confidence = min(confidence, 95.0)
        return direction, confidence
    
    def _build_signal_dict(self, direction: str, confidence: float, indicators: Dict) -> Dict:
        """Build signal dictionary"""
        return {
            'direction': direction,
            'confidence': round(confidence, 2),
            'source': 'alpaca_pro',
            'weight': 0.40,  # Same weight as Massive.com
            'entry_price': round(indicators['current_price'], 2),
            'indicators': {
                'sma_20': round(indicators['sma_20'], 2),
                'sma_50': round(indicators['sma_50'], 2),
                'volume_ratio': round(indicators['volume_ratio'], 2)
            }
        }

