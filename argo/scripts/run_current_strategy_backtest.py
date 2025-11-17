#!/usr/bin/env python3
"""
Current Strategy Backtest with Comparison
Tests Argo's most up-to-date strategy and compares with previous results
"""
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.backtest.strategy_backtester import StrategyBacktester
from argo.backtest.data_manager import DataManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Symbols to test (matching previous backtest)
SYMBOLS = [
    "AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "META", "AMD", "AMZN",
    "SPY", "QQQ",
    "BTC-USD", "ETH-USD"
]

async def run_current_strategy_backtest():
    """Run backtest with current strategy configuration"""
    
    print('\n' + '='*70)
    print('🚀 CURRENT STRATEGY BACKTEST')
    print('='*70)
    print(f'Testing {len(SYMBOLS)} symbols with current Argo strategy...')
    print('='*70 + '\n')
    
    # Initialize backtester (uses current config.json settings)
    backtester = StrategyBacktester(initial_capital=100000)
    
    results = []
    
    for i, symbol in enumerate(SYMBOLS, 1):
        print(f'\n[{i}/{len(SYMBOLS)}] 📊 Testing {symbol}...')
        
        try:
            # Run backtest with current strategy (min_confidence=55% for more signals)
            metrics = await backtester.run_backtest(
                symbol=symbol,
                min_confidence=55.0  # Lower threshold to generate more signals
            )
            
            if metrics and metrics.total_trades > 0:
                result = {
                    'symbol': symbol,
                    'config': 'current_strategy',
                    'method': 'standard',
                    'win_rate': float(metrics.win_rate_pct) if metrics.win_rate_pct else 0.0,
                    'total_return': float(metrics.total_return_pct) if metrics.total_return_pct else 0.0,
                    'sharpe_ratio': float(metrics.sharpe_ratio) if metrics.sharpe_ratio else 0.0,
                    'max_drawdown': float(metrics.max_drawdown_pct) if metrics.max_drawdown_pct else 0.0,
                    'total_trades': int(metrics.total_trades) if metrics.total_trades else 0,
                    'profit_factor': float(metrics.profit_factor) if metrics.profit_factor else 0.0,
                    'annualized_return': float(metrics.annualized_return_pct) if metrics.annualized_return_pct else 0.0
                }
                
                print(f'   ✅ Win Rate: {result["win_rate"]:.2f}%')
                print(f'   ✅ Total Return: {result["total_return"]:.2f}%')
                print(f'   ✅ Sharpe Ratio: {result["sharpe_ratio"]:.2f}')
                print(f'   ✅ Max Drawdown: {result["max_drawdown"]:.2f}%')
                print(f'   ✅ Total Trades: {result["total_trades"]}')
                
                results.append(result)
            else:
                print(f'   ⚠️  No trades generated or backtest failed')
                results.append({
                    'symbol': symbol,
                    'config': 'current_strategy',
                    'error': 'No trades generated' if metrics else 'Backtest failed'
                })
                
        except Exception as e:
            logger.error(f"Error backtesting {symbol}: {e}", exc_info=True)
            results.append({
                'symbol': symbol,
                'config': 'current_strategy',
                'error': str(e)
            })
    
    # Save results
    output_file = Path(__file__).parent.parent / "reports" / "current_strategy_backtest_results.json"
    output_file.parent.mkdir(exist_ok=True)
    
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'strategy_version': 'current',
        'results': results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f'\n✅ Results saved to: {output_file}')
    
    return results

if __name__ == '__main__':
    results = asyncio.run(run_current_strategy_backtest())
    print('\n✅ Backtest complete!\n')

