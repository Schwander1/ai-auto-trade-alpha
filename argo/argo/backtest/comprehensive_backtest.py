import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path

class ComprehensiveBacktester:
    """
    20-Year Backtesting Engine with Performance Metrics
    """
    
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        
    def load_historical_data(self, symbol, data_path='data/historical'):
        """Load 20-year historical data"""
        filepath = Path(data_path) / f'{symbol}_20y.csv'
        if filepath.exists():
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            return df
        return None
        
    def calculate_indicators(self, df):
        """Calculate technical indicators"""
        # Moving averages
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['SMA_200'] = df['Close'].rolling(200).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        
        return df
        
    def run_strategy(self, symbol, strategy='momentum'):
        """Run backtest for given strategy"""
        df = self.load_historical_data(symbol)
        if df is None:
            return None
            
        df = self.calculate_indicators(df)
        
        for i in range(200, len(df)):
            current_price = df.iloc[i]['Close']
            date = df.index[i]
            
            # Momentum strategy
            if strategy == 'momentum':
                if (df.iloc[i]['SMA_20'] > df.iloc[i]['SMA_50'] and 
                    df.iloc[i]['RSI'] < 70):
                    self.buy(symbol, current_price, date)
                elif (df.iloc[i]['SMA_20'] < df.iloc[i]['SMA_50'] and 
                      symbol in self.positions):
                    self.sell(symbol, current_price, date)
                    
            # Update equity curve
            self.update_equity(current_price)
            
        return self.get_performance_metrics()
        
    def buy(self, symbol, price, date):
        """Execute buy order"""
        if symbol not in self.positions:
            shares = int(self.capital * 0.1 / price)  # 10% position size
            if shares > 0:
                cost = shares * price
                self.capital -= cost
                self.positions[symbol] = {'shares': shares, 'entry_price': price, 'entry_date': date}
                self.trades.append({
                    'date': date,
                    'symbol': symbol,
                    'action': 'BUY',
                    'price': price,
                    'shares': shares,
                    'value': cost
                })
                
    def sell(self, symbol, price, date):
        """Execute sell order"""
        if symbol in self.positions:
            position = self.positions[symbol]
            proceeds = position['shares'] * price
            self.capital += proceeds
            
            pnl = proceeds - (position['shares'] * position['entry_price'])
            
            self.trades.append({
                'date': date,
                'symbol': symbol,
                'action': 'SELL',
                'price': price,
                'shares': position['shares'],
                'value': proceeds,
                'pnl': pnl
            })
            
            del self.positions[symbol]
            
    def update_equity(self, current_price):
        """Update equity curve"""
        position_value = sum(pos['shares'] * current_price 
                            for pos in self.positions.values())
        total_equity = self.capital + position_value
        self.equity_curve.append(total_equity)
        
    def get_performance_metrics(self):
        """Calculate comprehensive performance metrics"""
        equity = np.array(self.equity_curve)
        returns = np.diff(equity) / equity[:-1]
        
        # Calculate metrics
        total_return = (equity[-1] - self.initial_capital) / self.initial_capital
        annualized_return = (1 + total_return) ** (252 / len(equity)) - 1
        
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        # Maximum drawdown
        cumulative = np.maximum.accumulate(equity)
        drawdown = (equity - cumulative) / cumulative
        max_drawdown = np.min(drawdown)
        
        # Win rate
        winning_trades = [t for t in self.trades if t.get('pnl', 0) > 0]
        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0
        
        return {
            'total_return': total_return * 100,
            'annualized_return': annualized_return * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown * 100,
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'win_rate': win_rate * 100,
            'final_equity': equity[-1]
        }

if __name__ == '__main__':
    print("🎯 ARGO 20-Year Backtesting Engine")
    print("=" * 50)
    
    backtester = ComprehensiveBacktester(initial_capital=100000)
    
    symbols = ['AAPL', 'NVDA', 'TSLA', 'MSFT', 'SPY', 'QQQ']
    
    for symbol in symbols:
        print(f"\n📊 {symbol}:")
        metrics = backtester.run_strategy(symbol, 'momentum')
        
        if metrics:
            print(f"  Total Return: {metrics['total_return']:.2f}%")
            print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")
            print(f"  Win Rate: {metrics['win_rate']:.2f}%")
            print(f"  Total Trades: {metrics['total_trades']}")
        else:
            print(f"  ⚠️  No data available")
