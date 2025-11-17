#!/usr/bin/env python3
"""
Quick investigation: Run a mini backtest with enhanced logging to see what's happening
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.backtest.strategy_backtester import StrategyBacktester
from argo.backtest.data_manager import DataManager

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable DEBUG for enhancement logging
logging.getLogger('argo.backtest.performance_enhancer').setLevel(logging.DEBUG)
logging.getLogger('argo.backtest.strategy_backtester').setLevel(logging.DEBUG)

print("="*80)
print("QUICK INVESTIGATION: Single Symbol Backtest with Enhanced Logging")
print("="*80)
print()

# Initialize
backtester = StrategyBacktester(
    initial_capital=100000.0,
    min_holding_bars=5
)

# Run a short backtest on one symbol
print("Running backtest on AAPL...")
print("This will test the enhancement pipeline with detailed logging.")
print()

import asyncio
result = asyncio.run(backtester.run_backtest(
    symbol="AAPL",
    start_date=None,
    end_date=None,
    min_confidence=55.0,
    use_precalculated=True,
    use_parallel=False
))

if result:
    print("\n" + "="*80)
    print("RESULTS:")
    print("="*80)
    print(f"Win Rate: {result.win_rate:.2f}%")
    print(f"Total Return: {result.total_return:.2f}%")
    print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print(f"Total Trades: {result.total_trades}")
    print(f"Max Drawdown: {result.max_drawdown:.2f}%")
else:
    print("❌ Backtest returned None")

print("\n" + "="*80)
print("Check the logs above for [ENHANCEMENT] messages")
print("="*80)

