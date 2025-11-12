import os
import asyncio
from datetime import datetime
from typing import Dict, Optional
import yfinance as yf

class DataAggregator:
    def __init__(self):
        self.alpaca_key = os.getenv('ALPACA_API_KEY')
        self.alpha_key = os.getenv('ALPHA_VANTAGE_KEY')
        self.cache = {}
    
    async def get_stock_data(self, symbol: str) -> Dict:
        """Fetch real-time stock data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if hist.empty:
                return None
            
            return {
                'symbol': symbol,
                'current_price': float(hist['Close'][-1]),
                'close_prices': hist['Close'].tolist(),
                'volumes': hist['Volume'].tolist(),
                'high': float(hist['High'][-1]),
                'low': float(hist['Low'][-1]),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    async def get_crypto_data(self, symbol: str) -> Dict:
        """Fetch real-time crypto data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="7d", interval="1h")
            
            if hist.empty:
                return None
            
            return {
                'symbol': symbol,
                'current_price': float(hist['Close'][-1]),
                'close_prices': hist['Close'].tolist(),
                'volumes': hist['Volume'].tolist(),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error fetching crypto {symbol}: {e}")
            return None

aggregator = DataAggregator()
