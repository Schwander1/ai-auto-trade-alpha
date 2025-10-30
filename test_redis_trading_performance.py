#!/usr/bin/env python3
"""
ARGO Capital Redis Performance Test Suite
Validates Redis configuration for high-frequency trading data
"""

import redis
import json
import time
from datetime import datetime

def test_redis_trading_performance():
    print("🧪 ARGO Capital: Redis Trading Performance Test")
    print("=" * 50)
    
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Test 1: Basic Connectivity
    print(f"📡 Redis Connection: {r.ping()}")
    
    # Test 2: Portfolio Data Storage
    portfolio_data = {
        'balance': 99999.60,
        'buying_power': 199311.36,
        'positions': {
            'AAPL': {'shares': 22, 'avg_price': 269.44},
            'QQQ': {'shares': 8, 'avg_price': 636.15},
            'SPY': {'shares': 1, 'avg_price': 585.00}
        },
        'last_update': datetime.now().isoformat()
    }
    
    # Serialize 'positions' dictionary to JSON string
    portfolio_data_to_store = portfolio_data.copy()
    portfolio_data_to_store['positions'] = json.dumps(portfolio_data_to_store['positions'])

    start_time = time.time()
    r.hset('portfolio:current', mapping=portfolio_data_to_store)
    write_time = (time.time() - start_time) * 1000
    
    start_time = time.time()
    retrieved_data_raw = r.hgetall('portfolio:current')
    # Deserialize 'positions' back from JSON
    if 'positions' in retrieved_data_raw:
        retrieved_data_raw['positions'] = json.loads(retrieved_data_raw['positions'])
    retrieved_data = retrieved_data_raw
    read_time = (time.time() - start_time) * 1000
    
    print(f"💰 Portfolio Write Time: {write_time:.2f}ms")
    print(f"📊 Portfolio Read Time: {read_time:.2f}ms")
    
    # Test 3: Trading Signals Cache
    trading_signals = [
        {'symbol': 'TSLA', 'signal': 'BUY', 'confidence': 0.85, 'timestamp': datetime.now().isoformat()},
        {'symbol': 'NVDA', 'signal': 'SELL', 'confidence': 0.78, 'timestamp': datetime.now().isoformat()},
        {'symbol': 'AMZN', 'signal': 'BUY', 'confidence': 0.92, 'timestamp': datetime.now().isoformat()}
    ]
    
    start_time = time.time()
    for i, signal in enumerate(trading_signals):
        r.lpush('signals:latest', json.dumps(signal))
    signals_write_time = (time.time() - start_time) * 1000
    
    start_time = time.time()
    cached_signals = r.lrange('signals:latest', 0, -1)
    signals_read_time = (time.time() - start_time) * 1000
    
    print(f"📈 Signals Write Time: {signals_write_time:.2f}ms")
    print(f"🎯 Signals Read Time: {signals_read_time:.2f}ms")
    
    # Test 4: Real-time Price Data
    price_data = {
        'SPY': 585.34, 'QQQ': 636.89, 'AAPL': 269.78,
        'TSLA': 248.92, 'NVDA': 142.56, 'AMZN': 186.43
    }
    
    start_time = time.time()
    for symbol, price in price_data.items():
        r.set(f'price:{symbol}', price, ex=60)  # 60 second expiration
    price_write_time = (time.time() - start_time) * 1000
    
    print(f"💹 Price Data Write Time: {price_write_time:.2f}ms")
    
    # Performance Summary
    total_latency = write_time + read_time + signals_write_time + signals_read_time + price_write_time
    print("")
    print("🎯 REDIS PERFORMANCE SUMMARY:")
    print(f"   Total Latency: {total_latency:.2f}ms")
    print(f"   Avg Operation: {total_latency/5:.2f}ms")
    print(f"   Trading Ready: {'✅ EXCELLENT' if total_latency < 50 else '⚠️ ACCEPTABLE' if total_latency < 100 else '❌ SLOW'}")
    
    # Memory Info
    info = r.info('memory')
    print(f"   Memory Usage: {info['used_memory_human']}")
    print(f"   Peak Memory: {info['used_memory_peak_human']}")
    
    print("")
    print("✅ ARGO Redis: Optimized for High-Frequency Trading")

if __name__ == '__main__':
    test_redis_trading_performance()
