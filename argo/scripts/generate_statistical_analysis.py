#!/usr/bin/env python3
"""
Generate Statistical Analysis Report
Calculates p-values, confidence intervals, and statistical significance
"""
import json
import numpy as np
from scipy import stats
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def calculate_statistical_significance(
    returns: List[float],
    benchmark_returns: List[float] = None,
    min_trades: int = 30
) -> Dict:
    """
    Calculate statistical significance of backtest results
    
    Args:
        returns: List of trade returns
        benchmark_returns: Benchmark returns (e.g., buy-and-hold)
        min_trades: Minimum trades for statistical validity
    
    Returns:
        Dictionary with statistical metrics
    """
    if len(returns) < min_trades:
        return {
            'is_valid': False,
            'reason': f'Insufficient trades: {len(returns)} < {min_trades}',
            'n_trades': len(returns)
        }
    
    returns_array = np.array(returns)
    
    # Basic statistics
    mean_return = np.mean(returns_array)
    std_return = np.std(returns_array)
    sem = stats.sem(returns_array)  # Standard error of mean
    
    # Confidence intervals (95%)
    ci_95 = stats.t.interval(0.95, len(returns_array)-1, loc=mean_return, scale=sem)
    
    # T-test vs zero (is strategy profitable?)
    t_stat_zero, p_value_zero = stats.ttest_1samp(returns_array, 0)
    is_profitable = p_value_zero < 0.05 and mean_return > 0
    
    # T-test vs benchmark (if provided)
    vs_benchmark = None
    if benchmark_returns and len(benchmark_returns) > 0:
        benchmark_array = np.array(benchmark_returns)
        t_stat_bench, p_value_bench = stats.ttest_ind(returns_array, benchmark_array)
        vs_benchmark = {
            't_statistic': float(t_stat_bench),
            'p_value': float(p_value_bench),
            'is_significant': p_value_bench < 0.05,
            'mean_difference': float(mean_return - np.mean(benchmark_array))
        }
    
    return {
        'is_valid': True,
        'n_trades': len(returns),
        'mean_return': float(mean_return),
        'std_return': float(std_return),
        'sem': float(sem),
        'confidence_interval_95': [float(ci_95[0]), float(ci_95[1])],
        't_statistic_vs_zero': float(t_stat_zero),
        'p_value_vs_zero': float(p_value_zero),
        'is_profitable': is_profitable,
        'vs_benchmark': vs_benchmark
    }

def generate_analysis_report(results_file: str, output_file: str):
    """Generate comprehensive statistical analysis report"""
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'configurations': {}
    }
    
    for config_name, results in data.items():
        successful = [r for r in results if 'error' not in r]
        
        if not successful:
            continue
        
        # Extract returns from trades (if available)
        # For now, use total_return as proxy
        returns = [r.get('total_return', 0) / 100.0 for r in successful if r.get('total_return')]
        
        # Calculate statistics
        stats_result = calculate_statistical_significance(returns) if returns else None
        
        config_report = {
            'n_symbols': len(successful),
            'average_metrics': {},
            'statistical_analysis': stats_result
        }
        
        if 'win_rate' in successful[0]:
            wr = [r.get('win_rate', 0) for r in successful]
            tr = [r.get('total_return', 0) for r in successful]
            tt = [r.get('total_trades', 0) for r in successful]
            sh = [r.get('sharpe_ratio', 0) for r in successful if r.get('sharpe_ratio')]
            
            config_report['average_metrics'] = {
                'win_rate_pct': float(np.mean(wr)) if wr else 0,
                'total_return_pct': float(np.mean(tr)) if tr else 0,
                'total_trades': float(np.mean(tt)) if tt else 0,
                'sharpe_ratio': float(np.mean(sh)) if sh else 0
            }
        
        report['configurations'][config_name] = config_report
    
    # Save report
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*80)
    print("STATISTICAL ANALYSIS REPORT")
    print("="*80)
    
    for config_name, config_data in report['configurations'].items():
        print(f"\n{config_name.upper()}:")
        metrics = config_data.get('average_metrics', {})
        print(f"  Win Rate: {metrics.get('win_rate_pct', 0):.2f}%")
        print(f"  Return: {metrics.get('total_return_pct', 0):.2f}%")
        print(f"  Trades: {metrics.get('total_trades', 0):.0f}")
        print(f"  Sharpe: {metrics.get('sharpe_ratio', 0):.2f}")
        
        stats = config_data.get('statistical_analysis')
        if stats and stats.get('is_valid'):
            print(f"  Statistical Validity: ✅ ({stats['n_trades']} trades)")
            print(f"  P-value vs Zero: {stats.get('p_value_vs_zero', 0):.4f}")
            print(f"  Is Profitable: {'✅' if stats.get('is_profitable') else '❌'}")
            if stats.get('confidence_interval_95'):
                ci = stats['confidence_interval_95']
                print(f"  95% CI: [{ci[0]:.2f}%, {ci[1]:.2f}%]")
    
    print("\n" + "="*80)
    print(f"✅ Report saved to: {output_file}")
    print("="*80)

if __name__ == "__main__":
    results_file = "argo/reports/comprehensive_backtest_results.json"
    output_file = "argo/reports/statistical_analysis.json"
    
    generate_analysis_report(results_file, output_file)

