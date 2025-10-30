#!/usr/bin/env python3
"""
ARGO Capital Database Connection Helper
"""
import clickhouse_connect
import redis

# ClickHouse connection (port 8231 for HTTP)
def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host='localhost',
        port=8231,
        database='argo_capital'
    )

# Redis connection
def get_redis_client():
    return redis.Redis(
        host='localhost',
        port=6379,
        password='ArgoCapital2025!',
        decode_responses=True
    )

# Test connections
if __name__ == "__main__":
    print("🧪 Testing ARGO Capital Database Connections")
    
    # Test ClickHouse
    try:
        ch_client = get_clickhouse_client()
        result = ch_client.query("SELECT 'ClickHouse Connected!' as status")
        print("✅ ClickHouse:", result.first_row[0])
    except Exception as e:
        print("❌ ClickHouse:", str(e))
    
    # Test Redis
    try:
        redis_client = get_redis_client()
        redis_client.ping()
        print("✅ Redis: Connected!")
    except Exception as e:
        print("❌ Redis:", str(e))
