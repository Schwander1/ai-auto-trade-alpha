#!/usr/bin/env python3
"""
Alpaca market data ingestion pipeline
Fetches minute bars and loads into ClickHouse
"""
import os
import requests
import clickhouse_connect
from datetime import datetime, timedelta
from typing import List, Dict
import time
from dotenv import load_dotenv

load_dotenv()

class AlpacaDataIngester:
    def __init__(self):
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.data_url = "https://data.alpaca.markets/v2"

        if not self.api_key or not self.secret_key:
            raise ValueError("ALPACA_API_KEY and ALPACA_SECRET_KEY not found in environment")

        self.headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key
        }

        self.ch_client = clickhouse_connect.get_client(
            host=os.getenv('CLICKHOUSE_HOST', 'localhost'),
            port=int(os.getenv('CLICKHOUSE_PORT', 8123)),
            username=os.getenv('CLICKHOUSE_USER', 'default'),
            password=os.getenv('CLICKHOUSE_PASSWORD', 'password123')
        )

    def fetch_bars(self, symbol: str, start: str, end: str, timeframe: str = "1Min") -> List[Dict]:
        """Fetch bar data from Alpaca"""
        url = f"{self.data_url}/stocks/{symbol}/bars"
        params = {
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "adjustment": "raw",
            "limit": 10000
        }

        all_bars = []
        page_token = None

        while True:
            if page_token:
                params['page_token'] = page_token

            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                bars = data.get('bars', [])
                all_bars.extend(bars)

                page_token = data.get('next_page_token')
                if not page_token:
                    break

                time.sleep(0.1)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for {symbol}: {e}")
                break

        print(f"Fetched {len(all_bars)} bars for {symbol}")
        return all_bars

    def insert_bars(self, bars: List[Dict], symbol: str) -> int:
        """Insert bars into ClickHouse"""
        if not bars:
            return 0

        data = []
        for bar in bars:
            data.append([
                bar['t'],
                symbol,
                bar['o'],
                bar['h'],
                bar['l'],
                bar['c'],
                bar['v'],
                bar.get('n', 0),
                bar.get('vw', 0.0)
            ])

        self.ch_client.insert(
            "trading_db.market_data",
            data,
            column_names=["timestamp", "symbol", "open", "high", "low",
                         "close", "volume", "trade_count", "vwap"]
        )

        return len(data)

    def ingest_symbols(self, symbols: List[str], start: str, end: str):
        """Ingest data for multiple symbols"""
        total_inserted = 0

        for symbol in symbols:
            print(f"\n[{datetime.now()}] Processing {symbol}...")
            bars = self.fetch_bars(symbol, start, end)
            inserted = self.insert_bars(bars, symbol)
            total_inserted += inserted
            print(f"  ✓ Inserted {inserted} bars for {symbol}")

        print(f"\n[{datetime.now()}] ✓ Total inserted: {total_inserted} bars")
        return total_inserted

    def close(self):
        self.ch_client.close()


def main():
    """Main ingestion routine"""
    ingester = AlpacaDataIngester()

    symbols_str = os.getenv('DATA_SYMBOLS', 'AAPL,MSFT,GOOGL,TSLA,NVDA')
    symbols = [s.strip() for s in symbols_str.split(',')]
    lookback_days = int(os.getenv('DATA_LOOKBACK_DAYS', 7))

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=lookback_days)

    start_iso = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_iso = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"Starting ingestion: {start_iso} to {end_iso}")
    ingester.ingest_symbols(symbols, start_iso, end_iso)
    ingester.close()


if __name__ == "__main__":
    main()
