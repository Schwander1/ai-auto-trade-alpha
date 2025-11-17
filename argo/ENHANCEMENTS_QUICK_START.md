# Enhancements Quick Start Guide

## Overview

All Perplexity AI review enhancements are now fully implemented. This guide shows you how to use them.

## Quick Start

### 1. Collect Baseline Metrics

```bash
python -m argo.core.baseline_metrics --duration 60 --version "pre-enhancement"
```

### 2. Run Tests

```bash
# Run all unit tests
pytest argo/tests/unit/ -v

# Run validation script
./scripts/run_enhancement_validation.sh
```

### 3. Use Enhancements in Code

#### Chinese Models with Rate Limiting

```python
from argo.core.data_sources.chinese_models_source import ChineseModelsDataSource

source = ChineseModelsDataSource()
signal = await source.get_signal("AAPL", market_data)
cost_report = source.get_cost_report()
```

#### Risk Monitoring

```python
from argo.risk.prop_firm_risk_monitor import PropFirmRiskMonitor

monitor = PropFirmRiskMonitor({
    'max_drawdown_pct': 2.0,
    'daily_loss_limit_pct': 4.5,
    'initial_capital': 25000.0
})

await monitor.start_monitoring()
monitor.update_equity(24500.0)
```

#### Data Quality Validation

```python
from argo.validation.data_quality import DataQualityMonitor

monitor = DataQualityMonitor()
is_valid, issue = await monitor.validate_signal(signal, market_data)
```

#### Transaction Cost Analysis

```python
from argo.backtest.transaction_cost_analyzer import TransactionCostAnalyzer, Order, OrderType

analyzer = TransactionCostAnalyzer()
order = Order(symbol='AAPL', shares=100, price=175.0, side='buy', type=OrderType.MARKET)
costs = analyzer.calculate_costs(order, market_data)
```

#### Adaptive Weights

```python
from argo.core.adaptive_weight_manager import AdaptiveWeightManager

manager = AdaptiveWeightManager(initial_weights)
manager.update_performance('source1', was_correct=True, confidence=80.0)
new_weights = manager.adjust_weights()
```

#### Performance Monitoring

```python
from argo.core.performance_budget_monitor import get_performance_monitor

monitor = get_performance_monitor()
with monitor.measure("signal_generation"):
    signal = await generate_signal()
stats = monitor.get_statistics("signal_generation")
```

## Validation

After implementing changes, validate improvements:

```bash
# Collect after metrics
python -m argo.core.baseline_metrics --duration 60 --version "post-enhancement"

# Validate improvements
python -m argo.core.improvement_validator \
    --baseline baselines/baseline_YYYYMMDD_HHMMSS.json \
    --after baselines/baseline_YYYYMMDD_HHMMSS.json
```

## Example Integration

See `argo/examples/enhancement_integration_example.py` for a complete example showing all enhancements working together.

## Documentation

Full documentation: `docs/ENHANCEMENT_IMPLEMENTATION_COMPLETE.md`

