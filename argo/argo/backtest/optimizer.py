#!/usr/bin/env python3
"""
Parameter Optimizer
Optimizes strategy parameters using grid search or other methods
"""
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from argo.backtest.strategy_backtester import StrategyBacktester
import logging

logger = logging.getLogger(__name__)

class ParameterOptimizer:
    """Optimizes strategy parameters"""

    def __init__(self, backtester: StrategyBacktester):
        self.backtester = backtester

    async def grid_search(
        self,
        symbol: str,
        param_grid: Dict[str, List[float]],
        objective: str = "sharpe_ratio",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_confidence: float = 75.0,
        parallel: bool = True,
        max_workers: Optional[int] = None
    ) -> Dict:
        """
        Grid search for optimal parameters
        ENHANCED: Added parallel processing for faster optimization

        Args:
            symbol: Trading symbol
            param_grid: Dictionary of parameter names to lists of values
            objective: Objective to optimize (sharpe_ratio, win_rate, total_return, total_return_pct)
            start_date: Start date for backtest
            end_date: End date for backtest
            min_confidence: Minimum confidence threshold
            parallel: If True, run parameter combinations in parallel
            max_workers: Maximum number of parallel workers (default: CPU count)

        Returns:
            Best parameters and results
        """
        import asyncio
        import os
        from datetime import datetime

        # Generate all parameter combinations
        from itertools import product
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())

        total_combinations = 1
        for values in param_values:
            total_combinations *= len(values)

        logger.info(f"Starting grid search: {total_combinations} parameter combinations")

        # ENHANCED: Parallel processing for grid search
        if parallel and total_combinations > 1:
            num_cores = os.cpu_count() or 4
            max_workers = max_workers or min(num_cores, total_combinations, 8)  # Cap at 8

            logger.info(f"Running {total_combinations} combinations in parallel (max {max_workers} workers)")

            # Create semaphore to limit concurrent backtests
            semaphore = asyncio.Semaphore(max_workers)

            async def test_combination(combination, combination_num):
                async with semaphore:
                    params = dict(zip(param_names, combination))

                    if combination_num % 10 == 0:
                        logger.info(f"Testing combination {combination_num}/{total_combinations}: {params}")

                    try:
                        # Run backtest
                        metrics = await self.backtester.run_backtest(
                            symbol,
                            start_date=start_date,
                            end_date=end_date,
                            min_confidence=min_confidence
                        )

                        if metrics is None:
                            return None

                        # Extract objective score
                        score = self._extract_objective_score(metrics, objective)

                        return {
                            'params': params.copy(),
                            'score': score,
                            'metrics': metrics,
                            'combination_num': combination_num
                        }
                    except Exception as e:
                        logger.debug(f"Error testing parameters {params}: {e}")
                        return None

            # Create tasks for all combinations
            tasks = [
                test_combination(combination, i+1)
                for i, combination in enumerate(product(*param_values))
            ]

            # Run all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and None results
            all_results = [r for r in results if r is not None and not isinstance(r, Exception)]

        else:
            # Sequential processing (original)
            best_score = float('-inf')
            best_params = None
            all_results = []

            combination_num = 0
            for combination in product(*param_values):
                combination_num += 1
                params = dict(zip(param_names, combination))

                if combination_num % 10 == 0:
                    logger.info(f"Testing combination {combination_num}/{total_combinations}: {params}")

                try:
                    # Run backtest
                    metrics = await self.backtester.run_backtest(
                        symbol,
                        start_date=start_date,
                        end_date=end_date,
                        min_confidence=min_confidence
                    )

                    if metrics is None:
                        continue

                    # Extract objective score
                    score = self._extract_objective_score(metrics, objective)

                    # Store result
                    result = {
                        'params': params.copy(),
                        'score': score,
                        'metrics': metrics,
                        'combination_num': combination_num
                    }
                    all_results.append(result)

                    # Update best if better
                    if score > best_score:
                        best_score = score
                        best_params = params.copy()
                        logger.info(f"New best score: {best_score:.4f} with params: {best_params}")

                except Exception as e:
                    logger.debug(f"Error testing parameters {params}: {e}")
                    continue

        # Find best result
        if all_results:
            best_result = max(all_results, key=lambda x: x['score'])
            best_score = best_result['score']
            best_params = best_result['params']
        else:
            best_score = float('-inf')
            best_params = None

        logger.info(f"Grid search complete. Best score: {best_score:.4f}")
        logger.info(f"Best parameters: {best_params}")

        return {
            'best_params': best_params,
            'best_score': best_score,
            'all_results': all_results,
            'total_combinations': total_combinations,
            'tested_combinations': len(all_results)
        }

    def _extract_objective_score(self, metrics, objective: str) -> float:
        """Extract objective score from metrics"""
        if objective == "sharpe_ratio":
            return metrics.sharpe_ratio
        elif objective == "win_rate":
            return metrics.win_rate_pct
        elif objective == "total_return":
            return metrics.total_return_pct
        elif objective == "sortino_ratio":
            return metrics.sortino_ratio
        elif objective == "profit_factor":
            return metrics.profit_factor
        elif objective == "calmar_ratio":
            return getattr(metrics, 'calmar_ratio', 0.0)
        else:
            logger.warning(f"Unknown objective: {objective}, using sharpe_ratio")
            return metrics.sharpe_ratio
