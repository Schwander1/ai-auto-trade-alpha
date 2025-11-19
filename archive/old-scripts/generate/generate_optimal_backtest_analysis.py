#!/usr/bin/env python3
"""
Generate Optimal Backtest Analysis
Comprehensive comparison of all iterations to identify optimal configuration
"""
import json
import glob
from pathlib import Path
from typing import Dict, List
from datetime import datetime

def load_all_iterations() -> Dict:
    """Load all iteration results"""
    reports_dir = Path(__file__).parent.parent / "reports"
    iterations = {}
    
    for f in sorted(glob.glob(str(reports_dir / "iterative_v*_*_results.json"))):
        try:
            with open(f) as file:
                data = json.load(file)
                v = data.get('iteration_name', 'unknown')
                if v and v not in iterations:
                    summary = data.get('summary', {})
                    if summary and summary.get('total_symbols', 0) > 0:
                        iterations[v] = {
                            'summary': summary,
                            'config': data.get('strategy_config', {}),
                            'timestamp': data.get('timestamp', '')
                        }
        except Exception as e:
            print(f"Error loading {f}: {e}")
            continue
    
    return iterations

def calculate_composite_score(summary: Dict) -> float:
    """
    Calculate composite score for ranking iterations
    Higher is better
    """
    win_rate = summary.get('avg_win_rate', 0) / 100.0
    return_pct = summary.get('avg_total_return', 0) / 100.0
    sharpe = summary.get('avg_sharpe_ratio', 0)
    drawdown = abs(summary.get('avg_max_drawdown', 0)) / 100.0  # Make positive
    profit_factor = summary.get('avg_profit_factor', 0)
    
    # Normalize and weight
    # Win rate: 20%, Return: 25%, Sharpe: 25%, Drawdown: 15%, Profit Factor: 15%
    score = (
        win_rate * 0.20 +
        min(return_pct, 0.5) * 0.25 * 2 +  # Cap at 50% return, scale
        min(sharpe, 2.0) * 0.25 * 0.5 +  # Cap at 2.0 Sharpe, scale
        (1.0 - min(drawdown, 0.5)) * 0.15 * 2 +  # Lower drawdown is better
        min(profit_factor, 3.0) * 0.15 * 0.33  # Cap at 3.0, scale
    )
    
    return score

def generate_analysis_report(iterations: Dict) -> str:
    """Generate comprehensive analysis report"""
    
    # Calculate scores
    scored = []
    for v, data in iterations.items():
        score = calculate_composite_score(data['summary'])
        scored.append((v, score, data))
    
    # Sort by score
    scored.sort(key=lambda x: x[1], reverse=True)
    
    report = f"""# Optimal Backtest Configuration Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

This report analyzes all backtest iterations to identify the **optimal configuration** for production use.

---

## 📊 Iteration Rankings (Composite Score)

| Rank | Iteration | Score | Win Rate | Return | Sharpe | Drawdown | Profit Factor |
|------|-----------|-------|----------|--------|--------|----------|---------------|
"""
    
    for rank, (v, score, data) in enumerate(scored, 1):
        s = data['summary']
        report += f"| {rank} | **{v.upper()}** | {score:.3f} | {s.get('avg_win_rate', 0):.2f}% | {s.get('avg_total_return', 0):.2f}% | {s.get('avg_sharpe_ratio', 0):.2f} | {s.get('avg_max_drawdown', 0):.2f}% | {s.get('avg_profit_factor', 0):.2f} |\n"
    
    # Best iteration
    best_v, best_score, best_data = scored[0]
    best_summary = best_data['summary']
    
    report += f"""
---

## 🏆 Optimal Configuration: **{best_v.upper()}**

### Performance Metrics
- **Composite Score:** {best_score:.3f}
- **Win Rate:** {best_summary.get('avg_win_rate', 0):.2f}%
- **Total Return:** {best_summary.get('avg_total_return', 0):.2f}%
- **Sharpe Ratio:** {best_summary.get('avg_sharpe_ratio', 0):.2f}
- **Max Drawdown:** {best_summary.get('avg_max_drawdown', 0):.2f}%
- **Profit Factor:** {best_summary.get('avg_profit_factor', 0):.2f}
- **Total Trades:** {best_summary.get('total_trades_all_symbols', 0):,}

### Configuration
```json
{json.dumps(best_data['config'], indent=2)}
```

---

## 📈 Detailed Comparison

### Win Rate Analysis
"""
    
    # Win rate comparison
    win_rates = [(v, data['summary'].get('avg_win_rate', 0)) for v, _, data in scored]
    win_rates.sort(key=lambda x: x[1], reverse=True)
    report += "\n| Iteration | Win Rate |\n|-----------|----------|\n"
    for v, wr in win_rates[:5]:
        report += f"| {v.upper()} | {wr:.2f}% |\n"
    
    report += "\n### Return Analysis\n"
    returns = [(v, data['summary'].get('avg_total_return', 0)) for v, _, data in scored]
    returns.sort(key=lambda x: x[1], reverse=True)
    report += "\n| Iteration | Return |\n|-----------|--------|\n"
    for v, ret in returns[:5]:
        report += f"| {v.upper()} | {ret:.2f}% |\n"
    
    report += "\n### Sharpe Ratio Analysis\n"
    sharpes = [(v, data['summary'].get('avg_sharpe_ratio', 0)) for v, _, data in scored]
    sharpes.sort(key=lambda x: x[1], reverse=True)
    report += "\n| Iteration | Sharpe |\n|-----------|--------|\n"
    for v, sharpe in sharpes[:5]:
        report += f"| {v.upper()} | {sharpe:.2f} |\n"
    
    report += "\n### Drawdown Analysis\n"
    drawdowns = [(v, abs(data['summary'].get('avg_max_drawdown', 0))) for v, _, data in scored]
    drawdowns.sort(key=lambda x: x[1])  # Lower is better
    report += "\n| Iteration | Drawdown |\n|-----------|----------|\n"
    for v, dd in drawdowns[:5]:
        report += f"| {v.upper()} | -{dd:.2f}% |\n"
    
    report += "\n### Profit Factor Analysis\n"
    pf = [(v, data['summary'].get('avg_profit_factor', 0)) for v, _, data in scored]
    pf.sort(key=lambda x: x[1], reverse=True)
    report += "\n| Iteration | Profit Factor |\n|-----------|---------------|\n"
    for v, p in pf[:5]:
        report += f"| {v.upper()} | {p:.2f} |\n"
    
    report += f"""
---

## 🎯 Recommendations

### Best Overall: **{best_v.upper()}**
- **Best for:** Production use, balanced performance
- **Strengths:** {', '.join([s for s in [
        f"Best Sharpe ({best_summary.get('avg_sharpe_ratio', 0):.2f})" if best_summary.get('avg_sharpe_ratio', 0) == max(s['summary'].get('avg_sharpe_ratio', 0) for _, _, s in scored) else None,
        f"Best Profit Factor ({best_summary.get('avg_profit_factor', 0):.2f})" if best_summary.get('avg_profit_factor', 0) == max(s['summary'].get('avg_profit_factor', 0) for _, _, s in scored) else None,
        f"Good Returns ({best_summary.get('avg_total_return', 0):.2f}%)" if best_summary.get('avg_total_return', 0) > 10 else None
    ] if s is not None])}
- **Trade-offs:** {f"Drawdown: {best_summary.get('avg_max_drawdown', 0):.2f}%" if best_summary.get('avg_max_drawdown', 0) < -20 else "Acceptable drawdown"}

### Alternative Configurations

"""
    
    # Find best for specific metrics
    best_wr_v = win_rates[0][0]
    best_ret_v = returns[0][0]
    best_sharpe_v = sharpes[0][0]
    best_dd_v = drawdowns[0][0]
    
    report += f"""
- **Best Win Rate:** {best_wr_v.upper()} ({win_rates[0][1]:.2f}%)
- **Best Returns:** {best_ret_v.upper()} ({returns[0][1]:.2f}%)
- **Best Sharpe:** {best_sharpe_v.upper()} ({sharpes[0][1]:.2f})
- **Best Drawdown:** {best_dd_v.upper()} (-{drawdowns[0][1]:.2f}%)

---

## 📝 Conclusion

**Recommended Configuration:** **{best_v.upper()}**

This configuration provides the best overall balance of:
- Risk-adjusted returns (Sharpe ratio)
- Profitability (profit factor)
- Return generation
- Risk management

**Next Steps:**
1. Use {best_v.upper()} configuration for production
2. Monitor performance in live trading
3. Consider fine-tuning based on specific symbol performance
4. Continue iterative improvements

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return report

def main():
    """Main function"""
    print("Loading all iteration results...")
    iterations = load_all_iterations()
    
    if not iterations:
        print("❌ No iteration results found")
        return
    
    print(f"✅ Loaded {len(iterations)} iterations")
    
    print("Generating analysis report...")
    report = generate_analysis_report(iterations)
    
    # Save report
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    output_file = reports_dir / "OPTIMAL_BACKTEST_ANALYSIS.md"
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"✅ Analysis report saved to: {output_file}")
    
    # Print summary
    scored = []
    for v, data in iterations.items():
        score = calculate_composite_score(data['summary'])
        scored.append((v, score, data))
    scored.sort(key=lambda x: x[1], reverse=True)
    
    print("\n📊 Top 3 Iterations:")
    for rank, (v, score, data) in enumerate(scored[:3], 1):
        s = data['summary']
        print(f"\n{rank}. {v.upper()} (Score: {score:.3f})")
        print(f"   Win Rate: {s.get('avg_win_rate', 0):.2f}%")
        print(f"   Return: {s.get('avg_total_return', 0):.2f}%")
        print(f"   Sharpe: {s.get('avg_sharpe_ratio', 0):.2f}")
        print(f"   Drawdown: {s.get('avg_max_drawdown', 0):.2f}%")
        print(f"   Profit Factor: {s.get('avg_profit_factor', 0):.2f}")

if __name__ == '__main__':
    main()

