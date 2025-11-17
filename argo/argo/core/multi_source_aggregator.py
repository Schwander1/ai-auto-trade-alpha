#!/usr/bin/env python3
"""Multi-source data aggregation from Massive.com"""
import json, logging, pandas as pd, requests
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MultiSource")

class MultiSourceAggregator:
    def __init__(self, config_path='/root/argo-production/config.json'):
        with open(config_path) as f:
            self.config = json.load(f)
        self.massive_key = self.config['massive']['api_key']
        
    def fetch_massive_data(self, symbol, days=90):
        try:
            ticker = symbol if '-USD' not in symbol else f"X:{symbol.replace('-USD', '')}USD"
            end = datetime.now().strftime('%Y-%m-%d')
            start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}"
            
            params = {'adjusted': 'true', 'sort': 'asc', 'limit': 50000, 'apiKey': self.massive_key}
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
            
            logger.info(f"✅ {symbol}: {len(df)} bars from Massive.com")
            return df
            
        except Exception as e:
            logger.error(f"Massive {symbol}: {e}")
            return None
    
    def aggregate(self, symbol):
        return {
            'price_data': self.fetch_massive_data(symbol),
            'data_quality_score': 10
        }
