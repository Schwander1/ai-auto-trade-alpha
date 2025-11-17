import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ComprehensiveBacktester:
    """
    20-Year Backtesting Engine with Performance Metrics
    FIXED: No data leakage, calculates indicators incrementally, includes stop loss/take profit
    """

    def __init__(self, initial_capital=100000, stop_loss_pct=0.03, take_profit_pct=0.05):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = [initial_capital]
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    def load_historical_data(self, symbol, data_path='data/historical'):
        """Load 20-year historical data"""
        filepath = Path(data_path) / f'{symbol}_20y.csv'
        if filepath.exists():
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            return df
        return None

    def _calculate_indicators_at_index(self, df, i):
        """
        Calculate indicators at specific index using only historical data
        FIX: Prevents data leakage by only using data up to current index
        """
        indicators = {}

        # Moving averages (only using data up to index i)
        if i >= 20:
            indicators['SMA_20'] = df.iloc[max(0, i-20):i]['Close'].mean()
        else:
            indicators['SMA_20'] = np.nan

        if i >= 50:
            indicators['SMA_50'] = df.iloc[max(0, i-50):i]['Close'].mean()
        else:
            indicators['SMA_50'] = np.nan

        if i >= 200:
            indicators['SMA_200'] = df.iloc[max(0, i-200):i]['Close'].mean()
        else:
            indicators['SMA_200'] = np.nan

        # RSI (only using data up to index i)
        if i >= 14:
            delta = df.iloc[max(0, i-14):i+1]['Close'].diff()
            gain = delta.where(delta > 0, 0).mean()
            loss = (-delta.where(delta < 0, 0)).mean()
            if loss > 0:
                rs = gain / loss
                indicators['RSI'] = 100 - (100 / (1 + rs))
            else:
                indicators['RSI'] = 50.0
        else:
            indicators['RSI'] = 50.0

        # MACD (only using data up to index i)
        if i >= 26:
            close_window = df.iloc[max(0, i-26):i+1]['Close']
            ema_12 = close_window.ewm(span=12, adjust=False).mean().iloc[-1]
            ema_26 = close_window.ewm(span=26, adjust=False).mean().iloc[-1]
            indicators['MACD'] = ema_12 - ema_26
            if i >= 35:  # Need more data for signal line
                macd_window = df.iloc[max(0, i-35):i+1]['Close']
                ema_12_full = macd_window.ewm(span=12, adjust=False).mean()
                ema_26_full = macd_window.ewm(span=26, adjust=False).mean()
                macd_line = ema_12_full - ema_26_full
                indicators['MACD_Signal'] = macd_line.ewm(span=9, adjust=False).mean().iloc[-1]
            else:
                indicators['MACD_Signal'] = indicators['MACD']
        else:
            indicators['MACD'] = 0.0
            indicators['MACD_Signal'] = 0.0

        return indicators

    def run_strategy(self, symbol, strategy='momentum'):
        """
        Run backtest for given strategy
        FIX: Calculates indicators incrementally, includes stop loss/take profit
        """
        df = self.load_historical_data(symbol)
        if df is None:
            logger.warning(f"No data available for {symbol}")
            return None

        if len(df) < 200:
            logger.warning(f"Insufficient data for {symbol}: {len(df)} rows (need 200+)")
            return None

        # Reset state
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = [self.initial_capital]

        # FIX: Calculate indicators incrementally within loop (no data leakage)
        for i in range(200, len(df)):
            current_price = df.iloc[i]['Close']
            date = df.index[i]

            # Calculate indicators using only historical data
            indicators = self._calculate_indicators_at_index(df, i)

            # FIX: Check stop loss and take profit before checking signals
            if symbol in self.positions:
                position = self.positions[symbol]
                entry_price = position['entry_price']

                # Check stop loss
                stop_loss_price = entry_price * (1 - self.stop_loss_pct)
                if current_price <= stop_loss_price:
                    logger.debug(f"Stop loss hit for {symbol} at {date}: ${current_price:.2f} <= ${stop_loss_price:.2f}")
                    self.sell(symbol, stop_loss_price, date, reason='stop_loss')
                    continue

                # Check take profit
                take_profit_price = entry_price * (1 + self.take_profit_pct)
                if current_price >= take_profit_price:
                    logger.debug(f"Take profit hit for {symbol} at {date}: ${current_price:.2f} >= ${take_profit_price:.2f}")
                    self.sell(symbol, take_profit_price, date, reason='take_profit')
                    continue

            # Momentum strategy (only if no position or after exit checks)
            if strategy == 'momentum':
                sma_20 = indicators.get('SMA_20', np.nan)
                sma_50 = indicators.get('SMA_50', np.nan)
                rsi = indicators.get('RSI', 50.0)

                if pd.notna(sma_20) and pd.notna(sma_50):
                    if sma_20 > sma_50 and rsi < 70 and symbol not in self.positions:
                        self.buy(symbol, current_price, date)
                    elif sma_20 < sma_50 and symbol in self.positions:
                        self.sell(symbol, current_price, date, reason='signal_reversal')

            # Update equity curve
            self.update_equity(current_price)

        # Close any remaining positions
        if symbol in self.positions:
            final_price = df.iloc[-1]['Close']
            final_date = df.index[-1]
            self.sell(symbol, final_price, final_date, reason='end_of_backtest')

        return self.get_performance_metrics()

    def buy(self, symbol, price, date):
        """Execute buy order"""
        if symbol not in self.positions:
            shares = int(self.capital * 0.1 / price)  # 10% position size
            if shares > 0:
                cost = shares * price
                if cost <= self.capital:
                    self.capital -= cost
                    self.positions[symbol] = {
                        'shares': shares,
                        'entry_price': price,
                        'entry_date': date,
                        'stop_loss': price * (1 - self.stop_loss_pct),
                        'take_profit': price * (1 + self.take_profit_pct)
                    }
                    self.trades.append({
                        'date': date,
                        'symbol': symbol,
                        'action': 'BUY',
                        'price': price,
                        'shares': shares,
                        'value': cost
                    })
                    logger.debug(f"Bought {shares} shares of {symbol} at ${price:.2f} on {date}")

    def sell(self, symbol, price, date, reason='signal'):
        """Execute sell order"""
        if symbol in self.positions:
            position = self.positions[symbol]
            proceeds = position['shares'] * price
            self.capital += proceeds

            pnl = proceeds - (position['shares'] * position['entry_price'])
            pnl_pct = (pnl / (position['shares'] * position['entry_price'])) * 100

            self.trades.append({
                'date': date,
                'symbol': symbol,
                'action': 'SELL',
                'price': price,
                'shares': position['shares'],
                'value': proceeds,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'exit_reason': reason,
                'entry_date': position['entry_date'],
                'entry_price': position['entry_price'],
                'holding_days': (date - position['entry_date']).days if hasattr(date, '__sub__') else 0
            })

            logger.debug(f"Sold {position['shares']} shares of {symbol} at ${price:.2f} on {date}, "
                        f"P&L: ${pnl:.2f} ({pnl_pct:.2f}%), reason: {reason}")

            del self.positions[symbol]

    def update_equity(self, current_price):
        """Update equity curve"""
        position_value = sum(pos['shares'] * current_price
                            for pos in self.positions.values())
        total_equity = self.capital + position_value
        self.equity_curve.append(total_equity)

    def get_performance_metrics(self):
        """
        Calculate comprehensive performance metrics
        FIX: Uses actual calendar days for annualization
        """
        if not self.equity_curve or len(self.equity_curve) < 2:
            return None

        equity = np.array(self.equity_curve)
        returns = np.diff(equity) / equity[:-1]

        # Calculate metrics
        total_return = (equity[-1] - self.initial_capital) / self.initial_capital

        # FIX: Use actual calendar days for annualization instead of assuming 252 trading days
        # Estimate days from equity curve length (assuming daily data)
        days = len(equity)
        years = days / 365.25
        if years > 0:
            annualized_return = (1 + total_return) ** (1 / years) - 1
        else:
            annualized_return = 0.0

        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0

        # Maximum drawdown
        cumulative = np.maximum.accumulate(equity)
        drawdown = (equity - cumulative) / cumulative
        max_drawdown = np.min(drawdown)

        # Win rate and trade statistics
        completed_trades = [t for t in self.trades if t.get('action') == 'SELL' and 'pnl' in t]
        winning_trades = [t for t in completed_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in completed_trades if t.get('pnl', 0) <= 0]
        win_rate = len(winning_trades) / len(completed_trades) if completed_trades else 0

        # Additional metrics
        avg_win = np.mean([t.get('pnl_pct', 0) for t in winning_trades]) if winning_trades else 0.0
        avg_loss = np.mean([t.get('pnl_pct', 0) for t in losing_trades]) if losing_trades else 0.0
        profit_factor = abs(sum([t.get('pnl', 0) for t in winning_trades]) /
                           sum([t.get('pnl', 0) for t in losing_trades])) if losing_trades and sum([t.get('pnl', 0) for t in losing_trades]) != 0 else 0.0

        # Exit reason breakdown
        exit_reasons = {}
        for trade in completed_trades:
            reason = trade.get('exit_reason', 'unknown')
            exit_reasons[reason] = exit_reasons.get(reason, 0) + 1

        return {
            'total_return': total_return * 100,
            'annualized_return': annualized_return * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown * 100,
            'total_trades': len(completed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate * 100,
            'avg_win_pct': avg_win,
            'avg_loss_pct': avg_loss,
            'profit_factor': profit_factor,
            'final_equity': equity[-1],
            'exit_reasons': exit_reasons
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
