#!/usr/bin/env python3
"""
Result Visualizer
Generate visualizations and summaries of backtest results
"""
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class ResultVisualizer:
    """
    Generate visualizations and summaries of backtest results
    """

    @staticmethod
    def generate_summary_text(metrics: Any, symbol: Optional[str] = None) -> str:
        """
        Generate text summary of backtest results

        Args:
            metrics: BacktestMetrics object or dictionary
            symbol: Optional symbol name

        Returns:
            Formatted text summary
        """
        # Convert to dict if needed
        if hasattr(metrics, '__dict__'):
            data = metrics.__dict__
        elif isinstance(metrics, dict):
            data = metrics
        else:
            return "Invalid metrics format"

        symbol_str = f" for {symbol}" if symbol else ""
        summary = f"""
{'='*80}
BACKTEST RESULTS{symbol_str}
{'='*80}

PERFORMANCE METRICS:
  Total Return:        {data.get('total_return_pct', 0):.2f}%
  Annualized Return:   {data.get('annualized_return_pct', 0):.2f}%
  Sharpe Ratio:        {data.get('sharpe_ratio', 0):.2f}
  Sortino Ratio:       {data.get('sortino_ratio', 0):.2f}
  Max Drawdown:        {data.get('max_drawdown_pct', 0):.2f}%
  Calmar Ratio:        {data.get('calmar_ratio', 0):.2f}

TRADE STATISTICS:
  Total Trades:        {data.get('total_trades', 0)}
  Winning Trades:      {data.get('winning_trades', 0)}
  Losing Trades:       {data.get('losing_trades', 0)}
  Win Rate:            {data.get('win_rate_pct', 0):.2f}%
  Profit Factor:       {data.get('profit_factor', 0):.2f}

TRADE PERFORMANCE:
  Avg Win:             {data.get('avg_win_pct', 0):.2f}%
  Avg Loss:            {data.get('avg_loss_pct', 0):.2f}%
  Largest Win:         {data.get('largest_win_pct', 0):.2f}%
  Largest Loss:        {data.get('largest_loss_pct', 0):.2f}%

RISK METRICS:
  VaR (95%):           {data.get('var_95_pct', 0):.2f}%
  CVaR (95%):          {data.get('cvar_95_pct', 0):.2f}%
  Omega Ratio:         {data.get('omega_ratio', 0):.2f}
  Ulcer Index:         {data.get('ulcer_index', 0):.2f}

{'='*80}
"""
        return summary

    @staticmethod
    def plot_equity_curve(
        equity_curve: List[float],
        dates: List[Any],
        output_path: Optional[str] = None,
        title: str = "Equity Curve"
    ) -> bool:
        """
        Plot equity curve

        Args:
            equity_curve: List of equity values
            dates: List of dates
            output_path: Optional path to save plot
            title: Plot title

        Returns:
            True if successful
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib not available - cannot generate plots")
            return False

        try:
            fig, ax = plt.subplots(figsize=(12, 6))

            # Convert dates if needed
            if PANDAS_AVAILABLE and dates:
                try:
                    dates = pd.to_datetime(dates)
                except:
                    pass

            ax.plot(dates, equity_curve, linewidth=2, color='#2E86AB')
            ax.fill_between(dates, equity_curve, alpha=0.3, color='#2E86AB')
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Equity ($)', fontsize=12)
            ax.grid(True, alpha=0.3)

            # Format x-axis dates
            if dates and len(dates) > 0:
                try:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                    plt.xticks(rotation=45)
                except:
                    pass

            plt.tight_layout()

            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                logger.info(f"✅ Saved equity curve plot: {output_path}")
            else:
                plt.show()

            plt.close()
            return True
        except Exception as e:
            logger.error(f"Failed to plot equity curve: {e}", exc_info=True)
            return False

    @staticmethod
    def plot_drawdown(
        equity_curve: List[float],
        dates: List[Any],
        output_path: Optional[str] = None,
        title: str = "Drawdown Chart"
    ) -> bool:
        """
        Plot drawdown chart

        Args:
            equity_curve: List of equity values
            dates: List of dates
            output_path: Optional path to save plot
            title: Plot title

        Returns:
            True if successful
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib not available - cannot generate plots")
            return False

        try:
            import numpy as np

            # Calculate drawdown
            equity_array = np.array(equity_curve)
            cumulative_max = np.maximum.accumulate(equity_array)
            drawdown = (equity_array - cumulative_max) / cumulative_max * 100

            fig, ax = plt.subplots(figsize=(12, 6))

            # Convert dates if needed
            if PANDAS_AVAILABLE and dates:
                try:
                    dates = pd.to_datetime(dates)
                except:
                    pass

            ax.fill_between(dates, drawdown, 0, alpha=0.5, color='#D32F2F')
            ax.plot(dates, drawdown, linewidth=1, color='#B71C1C')
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Drawdown (%)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

            # Format x-axis dates
            if dates and len(dates) > 0:
                try:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                    plt.xticks(rotation=45)
                except:
                    pass

            plt.tight_layout()

            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                logger.info(f"✅ Saved drawdown plot: {output_path}")
            else:
                plt.show()

            plt.close()
            return True
        except Exception as e:
            logger.error(f"Failed to plot drawdown: {e}", exc_info=True)
            return False

    @staticmethod
    def plot_batch_comparison(
        batch_results: Dict[str, Any],
        output_path: Optional[str] = None,
        metric: str = 'total_return_pct'
    ) -> bool:
        """
        Plot comparison of multiple symbols from batch results

        Args:
            batch_results: Results from BatchBacktester
            output_path: Optional path to save plot
            metric: Metric to compare ('total_return_pct', 'sharpe_ratio', etc.)

        Returns:
            True if successful
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib not available - cannot generate plots")
            return False

        if 'successful' not in batch_results:
            logger.warning("No successful results to plot")
            return False

        try:
            symbols = []
            values = []

            for symbol, metrics in batch_results['successful'].items():
                if hasattr(metrics, '__dict__'):
                    data = metrics.__dict__
                elif isinstance(metrics, dict):
                    data = metrics
                else:
                    continue

                value = data.get(metric, 0)
                symbols.append(symbol)
                values.append(value)

            if not symbols:
                logger.warning("No valid data to plot")
                return False

            fig, ax = plt.subplots(figsize=(12, 6))

            # Sort by value
            sorted_data = sorted(zip(symbols, values), key=lambda x: x[1], reverse=True)
            symbols, values = zip(*sorted_data)

            colors = ['#2E86AB' if v >= 0 else '#D32F2F' for v in values]
            ax.barh(symbols, values, color=colors, alpha=0.7)
            ax.set_title(f'Batch Backtest Comparison: {metric.replace("_", " ").title()}',
                        fontsize=14, fontweight='bold')
            ax.set_xlabel(metric.replace('_', ' ').title(), fontsize=12)
            ax.set_ylabel('Symbol', fontsize=12)
            ax.grid(True, alpha=0.3, axis='x')
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)

            plt.tight_layout()

            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                logger.info(f"✅ Saved batch comparison plot: {output_path}")
            else:
                plt.show()

            plt.close()
            return True
        except Exception as e:
            logger.error(f"Failed to plot batch comparison: {e}", exc_info=True)
            return False

    @staticmethod
    def generate_report(
        metrics: Any,
        equity_curve: Optional[List[float]] = None,
        dates: Optional[List[Any]] = None,
        output_dir: str = "argo/data/reports",
        symbol: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Generate comprehensive report with summary and plots

        Args:
            metrics: BacktestMetrics object or dictionary
            equity_curve: Optional equity curve data
            dates: Optional dates for equity curve
            output_dir: Output directory
            symbol: Optional symbol name

        Returns:
            Dictionary of generated files and success status
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = symbol or "backtest"
        results = {}

        # Generate text summary
        summary_text = ResultVisualizer.generate_summary_text(metrics, symbol)
        summary_file = output_path / f"{timestamp}_summary.txt"
        try:
            with open(summary_file, 'w') as f:
                f.write(summary_text)
            results['summary'] = True
            logger.info(f"✅ Generated summary: {summary_file}")
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            results['summary'] = False

        # Generate plots if data available
        if equity_curve and dates and MATPLOTLIB_AVAILABLE:
            equity_file = output_path / f"{timestamp}_equity_curve.png"
            results['equity_plot'] = ResultVisualizer.plot_equity_curve(
                equity_curve, dates, str(equity_file),
                title=f"Equity Curve - {symbol}" if symbol else "Equity Curve"
            )

            drawdown_file = output_path / f"{timestamp}_drawdown.png"
            results['drawdown_plot'] = ResultVisualizer.plot_drawdown(
                equity_curve, dates, str(drawdown_file),
                title=f"Drawdown Chart - {symbol}" if symbol else "Drawdown Chart"
            )

        return results
