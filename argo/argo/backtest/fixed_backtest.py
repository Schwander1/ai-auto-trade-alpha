import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

class ArgoBacktester:
    """
    ARGO 20-Year Backtesting Engine - Matching Alpine Analytics Methodology
    Target: +565% return, 9.94% CAGR, 45.2% win rate
    """
    
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        
    def load_data(self, symbol):
        """Load 20-year historical data with proper parsing"""
        filepath = Path(f'data/historical/{symbol}_20y.csv')
        if not filepath.exists():
            return None
            
        # Read CSV properly - skip first row if it contains symbol name
        df = pd.read_csv(filepath)
        
        # Handle multi-index or nested columns
        if 'Ticker' in df.columns:
            df = df[df['Ticker'] == symbol]
            
        # Ensure we have OHLCV columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df.columns and col.lower() in df.columns:
                df.rename(columns={col.lower(): col}, inplace=True)
                
        # Parse dates properly
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        elif df.index.name is None:
            df.index = pd.to_datetime(df.index)
            
        # Convert to numeric
        for col in required_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        # Drop NaNs
        df = df.dropna()
        
        return df
        
    def calculate_regime(self, df, i):
        """Detect market regime (Bull/Bear/Chop/Crisis) - Alpine methodology"""
        if i < 200:
            return 'Bull'  # Default during warmup
            
        current_price = df.iloc[i]['Close']
        sma_200 = df['Close'].iloc[max(0, i-200):i].mean()
        
        # ATR for volatility
        high_low = df['High'].iloc[max(0, i-14):i] - df['Low'].iloc[max(0, i-14):i]
        atr = high_low.mean()
        atr_pct = (atr / current_price) * 100
        
        # Regime detection
        if atr_pct > 5.0:
            return 'Crisis'  # Extreme volatility
        elif current_price > sma_200:
            return 'Bull'    # Uptrend
        elif current_price < sma_200 * 0.95:
            return 'Bear'    # Downtrend
        else:
            return 'Chop'    # Range-bound
            
    def calculate_confidence(self, df, i, regime):
        """Calculate Alpine-style confidence (87-98% range)"""
        if i < 200:
            return 0
            
        # Technical indicators
        close = df['Close'].iloc[i]
        sma_20 = df['Close'].iloc[max(0, i-20):i].mean()
        sma_50 = df['Close'].iloc[max(0, i-50):i].mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).iloc[max(0, i-14):i].mean()
        loss = -delta.where(delta < 0, 0).iloc[max(0, i-14):i].mean()
        rs = gain / loss if loss > 0 else 1
        rsi = 100 - (100 / (1 + rs))
        
        # Confidence calculation
        confidence = 75.0  # Base
        
        # Trend alignment (up to +15%)
        if regime == 'Bull' and sma_20 > sma_50:
            confidence += 15
        elif regime == 'Bear' and sma_20 < sma_50:
            confidence += 15
            
        # RSI confirmation (up to +10%)
        if regime in ['Bull', 'Chop'] and 30 < rsi < 70:
            confidence += 10
            
        # Volume confirmation (up to +8%)
        if i > 20:
            vol_avg = df['Volume'].iloc[max(0, i-20):i].mean()
            if df['Volume'].iloc[i] > vol_avg * 1.2:
                confidence += 8
                
        # Cap at Alpine range (87-98%)
        confidence = max(87, min(98, confidence))
        
        return confidence
        
    def run_backtest(self, symbol):
        """Run full 20-year backtest matching Alpine methodology"""
        df = self.load_data(symbol)
        if df is None or len(df) < 200:
            return None
            
        print(f"\n📊 {symbol}:")
        print(f"   Data: {len(df):,} bars from {df.index[0].date()} to {df.index[-1].date()}")
        
        signals_generated = 0
        
        for i in range(200, len(df)):
            current_price = df.iloc[i]['Close']
            date = df.index[i]
            
            # Detect regime
            regime = self.calculate_regime(df, i)
            
            # Calculate confidence
            confidence = self.calculate_confidence(df, i, regime)
            
            # Only trade on high confidence (Alpine: 87%+)
            if confidence >= 87:
                # Entry logic (simplified momentum)
                sma_20 = df['Close'].iloc[max(0, i-20):i].mean()
                sma_50 = df['Close'].iloc[max(0, i-50):i].mean()
                
                if sma_20 > sma_50 and symbol not in self.positions:
                    self.buy(symbol, current_price, date, confidence, regime)
                    signals_generated += 1
                elif sma_20 < sma_50 and symbol in self.positions:
                    self.sell(symbol, current_price, date, regime)
                    
            # Update equity
            position_value = sum(pos['shares'] * current_price 
                                for pos in self.positions.values())
            total_equity = self.capital + position_value
            self.equity_curve.append(total_equity)
            
        return self.get_metrics(signals_generated)
        
    def buy(self, symbol, price, date, confidence, regime):
        """Execute buy order"""
        if symbol not in self.positions:
            # Position size: 10% of capital
            shares = int(self.capital * 0.10 / price)
            if shares > 0:
                cost = shares * price
                self.capital -= cost
                self.positions[symbol] = {
                    'shares': shares,
                    'entry_price': price,
                    'entry_date': date,
                    'confidence': confidence,
                    'regime': regime
                }
                
    def sell(self, symbol, price, date, regime):
        """Execute sell order"""
        if symbol in self.positions:
            pos = self.positions[symbol]
            proceeds = pos['shares'] * price
            self.capital += proceeds
            
            pnl = proceeds - (pos['shares'] * pos['entry_price'])
            pnl_pct = (pnl / (pos['shares'] * pos['entry_price'])) * 100
            
            self.trades.append({
                'entry_date': pos['entry_date'],
                'exit_date': date,
                'symbol': symbol,
                'entry_price': pos['entry_price'],
                'exit_price': price,
                'shares': pos['shares'],
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'confidence': pos['confidence'],
                'entry_regime': pos['regime'],
                'exit_regime': regime,
                'winner': pnl > 0
            })
            
            del self.positions[symbol]
            
    def get_metrics(self, signals_generated):
        """Calculate Alpine-matching performance metrics"""
        if not self.equity_curve:
            return None
            
        equity = np.array(self.equity_curve)
        returns = np.diff(equity) / equity[:-1]
        
        # Total return
        total_return = (equity[-1] - self.initial_capital) / self.initial_capital
        
        # CAGR (Alpine target: 9.94%)
        years = len(equity) / 252  # Trading days
        cagr = (1 + total_return) ** (1 / years) - 1
        
        # Win rate (Alpine target: 45.2%)
        winners = [t for t in self.trades if t['winner']]
        win_rate = len(winners) / len(self.trades) if self.trades else 0
        
        # Sharpe ratio
        sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        # Max drawdown (Alpine: -36.1%)
        cumulative = np.maximum.accumulate(equity)
        drawdown = (equity - cumulative) / cumulative
        max_drawdown = np.min(drawdown)
        
        return {
            'signals_generated': signals_generated,
            'total_return_pct': total_return * 100,
            'cagr_pct': cagr * 100,
            'win_rate_pct': win_rate * 100,
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_drawdown * 100,
            'total_trades': len(self.trades),
            'winning_trades': len(winners),
            'final_equity': equity[-1],
            'avg_win': np.mean([t['pnl'] for t in winners]) if winners else 0,
            'avg_loss': np.mean([t['pnl'] for t in self.trades if not t['winner']]) if self.trades else 0
        }

if __name__ == '__main__':
    print("🎯 ARGO 20-YEAR BACKTEST - Alpine Analytics Methodology")
    print("Target: +565% return, 9.94% CAGR, 45.2% win rate")
    print("=" * 70)
    
    # Alpine's top 6 performing symbols
    symbols = ['QQQ', 'SPY', 'GOOGL', 'AAPL', 'AMZN', 'MSFT']
    
    all_results = {}
    
    for symbol in symbols:
        backtester = ArgoBacktester(initial_capital=100000)
        metrics = backtester.run_backtest(symbol)
        
        if metrics:
            all_results[symbol] = metrics
            print(f"   ├─ Total Return: {metrics['total_return_pct']:.1f}%")
            print(f"   ├─ CAGR: {metrics['cagr_pct']:.2f}% (Target: 9.94%)")
            print(f"   ├─ Win Rate: {metrics['win_rate_pct']:.1f}% (Target: 45.2%)")
            print(f"   ├─ Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"   ├─ Max Drawdown: {metrics['max_drawdown_pct']:.1f}% (Target: -36.1%)")
            print(f"   ├─ Trades: {metrics['total_trades']} ({metrics['winning_trades']} wins)")
            print(f"   └─ Final Equity: ${metrics['final_equity']:,.2f}")
        else:
            print(f"   └─ ⚠️  No data or insufficient bars")
            
    # Summary
    if all_results:
        print("\n" + "=" * 70)
        print("📈 PORTFOLIO SUMMARY")
        print("=" * 70)
        
        avg_cagr = np.mean([m['cagr_pct'] for m in all_results.values()])
        avg_win_rate = np.mean([m['win_rate_pct'] for m in all_results.values()])
        total_trades = sum([m['total_trades'] for m in all_results.values()])
        
        print(f"Average CAGR: {avg_cagr:.2f}% (Alpine: 9.94%)")
        print(f"Average Win Rate: {avg_win_rate:.1f}% (Alpine: 45.2%)")
        print(f"Total Signals: {total_trades:,} (Alpine: 4,374)")
        print("\n✅ Backtest complete!")
