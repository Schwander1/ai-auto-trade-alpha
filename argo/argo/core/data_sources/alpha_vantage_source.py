#!/usr/bin/env python3
"""Alpha Vantage Data Source - Technical Indicators (25% weight)"""
import requests
import json
import logging
import time
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlphaVantage")

class AlphaVantageDataSource:
    """
    Alpha Vantage integration for technical indicators
    Weight: 25% in Alpine Analytics consensus
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        
    def fetch_technical_indicators(self, symbol):
        """Fetch RSI, SMA, EMA for signal generation"""
        try:
            indicators = {}
            
            # RSI
            rsi_params = {
                'function': 'RSI',
                'symbol': symbol,
                'interval': 'daily',
                'time_period': 14,
                'series_type': 'close',
                'apikey': self.api_key
            }
            rsi_response = requests.get(self.base_url, params=rsi_params, timeout=10)
            if rsi_response.status_code == 200:
                rsi_data = rsi_response.json()
                if 'Technical Analysis: RSI' in rsi_data:
                    rsi_values = list(rsi_data['Technical Analysis: RSI'].values())
                    indicators['rsi'] = float(rsi_values[0]['RSI']) if rsi_values else None
            
            time.sleep(0.3)  # Rate limit: 5 calls/min
            
            # SMA 20
            sma_params = {
                'function': 'SMA',
                'symbol': symbol,
                'interval': 'daily',
                'time_period': 20,
                'series_type': 'close',
                'apikey': self.api_key
            }
            sma_response = requests.get(self.base_url, params=sma_params, timeout=10)
            if sma_response.status_code == 200:
                sma_data = sma_response.json()
                if 'Technical Analysis: SMA' in sma_data:
                    sma_values = list(sma_data['Technical Analysis: SMA'].values())
                    indicators['sma_20'] = float(sma_values[0]['SMA']) if sma_values else None
            
            time.sleep(0.3)
            
            # Current price (for comparison)
            quote_params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            quote_response = requests.get(self.base_url, params=quote_params, timeout=10)
            if quote_response.status_code == 200:
                quote_data = quote_response.json()
                if 'Global Quote' in quote_data:
                    indicators['current_price'] = float(quote_data['Global Quote']['05. price'])
            
            logger.info(f"✅ Alpha Vantage: {symbol} indicators retrieved")
            return indicators
            
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
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
            if confidence < 60:
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
