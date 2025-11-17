#!/usr/bin/env python3
"""
Results Analyzer
Utilities for analyzing and comparing backtest results
ENHANCED: New utility for comprehensive backtest analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from argo.backtest.results_storage import ResultsStorage
import logging

logger = logging.getLogger(__name__)

class ResultsAnalyzer:
    """
    Analyze and compare backtest results
    ENHANCED: Comprehensive analysis utilities
    """

    def __init__(self, results_storage: Optional[ResultsStorage] = None):
        self.storage = results_storage or ResultsStorage()

    def analyze_performance_trends(
        self,
        symbol: str,
        days: int = 30
    ) -> Dict:
        """
        Analyze performance trends over time for a symbol

        Args:
            symbol: Trading symbol
            days: Number of days to analyze

        Returns:
            Dictionary with trend analysis
        """
        results = self.storage.get_results(symbol=symbol, limit=100)

        if not results:
            return {"error": f"No results found for {symbol}"}

        # Filter by date
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        recent_results = [
            r for r in results
            if r.get('created_at') and datetime.fromisoformat(r['created_at']).timestamp() > cutoff_date
        ]

        if not recent_results:
            return {"error": f"No recent results found for {symbol}"}

        # Extract metrics
        returns = [r.get('total_return_pct', 0) for r in recent_results]
        sharpe_ratios = [r.get('sharpe_ratio', 0) for r in recent_results]
        win_rates = [r.get('win_rate_pct', 0) for r in recent_results]

        # Calculate trends
        trend_analysis = {
            'symbol': symbol,
            'period_days': days,
            'total_backtests': len(recent_results),
            'metrics': {
                'total_return': {
                    'current': returns[0] if returns else 0,
                    'average': np.mean(returns) if returns else 0,
                    'trend': 'improving' if len(returns) > 1 and returns[0] > returns[-1] else 'declining',
                    'volatility': np.std(returns) if returns else 0
                },
                'sharpe_ratio': {
                    'current': sharpe_ratios[0] if sharpe_ratios else 0,
                    'average': np.mean(sharpe_ratios) if sharpe_ratios else 0,
                    'trend': 'improving' if len(sharpe_ratios) > 1 and sharpe_ratios[0] > sharpe_ratios[-1] else 'declining',
                    'volatility': np.std(sharpe_ratios) if sharpe_ratios else 0
                },
                'win_rate': {
                    'current': win_rates[0] if win_rates else 0,
                    'average': np.mean(win_rates) if win_rates else 0,
                    'trend': 'improving' if len(win_rates) > 1 and win_rates[0] > win_rates[-1] else 'declining',
                    'volatility': np.std(win_rates) if win_rates else 0
                }
            }
        }

        return trend_analysis

    def find_best_strategies(
        self,
        symbol: Optional[str] = None,
        metric: str = 'sharpe_ratio',
        limit: int = 10
    ) -> List[Dict]:
        """
        Find best performing strategies

        Args:
            symbol: Optional symbol filter
            metric: Metric to rank by (sharpe_ratio, total_return_pct, etc.)
            limit: Number of results to return

        Returns:
            List of best performing backtests
        """
        results = self.storage.get_results(symbol=symbol, limit=1000)

        if not results:
            return []

        # Sort by metric
        sorted_results = sorted(
            results,
            key=lambda x: x.get(metric, 0),
            reverse=True
        )

        return sorted_results[:limit]

    def analyze_risk_return_tradeoff(
        self,
        symbol: Optional[str] = None
    ) -> Dict:
        """
        Analyze risk-return tradeoff

        Args:
            symbol: Optional symbol filter

        Returns:
            Risk-return analysis
        """
        results = self.storage.get_results(symbol=symbol, limit=1000)

        if not results:
            return {"error": "No results found"}

        # Extract risk and return metrics
        returns = [r.get('total_return_pct', 0) for r in results]
        drawdowns = [abs(r.get('max_drawdown_pct', 0)) for r in results]
        sharpe_ratios = [r.get('sharpe_ratio', 0) for r in results]
        var_95 = [r.get('var_95_pct', 0) for r in results]

        # Calculate correlations
        correlation_matrix = np.corrcoef([
            returns,
            drawdowns,
            sharpe_ratios,
            var_95
        ])

        analysis = {
            'total_backtests': len(results),
            'statistics': {
                'returns': {
                    'mean': np.mean(returns),
                    'std': np.std(returns),
                    'min': np.min(returns),
                    'max': np.max(returns)
                },
                'drawdowns': {
                    'mean': np.mean(drawdowns),
                    'std': np.std(drawdowns),
                    'min': np.min(drawdowns),
                    'max': np.max(drawdowns)
                },
                'sharpe_ratios': {
                    'mean': np.mean(sharpe_ratios),
                    'std': np.std(sharpe_ratios),
                    'min': np.min(sharpe_ratios),
                    'max': np.max(sharpe_ratios)
                }
            },
            'correlations': {
                'return_vs_drawdown': float(correlation_matrix[0, 1]),
                'return_vs_sharpe': float(correlation_matrix[0, 2]),
                'drawdown_vs_sharpe': float(correlation_matrix[1, 2])
            },
            'efficient_frontier': {
                'best_return': max(returns) if returns else 0,
                'lowest_drawdown': min(drawdowns) if drawdowns else 0,
                'best_sharpe': max(sharpe_ratios) if sharpe_ratios else 0
            }
        }

        return analysis

    def generate_performance_report(
        self,
        backtest_ids: List[str]
    ) -> Dict:
        """
        Generate comprehensive performance report for multiple backtests

        Args:
            backtest_ids: List of backtest IDs to analyze

        Returns:
            Comprehensive performance report
        """
        results = []
        for backtest_id in backtest_ids:
            result = self.storage.get_results(backtest_id=backtest_id)
            if result:
                results.append(result[0])

        if not results:
            return {"error": "No results found"}

        # Aggregate metrics
        report = {
            'backtest_ids': backtest_ids,
            'count': len(results),
            'summary': {
                'avg_return': np.mean([r.get('total_return_pct', 0) for r in results]),
                'avg_sharpe': np.mean([r.get('sharpe_ratio', 0) for r in results]),
                'avg_win_rate': np.mean([r.get('win_rate_pct', 0) for r in results]),
                'avg_max_drawdown': np.mean([r.get('max_drawdown_pct', 0) for r in results]),
                'total_trades': sum([r.get('total_trades', 0) for r in results])
            },
            'best_performers': {
                'highest_return': max(results, key=lambda x: x.get('total_return_pct', 0)),
                'best_sharpe': max(results, key=lambda x: x.get('sharpe_ratio', 0)),
                'lowest_drawdown': min(results, key=lambda x: x.get('max_drawdown_pct', 0)),
                'highest_win_rate': max(results, key=lambda x: x.get('win_rate_pct', 0))
            },
            'risk_metrics': {
                'avg_var_95': np.mean([r.get('var_95_pct', 0) for r in results]),
                'avg_cvar_95': np.mean([r.get('cvar_95_pct', 0) for r in results]),
                'avg_calmar': np.mean([r.get('calmar_ratio', 0) for r in results]),
                'avg_ulcer_index': np.mean([r.get('ulcer_index', 0) for r in results])
            }
        }

        return report
