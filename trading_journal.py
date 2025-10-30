#!/usr/bin/env python3
"""
ARGO Capital Professional Trading Journal
Automated trade logging and performance analysis
"""

import json
import redis
from datetime import datetime
import csv
import os

class ArgoTradingJournal:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.journal_file = 'logs/trading_journal.csv'
        self.ensure_journal_exists()
    
    def ensure_journal_exists(self):
        """Create journal CSV if it doesn't exist"""
        if not os.path.exists(self.journal_file):
            with open(self.journal_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Date', 'Time', 'Symbol', 'Action', 'Shares', 'Price',
                    'Value', 'Confidence', 'Strategy', 'Portfolio_Balance',
                    'Notes'
                ])
    
    def log_trade_entry(self, symbol, action, shares, price, confidence, strategy='ML_Signal'):
        """Log a trade entry to the journal"""
        try:
            # Get current portfolio balance
            balance = self.redis_client.hget('portfolio:current', 'balance') or '0'
            
            # Calculate trade value
            value = float(shares) * float(price)
            
            # Create trade entry
            trade_entry = [
                datetime.now().strftime('%Y-%m-%d'),
                datetime.now().strftime('%H:%M:%S'),
                symbol,
                action,
                shares,
                f'{float(price):.2f}',
                f'{value:.2f}',
                f'{float(confidence):.1%}',
                strategy,
                f'{float(balance):.2f}',
                f'{action} signal executed - {confidence:.1%} confidence'
            ]
            
            # Write to CSV
            with open(self.journal_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(trade_entry)
            
            print(f"📝 Trade logged: {symbol} {action} {shares} @ ${price:.2f}")
            
        except Exception as e:
            print(f"❌ Journal logging error: {e}")
    
    def generate_daily_summary(self):
        """Generate daily trading summary"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📊 ARGO CAPITAL TRADING JOURNAL - {today}")
        print("=" * 50)
        
        if not os.path.exists(self.journal_file):
            print("📝 No trading journal found")
            return
        
        # Read today's trades
        todays_trades = []
        with open(self.journal_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Date'] == today:
                    todays_trades.append(row)
        
        if not todays_trades:
            print("📝 No trades executed today")
            return
        
        # Summary statistics
        total_trades = len(todays_trades)
        buy_trades = sum(1 for t in todays_trades if t['Action'] == 'BUY')
        sell_trades = sum(1 for t in todays_trades if t['Action'] == 'SELL')
        total_value = sum(float(t['Value']) for t in todays_trades)
        avg_confidence = sum(float(t['Confidence'].strip('%')) for t in todays_trades) / total_trades
        
        print(f"📈 Daily Trading Summary:")
        print(f"   Total Trades: {total_trades}")
        print(f"   Buy Orders: {buy_trades}")
        print(f"   Sell Orders: {sell_trades}")
        print(f"   Total Value: ${total_value:,.2f}")
        print(f"   Avg Confidence: {avg_confidence:.1f}%")
        
        print(f"\n📋 Trade Details:")
        for trade in todays_trades:
            print(f"   {trade['Time']} | {trade['Symbol']} {trade['Action']} "
                  f"{trade['Shares']} @ ${trade['Price']} ({trade['Confidence']})")
        
        print(f"\n✅ Trading Journal Summary Complete")

if __name__ == '__main__':
    journal = ArgoTradingJournal()
    journal.generate_daily_summary()
