#!/usr/bin/env python3
"""
Compare All Backtest Iterations
Baseline → Optimized → Refined
"""
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

def load_baseline() -> List[Dict]:
    """Load baseline results"""
    file_path = Path(__file__).parent.parent / "reports" / "comprehensive_backtest_results.json"
    if file_path.exists():
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data.get('baseline', [])
    return []

def load_current() -> List[Dict]:
    """Load current/optimized results"""
    file_path = Path(__file__).parent.parent / "reports" / "current_strategy_backtest_results.json"
    if file_path.exists():
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data.get('results', [])
    return []

def compare_all(baseline: List[Dict], optimized: List[Dict], refined: List[Dict]) -> Dict:
    """Compare all three iterations"""
    
    baseline_by_symbol = {r['symbol']: r for r in baseline if 'error' not in r}
    optimized_by_symbol = {r['symbol']: r for r in optimized if 'error' not in r}
    refined_by_symbol = {r['symbol']: r for r in refined if 'error' not in r}
    
    common_symbols = set(baseline_by_symbol.keys()) & set(optimized_by_symbol.keys()) & set(refined_by_symbol.keys())
    
    # Overall stats
    baseline_returns = [r['total_return'] for r in baseline_by_symbol.values() if 'total_return' in r]
    optimized_returns = [r['total_return'] for r in optimized_by_symbol.values() if 'total_return' in r]
    refined_returns = [r['total_return'] for r in refined_by_symbol.values() if 'total_return' in r]
    
    baseline_win = [r['win_rate'] for r in baseline_by_symbol.values() if 'win_rate' in r]
    optimized_win = [r['win_rate'] for r in optimized_by_symbol.values() if 'win_rate' in r]
    refined_win = [r['win_rate'] for r in refined_by_symbol.values() if 'win_rate' in r]
    
    baseline_sharpe = [r['sharpe_ratio'] for r in baseline_by_symbol.values() if 'sharpe_ratio' in r]
    optimized_sharpe = [r['sharpe_ratio'] for r in optimized_by_symbol.values() if 'sharpe_ratio' in r]
    refined_sharpe = [r['sharpe_ratio'] for r in refined_by_symbol.values() if 'sharpe_ratio' in r]
    
    comparison = {
        'timestamp': datetime.now().isoformat(),
        'overall': {
            'baseline': {
                'avg_return': sum(baseline_returns) / len(baseline_returns) if baseline_returns else 0,
                'avg_win_rate': sum(baseline_win) / len(baseline_win) if baseline_win else 0,
                'avg_sharpe': sum(baseline_sharpe) / len(baseline_sharpe) if baseline_sharpe else 0
            },
            'optimized': {
                'avg_return': sum(optimized_returns) / len(optimized_returns) if optimized_returns else 0,
                'avg_win_rate': sum(optimized_win) / len(optimized_win) if optimized_win else 0,
                'avg_sharpe': sum(optimized_sharpe) / len(optimized_sharpe) if optimized_sharpe else 0
            },
            'refined': {
                'avg_return': sum(refined_returns) / len(refined_returns) if refined_returns else 0,
                'avg_win_rate': sum(refined_win) / len(refined_win) if refined_win else 0,
                'avg_sharpe': sum(refined_sharpe) / len(refined_sharpe) if refined_sharpe else 0
            }
        },
        'symbols': {}
    }
    
    # Per-symbol
    for symbol in sorted(common_symbols):
        base = baseline_by_symbol[symbol]
        opt = optimized_by_symbol[symbol]
        ref = refined_by_symbol[symbol]
        
        comparison['symbols'][symbol] = {
            'baseline': {
                'return': base.get('total_return', 0),
                'win_rate': base.get('win_rate', 0),
                'sharpe': base.get('sharpe_ratio', 0)
            },
            'optimized': {
                'return': opt.get('total_return', 0),
                'win_rate': opt.get('win_rate', 0),
                'sharpe': opt.get('sharpe_ratio', 0)
            },
            'refined': {
                'return': ref.get('total_return', 0),
                'win_rate': ref.get('win_rate', 0),
                'sharpe': ref.get('sharpe_ratio', 0)
            },
            'improvements': {
                'optimized_vs_baseline': {
                    'return': opt.get('total_return', 0) - base.get('total_return', 0),
                    'win_rate': opt.get('win_rate', 0) - base.get('win_rate', 0),
                    'sharpe': opt.get('sharpe_ratio', 0) - base.get('sharpe_ratio', 0)
                },
                'refined_vs_optimized': {
                    'return': ref.get('total_return', 0) - opt.get('total_return', 0),
                    'win_rate': ref.get('win_rate', 0) - opt.get('win_rate', 0),
                    'sharpe': ref.get('sharpe_ratio', 0) - opt.get('sharpe_ratio', 0)
                },
                'refined_vs_baseline': {
                    'return': ref.get('total_return', 0) - base.get('total_return', 0),
                    'win_rate': ref.get('win_rate', 0) - base.get('win_rate', 0),
                    'sharpe': ref.get('sharpe_ratio', 0) - base.get('sharpe_ratio', 0)
                }
            }
        }
    
    return comparison

def print_comparison(comparison: Dict):
    """Print formatted comparison"""
    print('\n' + '='*100)
    print('📊 COMPREHENSIVE BACKTEST COMPARISON: Baseline → Optimized → Refined')
    print('='*100)
    
    overall = comparison['overall']
    base = overall['baseline']
    opt = overall['optimized']
    ref = overall['refined']
    
    print(f'\n📈 OVERALL PERFORMANCE')
    print('-'*100)
    print(f'{"Metric":<25} {"Baseline":<15} {"Optimized":<15} {"Refined":<15} {"Refined vs Baseline":<15}')
    print('-'*100)
    print(f'{"Avg Return (%)":<25} {base["avg_return"]:>14.2f}% {opt["avg_return"]:>14.2f}% {ref["avg_return"]:>14.2f}% {ref["avg_return"]-base["avg_return"]:>+14.2f}%')
    print(f'{"Avg Win Rate (%)":<25} {base["avg_win_rate"]:>14.2f}% {opt["avg_win_rate"]:>14.2f}% {ref["avg_win_rate"]:>14.2f}% {ref["avg_win_rate"]-base["avg_win_rate"]:>+14.2f}%')
    print(f'{"Avg Sharpe Ratio":<25} {base["avg_sharpe"]:>14.2f}  {opt["avg_sharpe"]:>14.2f}  {ref["avg_sharpe"]:>14.2f}  {ref["avg_sharpe"]-base["avg_sharpe"]:>+14.2f}')
    
    print(f'\n🎯 REFINEMENT IMPROVEMENTS (Refined vs Optimized)')
    print('-'*100)
    ref_vs_opt_return = ref["avg_return"] - opt["avg_return"]
    ref_vs_opt_win = ref["avg_win_rate"] - opt["avg_win_rate"]
    ref_vs_opt_sharpe = ref["avg_sharpe"] - opt["avg_sharpe"]
    print(f'Return Change: {ref_vs_opt_return:+.2f}%')
    print(f'Win Rate Change: {ref_vs_opt_win:+.2f}%')
    print(f'Sharpe Change: {ref_vs_opt_sharpe:+.2f}')
    
    print(f'\n📊 PER-SYMBOL COMPARISON (Top Improvements)')
    print('-'*100)
    print(f'{"Symbol":<10} {"Metric":<15} {"Baseline":<12} {"Optimized":<12} {"Refined":<12} {"Refined vs Baseline":<12}')
    print('-'*100)
    
    # Sort by refined vs baseline return improvement
    sorted_symbols = sorted(
        comparison['symbols'].items(),
        key=lambda x: x[1]['improvements']['refined_vs_baseline']['return'],
        reverse=True
    )
    
    for symbol, data in sorted_symbols[:10]:
        base_data = data['baseline']
        opt_data = data['optimized']
        ref_data = data['refined']
        improvement = data['improvements']['refined_vs_baseline']
        
        print(f'\n{symbol}:')
        print(f'  {"Return (%)":<15} {base_data["return"]:>11.2f}% {opt_data["return"]:>11.2f}% {ref_data["return"]:>11.2f}% {improvement["return"]:>+11.2f}%')
        print(f'  {"Win Rate (%)":<15} {base_data["win_rate"]:>11.2f}% {opt_data["win_rate"]:>11.2f}% {ref_data["win_rate"]:>11.2f}% {improvement["win_rate"]:>+11.2f}%')
        print(f'  {"Sharpe Ratio":<15} {base_data["sharpe"]:>11.2f}  {opt_data["sharpe"]:>11.2f}  {ref_data["sharpe"]:>11.2f}  {improvement["sharpe"]:>+11.2f}')
    
    print('\n' + '='*100 + '\n')

def main():
    baseline = load_baseline()
    optimized = load_current()  # This will be the optimized version
    refined = load_current()  # This will be the refined version (same file, updated)
    
    if not baseline or not refined:
        print("❌ Missing data for comparison")
        return
    
    comparison = compare_all(baseline, optimized, refined)
    print_comparison(comparison)
    
    # Save
    output_file = Path(__file__).parent.parent / "reports" / "all_iterations_comparison.json"
    with open(output_file, 'w') as f:
        json.dump(comparison, f, indent=2)
    print(f"✅ Comparison saved to: {output_file}\n")

if __name__ == '__main__':
    main()

