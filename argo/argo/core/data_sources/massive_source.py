#!/usr/bin/env python3
"""Massive.com (Polygon.io) Data Source - Primary Market Data (40% weight)"""
import requests
import json
import logging
import time
import pandas as pd
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Massive")

class MassiveDataSource:
    """
    Massive.com (Polygon.io) integration for market data
    Weight: 40% in Alpine Analytics consensus (primary source)
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        
    def fetch_price_data(self, symbol, days=90):
        """Fetch historical price data"""
        try:
            ticker = symbol if '-USD' not in symbol else f"X:{symbol.replace('-USD', '')}USD"
            end = datetime.now().strftime('%Y-%m-%d')
            start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}"
            
            params = {'adjusted': 'true', 'sort': 'asc', 'limit': 50000, 'apiKey': self.api_key}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            if data.get('status') not in ['OK', 'DELAYED'] or not data.get('results'):
                return None
            
            df = pd.DataFrame(data['results'])
            df['Date'] = pd.to_datetime(df['t'], unit='ms')
            df = df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'})
            df = df.set_index('Date')[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            logger.info(f"✅ Massive: {symbol} - {len(df)} bars")
            time.sleep(0.15)
            return df
            
        except Exception as e:
            logger.error(f"Massive error for {symbol}: {e}")
            return None
    
    def generate_signal(self, df, symbol):
        """Generate signal from price data"""
        if df is None or len(df) < 50:
            return None
        
        try:
            # Calculate indicators
            df['SMA_20'] = df['Close'].rolling(20).mean()
            df['SMA_50'] = df['Close'].rolling(50).mean()
            df['Volume_SMA'] = df['Volume'].rolling(20).mean()
            
            latest = df.iloc[-1]
            current_price = latest['Close']
            sma_20 = latest['SMA_20']
            sma_50 = latest['SMA_50']
            volume_ratio = latest['Volume'] / latest['Volume_SMA']
            
            # Signal logic
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
            
            if confidence < 65:
                return None
            
            return {
                'direction': direction,
                'confidence': round(confidence, 2),
                'source': 'massive',
                'weight': 0.40,
                'entry_price': round(current_price, 2),
                'indicators': {
                    'sma_20': round(sma_20, 2),
                    'sma_50': round(sma_50, 2),
                    'volume_ratio': round(volume_ratio, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return None
