#!/usr/bin/env python3
"""
Backtest Template
Standard template for running backtests with best practices
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from argo.backtest.strategy_backtester import StrategyBacktester
from argo.backtest.constants import BacktestConstants

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_backtest_template(
    symbol: str,
    min_confidence: float = None,
    initial_capital: float = None,
    use_enhanced_cost_model: bool = True,
    enable_volume_confirmation: bool = True
):
    """
    Template function for running a backtest
    
    Args:
        symbol: Trading symbol to backtest
        min_confidence: Minimum confidence threshold (default: BacktestConstants.DEFAULT_MIN_CONFIDENCE)
        initial_capital: Starting capital (default: BacktestConstants.DEFAULT_INITIAL_CAPITAL)
        use_enhanced_cost_model: Use EnhancedTransactionCostModel (default: True)
        enable_volume_confirmation: Enable volume confirmation filter (default: True)
    
    Returns:
        BacktestMetrics or None
    """
    # Use defaults if not specified
    if min_confidence is None:
        min_confidence = BacktestConstants.DEFAULT_MIN_CONFIDENCE
    if initial_capital is None:
        initial_capital = BacktestConstants.DEFAULT_INITIAL_CAPITAL
    
    # Initialize backtester with best practices
    backtester = StrategyBacktester(
        initial_capital=initial_capital,
        use_enhanced_cost_model=use_enhanced_cost_model,
        use_cost_modeling=True,  # Always enable cost modeling
        min_holding_bars=5  # Minimum holding period
    )
    
    logger.info(f"Running backtest for {symbol}")
    logger.info(f"  Min Confidence: {min_confidence}%")
    logger.info(f"  Initial Capital: ${initial_capital:,.2f}")
    logger.info(f"  Enhanced Cost Model: {use_enhanced_cost_model}")
    logger.info(f"  Volume Confirmation: {enable_volume_confirmation}")
    
    try:
        # Run backtest
        metrics = await backtester.run_backtest(
            symbol=symbol,
            min_confidence=min_confidence
        )
        
        if metrics is None:
            logger.error(f"Backtest returned None for {symbol}")
            return None
        
        # Validate state
        validation_issues = backtester.validate_state()
        if validation_issues:
            logger.warning(f"Validation issues found for {symbol}:")
            for issue in validation_issues:
                logger.warning(f"  - {issue}")
        
        # Log results
        logger.info(f"✅ Backtest complete for {symbol}")
        logger.info(f"  Win Rate: {metrics.win_rate_pct:.2f}%")
        logger.info(f"  Total Return: {metrics.total_return_pct:.2f}%")
        logger.info(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        logger.info(f"  Max Drawdown: {metrics.max_drawdown_pct:.2f}%")
        logger.info(f"  Profit Factor: {metrics.profit_factor:.2f}")
        logger.info(f"  Total Trades: {metrics.total_trades}")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error running backtest for {symbol}: {e}", exc_info=True)
        return None


async def main():
    """Example usage"""
    # Example: Run backtest for AAPL
    metrics = await run_backtest_template(
        symbol='AAPL',
        min_confidence=60.0,
        use_enhanced_cost_model=True,
        enable_volume_confirmation=True
    )
    
    if metrics:
        print(f"\n📊 Results:")
        print(f"  Win Rate: {metrics.win_rate_pct:.2f}%")
        print(f"  Total Return: {metrics.total_return_pct:.2f}%")
        print(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}")


if __name__ == '__main__':
    asyncio.run(main())

