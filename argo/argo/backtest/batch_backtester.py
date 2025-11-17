#!/usr/bin/env python3
"""
Batch Backtester
Runs backtests on multiple symbols in parallel with resource management
OPTIMIZATION: Parallel processing with controlled concurrency
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import os

from argo.backtest.strategy_backtester import StrategyBacktester
from argo.backtest.base_backtester import BacktestMetrics
from argo.backtest.constants import BacktestConstants

logger = logging.getLogger(__name__)


class BatchBacktester:
    """
    Batch backtester for running multiple symbol backtests in parallel
    OPTIMIZATION: Controlled concurrency, memory-efficient, progress tracking
    """

    def __init__(
        self,
        initial_capital: float = BacktestConstants.DEFAULT_INITIAL_CAPITAL,
        max_workers: Optional[int] = None,
        use_cost_modeling: bool = True,
        use_enhanced_cost_model: bool = True
    ):
        """
        Initialize batch backtester

        Args:
            initial_capital: Initial capital for each backtest
            max_workers: Maximum parallel workers (default: CPU count)
            use_cost_modeling: Enable transaction cost modeling
            use_enhanced_cost_model: Use enhanced cost model
        """
        self.initial_capital = initial_capital
        self.use_cost_modeling = use_cost_modeling
        self.use_enhanced_cost_model = use_enhanced_cost_model

        # Determine optimal worker count
        num_cores = os.cpu_count() or 4
        self.max_workers = max_workers or min(num_cores, 8)  # Cap at 8 to prevent overload

        logger.info(f"BatchBacktester initialized: max_workers={self.max_workers}, "
                   f"initial_capital=${initial_capital:,.2f}")

    async def run_batch(
        self,
        symbols: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_confidence: float = BacktestConstants.DEFAULT_MIN_CONFIDENCE,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Run backtests on multiple symbols in parallel

        Args:
            symbols: List of symbols to backtest
            start_date: Start date for backtests
            end_date: End date for backtests
            min_confidence: Minimum confidence threshold
            save_results: Save results to storage

        Returns:
            Dictionary with results for each symbol
        """
        logger.info(f"Starting batch backtest: {len(symbols)} symbols")

        # Create semaphore to limit concurrent backtests
        semaphore = asyncio.Semaphore(self.max_workers)

        async def run_single_backtest(symbol: str, index: int) -> tuple[str, Optional[BacktestMetrics], Optional[str]]:
            """Run a single backtest with resource management"""
            async with semaphore:
                try:
                    logger.info(f"[{index+1}/{len(symbols)}] Starting backtest for {symbol}")

                    # Create backtester instance
                    bt = StrategyBacktester(
                        initial_capital=self.initial_capital,
                        use_cost_modeling=self.use_cost_modeling,
                        use_enhanced_cost_model=self.use_enhanced_cost_model
                    )

                    # Run backtest
                    result = await bt.run_backtest(
                        symbol,
                        start_date=start_date,
                        end_date=end_date,
                        min_confidence=min_confidence
                    )

                    if result:
                        logger.info(f"[{index+1}/{len(symbols)}] ✅ {symbol}: "
                                   f"{result.total_return_pct:.2f}% return, "
                                   f"{result.win_rate_pct:.1f}% win rate, "
                                   f"{result.sharpe_ratio:.2f} Sharpe")

                        # Save results if enabled
                        if save_results:
                            try:
                                from argo.backtest.results_storage import ResultsStorage
                                storage = ResultsStorage()
                                storage.save_result(
                                    backtest_id=f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                    symbol=symbol,
                                    metrics=result,
                                    start_date=start_date,
                                    end_date=end_date
                                )
                            except Exception as e:
                                logger.debug(f"Failed to save results for {symbol}: {e}")

                        return symbol, result, None
                    else:
                        logger.warning(f"[{index+1}/{len(symbols)}] ⚠️ {symbol}: No results")
                        return symbol, None, "No results"

                except Exception as e:
                    logger.error(f"[{index+1}/{len(symbols)}] ❌ {symbol}: Error - {e}", exc_info=True)
                    return symbol, None, str(e)

        # Run all backtests in parallel
        tasks = [run_single_backtest(symbol, i) for i, symbol in enumerate(symbols)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        successful = {}
        failed = {}

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Unexpected error in batch backtest: {result}")
                continue

            symbol, metrics, error = result
            if metrics:
                successful[symbol] = metrics
            else:
                failed[symbol] = error or "Unknown error"

        # Calculate aggregate statistics
        aggregate_stats = self._calculate_aggregate_stats(successful)

        logger.info(f"Batch backtest complete: {len(successful)} successful, {len(failed)} failed")

        return {
            'successful': successful,
            'failed': failed,
            'total_symbols': len(symbols),
            'successful_count': len(successful),
            'failed_count': len(failed),
            'aggregate_stats': aggregate_stats
        }

    def _calculate_aggregate_stats(self, results: Dict[str, BacktestMetrics]) -> Dict[str, Any]:
        """Calculate aggregate statistics across all backtests"""
        if not results:
            return {}

        # Calculate averages
        total_returns = [r.total_return_pct for r in results.values()]
        sharpe_ratios = [r.sharpe_ratio for r in results.values()]
        win_rates = [r.win_rate_pct for r in results.values()]
        max_drawdowns = [r.max_drawdown_pct for r in results.values()]

        # Find best and worst performers
        best_symbol = max(results.keys(), key=lambda s: results[s].total_return_pct)
        worst_symbol = min(results.keys(), key=lambda s: results[s].total_return_pct)

        return {
            'avg_total_return_pct': sum(total_returns) / len(total_returns),
            'avg_sharpe_ratio': sum(sharpe_ratios) / len(sharpe_ratios),
            'avg_win_rate_pct': sum(win_rates) / len(win_rates),
            'avg_max_drawdown_pct': sum(max_drawdowns) / len(max_drawdowns),
            'best_symbol': best_symbol,
            'best_return_pct': results[best_symbol].total_return_pct,
            'worst_symbol': worst_symbol,
            'worst_return_pct': results[worst_symbol].total_return_pct,
            'total_trades': sum(r.total_trades for r in results.values()),
            'total_winning_trades': sum(r.winning_trades for r in results.values()),
            'total_losing_trades': sum(r.losing_trades for r in results.values())
        }

    async def run_batch_from_file(
        self,
        symbols_file: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run batch backtest from a file containing symbols (one per line)

        Args:
            symbols_file: Path to file with symbols (one per line)
            **kwargs: Additional arguments passed to run_batch

        Returns:
            Dictionary with results
        """
        symbols_path = Path(symbols_file)
        if not symbols_path.exists():
            raise FileNotFoundError(f"Symbols file not found: {symbols_file}")

        # Read symbols from file
        with open(symbols_path, 'r') as f:
            symbols = [line.strip().upper() for line in f if line.strip() and not line.startswith('#')]

        logger.info(f"Loaded {len(symbols)} symbols from {symbols_file}")

        return await self.run_batch(symbols, **kwargs)
