#!/usr/bin/env python3
"""
ClickHouse schema initialization for AI Auto-Trade Alpha
Creates trading_db database and market_data table
"""
import clickhouse_connect
import os
from datetime import datetime

def setup_schema():
    client = clickhouse_connect.get_client(
        host=os.getenv('CLICKHOUSE_HOST', 'localhost'),
        port=int(os.getenv('CLICKHOUSE_PORT', 8123)),
        username=os.getenv('CLICKHOUSE_USER', 'default'),
        password=os.getenv('CLICKHOUSE_PASSWORD', 'password123')
    )

    client.command("CREATE DATABASE IF NOT EXISTS trading_db")
    print(f"[{datetime.now()}] Database 'trading_db' created/verified")

    client.command("""
        CREATE TABLE IF NOT EXISTS trading_db.market_data (
            timestamp DateTime64(3),
            symbol String,
            open Float64,
            high Float64,
            low Float64,
            close Float64,
            volume Float64,
            trade_count UInt32 DEFAULT 0,
            vwap Float64 DEFAULT 0
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(timestamp)
        ORDER BY (symbol, timestamp)
        TTL timestamp + INTERVAL 90 DAY
        SETTINGS index_granularity = 8192
    """)
    print(f"[{datetime.now()}] Table 'market_data' created/verified")

    result = client.query("DESCRIBE trading_db.market_data")
    print("\n✓ Schema Verification:")
    for row in result.result_rows:
        print(f"  {row[0]}: {row[1]}")

    client.close()
    print(f"\n[{datetime.now()}] ✓ ClickHouse setup complete!")

if __name__ == "__main__":
    setup_schema()
