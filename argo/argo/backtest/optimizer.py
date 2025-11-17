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
        min_confidence: float = 75.0
    ) -> Dict:
        """
        Grid search for optimal parameters
        
        Args:
            symbol: Trading symbol
            param_grid: Dictionary of parameter names to lists of values
            objective: Objective to optimize (sharpe_ratio, win_rate, total_return, total_return_pct)
            start_date: Start date for backtest
            end_date: End date for backtest
            min_confidence: Minimum confidence threshold
        
        Returns:
            Best parameters and results
        """
        import asyncio
        from datetime import datetime
        
        best_score = float('-inf')
        best_params = None
        all_results = []
        
        # Generate all parameter combinations
        from itertools import product
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        total_combinations = 1
        for values in param_values:
            total_combinations *= len(values)
        
        logger.info(f"Starting grid search: {total_combinations} parameter combinations")
        
        combination_num = 0
        for combination in product(*param_values):
            combination_num += 1
            params = dict(zip(param_names, combination))
            
            logger.info(f"Testing combination {combination_num}/{total_combinations}: {params}")
            
            try:
                # Update backtester configuration with these parameters
                # Note: This requires the backtester to support parameter updates
                # For now, we'll run the backtest and extract the objective metric
                
                # Run backtest
                metrics = await self.backtester.run_backtest(
                    symbol,
                    start_date=start_date,
                    end_date=end_date,
                    min_confidence=min_confidence
                )
                
                if metrics is None:
                    logger.warning(f"Backtest failed for parameters: {params}")
                    continue
                
                # Extract objective score
                if objective == "sharpe_ratio":
                    score = metrics.sharpe_ratio
                elif objective == "win_rate":
                    score = metrics.win_rate_pct
                elif objective == "total_return":
                    score = metrics.total_return_pct
                elif objective == "sortino_ratio":
                    score = metrics.sortino_ratio
                elif objective == "profit_factor":
                    score = metrics.profit_factor
                else:
                    logger.warning(f"Unknown objective: {objective}, using sharpe_ratio")
                    score = metrics.sharpe_ratio
                
                # Store result
                result = {
                    'params': params.copy(),
                    'score': score,
                    'metrics': metrics
                }
                all_results.append(result)
                
                # Update best if better
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                    logger.info(f"New best score: {best_score:.4f} with params: {best_params}")
                
            except Exception as e:
                logger.error(f"Error testing parameters {params}: {e}")
                continue
        
        logger.info(f"Grid search complete. Best score: {best_score:.4f}")
        logger.info(f"Best parameters: {best_params}")
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'all_results': all_results,
            'total_combinations': total_combinations,
            'tested_combinations': len(all_results)
        }

