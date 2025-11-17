#!/usr/bin/env python3
"""
Test enhancement on a single signal to verify it's working
"""

import sys
import logging
import asyncio
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.backtest.strategy_backtester import StrategyBacktester

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

# Enable DEBUG for enhancement logging
logging.getLogger('argo.backtest.performance_enhancer').setLevel(logging.INFO)
logging.getLogger('argo.backtest.strategy_backtester').setLevel(logging.INFO)

async def main():
    print("="*80)
    print("ENHANCEMENT TEST: Single Symbol Backtest")
    print("="*80)
    print()
    
    backtester = StrategyBacktester(
        initial_capital=100000.0,
        min_holding_bars=5
    )
    
    print("Running backtest on AAPL with enhanced logging...")
    print("Looking for [ENHANCEMENT] messages in the output...")
    print()
    
    result = await backtester.run_backtest(
        symbol="AAPL",
        start_date=None,
        end_date=None,
        min_confidence=55.0
    )
    
    print()
    print("="*80)
    if result:
        print("RESULTS:")
        print("="*80)
        print(f"Win Rate: {result.win_rate:.2f}%")
        print(f"Total Return: {result.total_return:.2f}%")
        print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"Total Trades: {result.total_trades}")
        print(f"Max Drawdown: {result.max_drawdown:.2f}%")
    else:
        print("❌ Backtest returned None")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())

