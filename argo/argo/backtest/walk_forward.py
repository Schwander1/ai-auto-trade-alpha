#!/usr/bin/env python3
"""
Walk-Forward Testing Framework
Implements rolling window validation for robust backtesting
ENHANCED: Added parallel processing for faster execution
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
        end_date: datetime,
        parallel: bool = True
    ) -> List[Dict]:
        """
        Run walk-forward test
        ENHANCED: Added parallel processing for faster execution

        Args:
            symbol: Trading symbol
            start_date: Start date for walk-forward test
            end_date: End date for walk-forward test
            parallel: If True, run windows in parallel (faster)

        Returns:
            List of test results for each window
        """
        # Generate all windows first
        windows = []
        current_date = start_date

        while current_date + timedelta(days=self.train_days + self.test_days) <= end_date:
            train_start = current_date
            train_end = current_date + timedelta(days=self.train_days)
            test_start = train_end
            test_end = test_start + timedelta(days=self.test_days)

            windows.append({
                'train_start': train_start,
                'train_end': train_end,
                'test_start': test_start,
                'test_end': test_end
            })

            current_date += timedelta(days=self.step_days)

        logger.info(f"Running walk-forward test: {len(windows)} windows")

        # ENHANCED: Run windows in parallel if enabled
        if parallel and len(windows) > 1:
            import asyncio
            import os

            # Determine optimal concurrency
            num_cores = os.cpu_count() or 4
            max_concurrent = min(num_cores, len(windows), 8)  # Cap at 8 to prevent overload

            logger.info(f"Running {len(windows)} windows in parallel (max {max_concurrent} concurrent)")

            # Process windows in batches
            semaphore = asyncio.Semaphore(max_concurrent)

            async def run_window(window):
                async with semaphore:
                    return await self._run_single_window(symbol, window)

            # Run all windows
            tasks = [run_window(window) for window in windows]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error in window {i+1}: {result}")
                    continue
                if result:
                    self.results.append(result)
        else:
            # Sequential processing (original)
            for window in windows:
                result = await self._run_single_window(symbol, window)
                if result:
                    self.results.append(result)

        # Sort results by test_start date
        self.results.sort(key=lambda x: x['test_start'])

        return self.results

    async def _run_single_window(
        self,
        symbol: str,
        window: Dict
    ) -> Optional[Dict]:
        """Run backtest for a single window"""
        train_start = window['train_start']
        train_end = window['train_end']
        test_start = window['test_start']
        test_end = window['test_end']

        logger.info(f"Window: Train {train_start.date()} to {train_end.date()}, "
                   f"Test {test_start.date()} to {test_end.date()}")

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
            return None

        if metrics:
            return {
                'train_start': train_start,
                'train_end': train_end,
                'test_start': test_start,
                'test_end': test_end,
                'metrics': metrics
            }
        return None

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
