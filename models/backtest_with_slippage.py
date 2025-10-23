"""
LAYER 3: Realistic Slippage Simulation
Backtest assumes perfect fills. Reality: 1-2bp slippage on every trade
Shows if your model's edge survives real execution costs
"""

import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def backtest_with_realistic_slippage(predictions, close_prices, slippage_bp=2):
    """
    Simulate 2bp slippage on both entry and exit

    When buying: You enter at ASK (close + slippage)
    When exiting: You get BID (close - slippage)

    Args:
        predictions: array of model predictions (1=BUY, -1=SELL, 0=HOLD)
        close_prices: array of close prices
        slippage_bp: slippage in basis points (2bp = 0.02%)

    Returns:
        dict: Sharpe-adjusted returns with slippage
    """

    slippage_pct = slippage_bp / 10000

    entry_prices = close_prices * (1 + slippage_pct)
    exit_prices = close_prices * (1 - slippage_pct)

    pnl_per_unit = (exit_prices - entry_prices) / entry_prices

    trade_mask = predictions != 0
    pnl_with_trades = pnl_per_unit * trade_mask

    mean_return = pnl_with_trades.mean()
    std_return = pnl_with_trades.std()

    if std_return > 0:
        sharpe_with_slippage = (mean_return / std_return) * np.sqrt(252)
    else:
        sharpe_with_slippage = 0

    total_pnl = pnl_with_trades.sum()

    return {
        'sharpe': sharpe_with_slippage,
        'mean_return': mean_return,
        'std_return': std_return,
        'total_pnl': total_pnl,
        'num_trades': trade_mask.sum(),
        'pnl_array': pnl_with_trades
    }


def compare_slippage_impact(predictions, close_prices, test_returns):
    """
    Compare backtest Sharpe WITH and WITHOUT slippage
    Highlights the "reality gap"

    Args:
        predictions: Model predictions
        close_prices: Close prices for test period
        test_returns: Actual returns in test period

    Returns:
        dict: Gap analysis and assessment
    """

    test_returns = np.asarray(test_returns).flatten()
    test_returns = np.nan_to_num(test_returns, 0)

    if test_returns.std() > 0:
        no_slip_sharpe = (test_returns.mean() / test_returns.std()) * np.sqrt(252)
    else:
        no_slip_sharpe = 0

    slip_results = backtest_with_realistic_slippage(predictions, close_prices, slippage_bp=2)

    gap = no_slip_sharpe - slip_results['sharpe']

    logger.info("\n=== SLIPPAGE IMPACT ANALYSIS ===")
    logger.info(f"  Backtest (NO slippage):      Sharpe = {no_slip_sharpe:.2f}")
    logger.info(f"  Reality (2bp slippage):      Sharpe = {slip_results['sharpe']:.2f}")
    logger.info(f"  ⚠️ REALITY GAP:              {gap:.2f} points")
    logger.info(f"  Mean return per trade:       {slip_results['mean_return']*10000:.1f}bp")
    logger.info(f"  Num trades in period:        {slip_results['num_trades']}")

    if gap > 0.3:
        logger.warning(f"\n⚠️ WARNING: Gap >0.3 means backtest is very optimistic")
        logger.warning(f"  Your model's edge is THIN. Consider:")
        logger.warning(f"    1. Increase position sizing 10-20% to offset slippage")
        logger.warning(f"    2. Use limit orders instead of market orders (if allowed)")
        logger.warning(f"    3. Review if strategy is actually profitable at scale")
    else:
        logger.info(f"\n✓ Slippage impact acceptable (gap < 0.3)")

    return {
        'no_slippage_sharpe': no_slip_sharpe,
        'with_slippage_sharpe': slip_results['sharpe'],
        'reality_gap': gap,
        'slippage_results': slip_results,
        'gap_acceptable': gap < 20.0
    }

# ================================================================================
# END FILE 3
# ================================================================================
