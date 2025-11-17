#!/usr/bin/env python3
"""
Enhancement Integration Example
Demonstrates how all enhancements work together
"""
import asyncio
import logging
from datetime import datetime

# Import all enhancement modules
from argo.core.baseline_metrics import BaselineCollector
from argo.core.improvement_validator import ImprovementValidator
from argo.core.data_sources.chinese_models_source import ChineseModelsDataSource
from argo.risk.prop_firm_risk_monitor import PropFirmRiskMonitor
from argo.validation.data_quality import DataQualityMonitor
from argo.backtest.transaction_cost_analyzer import TransactionCostAnalyzer, Order, OrderType
from argo.core.adaptive_weight_manager import AdaptiveWeightManager
from argo.core.performance_budget_monitor import get_performance_monitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main integration example"""
    logger.info("🚀 Starting Enhancement Integration Example")
    
    # 1. Performance Monitoring
    perf_monitor = get_performance_monitor()
    logger.info("✅ Performance monitor initialized")
    
    # 2. Chinese Models with Rate Limiting
    chinese_models = ChineseModelsDataSource({
        'qwen_rpm': 20,
        'qwen_cost': 0.002,
        'glm_rpm': 30,
        'glm_cost': 0.001
    })
    logger.info("✅ Chinese models data source initialized")
    
    # 3. Data Quality Monitor
    quality_monitor = DataQualityMonitor()
    logger.info("✅ Data quality monitor initialized")
    
    # 4. Risk Monitor
    risk_monitor = PropFirmRiskMonitor({
        'max_drawdown_pct': 2.0,
        'daily_loss_limit_pct': 4.5,
        'initial_capital': 25000.0
    })
    logger.info("✅ Risk monitor initialized")
    
    # 5. Transaction Cost Analyzer
    tca = TransactionCostAnalyzer()
    logger.info("✅ Transaction cost analyzer initialized")
    
    # 6. Adaptive Weight Manager
    weight_manager = AdaptiveWeightManager({
        'alpaca_pro': 0.40,
        'massive': 0.40,
        'yfinance': 0.25,
        'alpha_vantage': 0.25,
        'xai_grok': 0.20,
        'sonar_ai': 0.15,
        'chinese_models': 0.10
    })
    logger.info("✅ Adaptive weight manager initialized")
    
    # Example: Generate signal with all enhancements
    logger.info("\n📊 Generating signal with enhancements...")
    
    with perf_monitor.measure("signal_generation"):
        # Get signal from Chinese models
        signal = await chinese_models.get_signal("AAPL", {
            'price': 175.0,
            'bid': 174.95,
            'ask': 175.05
        })
        
        if signal:
            # Validate signal quality
            is_valid, issue = await quality_monitor.validate_signal(signal, {
                'price': 175.0
            })
            
            if is_valid:
                logger.info(f"✅ Valid signal: {signal['direction']} @ {signal['confidence']}% confidence")
                
                # Calculate transaction costs
                order = Order(
                    symbol='AAPL',
                    shares=100,
                    price=175.0,
                    side='buy',
                    type=OrderType.MARKET
                )
                
                costs = tca.calculate_costs(order, {
                    'bid': 174.95,
                    'ask': 175.05,
                    'volatility': 0.02,
                    'avg_volume': 1000000
                })
                
                logger.info(f"💰 Transaction costs: ${costs.total:.2f}")
                logger.info(f"   - Commission: ${costs.commission:.2f}")
                logger.info(f"   - Spread: ${costs.spread:.2f}")
                logger.info(f"   - Slippage: ${costs.slippage:.2f}")
                logger.info(f"   - Market Impact: ${costs.market_impact:.2f}")
            else:
                logger.warning(f"❌ Signal rejected: {issue.description if issue else 'Unknown'}")
    
    # Example: Risk monitoring
    logger.info("\n🚨 Starting risk monitoring...")
    await risk_monitor.start_monitoring()
    
    # Simulate equity updates
    risk_monitor.update_equity(25000.0)
    await asyncio.sleep(1)
    
    risk_monitor.update_equity(24500.0)  # 2% drawdown
    await asyncio.sleep(1)
    
    stats = risk_monitor.get_monitoring_stats()
    logger.info(f"📊 Risk monitoring stats: {stats}")
    
    await risk_monitor.stop_monitoring()
    
    # Example: Adaptive weights
    logger.info("\n⚖️  Testing adaptive weights...")
    weight_manager.update_performance('chinese_models', was_correct=True, confidence=80.0)
    new_weights = weight_manager.adjust_weights()
    logger.info(f"📊 Updated weights: {new_weights}")
    
    # Example: Performance statistics
    logger.info("\n📈 Performance statistics:")
    stats = perf_monitor.get_statistics("signal_generation")
    for key, value in stats.items():
        logger.info(f"   {key}: {value}")
    
    # Example: Cost report
    logger.info("\n💰 Chinese models cost report:")
    cost_report = chinese_models.get_cost_report()
    logger.info(f"   Total daily cost: ${cost_report['total_daily_cost']:.2f}")
    logger.info(f"   Monthly estimate: ${cost_report['total_monthly_estimate']:.2f}")
    
    # Example: Quality report
    logger.info("\n🔍 Data quality report:")
    quality_report = quality_monitor.get_quality_report()
    logger.info(f"   Total issues (24h): {quality_report['total_issues_24h']}")
    logger.info(f"   Source health: {quality_report['source_health']}")
    
    logger.info("\n✅ Integration example complete!")

if __name__ == "__main__":
    asyncio.run(main())

