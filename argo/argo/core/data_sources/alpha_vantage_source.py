#!/usr/bin/env python3
"""Alpha Vantage Data Source - Technical Indicators (25% weight)"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import logging
import asyncio
import pandas as pd
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlphaVantage")

class AlphaVantageDataSource:
    """
    Alpha Vantage integration for technical indicators
    Weight: 25% in Alpine Analytics consensus
    Connection Pooling: HTTP session with connection reuse for better performance
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        
        # HTTP Session with connection pooling for better performance
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        # OPTIMIZATION 14: Increased connection pool sizes
        adapter = HTTPAdapter(
            pool_connections=20,  # Increased from 10
            pool_maxsize=50,      # Increased from 20
            max_retries=retry_strategy,
            pool_block=False
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # OPTIMIZATION: Rate limiting and circuit breaker
        try:
            from argo.core.rate_limiter import get_rate_limiter
            from argo.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
            self.rate_limiter = get_rate_limiter()
            self.circuit_breaker = CircuitBreaker('alpha_vantage', CircuitBreakerConfig(
                failure_threshold=5,
                success_threshold=2,
                timeout=60.0
            ))
        except ImportError:
            self.rate_limiter = None
            self.circuit_breaker = None
        
    async def fetch_technical_indicators(self, symbol):
        """Fetch RSI, SMA, EMA for signal generation (async with connection pooling)
        Note: Alpha Vantage has limited crypto support - crypto symbols may return None
        """
        # Check if crypto symbol - Alpha Vantage has limited crypto support
        is_crypto = '-USD' in symbol or symbol.startswith('BTC') or symbol.startswith('ETH')
        if is_crypto:
            logger.debug(f"⚠️  Alpha Vantage: Limited crypto support for {symbol} - may return None")
            # Alpha Vantage doesn't support all crypto symbols well, return None gracefully
            # Other sources (Massive.com, xAI Grok, Sonar) will handle crypto
            return None
        
        try:
            indicators = {}
            
            # Fetch RSI
            rsi = await self._fetch_rsi(symbol)
            if rsi is not None:
                indicators['rsi'] = rsi
            
            await asyncio.sleep(0.3)  # Rate limit: 5 calls/min (non-blocking)
            
            # Fetch SMA 20
            sma_20 = await self._fetch_sma(symbol)
            if sma_20 is not None:
                indicators['sma_20'] = sma_20
            
            await asyncio.sleep(0.3)  # Rate limit (non-blocking)
            
            # Fetch current price
            current_price = await self._fetch_current_price(symbol)
            if current_price is not None:
                indicators['current_price'] = current_price
            
            logger.info(f"✅ Alpha Vantage: {symbol} indicators retrieved")
            return indicators
            
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            return None
    
    async def _fetch_rsi(self, symbol: str) -> Optional[float]:
        """Fetch RSI indicator"""
        # OPTIMIZATION: Rate limiting
        if self.rate_limiter:
            await self.rate_limiter.wait_for_permission('alpha_vantage')
        
        params = {
            'function': 'RSI',
            'symbol': symbol,
            'interval': 'daily',
            'time_period': 14,
            'series_type': 'close',
            'apikey': self.api_key
        }
        
        # OPTIMIZATION: Circuit breaker protection
        if self.circuit_breaker:
            async def _fetch():
                return await asyncio.to_thread(self.session.get, self.base_url, params=params, timeout=10)
            response = await self.circuit_breaker.call_async(_fetch)
        else:
            response = await asyncio.to_thread(self.session.get, self.base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            rsi_data = response.json()
            if 'Technical Analysis: RSI' in rsi_data:
                rsi_values = list(rsi_data['Technical Analysis: RSI'].values())
                return float(rsi_values[0]['RSI']) if rsi_values else None
        return None
    
    async def _fetch_sma(self, symbol: str) -> Optional[float]:
        """Fetch SMA 20 indicator"""
        # OPTIMIZATION: Rate limiting
        if self.rate_limiter:
            await self.rate_limiter.wait_for_permission('alpha_vantage')
        
        params = {
            'function': 'SMA',
            'symbol': symbol,
            'interval': 'daily',
            'time_period': 20,
            'series_type': 'close',
            'apikey': self.api_key
        }
        
        # OPTIMIZATION: Circuit breaker protection
        if self.circuit_breaker:
            async def _fetch():
                return await asyncio.to_thread(self.session.get, self.base_url, params=params, timeout=10)
            response = await self.circuit_breaker.call_async(_fetch)
        else:
            response = await asyncio.to_thread(self.session.get, self.base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            sma_data = response.json()
            if 'Technical Analysis: SMA' in sma_data:
                sma_values = list(sma_data['Technical Analysis: SMA'].values())
                return float(sma_values[0]['SMA']) if sma_values else None
        return None
    
    async def _fetch_current_price(self, symbol: str) -> Optional[float]:
        """Fetch current price"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        response = await asyncio.to_thread(self.session.get, self.base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            quote_data = response.json()
            if 'Global Quote' in quote_data:
                return float(quote_data['Global Quote']['05. price'])
        return None
    
    def generate_signal(self, indicators, symbol):
        """Generate LONG/SHORT/NEUTRAL signal from technical indicators"""
        if not indicators:
            return None
        
        try:
            rsi = indicators.get('rsi')
            sma_20 = indicators.get('sma_20')
            current_price = indicators.get('current_price')
            
            if not all([rsi, sma_20, current_price]):
                return None
            
            # Signal logic
            confidence = 50.0  # Base confidence
            direction = 'NEUTRAL'
            
            # RSI-based signals
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
            
            # Price vs SMA trend
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
            
            # Cap confidence at 95
            confidence = min(confidence, 95.0)
            
            # Only return if confidence >= 60
            # Allow signals even with lower confidence - consensus will filter them
            # Only filter out completely invalid signals (confidence < 50)
            if confidence < 50:
                return None
            
            return {
                'direction': direction,
                'confidence': round(confidence, 2),
                'source': 'alpha_vantage',
                'weight': 0.25,
                'indicators': {
                    'rsi': round(rsi, 2),
                    'sma_20': round(sma_20, 2),
                    'current_price': round(current_price, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return None
