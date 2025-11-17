#!/usr/bin/env python3
"""
Prop Firm Backtest Suite
Runs comprehensive tests with multiple configurations
"""
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.backtest.prop_firm_backtester import PropFirmBacktester
from argo.scripts.run_prop_firm_backtest import run_prop_firm_backtest, save_results

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def run_test_suite():
    """Run comprehensive test suite"""
    print("\n" + "="*80)
    print("🚀 PROP FIRM BACKTEST SUITE")
    print("="*80)
    
    symbols = ["SPY", "QQQ", "AAPL"]
    
    # Test configurations
    configs = [
        {"name": "Baseline", "confidence": 80.0, "position_size": 10.0, "max_positions": 5},
        {"name": "Conservative", "confidence": 85.0, "position_size": 5.0, "max_positions": 3},
        {"name": "Very Conservative", "confidence": 90.0, "position_size": 5.0, "max_positions": 2},
    ]
    
    all_results = {}
    
    for config in configs:
        print(f"\n{'='*80}")
        print(f"📊 Testing Configuration: {config['name']}")
        print(f"   Confidence: {config['confidence']}%")
        print(f"   Position Size: {config['position_size']}%")
        print(f"   Max Positions: {config['max_positions']}")
        print(f"{'='*80}\n")
        
        config_results = {}
        
        for symbol in symbols:
            print(f"Testing {symbol}...")
            
            # Create custom backtester
            backtester = PropFirmBacktester(
                initial_capital=25000.0,
                min_confidence=config['confidence'],
                max_position_size_pct=config['position_size'],
                max_positions=config['max_positions']
            )
            
            metrics = await backtester.run_backtest(symbol)
            
            if metrics:
                report = backtester.get_prop_firm_report()
                
                config_results[symbol] = {
                    'metrics': {
                        'total_return_pct': metrics.total_return_pct,
                        'win_rate_pct': metrics.win_rate_pct,
                        'sharpe_ratio': metrics.sharpe_ratio,
                        'max_drawdown_pct': metrics.max_drawdown_pct,
                        'total_trades': metrics.total_trades,
                    },
                    'prop_firm_metrics': report,
                    'compliant': report['drawdown_compliant'] and report['daily_loss_compliant']
                }
                
                status = "✅" if config_results[symbol]['compliant'] else "❌"
                print(f"   {status} {symbol}: Return={metrics.total_return_pct:+.2f}%, "
                      f"Win Rate={metrics.win_rate_pct:.2f}%, Trades={metrics.total_trades}")
            else:
                print(f"   ❌ {symbol}: Failed")
                config_results[symbol] = None
        
        all_results[config['name']] = config_results
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUITE SUMMARY")
    print("="*80)
    
    for config_name, results in all_results.items():
        compliant = sum(1 for r in results.values() if r and r.get('compliant', False))
        total = len([r for r in results.values() if r is not None])
        
        print(f"\n{config_name}:")
        print(f"   Compliant: {compliant}/{total}")
        
        for symbol, result in results.items():
            if result:
                status = "✅" if result['compliant'] else "❌"
                metrics = result['metrics']
                print(f"   {status} {symbol}: {metrics['total_return_pct']:+.2f}% return, "
                      f"{metrics['win_rate_pct']:.2f}% win rate, {metrics['total_trades']} trades")
    
    # Save results
    output_file = f"argo/reports/prop_firm_suite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_results({
        'configurations': configs,
        'results': all_results,
        'timestamp': datetime.now().isoformat()
    }, output_file)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("\n" + "="*80)
    
    return all_results


if __name__ == "__main__":
    asyncio.run(run_test_suite())

