#!/usr/bin/env python3
"""
Walk-Forward Testing Framework
Implements rolling window validation for robust backtesting
"""
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from argo.backtest.base_backtester import BaseBacktester, BacktestMetrics
import logging

logger = logging.getLogger(__name__)

class WalkForwardTester:
    """Walk-forward testing with rolling windows"""
    
    def __init__(
        self,
        backtester: BaseBacktester,
        train_days: int = 252,  # 1 year
        test_days: int = 63,    # 1 quarter
        step_days: int = 21     # 1 month
    ):
        """
        Initialize walk-forward tester
        
        Args:
            backtester: Backtester instance to use
            train_days: Training window size in days
            test_days: Testing window size in days
            step_days: Step size between windows
        """
        self.backtester = backtester
        self.train_days = train_days
        self.test_days = test_days
        self.step_days = step_days
        self.results: List[Dict] = []
        
    async def run_walk_forward(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Run walk-forward test
        
        Returns:
            List of test results for each window
        """
        current_date = start_date
        
        while current_date + timedelta(days=self.train_days + self.test_days) <= end_date:
            train_start = current_date
            train_end = current_date + timedelta(days=self.train_days)
            test_start = train_end
            test_end = test_start + timedelta(days=self.test_days)
            
            logger.info(f"Window: Train {train_start.date()} to {train_end.date()}, "
                       f"Test {test_start.date()} to {test_end.date()}")
            
            # Run backtest on test period
            # Note: run_backtest is async, so we need to handle it properly
            import asyncio
            try:
                # Check if backtester has async run_backtest
                if asyncio.iscoroutinefunction(self.backtester.run_backtest):
                    metrics = await self.backtester.run_backtest(
                        symbol,
                        start_date=test_start,
                        end_date=test_end
                    )
                else:
                    # Fallback for sync backtesters
                    metrics = self.backtester.run_backtest(
                        symbol,
                        start_date=test_start,
                        end_date=test_end
                    )
            except Exception as e:
                logger.error(f"Error running backtest for window: {e}")
                metrics = None
            
            if metrics:
                self.results.append({
                    'train_start': train_start,
                    'train_end': train_end,
                    'test_start': test_start,
                    'test_end': test_end,
                    'metrics': metrics
                })
            
            # Move to next window
            current_date += timedelta(days=self.step_days)
        
        return self.results
    
    def get_summary(self) -> Dict:
        """Get summary statistics across all windows"""
        if not self.results:
            return {}
        
        returns = [r['metrics'].total_return_pct for r in self.results]
        win_rates = [r['metrics'].win_rate_pct for r in self.results]
        sharpe_ratios = [r['metrics'].sharpe_ratio for r in self.results]
        
        return {
            'total_windows': len(self.results),
            'avg_return': sum(returns) / len(returns),
            'std_return': pd.Series(returns).std(),
            'avg_win_rate': sum(win_rates) / len(win_rates),
            'avg_sharpe': sum(sharpe_ratios) / len(sharpe_ratios),
            'consistency': len([r for r in returns if r > 0]) / len(returns)
        }

