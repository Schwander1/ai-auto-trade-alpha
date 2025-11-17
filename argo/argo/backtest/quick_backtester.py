"""Robust Backtesting - 5 Year Validation
FIXED: Removed look-ahead bias, calculate actual max drawdown
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import hashlib
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    symbol: str
    win_rate: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    total_trades: int
    winning_trades: int

class QuickBacktester:
    """
    Simple momentum backtester
    FIXED: No look-ahead bias, calculates actual metrics
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
    
    def run(self, symbol: str, years: int = 5):
        """
        Simple momentum backtest - FIXED VERSION
        No look-ahead bias, calculates actual max drawdown
        """
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            end = datetime.now()
            start = end - timedelta(days=years*365)
            df = ticker.history(start=start, end=end)
            
            if df.empty or len(df) < 100:
                logger.warning(f"Insufficient data for {symbol}: {len(df)} rows")
                return None
            
            # FIX: Calculate indicators incrementally to prevent look-ahead bias
            df["returns"] = df["Close"].pct_change()
            df["signal"] = 0
            df["mom"] = np.nan
            
            # Calculate momentum incrementally (only using past data)
            for i in range(20, len(df)):
                # Only use data up to current bar
                df.loc[df.index[i], "mom"] = df.iloc[i-20:i]["returns"].mean()
                
                if pd.notna(df.loc[df.index[i], "mom"]):
                    if df.loc[df.index[i], "mom"] > 0.001:
                        df.loc[df.index[i], "signal"] = 1
                    elif df.loc[df.index[i], "mom"] < -0.001:
                        df.loc[df.index[i], "signal"] = -1
            
            # Simulate trades with equity curve tracking
            trades = []
            position = 0
            entry = 0
            entry_price = 0.0
            capital = self.initial_capital
            equity_curve = [capital]
            
            for i in range(20, len(df)):  # Start after warmup period
                current_price = df.iloc[i]["Close"]
                
                # Update equity curve
                if position == 1:
                    # In position: equity = capital + position value
                    position_value = (capital / entry_price) * current_price
                    equity = capital + (position_value - capital)
                else:
                    equity = capital
                
                equity_curve.append(equity)
                
                # Check signals
                if df.iloc[i]["signal"] == 1 and position == 0:
                    position = 1
                    entry_price = current_price
                    entry = i
                elif df.iloc[i]["signal"] == -1 and position == 1:
                    exit_price = current_price
                    profit_pct = (exit_price - entry_price) / entry_price
                    
                    # Update capital
                    position_value = (capital / entry_price) * exit_price
                    capital = position_value
                    
                    trades.append({
                        "profit": profit_pct,
                        "win": profit_pct > 0,
                        "entry_price": entry_price,
                        "exit_price": exit_price
                    })
                    position = 0
            
            # Close any remaining position
            if position == 1:
                exit_price = df.iloc[-1]["Close"]
                profit_pct = (exit_price - entry_price) / entry_price
                position_value = (capital / entry_price) * exit_price
                capital = position_value
                trades.append({
                    "profit": profit_pct,
                    "win": profit_pct > 0,
                    "entry_price": entry_price,
                    "exit_price": exit_price
                })
                equity_curve[-1] = capital
            
            if not trades:
                logger.warning(f"No trades executed for {symbol}")
                return None
            
            # FIX: Calculate actual max drawdown from equity curve
            equity_array = np.array(equity_curve)
            cumulative_max = np.maximum.accumulate(equity_array)
            drawdown = (equity_array - cumulative_max) / cumulative_max
            max_drawdown = np.min(drawdown) * 100  # Convert to percentage
            
            # Calculate metrics
            wins = [t for t in trades if t["win"]]
            win_rate = (len(wins) / len(trades)) * 100 if trades else 0.0
            
            # Total return from equity curve
            total_return = ((equity_array[-1] - equity_array[0]) / equity_array[0]) * 100
            
            # Sharpe ratio from trade returns
            returns = pd.Series([t["profit"] for t in trades])
            sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0.0
            
            result = BacktestResult(
                symbol=symbol,
                win_rate=win_rate,
                total_return=total_return,
                sharpe_ratio=sharpe,
                max_drawdown=max_drawdown,  # FIX: Actual calculated value
                total_trades=len(trades),
                winning_trades=len(wins)
            )
            
            logger.info(f"Backtest complete for {symbol}: {len(trades)} trades, "
                       f"{win_rate:.1f}% win rate, {total_return:.1f}% return, "
                       f"{max_drawdown:.1f}% max drawdown")
            
            return result
        except Exception as e:
            logger.error(f"Backtest error for {symbol}: {e}", exc_info=True)
            return None

backtester = QuickBacktester()
