#!/usr/bin/env python3
"""
Local Backtesting Runner
Runs comprehensive backtests locally before production
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.backtest.strategy_backtester import StrategyBacktester
from argo.backtest.profit_backtester import ProfitBacktester
from argo.backtest.results_storage import ResultsStorage
from argo.backtest.data_manager import DataManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_local_backtests():
    """Run comprehensive local backtests"""
    
    print('\n' + '='*70)
    print('🧪 LOCAL BACKTESTING SUITE')
    print('='*70)
    
    # Test symbols
    symbols = ["AAPL", "NVDA", "BTC-USD", "ETH-USD"]
    
    # Initialize components
    strategy_backtester = StrategyBacktester()
    profit_backtester = ProfitBacktester()
    results_storage = ResultsStorage()
    data_manager = DataManager()
    
    print(f'\n📊 Testing {len(symbols)} symbols...')
    
    all_results = []
    
    for symbol in symbols:
        print(f'\n📈 Testing {symbol}...')
        
        # Strategy backtest (signal quality)
        print(f'   Running strategy backtest...')
        strategy_metrics = await strategy_backtester.run_backtest(symbol)
        
        if strategy_metrics:
            print(f'   ✅ Strategy Backtest Results:')
            print(f'      Win Rate: {strategy_metrics.win_rate_pct:.2f}%')
            print(f'      Total Return: {strategy_metrics.total_return_pct:.2f}%')
            print(f'      Sharpe Ratio: {strategy_metrics.sharpe_ratio:.2f}')
            
            # Save results
            backtest_id = f"strategy_{symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            results_storage.save_results(
                backtest_id, symbol, strategy_metrics, strategy_type="strategy"
            )
        
        # Profit backtest (trading profitability)
        print(f'   Running profit backtest...')
        profit_metrics = await profit_backtester.run_backtest(symbol)
        
        if profit_metrics:
            print(f'   ✅ Profit Backtest Results:')
            print(f'      Total Return: {profit_metrics.total_return_pct:.2f}%')
            print(f'      Sharpe Ratio: {profit_metrics.sharpe_ratio:.2f}')
            print(f'      Max Drawdown: {profit_metrics.max_drawdown_pct:.2f}%')
            
            # Save results
            backtest_id = f"profit_{symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            results_storage.save_results(
                backtest_id, symbol, profit_metrics, strategy_type="profit"
            )
        
        all_results.append({
            'symbol': symbol,
            'strategy': strategy_metrics,
            'profit': profit_metrics
        })
    
    # Summary
    print('\n' + '='*70)
    print('📊 BACKTEST SUMMARY')
    print('='*70)
    
    for result in all_results:
        print(f'\n{result["symbol"]}:')
        if result['strategy']:
            print(f'   Strategy Win Rate: {result["strategy"].win_rate_pct:.2f}%')
        if result['profit']:
            print(f'   Profit Return: {result["profit"].total_return_pct:.2f}%')
    
    print('\n✅ Backtesting complete!')
    print('='*70 + '\n')
    
    return all_results

if __name__ == '__main__':
    results = asyncio.run(run_local_backtests())
    sys.exit(0)

