#!/usr/bin/env python3
"""
Generate Comprehensive Analysis Report
Master script that runs all analysis tools and creates a unified report
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_script(script_name: str) -> bool:
    """Run a Python script and return success status"""
    script_path = Path(__file__).parent / script_name
    if not script_path.exists():
        print(f"⚠️  Script not found: {script_name}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Error running {script_name}:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  Timeout running {script_name}")
        return False
    except Exception as e:
        print(f"❌ Exception running {script_name}: {e}")
        return False

def generate_master_report():
    """Generate master report linking all analyses"""
    reports_dir = Path(__file__).parent.parent / "reports"
    
    report = f"""# Comprehensive Backtest Analysis - Iterative V7

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📚 Analysis Reports

This comprehensive analysis includes multiple reports covering different aspects of the Iterative V7 backtest results.

### 1. Comparison Report (V6 vs V7)
**File:** [V6_V7_COMPARISON_REPORT.md](V6_V7_COMPARISON_REPORT.md)

Compares Iterative V6 and V7 iterations to identify improvements and regressions.

**Key Findings:**
- Overall performance comparison
- Per-symbol changes
- Improvement analysis

---

### 2. Detailed Symbol Analysis
**File:** [DETAILED_SYMBOL_ANALYSIS.md](DETAILED_SYMBOL_ANALYSIS.md)

Provides trade-level analysis for each symbol including:
- Trade statistics (winning/losing/breakeven)
- Performance metrics (P&L, returns, risk/reward)
- Trade duration analysis
- Signal confidence analysis

---

### 3. Best/Worst Performers Summary
**File:** [BEST_WORST_PERFORMERS.md](BEST_WORST_PERFORMERS.md)

Ranks symbols by various metrics:
- Top performers by return, win rate, Sharpe ratio
- Underperformers analysis
- Complete rankings tables
- Key insights and recommendations

---

### 4. Visualizations
**Directory:** [charts/](charts/)

Performance charts and graphs:
- **performance_metrics.png** - Win rate, returns, Sharpe, drawdown by symbol
- **trade_statistics.png** - Trade counts and win/loss breakdown
- **risk_reward_analysis.png** - Risk/reward scatter plot
- **equity_curves.png** - Equity curves for each symbol

---

## 📊 Quick Summary

### Overall Performance (V7)
- **Avg Win Rate:** 43.31%
- **Avg Total Return:** 43.06%
- **Avg Sharpe Ratio:** 0.86
- **Avg Max Drawdown:** -23.21%
- **Total Trades:** 6,075

### Top 3 Symbols by Return
1. TSLA: 94.59%
2. NVDA: 93.75%
3. AMD: 66.34%

### Bottom 3 Symbols by Return
1. META: 6.93%
2. ETH-USD: 15.90%
3. BTC-USD: 20.98%

---

## 🎯 Recommendations

1. **Focus on High Performers:** TSLA, NVDA, and AMD show exceptional returns
2. **Investigate Underperformers:** META, ETH-USD, and BTC-USD may need strategy adjustments
3. **Risk Management:** Average drawdown of -23.21% suggests room for improvement
4. **Win Rate Optimization:** 43.31% win rate could be improved with better entry/exit criteria

---

## 📁 Files Generated

- `V6_V7_COMPARISON_REPORT.md` - Comparison between iterations
- `DETAILED_SYMBOL_ANALYSIS.md` - Detailed trade analysis
- `BEST_WORST_PERFORMERS.md` - Performance rankings
- `v6_v7_comparison.json` - Comparison data (JSON)
- `charts/performance_metrics.png` - Performance charts
- `charts/trade_statistics.png` - Trade statistics charts
- `charts/risk_reward_analysis.png` - Risk/reward visualization
- `charts/equity_curves.png` - Equity curve charts

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    output_file = reports_dir / "COMPREHENSIVE_ANALYSIS_INDEX.md"
    with open(output_file, 'w') as f:
        f.write(report)
    
    return output_file

def main():
    """Main function"""
    print("="*80)
    print("🚀 COMPREHENSIVE BACKTEST ANALYSIS GENERATOR")
    print("="*80)
    print()
    
    scripts = [
        "generate_v6_v7_comparison.py",
        "generate_detailed_analysis.py",
        "generate_performers_summary.py",
        "generate_visualizations.py",
    ]
    
    results = {}
    
    for script in scripts:
        print(f"Running {script}...")
        print("-" * 80)
        success = run_script(script)
        results[script] = success
        print()
    
    print("="*80)
    print("📊 GENERATING MASTER REPORT")
    print("="*80)
    print()
    
    master_report = generate_master_report()
    
    print("="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)
    print()
    print("Generated Reports:")
    print(f"  📄 Master Index: {master_report}")
    print()
    
    for script, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {script}")
    
    print()
    print("View the master report for links to all analysis files.")
    print()

if __name__ == '__main__':
    main()

