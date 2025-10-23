#!/usr/bin/env python3
"""
Enhanced Mock Data Generator
Generates realistic market data with trends, volatility, and sector personalities
"""
import os
import clickhouse_connect
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

load_dotenv()

class EnhancedMockDataGenerator:
    def __init__(self):
        self.ch_client = clickhouse_connect.get_client(
            host=os.getenv('CLICKHOUSE_HOST', 'localhost'),
            port=int(os.getenv('CLICKHOUSE_PORT', 8123)),
            username=os.getenv('CLICKHOUSE_USER', 'default'),
            password=os.getenv('CLICKHOUSE_PASSWORD', 'password123')
        )

        # Symbol personalities
        self.symbol_config = {
            'AAPL': {'base_price': 180, 'volatility': 0.015, 'trend_bias': 0.0002},
            'MSFT': {'base_price': 380, 'volatility': 0.018, 'trend_bias': 0.0003},
            'GOOGL': {'base_price': 140, 'volatility': 0.020, 'trend_bias': 0.0001},
            'TSLA': {'base_price': 250, 'volatility': 0.035, 'trend_bias': -0.0001},
            'NVDA': {'base_price': 500, 'volatility': 0.025, 'trend_bias': 0.0005}
        }

    def generate_realistic_bars(self, symbol: str, days: int = 60) -> list:
        """Generate realistic OHLCV bars with trends and volatility"""
        config = self.symbol_config[symbol]
        bars = []

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)

        current_date = start_time.date()
        end_date = end_time.date()

        # Initialize price
        base_price = config['base_price']
        trend = random.choice(['up', 'down', 'sideways'])
        trend_duration = random.randint(3, 10)
        trend_counter = 0

        while current_date <= end_date:
            if current_date.weekday() < 5:  # Trading days only

                # Change trend periodically
                if trend_counter >= trend_duration:
                    trend = random.choice(['up', 'down', 'sideways'])
                    trend_duration = random.randint(3, 10)
                    trend_counter = 0

                trend_counter += 1

                # Apply trend to base price
                if trend == 'up':
                    base_price *= (1 + config['trend_bias'] * 10)
                elif trend == 'down':
                    base_price *= (1 - config['trend_bias'] * 10)

                # Generate 8 hourly bars per day
                for hour in range(13, 21):
                    current_time = datetime.combine(current_date, datetime.min.time()).replace(hour=hour)

                    # Intraday volatility
                    volatility_factor = config['volatility'] * random.uniform(0.5, 2.0)

                    # OHLC generation
                    open_price = base_price * (1 + random.uniform(-volatility_factor, volatility_factor))
                    high_price = open_price * (1 + random.uniform(0, volatility_factor * 1.5))
                    low_price = open_price * (1 - random.uniform(0, volatility_factor * 1.5))
                    close_price = low_price + (high_price - low_price) * random.uniform(0.3, 0.7)

                    # Volume correlation with price movement
                    price_change = abs(close_price - open_price)
                    volume = int(300000 + (price_change * random.uniform(50000, 150000)))

                    bars.append({
                        't': current_time.isoformat() + 'Z',
                        'o': round(open_price, 2),
                        'h': round(high_price, 2),
                        'l': round(low_price, 2),
                        'c': round(close_price, 2),
                        'v': volume,
                        'n': random.randint(500, 2000),
                        'vw': round((open_price + close_price) / 2, 2)
                    })

                    # Update base for next bar
                    base_price = close_price

            current_date += timedelta(days=1)

        return bars

    def insert_bars(self, bars: list, symbol: str) -> int:
        """Insert bars into ClickHouse"""
        if not bars:
            return 0

        data = [[b['t'], symbol, b['o'], b['h'], b['l'], b['c'], b['v'], b['n'], b['vw']] for b in bars]

        self.ch_client.insert(
            'trading_db.market_data',
            data,
            column_names=['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']
        )

        return len(data)

    def generate_all(self, days: int = 60):
        """Generate data for all symbols"""
        total_inserted = 0

        for symbol in self.symbol_config.keys():
            print(f"[{datetime.now()}] Generating {days}-day data for {symbol}...")
            bars = self.generate_realistic_bars(symbol, days)
            inserted = self.insert_bars(bars, symbol)
            total_inserted += inserted
            print(f"  ✓ Inserted {inserted} bars for {symbol}")

        print(f"\n✓ Total inserted: {total_inserted} bars")
        print(f"✓ Average per symbol: {total_inserted // len(self.symbol_config)}")

        return total_inserted

    def close(self):
        self.ch_client.close()


def main():
    generator = EnhancedMockDataGenerator()

    # Generate 60 days of data (~2000 bars per symbol)
    generator.generate_all(days=60)

    generator.close()


if __name__ == "__main__":
    main()
