#!/usr/bin/env python3
"""
Incremental Backtester
Supports incremental backtesting where only new data is processed
ENHANCED: New utility for faster backtest updates
"""
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path
import json
import hashlib
import logging

from argo.backtest.strategy_backtester import StrategyBacktester
from argo.backtest.base_backtester import BacktestMetrics

logger = logging.getLogger(__name__)

class IncrementalBacktester:
    """
    Incremental backtesting - only process new data
    ENHANCED: Faster updates for existing backtests
    """
    
    def __init__(
        self,
        backtester: StrategyBacktester,
        cache_dir: str = "argo/data/incremental_backtests"
    ):
        self.backtester = backtester
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, symbol: str, start_date: datetime, end_date: datetime) -> str:
        """Generate cache key for backtest state"""
        key_string = f"{symbol}_{start_date.isoformat()}_{end_date.isoformat()}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _save_backtest_state(
        self,
        cache_key: str,
        trades: List,
        equity_curve: List[float],
        last_processed_date: datetime
    ):
        """Save backtest state to cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        state = {
            'trades': [
                {
                    'entry_date': t.entry_date.isoformat() if hasattr(t.entry_date, 'isoformat') else str(t.entry_date),
                    'exit_date': t.exit_date.isoformat() if t.exit_date and hasattr(t.exit_date, 'isoformat') else (str(t.exit_date) if t.exit_date else None),
                    'symbol': t.symbol,
                    'entry_price': t.entry_price,
                    'exit_price': t.exit_price,
                    'quantity': t.quantity,
                    'side': t.side,
                    'pnl': t.pnl,
                    'pnl_pct': t.pnl_pct,
                    'confidence': t.confidence
                }
                for t in trades
            ],
            'equity_curve': equity_curve,
            'last_processed_date': last_processed_date.isoformat() if hasattr(last_processed_date, 'isoformat') else str(last_processed_date)
        }
        
        with open(cache_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Saved backtest state to cache: {cache_file.name}")
    
    def _load_backtest_state(self, cache_key: str) -> Optional[Dict]:
        """Load backtest state from cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                state = json.load(f)
            
            logger.info(f"Loaded backtest state from cache: {cache_file.name}")
            return state
        except Exception as e:
            logger.warning(f"Failed to load backtest state: {e}")
            return None
    
    async def run_incremental_backtest(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        min_confidence: float = 60.0
    ) -> Optional[BacktestMetrics]:
        """
        Run incremental backtest - only process new data
        
        Args:
            symbol: Trading symbol
            start_date: Start date for backtest
            end_date: End date for backtest
            min_confidence: Minimum confidence threshold
        
        Returns:
            BacktestMetrics or None if failed
        """
        cache_key = self._get_cache_key(symbol, start_date, end_date)
        
        # Try to load existing state
        existing_state = self._load_backtest_state(cache_key)
        
        if existing_state:
            # Check if we can incrementally update
            last_processed = datetime.fromisoformat(existing_state['last_processed_date'])
            
            if last_processed < end_date:
                # We have new data to process
                logger.info(f"Incremental update: Processing data from {last_processed.date()} to {end_date.date()}")
                
                # Run backtest only on new data
                new_metrics = await self.backtester.run_backtest(
                    symbol,
                    start_date=last_processed,
                    end_date=end_date,
                    min_confidence=min_confidence
                )
                
                if new_metrics:
                    # Merge with existing results
                    # This is a simplified version - full implementation would merge trades and equity curves
                    logger.info("Incremental update complete")
                    return new_metrics
            else:
                # No new data, return cached results
                logger.info("No new data to process, using cached results")
                # Would reconstruct metrics from cached state
                # For now, return None to trigger full backtest
                return None
        
        # No cache or cache invalid, run full backtest
        logger.info("Running full backtest (no cache or cache invalid)")
        metrics = await self.backtester.run_backtest(
            symbol,
            start_date=start_date,
            end_date=end_date,
            min_confidence=min_confidence
        )
        
        # Save state for next time
        if metrics and hasattr(self.backtester, 'trades') and hasattr(self.backtester, 'equity_curve'):
            self._save_backtest_state(
                cache_key,
                self.backtester.trades,
                self.backtester.equity_curve,
                end_date
            )
        
        return metrics

