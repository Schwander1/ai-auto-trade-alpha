#!/usr/bin/env python3
"""
Generate Best/Worst Performers Summary
Creates a comprehensive summary of top and bottom performing symbols
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

def load_v7_results() -> Dict:
    """Load V7 backtest results"""
    reports_dir = Path(__file__).parent.parent / "reports"
    
    v7_files = list(reports_dir.glob("iterative_v7_*_results.json"))
    if v7_files:
        latest_file = max(v7_files, key=lambda p: p.stat().st_mtime)
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    current_file = reports_dir / "current_strategy_backtest_results.json"
    if current_file.exists():
        with open(current_file, 'r') as f:
            return json.load(f)
    
    return {}

def rank_symbols(results: List[Dict]) -> Dict:
    """Rank symbols by various metrics"""
    valid_results = [r for r in results if 'error' not in r and 'metrics' in r]
    
    rankings = {
        'by_return': sorted(valid_results, key=lambda x: x['metrics'].get('total_return', 0), reverse=True),
        'by_win_rate': sorted(valid_results, key=lambda x: x['metrics'].get('win_rate', 0), reverse=True),
        'by_sharpe': sorted(valid_results, key=lambda x: x['metrics'].get('sharpe_ratio', 0), reverse=True),
        'by_profit_factor': sorted(valid_results, key=lambda x: x['metrics'].get('profit_factor', 0), reverse=True),
        'by_max_drawdown': sorted(valid_results, key=lambda x: x['metrics'].get('max_drawdown', 0)),  # Lower is better
        'by_total_trades': sorted(valid_results, key=lambda x: x['metrics'].get('total_trades', 0), reverse=True),
    }
    
    return rankings

def generate_summary_report(v7_data: Dict, rankings: Dict) -> str:
    """Generate best/worst performers summary"""
    
    report = f"""# Best/Worst Performers Summary - Iterative V7

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Iteration:** {v7_data.get('iteration_name', 'iterative_v7')}

---

## 🏆 Top Performers

### Top 3 by Total Return

"""
    
    top_returns = rankings['by_return'][:3]
    for i, result in enumerate(top_returns, 1):
        symbol = result['symbol']
        metrics = result['metrics']
        report += f"""#### {i}. {symbol}
- **Total Return:** {metrics.get('total_return', 0):.2f}%
- **Win Rate:** {metrics.get('win_rate', 0):.2f}%
- **Sharpe Ratio:** {metrics.get('sharpe_ratio', 0):.2f}
- **Max Drawdown:** {metrics.get('max_drawdown', 0):.2f}%
- **Profit Factor:** {metrics.get('profit_factor', 0):.2f}
- **Total Trades:** {metrics.get('total_trades', 0)}

"""
    
    report += """### Top 3 by Win Rate

"""
    
    top_win_rate = rankings['by_win_rate'][:3]
    for i, result in enumerate(top_win_rate, 1):
        symbol = result['symbol']
        metrics = result['metrics']
        report += f"""#### {i}. {symbol}
- **Win Rate:** {metrics.get('win_rate', 0):.2f}%
- **Total Return:** {metrics.get('total_return', 0):.2f}%
- **Sharpe Ratio:** {metrics.get('sharpe_ratio', 0):.2f}
- **Total Trades:** {metrics.get('total_trades', 0)}

"""
    
    report += """### Top 3 by Sharpe Ratio

"""
    
    top_sharpe = rankings['by_sharpe'][:3]
    for i, result in enumerate(top_sharpe, 1):
        symbol = result['symbol']
        metrics = result['metrics']
        report += f"""#### {i}. {symbol}
- **Sharpe Ratio:** {metrics.get('sharpe_ratio', 0):.2f}
- **Total Return:** {metrics.get('total_return', 0):.2f}%
- **Win Rate:** {metrics.get('win_rate', 0):.2f}%
- **Max Drawdown:** {metrics.get('max_drawdown', 0):.2f}%

"""
    
    report += """### Top 3 by Profit Factor

"""
    
    top_pf = rankings['by_profit_factor'][:3]
    for i, result in enumerate(top_pf, 1):
        symbol = result['symbol']
        metrics = result['metrics']
        report += f"""#### {i}. {symbol}
- **Profit Factor:** {metrics.get('profit_factor', 0):.2f}
- **Total Return:** {metrics.get('total_return', 0):.2f}%
- **Win Rate:** {metrics.get('win_rate', 0):.2f}%
- **Total Trades:** {metrics.get('total_trades', 0)}

"""
    
    report += """---

## ⚠️ Underperformers

### Bottom 3 by Total Return

"""
    
    bottom_returns = rankings['by_return'][-3:]
    for i, result in enumerate(reversed(bottom_returns), 1):
        symbol = result['symbol']
        metrics = result['metrics']
        report += f"""#### {i}. {symbol}
- **Total Return:** {metrics.get('total_return', 0):.2f}%
- **Win Rate:** {metrics.get('win_rate', 0):.2f}%
- **Sharpe Ratio:** {metrics.get('sharpe_ratio', 0):.2f}
- **Max Drawdown:** {metrics.get('max_drawdown', 0):.2f}%
- **Profit Factor:** {metrics.get('profit_factor', 0):.2f}
- **Total Trades:** {metrics.get('total_trades', 0)}

"""
    
    report += """### Bottom 3 by Win Rate

"""
    
    bottom_win_rate = rankings['by_win_rate'][-3:]
    for i, result in enumerate(reversed(bottom_win_rate), 1):
        symbol = result['symbol']
        metrics = result['metrics']
        report += f"""#### {i}. {symbol}
- **Win Rate:** {metrics.get('win_rate', 0):.2f}%
- **Total Return:** {metrics.get('total_return', 0):.2f}%
- **Sharpe Ratio:** {metrics.get('sharpe_ratio', 0):.2f}
- **Total Trades:** {metrics.get('total_trades', 0)}

"""
    
    report += """### Worst 3 by Max Drawdown

"""
    
    worst_dd = rankings['by_max_drawdown'][-3:]
    for i, result in enumerate(reversed(worst_dd), 1):
        symbol = result['symbol']
        metrics = result['metrics']
        report += f"""#### {i}. {symbol}
- **Max Drawdown:** {metrics.get('max_drawdown', 0):.2f}%
- **Total Return:** {metrics.get('total_return', 0):.2f}%
- **Win Rate:** {metrics.get('win_rate', 0):.2f}%
- **Sharpe Ratio:** {metrics.get('sharpe_ratio', 0):.2f}

"""
    
    report += """---

## 📊 Complete Rankings

### By Total Return
| Rank | Symbol | Return | Win Rate | Sharpe | Max DD | Profit Factor |
|------|--------|--------|----------|--------|--------|---------------|
"""
    
    for i, result in enumerate(rankings['by_return'], 1):
        symbol = result['symbol']
        metrics = result['metrics']
        report += f"| {i} | {symbol} | {metrics.get('total_return', 0):.2f}% | {metrics.get('win_rate', 0):.2f}% | {metrics.get('sharpe_ratio', 0):.2f} | {metrics.get('max_drawdown', 0):.2f}% | {metrics.get('profit_factor', 0):.2f} |\n"
    
    report += """
### By Win Rate
| Rank | Symbol | Win Rate | Return | Sharpe | Total Trades |
|------|--------|----------|--------|--------|--------------|
"""
    
    for i, result in enumerate(rankings['by_win_rate'], 1):
        symbol = result['symbol']
        metrics = result['metrics']
        report += f"| {i} | {symbol} | {metrics.get('win_rate', 0):.2f}% | {metrics.get('total_return', 0):.2f}% | {metrics.get('sharpe_ratio', 0):.2f} | {metrics.get('total_trades', 0)} |\n"
    
    report += """
### By Sharpe Ratio
| Rank | Symbol | Sharpe | Return | Win Rate | Max DD |
|------|--------|--------|--------|----------|--------|
"""
    
    for i, result in enumerate(rankings['by_sharpe'], 1):
        symbol = result['symbol']
        metrics = result['metrics']
        report += f"| {i} | {symbol} | {metrics.get('sharpe_ratio', 0):.2f} | {metrics.get('total_return', 0):.2f}% | {metrics.get('win_rate', 0):.2f}% | {metrics.get('max_drawdown', 0):.2f}% |\n"
    
    report += """
---

## 🎯 Key Insights

### Best Overall Performer
"""
    
    # Calculate composite score
    best_overall = None
    best_score = -float('inf')
    
    for result in rankings['by_return']:
        metrics = result['metrics']
        # Composite score: weighted combination
        score = (
            metrics.get('total_return', 0) * 0.4 +
            metrics.get('win_rate', 0) * 0.2 +
            metrics.get('sharpe_ratio', 0) * 10 * 0.2 +
            metrics.get('profit_factor', 0) * 10 * 0.2
        )
        if score > best_score:
            best_score = score
            best_overall = result
    
    if best_overall:
        symbol = best_overall['symbol']
        metrics = best_overall['metrics']
        report += f"""
**{symbol}** stands out as the best overall performer with:
- Exceptional return of {metrics.get('total_return', 0):.2f}%
- Strong win rate of {metrics.get('win_rate', 0):.2f}%
- Solid Sharpe ratio of {metrics.get('sharpe_ratio', 0):.2f}
- Profit factor of {metrics.get('profit_factor', 0):.2f}

"""
    
    report += """### Areas for Improvement
"""
    
    worst_return = rankings['by_return'][-1]
    worst_win = rankings['by_win_rate'][-1]
    
    report += f"""
- **Lowest Return:** {worst_return['symbol']} at {worst_return['metrics'].get('total_return', 0):.2f}%
- **Lowest Win Rate:** {worst_win['symbol']} at {worst_win['metrics'].get('win_rate', 0):.2f}%

These symbols may benefit from strategy adjustments or could be candidates for exclusion if performance doesn't improve.

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return report

def main():
    """Main function"""
    print("Loading V7 results...")
    v7_data = load_v7_results()
    
    if not v7_data:
        print("❌ Error: Could not load V7 results")
        return
    
    results = v7_data.get('results', [])
    print("Ranking symbols...")
    rankings = rank_symbols(results)
    
    print("Generating summary report...")
    report = generate_summary_report(v7_data, rankings)
    
    # Save report
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    output_file = reports_dir / "BEST_WORST_PERFORMERS.md"
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Summary report saved to: {output_file}\n")
    
    # Print quick summary
    print("🏆 Top 3 by Return:")
    for i, result in enumerate(rankings['by_return'][:3], 1):
        print(f"   {i}. {result['symbol']}: {result['metrics'].get('total_return', 0):.2f}%")
    
    print("\n⚠️  Bottom 3 by Return:")
    for i, result in enumerate(reversed(rankings['by_return'][-3:]), 1):
        print(f"   {i}. {result['symbol']}: {result['metrics'].get('total_return', 0):.2f}%")
    print()

if __name__ == '__main__':
    main()

