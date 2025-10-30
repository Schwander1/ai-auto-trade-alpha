#!/usr/bin/env python3
"""
ARGO Capital Redis Trading Integration Module
Professional-grade Redis integration for high-frequency trading data management
"""

import redis
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal

class ArgoRedisTrading:
    def __init__(self, host='localhost', port=6379, db=0):
        """Initialize ARGO Capital Redis Trading Integration"""
        self.redis_client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            decode_responses=True,
            health_check_interval=30
        )
        self.logger = logging.getLogger('ArgoRedis')
        
    def store_portfolio(self, portfolio_data: Dict) -> bool:
        """Store portfolio data with proper JSON serialization"""
        try:
            # Prepare data for Redis storage
            redis_data = {}
            for key, value in portfolio_data.items():
                if isinstance(value, dict):
                    redis_data[key] = json.dumps(value, default=str)
                elif isinstance(value, Decimal):
                    redis_data[key] = str(value)
                else:
                    redis_data[key] = value
            
            # Store with timestamp
            redis_data['last_update'] = datetime.now().isoformat()
            
            # Store in Redis hash
            self.redis_client.hset('portfolio:current', mapping=redis_data)
            
            # Set expiration for safety (24 hours)
            self.redis_client.expire('portfolio:current', 86400)
            
            self.logger.info(f"Portfolio stored successfully: Balance {portfolio_data.get('balance', 'N/A')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Portfolio storage error: {e}")
            return False
    
    def get_portfolio(self) -> Optional[Dict]:
        """Retrieve portfolio data with proper JSON deserialization"""
        try:
            raw_data = self.redis_client.hgetall('portfolio:current')
            if not raw_data:
                return None
            
            # Deserialize JSON fields
            portfolio_data = {}
            for key, value in raw_data.items():
                if key in ['positions', 'orders', 'risk_metrics']:
                    try:
                        portfolio_data[key] = json.loads(value)
                    except json.JSONDecodeError:
                        portfolio_data[key] = value
                elif key in ['balance', 'buying_power']:
                    try:
                        portfolio_data[key] = float(value)
                    except ValueError:
                        portfolio_data[key] = value
                else:
                    portfolio_data[key] = value
            
            return portfolio_data
            
        except Exception as e:
            self.logger.error(f"Portfolio retrieval error: {e}")
            return None
    
    def store_trading_signal(self, signal: Dict) -> bool:
        """Store trading signal with timestamp and expiration"""
        try:
            signal_data = signal.copy()
            signal_data['timestamp'] = datetime.now().isoformat()
            signal_data['expires_at'] = (datetime.now() + timedelta(minutes=30)).isoformat()
            
            # Store in sorted set by confidence score
            score = signal_data.get('confidence', 0) * 100
            self.redis_client.zadd('signals:active', {json.dumps(signal_data): score})
            
            # Also store in list for chronological access
            self.redis_client.lpush('signals:chronological', json.dumps(signal_data))
            
            # Trim chronological list to last 100 signals
            self.redis_client.ltrim('signals:chronological', 0, 99)
            
            # Set expiration for active signals (1 hour)
            self.redis_client.expire('signals:active', 3600)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Signal storage error: {e}")
            return False
    
    def get_high_confidence_signals(self, min_confidence: float = 0.75) -> List[Dict]:
        """Retrieve high-confidence trading signals"""
        try:
            min_score = min_confidence * 100
            signals_raw = self.redis_client.zrevrangebyscore(
                'signals:active', '+inf', min_score, withscores=True
            )
            
            signals = []
            for signal_json, score in signals_raw:
                try:
                    signal_data = json.loads(signal_json)
                    signal_data['score'] = score / 100
                    
                    # Check if signal is still valid
                    expires_at = datetime.fromisoformat(signal_data.get('expires_at', ''))
                    if datetime.now() < expires_at:
                        signals.append(signal_data)
                        
                except (json.JSONDecodeError, ValueError):
                    continue
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Signal retrieval error: {e}")
            return []
    
    def store_price_data(self, symbol: str, price: float, volume: int = 0) -> bool:
        """Store real-time price data with volume"""
        try:
            price_data = {
                'price': price,
                'volume': volume,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store current price
            self.redis_client.set(f'price:{symbol}', json.dumps(price_data), ex=300)  # 5 min expiry
            
            # Store in time series (last 100 prices)
            self.redis_client.lpush(f'prices:{symbol}:history', json.dumps(price_data))
            self.redis_client.ltrim(f'prices:{symbol}:history', 0, 99)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Price storage error for {symbol}: {e}")
            return False
    
    def get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Retrieve current prices for multiple symbols"""
        try:
            prices = {}
            pipe = self.redis_client.pipeline()
            
            # Batch get all prices
            for symbol in symbols:
                pipe.get(f'price:{symbol}')
            
            results = pipe.execute()
            
            for symbol, result in zip(symbols, results):
                if result:
                    try:
                        price_data = json.loads(result)
                        prices[symbol] = float(price_data['price'])
                    except (json.JSONDecodeError, ValueError, KeyError):
                        continue
            
            return prices
            
        except Exception as e:
            self.logger.error(f"Price retrieval error: {e}")
            return {}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get Redis system health metrics"""
        try:
            info = self.redis_client.info()
            return {
                'connected': True,
                'memory_used': info.get('used_memory_human', 'Unknown'),
                'memory_peak': info.get('used_memory_peak_human', 'Unknown'),
                'total_commands': info.get('total_commands_processed', 0),
                'uptime_seconds': info.get('uptime_in_seconds', 0),
                'connected_clients': info.get('connected_clients', 0),
                'portfolio_keys': self.redis_client.exists('portfolio:current'),
                'active_signals': self.redis_client.zcard('signals:active'),
                'price_keys': len(self.redis_client.keys('price:*'))
            }
        except Exception as e:
            return {'connected': False, 'error': str(e)}

# ARGO Capital Redis Integration Test
if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Initialize Redis integration
    argo_redis = ArgoRedisTrading()
    
    print("🎯 ARGO Capital Redis Integration Test")
    print("=" * 50)
    
    # Test portfolio storage
    test_portfolio = {
        'balance': 99999.60,
        'buying_power': 199311.36,
        'positions': {
            'AAPL': {'shares': 22, 'avg_price': 269.44, 'market_value': 5927.68},
            'QQQ': {'shares': 8, 'avg_price': 636.15, 'market_value': 5089.20}
        },
        'daily_pnl': 1234.56,
        'risk_metrics': {
            'max_position_pct': 15.0,
            'daily_stop_loss': -3.0,
            'current_risk': 11.2
        }
    }
    
    if argo_redis.store_portfolio(test_portfolio):
        print("✅ Portfolio Storage: SUCCESS")
        
        retrieved = argo_redis.get_portfolio()
        if retrieved:
            print(f"💰 Retrieved Balance: ${retrieved['balance']:,.2f}")
            print(f"💳 Retrieved Buying Power: ${retrieved['buying_power']:,.2f}")
            print(f"📊 Position Count: {len(retrieved.get('positions', {}))}")
    
    # Test trading signals
    test_signals = [
        {'symbol': 'TSLA', 'signal': 'BUY', 'confidence': 0.85, 'price_target': 250.00},
        {'symbol': 'NVDA', 'signal': 'SELL', 'confidence': 0.92, 'price_target': 140.00},
        {'symbol': 'AMZN', 'signal': 'BUY', 'confidence': 0.78, 'price_target': 190.00}
    ]
    
    for signal in test_signals:
        argo_redis.store_trading_signal(signal)
    
    high_conf_signals = argo_redis.get_high_confidence_signals(0.75)
    print(f"📈 High-Confidence Signals: {len(high_conf_signals)}")
    
    # Test price data
    test_prices = {'SPY': 585.34, 'QQQ': 636.89, 'AAPL': 269.78, 'TSLA': 248.92}
    for symbol, price in test_prices.items():
        argo_redis.store_price_data(symbol, price, volume=1000000)
    
    current_prices = argo_redis.get_current_prices(list(test_prices.keys()))
    print(f"💹 Current Prices Cached: {len(current_prices)}")
    
    # System health check
    health = argo_redis.get_system_health()
    print(f"🏥 System Health: {'✅ HEALTHY' if health['connected'] else '❌ ERROR'}")
    if health['connected']:
        print(f"   Memory Usage: {health['memory_used']}")
        print(f"   Active Signals: {health['active_signals']}")
        print(f"   Price Keys: {health['price_keys']}")
    
    print("")
    print("🚀 ARGO Redis Integration: ENTERPRISE-READY")
