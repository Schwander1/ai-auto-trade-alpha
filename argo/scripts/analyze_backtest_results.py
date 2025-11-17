#!/usr/bin/env python3
"""
Backtest Results Analyzer
Comprehensive analysis and visualization of backtest results
"""
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BacktestResultsAnalyzer:
    """Analyze and visualize backtest results"""
    
    def __init__(self, results_file: str = "argo/reports/comprehensive_backtest_results.json"):
        """Initialize analyzer with results file"""
        self.results_file = Path(results_file)
        self.results = None
        self.df = None
        
    def load_results(self) -> bool:
        """Load backtest results from JSON file"""
        try:
            with open(self.results_file, 'r') as f:
                self.results = json.load(f)
            logger.info(f"✅ Loaded results from {self.results_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to load results: {e}")
            return False
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert results to pandas DataFrame for analysis"""
        if not self.results:
            self.load_results()
        
        rows = []
        for config_name, config_results in self.results.items():
            for result in config_results:
                row = {
                    'config': config_name,
                    **result
                }
                rows.append(row)
        
        self.df = pd.DataFrame(rows)
        logger.info(f"✅ Converted to DataFrame: {len(self.df)} rows")
        return self.df
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics across all configurations"""
        if self.df is None:
            self.to_dataframe()
        
        summary = {
            'total_backtests': len(self.df),
            'total_symbols': self.df['symbol'].nunique(),
            'total_configs': self.df['config'].nunique(),
            'total_trades': int(self.df['total_trades'].sum()),
            'avg_win_rate': float(self.df['win_rate'].mean()),
            'avg_return': float(self.df['total_return'].mean()),
            'avg_sharpe': float(self.df['sharpe_ratio'].mean()),
            'avg_max_drawdown': float(self.df['max_drawdown'].mean()),
            'best_config': self._get_best_config(),
            'best_symbol': self._get_best_symbol(),
            'worst_config': self._get_worst_config(),
            'worst_symbol': self._get_worst_symbol()
        }
        
        return summary
    
    def _get_best_config(self) -> Dict:
        """Get best performing configuration"""
        if self.df is None:
            self.to_dataframe()
        
        config_stats = self.df.groupby('config').agg({
            'win_rate': 'mean',
            'total_return': 'mean',
            'sharpe_ratio': 'mean',
            'total_trades': 'sum'
        }).reset_index()
        
        # Score = weighted combination of metrics
        config_stats['score'] = (
            config_stats['win_rate'] * 0.3 +
            config_stats['total_return'] * 0.3 +
            config_stats['sharpe_ratio'] * 100 * 0.4
        )
        
        best = config_stats.loc[config_stats['score'].idxmax()]
        return {
            'config': best['config'],
            'win_rate': float(best['win_rate']),
            'total_return': float(best['total_return']),
            'sharpe_ratio': float(best['sharpe_ratio']),
            'total_trades': int(best['total_trades'])
        }
    
    def _get_worst_config(self) -> Dict:
        """Get worst performing configuration"""
        if self.df is None:
            self.to_dataframe()
        
        config_stats = self.df.groupby('config').agg({
            'win_rate': 'mean',
            'total_return': 'mean',
            'sharpe_ratio': 'mean',
            'total_trades': 'sum'
        }).reset_index()
        
        config_stats['score'] = (
            config_stats['win_rate'] * 0.3 +
            config_stats['total_return'] * 0.3 +
            config_stats['sharpe_ratio'] * 100 * 0.4
        )
        
        worst = config_stats.loc[config_stats['score'].idxmin()]
        return {
            'config': worst['config'],
            'win_rate': float(worst['win_rate']),
            'total_return': float(worst['total_return']),
            'sharpe_ratio': float(worst['sharpe_ratio']),
            'total_trades': int(worst['total_trades'])
        }
    
    def _get_best_symbol(self) -> Dict:
        """Get best performing symbol"""
        if self.df is None:
            self.to_dataframe()
        
        symbol_stats = self.df.groupby('symbol').agg({
            'win_rate': 'mean',
            'total_return': 'mean',
            'sharpe_ratio': 'mean',
            'total_trades': 'sum'
        }).reset_index()
        
        symbol_stats['score'] = (
            symbol_stats['win_rate'] * 0.3 +
            symbol_stats['total_return'] * 0.3 +
            symbol_stats['sharpe_ratio'] * 100 * 0.4
        )
        
        best = symbol_stats.loc[symbol_stats['score'].idxmax()]
        return {
            'symbol': best['symbol'],
            'win_rate': float(best['win_rate']),
            'total_return': float(best['total_return']),
            'sharpe_ratio': float(best['sharpe_ratio']),
            'total_trades': int(best['total_trades'])
        }
    
    def _get_worst_symbol(self) -> Dict:
        """Get worst performing symbol"""
        if self.df is None:
            self.to_dataframe()
        
        symbol_stats = self.df.groupby('symbol').agg({
            'win_rate': 'mean',
            'total_return': 'mean',
            'sharpe_ratio': 'mean',
            'total_trades': 'sum'
        }).reset_index()
        
        symbol_stats['score'] = (
            symbol_stats['win_rate'] * 0.3 +
            symbol_stats['total_return'] * 0.3 +
            symbol_stats['sharpe_ratio'] * 100 * 0.4
        )
        
        worst = symbol_stats.loc[symbol_stats['score'].idxmin()]
        return {
            'symbol': worst['symbol'],
            'win_rate': float(worst['win_rate']),
            'total_return': float(worst['total_return']),
            'sharpe_ratio': float(worst['sharpe_ratio']),
            'total_trades': int(worst['total_trades'])
        }
    
    def compare_configs(self) -> pd.DataFrame:
        """Compare performance across configurations"""
        if self.df is None:
            self.to_dataframe()
        
        comparison = self.df.groupby('config').agg({
            'win_rate': ['mean', 'std', 'min', 'max'],
            'total_return': ['mean', 'std', 'min', 'max'],
            'sharpe_ratio': ['mean', 'std', 'min', 'max'],
            'max_drawdown': ['mean', 'std', 'min', 'max'],
            'total_trades': ['sum', 'mean']
        }).round(2)
        
        return comparison
    
    def compare_symbols(self) -> pd.DataFrame:
        """Compare performance across symbols"""
        if self.df is None:
            self.to_dataframe()
        
        comparison = self.df.groupby('symbol').agg({
            'win_rate': ['mean', 'std', 'min', 'max'],
            'total_return': ['mean', 'std', 'min', 'max'],
            'sharpe_ratio': ['mean', 'std', 'min', 'max'],
            'max_drawdown': ['mean', 'std', 'min', 'max'],
            'total_trades': ['sum', 'mean']
        }).round(2)
        
        return comparison
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate comprehensive analysis report"""
        if self.df is None:
            self.to_dataframe()
        
        summary = self.get_summary_stats()
        config_comparison = self.compare_configs()
        symbol_comparison = self.compare_symbols()
        
        report = f"""
# Backtest Results Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

**Total Backtests:** {summary['total_backtests']}
**Total Symbols:** {summary['total_symbols']}
**Total Configurations:** {summary['total_configs']}
**Total Trades:** {summary['total_trades']:,}

### Average Performance
- **Win Rate:** {summary['avg_win_rate']:.2f}%
- **Total Return:** {summary['avg_return']:.2f}%
- **Sharpe Ratio:** {summary['avg_sharpe']:.2f}
- **Max Drawdown:** {summary['avg_max_drawdown']:.2f}%

### Best Configuration
- **Config:** {summary['best_config']['config']}
- **Win Rate:** {summary['best_config']['win_rate']:.2f}%
- **Total Return:** {summary['best_config']['total_return']:.2f}%
- **Sharpe Ratio:** {summary['best_config']['sharpe_ratio']:.2f}
- **Total Trades:** {summary['best_config']['total_trades']:,}

### Best Symbol
- **Symbol:** {summary['best_symbol']['symbol']}
- **Win Rate:** {summary['best_symbol']['win_rate']:.2f}%
- **Total Return:** {summary['best_symbol']['total_return']:.2f}%
- **Sharpe Ratio:** {summary['best_symbol']['sharpe_ratio']:.2f}
- **Total Trades:** {summary['best_symbol']['total_trades']:,}

## Configuration Comparison

{config_comparison.to_string()}

## Symbol Comparison

{symbol_comparison.to_string()}

## Detailed Results

### Top 10 Performers (by Sharpe Ratio)
{self.df.nlargest(10, 'sharpe_ratio')[['symbol', 'config', 'win_rate', 'total_return', 'sharpe_ratio', 'total_trades']].to_string(index=False)}

### Bottom 10 Performers (by Sharpe Ratio)
{self.df.nsmallest(10, 'sharpe_ratio')[['symbol', 'config', 'win_rate', 'total_return', 'sharpe_ratio', 'total_trades']].to_string(index=False)}

### Most Active (by Trade Count)
{self.df.nlargest(10, 'total_trades')[['symbol', 'config', 'win_rate', 'total_return', 'sharpe_ratio', 'total_trades']].to_string(index=False)}
"""
        
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(report)
            logger.info(f"✅ Report saved to {output_path}")
        
        return report
    
    def export_to_csv(self, output_file: str = "argo/reports/backtest_results_analysis.csv"):
        """Export results to CSV for further analysis"""
        if self.df is None:
            self.to_dataframe()
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(output_path, index=False)
        logger.info(f"✅ Results exported to {output_path}")

def main():
    """Main analysis function"""
    analyzer = BacktestResultsAnalyzer()
    
    if not analyzer.load_results():
        print("❌ Failed to load results")
        return
    
    print("\n" + "="*80)
    print("📊 BACKTEST RESULTS ANALYSIS")
    print("="*80)
    
    # Generate summary
    summary = analyzer.get_summary_stats()
    print("\n📈 Summary Statistics:")
    print(f"   Total Backtests: {summary['total_backtests']}")
    print(f"   Total Symbols: {summary['total_symbols']}")
    print(f"   Total Configurations: {summary['total_configs']}")
    print(f"   Total Trades: {summary['total_trades']:,}")
    print(f"   Avg Win Rate: {summary['avg_win_rate']:.2f}%")
    print(f"   Avg Return: {summary['avg_return']:.2f}%")
    print(f"   Avg Sharpe: {summary['avg_sharpe']:.2f}")
    
    print("\n🏆 Best Configuration:")
    best_config = summary['best_config']
    print(f"   Config: {best_config['config']}")
    print(f"   Win Rate: {best_config['win_rate']:.2f}%")
    print(f"   Return: {best_config['total_return']:.2f}%")
    print(f"   Sharpe: {best_config['sharpe_ratio']:.2f}")
    
    print("\n📊 Configuration Comparison:")
    print(analyzer.compare_configs())
    
    print("\n📊 Symbol Comparison:")
    print(analyzer.compare_symbols())
    
    # Generate full report
    report_file = "argo/reports/backtest_analysis_report.md"
    analyzer.generate_report(report_file)
    print(f"\n✅ Full report saved to: {report_file}")
    
    # Export to CSV
    analyzer.export_to_csv()
    print(f"✅ Results exported to CSV")

if __name__ == "__main__":
    main()

