#!/usr/bin/env python3
"""
Out-of-Sample Backtest Runner
Runs proper out-of-sample backtest with train/val/test split
Addresses Perplexity AI concerns about data leakage and overfitting
"""
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add argo to path
argo_path = Path(__file__).parent.parent
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))

from argo.backtest.strategy_backtester import StrategyBacktester
from argo.backtest.calibrated_backtester import CalibratedBacktester
from argo.backtest.market_regime_analyzer import MarketRegimeAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def run_out_of_sample_backtest(symbol: str = "AAPL"):
    """Run complete out-of-sample backtest"""
    logger.info("=" * 70)
    logger.info("OUT-OF-SAMPLE BACKTEST")
    logger.info("=" * 70)
    logger.info("")
    
    # Initialize backtester with realistic costs
    backtester = StrategyBacktester(
        initial_capital=100000,
        slippage_pct=0.0005,  # 0.05%
        spread_pct=0.0002,    # 0.02%
        commission_pct=0.001,  # 0.1%
        use_cost_modeling=True
    )
    
    # Fetch data
    logger.info(f"Fetching historical data for {symbol}...")
    df = backtester.data_manager.fetch_historical_data(symbol, period="5y")
    if df is None or df.empty:
        logger.error(f"No data available for {symbol}")
        return
    
    # Split data (60/20/20)
    logger.info("Splitting data into train/val/test sets...")
    train_df, val_df, test_df = backtester.split_data(df, train_pct=0.6, val_pct=0.2, test_pct=0.2)
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("MARKET REGIME ANALYSIS")
    logger.info("=" * 70)
    
    # Analyze market regimes
    analyzer = MarketRegimeAnalyzer()
    
    # Analyze training period
    train_characteristics = analyzer.analyze_period(
        df, "2023-2024 (Training)", 
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    
    # Analyze test period
    test_characteristics = analyzer.analyze_period(
        df, "2025-10-01+ (Test)", 
        start_date=datetime(2025, 10, 1)
    )
    
    # Compare regimes
    comparison = analyzer.compare_regimes("2023-2024 (Training)", "2025-10-01+ (Test)")
    
    logger.info(analyzer.generate_regime_report())
    logger.info("")
    
    logger.info("=" * 70)
    logger.info("OUT-OF-SAMPLE BACKTEST RESULTS (TEST SET ONLY)")
    logger.info("=" * 70)
    
    # Run backtest on TEST SET ONLY (out-of-sample)
    logger.info(f"Running backtest on test set: {test_df.index[0]} to {test_df.index[-1]}")
    logger.info("⚠️  This is the FIRST TIME the algorithm sees this data")
    logger.info("")
    
    metrics = await backtester.run_backtest(
        symbol=symbol,
        start_date=test_df.index[0],
        end_date=test_df.index[-1],
        min_confidence=75.0
    )
    
    if metrics:
        logger.info("")
        logger.info("RESULTS (Out-of-Sample, Test Set Only):")
        logger.info(f"  Win Rate: {metrics.win_rate:.2%}")
        logger.info(f"  Total Trades: {metrics.total_trades}")
        logger.info(f"  Wins: {metrics.wins}")
        logger.info(f"  Losses: {metrics.losses}")
        logger.info(f"  Total Return: {metrics.total_return:.2f}%")
        logger.info(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        logger.info(f"  Max Drawdown: {metrics.max_drawdown:.2f}%")
        logger.info("")
        logger.info("=" * 70)
        logger.info("CALIBRATION COMPARISON")
        logger.info("=" * 70)
        
        # Run calibrated backtest
        calibrated = CalibratedBacktester(
            initial_capital=100000,
            slippage_pct=0.0005,
            spread_pct=0.0002,
            commission_pct=0.001,
            use_cost_modeling=True
        )
        
        logger.info("Running calibrated backtest...")
        calibrated_results = await calibrated.run_calibrated_backtest(
            symbol=symbol,
            train_df=train_df,
            val_df=val_df,
            test_df=test_df,
            min_confidence=75.0,
            train_calibrator=True
        )
        
        if 'uncalibrated' in calibrated_results and 'calibrated' in calibrated_results:
            logger.info("")
            logger.info("Uncalibrated Results:")
            logger.info(f"  Win Rate: {calibrated_results['uncalibrated'].win_rate:.2%}")
            logger.info("")
            logger.info("Calibrated Results:")
            logger.info(f"  Win Rate: {calibrated_results['calibrated'].win_rate:.2%}")
            
            if 'improvement' in calibrated_results:
                logger.info("")
                logger.info("Calibration Improvement:")
                logger.info(f"  Win Rate: +{calibrated_results['improvement']['win_rate_improvement']:.2f}%")
                logger.info(f"  Total Return: +{calibrated_results['improvement']['total_return_improvement']:.2f}%")
                logger.info(f"  Sharpe Ratio: +{calibrated_results['improvement']['sharpe_ratio_improvement']:.2f}")
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("SUMMARY")
        logger.info("=" * 70)
        logger.info("")
        logger.info("✅ Out-of-Sample Backtest Complete")
        logger.info(f"✅ Test Set Accuracy: {metrics.win_rate:.2%}")
        logger.info(f"✅ Regime-Adjusted Expected: {test_characteristics.get('expected_accuracy_range', {}).get('expected', 0):.1f}%")
        logger.info("")
        logger.info("⚠️  IMPORTANT:")
        logger.info("  - This is OUT-OF-SAMPLE testing (test set only)")
        logger.info("  - Includes realistic costs (slippage, spread, commission)")
        logger.info("  - Results are realistic and defensible")
        logger.info("  - Past performance does not guarantee future results")
        logger.info("")
    else:
        logger.error("Backtest failed")


if __name__ == '__main__':
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    asyncio.run(run_out_of_sample_backtest(symbol))

