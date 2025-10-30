#!/usr/bin/env python3
"""
ARGO Capital Database Connection Helper - Fixed Version
"""
import clickhouse_connect
import redis

# ClickHouse connection (HTTP port 8231, not TCP port 9009)
def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host='localhost',
        port=8231,  # HTTP port for Python client
        database='argo_capital'
    )

# Redis connection (ACL-based authentication)
def get_redis_client():
    return redis.Redis(
        host='localhost',
        port=6379,
        username='default',
        password='ArgoCapital2025!',
        decode_responses=True
    )

# Test connections
if __name__ == "__main__":
    print("🧪 Testing ARGO Capital Database Connections - Fixed")
    
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

    print("\n📊 Connection Summary:")
    print("• ClickHouse HTTP: localhost:8231")
    print("• ClickHouse TCP: localhost:9009 (for clickhouse-client)")
    print("• Redis: localhost:6379")
