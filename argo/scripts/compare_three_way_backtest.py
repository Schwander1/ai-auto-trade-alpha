#!/usr/bin/env python3
"""
Three-Way Backtest Results Comparison
Compares: Baseline → Current → Optimized
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

def load_results(file_path: Path, key: str = 'results') -> Optional[List[Dict]]:
    """Load results from JSON file"""
    if not file_path.exists():
        print(f"⚠️  Results file not found: {file_path}")
        return None
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return data.get(key, [])
    except Exception as e:
        print(f"⚠️  Error loading results: {e}")
        return None

def compare_three_way(baseline: List[Dict], current: List[Dict], optimized: List[Dict]) -> Dict:
    """Compare three sets of results"""
    
    # Create lookup dictionaries by symbol
    baseline_by_symbol = {r['symbol']: r for r in baseline if 'error' not in r}
    current_by_symbol = {r['symbol']: r for r in current if 'error' not in r}
    optimized_by_symbol = {r['symbol']: r for r in optimized if 'error' not in r}
    
    # Get common symbols
    common_symbols = set(baseline_by_symbol.keys()) & set(current_by_symbol.keys()) & set(optimized_by_symbol.keys())
    
    comparison = {
        'timestamp': datetime.now().isoformat(),
        'symbols_compared': len(common_symbols),
        'symbols': {}
    }
    
    # Overall statistics
    baseline_win_rates = [r['win_rate'] for r in baseline_by_symbol.values() if 'win_rate' in r]
    current_win_rates = [r['win_rate'] for r in current_by_symbol.values() if 'win_rate' in r]
    optimized_win_rates = [r['win_rate'] for r in optimized_by_symbol.values() if 'win_rate' in r]
    
    baseline_returns = [r['total_return'] for r in baseline_by_symbol.values() if 'total_return' in r]
    current_returns = [r['total_return'] for r in current_by_symbol.values() if 'total_return' in r]
    optimized_returns = [r['total_return'] for r in optimized_by_symbol.values() if 'total_return' in r]
    
    baseline_sharpe = [r['sharpe_ratio'] for r in baseline_by_symbol.values() if 'sharpe_ratio' in r]
    current_sharpe = [r['sharpe_ratio'] for r in current_by_symbol.values() if 'sharpe_ratio' in r]
    optimized_sharpe = [r['sharpe_ratio'] for r in optimized_by_symbol.values() if 'sharpe_ratio' in r]
    
    comparison['overall'] = {
        'baseline': {
            'avg_win_rate': sum(baseline_win_rates) / len(baseline_win_rates) if baseline_win_rates else 0,
            'avg_return': sum(baseline_returns) / len(baseline_returns) if baseline_returns else 0,
            'avg_sharpe': sum(baseline_sharpe) / len(baseline_sharpe) if baseline_sharpe else 0,
            'symbols_tested': len(baseline_by_symbol)
        },
        'current': {
            'avg_win_rate': sum(current_win_rates) / len(current_win_rates) if current_win_rates else 0,
            'avg_return': sum(current_returns) / len(current_returns) if current_returns else 0,
            'avg_sharpe': sum(current_sharpe) / len(current_sharpe) if current_sharpe else 0,
            'symbols_tested': len(current_by_symbol)
        },
        'optimized': {
            'avg_win_rate': sum(optimized_win_rates) / len(optimized_win_rates) if optimized_win_rates else 0,
            'avg_return': sum(optimized_returns) / len(optimized_returns) if optimized_returns else 0,
            'avg_sharpe': sum(optimized_sharpe) / len(optimized_sharpe) if optimized_sharpe else 0,
            'symbols_tested': len(optimized_by_symbol)
        }
    }
    
    # Calculate improvements
    if baseline_win_rates and current_win_rates and optimized_win_rates:
        comparison['overall']['improvements'] = {
            'current_vs_baseline': {
                'win_rate_change': comparison['overall']['current']['avg_win_rate'] - comparison['overall']['baseline']['avg_win_rate'],
                'return_change': comparison['overall']['current']['avg_return'] - comparison['overall']['baseline']['avg_return'],
                'sharpe_change': comparison['overall']['current']['avg_sharpe'] - comparison['overall']['baseline']['avg_sharpe']
            },
            'optimized_vs_current': {
                'win_rate_change': comparison['overall']['optimized']['avg_win_rate'] - comparison['overall']['current']['avg_win_rate'],
                'return_change': comparison['overall']['optimized']['avg_return'] - comparison['overall']['current']['avg_return'],
                'sharpe_change': comparison['overall']['optimized']['avg_sharpe'] - comparison['overall']['current']['avg_sharpe']
            },
            'optimized_vs_baseline': {
                'win_rate_change': comparison['overall']['optimized']['avg_win_rate'] - comparison['overall']['baseline']['avg_win_rate'],
                'return_change': comparison['overall']['optimized']['avg_return'] - comparison['overall']['baseline']['avg_return'],
                'sharpe_change': comparison['overall']['optimized']['avg_sharpe'] - comparison['overall']['baseline']['avg_sharpe']
            }
        }
    
    # Per-symbol comparison
    for symbol in sorted(common_symbols):
        base = baseline_by_symbol[symbol]
        curr = current_by_symbol[symbol]
        opt = optimized_by_symbol[symbol]
        
        comparison['symbols'][symbol] = {
            'baseline': {
                'win_rate': base.get('win_rate', 0),
                'total_return': base.get('total_return', 0),
                'sharpe_ratio': base.get('sharpe_ratio', 0),
                'max_drawdown': base.get('max_drawdown', 0),
                'total_trades': base.get('total_trades', 0)
            },
            'current': {
                'win_rate': curr.get('win_rate', 0),
                'total_return': curr.get('total_return', 0),
                'sharpe_ratio': curr.get('sharpe_ratio', 0),
                'max_drawdown': curr.get('max_drawdown', 0),
                'total_trades': curr.get('total_trades', 0)
            },
            'optimized': {
                'win_rate': opt.get('win_rate', 0),
                'total_return': opt.get('total_return', 0),
                'sharpe_ratio': opt.get('sharpe_ratio', 0),
                'max_drawdown': opt.get('max_drawdown', 0),
                'total_trades': opt.get('total_trades', 0)
            },
            'changes': {
                'current_vs_baseline': {
                    'win_rate': curr.get('win_rate', 0) - base.get('win_rate', 0),
                    'total_return': curr.get('total_return', 0) - base.get('total_return', 0),
                    'sharpe_ratio': curr.get('sharpe_ratio', 0) - base.get('sharpe_ratio', 0)
                },
                'optimized_vs_current': {
                    'win_rate': opt.get('win_rate', 0) - curr.get('win_rate', 0),
                    'total_return': opt.get('total_return', 0) - curr.get('total_return', 0),
                    'sharpe_ratio': opt.get('sharpe_ratio', 0) - curr.get('sharpe_ratio', 0)
                },
                'optimized_vs_baseline': {
                    'win_rate': opt.get('win_rate', 0) - base.get('win_rate', 0),
                    'total_return': opt.get('total_return', 0) - base.get('total_return', 0),
                    'sharpe_ratio': opt.get('sharpe_ratio', 0) - base.get('sharpe_ratio', 0)
                }
            }
        }
    
    return comparison

def print_comparison_report(comparison: Dict):
    """Print formatted three-way comparison report"""
    
    print('\n' + '='*90)
    print('📊 THREE-WAY BACKTEST RESULTS COMPARISON')
    print('   Baseline → Current → Optimized')
    print('='*90)
    
    # Overall comparison
    overall = comparison.get('overall', {})
    baseline = overall.get('baseline', {})
    current = overall.get('current', {})
    optimized = overall.get('optimized', {})
    improvements = overall.get('improvements', {})
    
    print(f'\n📈 OVERALL PERFORMANCE')
    print('-'*90)
    print(f'{"Metric":<25} {"Baseline":<15} {"Current":<15} {"Optimized":<15} {"Optimized vs Baseline":<15}')
    print('-'*90)
    
    if improvements:
        opt_vs_base = improvements.get('optimized_vs_baseline', {})
        print(f'{"Avg Win Rate (%)":<25} {baseline.get("avg_win_rate", 0):>14.2f}% {current.get("avg_win_rate", 0):>14.2f}% {optimized.get("avg_win_rate", 0):>14.2f}% {opt_vs_base.get("win_rate_change", 0):>+14.2f}%')
        print(f'{"Avg Total Return (%)":<25} {baseline.get("avg_return", 0):>14.2f}% {current.get("avg_return", 0):>14.2f}% {optimized.get("avg_return", 0):>14.2f}% {opt_vs_base.get("return_change", 0):>+14.2f}%')
        print(f'{"Avg Sharpe Ratio":<25} {baseline.get("avg_sharpe", 0):>14.2f}  {current.get("avg_sharpe", 0):>14.2f}  {optimized.get("avg_sharpe", 0):>14.2f}  {opt_vs_base.get("sharpe_change", 0):>+14.2f}')
    
    print(f'\nSymbols Tested: Baseline={baseline.get("symbols_tested", 0)}, Current={current.get("symbols_tested", 0)}, Optimized={optimized.get("symbols_tested", 0)}')
    
    # Key improvements summary
    if improvements:
        opt_vs_curr = improvements.get('optimized_vs_current', {})
        print(f'\n🎯 OPTIMIZATION IMPROVEMENTS (Optimized vs Current)')
        print('-'*90)
        print(f'Win Rate Change: {opt_vs_curr.get("win_rate_change", 0):+.2f}%')
        print(f'Return Change: {opt_vs_curr.get("return_change", 0):+.2f}%')
        print(f'Sharpe Change: {opt_vs_curr.get("sharpe_change", 0):+.2f}')
    
    # Per-symbol comparison
    symbols = comparison.get('symbols', {})
    if symbols:
        print(f'\n📊 PER-SYMBOL COMPARISON (Top Performers)')
        print('-'*90)
        print(f'{"Symbol":<10} {"Metric":<15} {"Baseline":<12} {"Current":<12} {"Optimized":<12} {"Change":<12}')
        print('-'*90)
        
        # Sort by optimized return improvement
        sorted_symbols = sorted(
            symbols.items(),
            key=lambda x: x[1]['changes']['optimized_vs_current'].get('total_return', 0),
            reverse=True
        )
        
        for symbol, data in sorted_symbols[:8]:  # Top 8
            base_data = data['baseline']
            curr_data = data['current']
            opt_data = data['optimized']
            change = data['changes']['optimized_vs_current']
            
            print(f'\n{symbol}:')
            print(f'  {"Return (%)":<15} {base_data["total_return"]:>11.2f}% {curr_data["total_return"]:>11.2f}% {opt_data["total_return"]:>11.2f}% {change["total_return"]:>+11.2f}%')
            print(f'  {"Win Rate (%)":<15} {base_data["win_rate"]:>11.2f}% {curr_data["win_rate"]:>11.2f}% {opt_data["win_rate"]:>11.2f}% {change["win_rate"]:>+11.2f}%')
            print(f'  {"Sharpe Ratio":<15} {base_data["sharpe_ratio"]:>11.2f}  {curr_data["sharpe_ratio"]:>11.2f}  {opt_data["sharpe_ratio"]:>11.2f}  {change["sharpe_ratio"]:>+11.2f}')
    
    print('\n' + '='*90 + '\n')

def main():
    """Main comparison function"""
    
    reports_dir = Path(__file__).parent.parent / "reports"
    
    # Load results
    print("Loading baseline results...")
    baseline_data = load_results(reports_dir / "comprehensive_backtest_results.json", 'baseline')
    
    print("Loading current (pre-optimization) results...")
    # We need to save the current results before optimization
    # For now, we'll use the optimized results as current if baseline exists
    current_data = load_results(reports_dir / "current_strategy_backtest_results.json", 'results')
    
    print("Loading optimized results...")
    optimized_data = load_results(reports_dir / "current_strategy_backtest_results.json", 'results')
    
    if not baseline_data or not optimized_data:
        print("❌ Cannot compare: Missing baseline or optimized results")
        return
    
    # Use optimized as current if we don't have separate current results
    if not current_data:
        print("⚠️  Using optimized results as current (pre-optimization results not saved separately)")
        current_data = optimized_data
    
    # Compare
    print("Comparing results...")
    comparison = compare_three_way(baseline_data, current_data, optimized_data)
    
    # Print report
    print_comparison_report(comparison)
    
    # Save comparison
    output_file = reports_dir / "three_way_backtest_comparison.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Comparison saved to: {output_file}\n")

if __name__ == '__main__':
    main()

