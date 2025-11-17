# Performance Evaluation Script

## Overview

The `evaluate_performance.py` script provides comprehensive performance evaluation for three key components of the Argo trading system:

1. **Signal Generator** - Evaluates signal generation performance, cache efficiency, and API latency
2. **Production Trading** - Analyzes production trading performance, win rates, P&L, and returns
3. **Prop Firm Trading** - Monitors prop firm trading with compliance metrics and risk limits

## Usage

### Basic Usage

Evaluate all components for the last 30 days:
```bash
python scripts/evaluate_performance.py
```

### Evaluate Specific Component

Evaluate only signal generator:
```bash
python scripts/evaluate_performance.py --component signal
```

Evaluate only production trading:
```bash
python scripts/evaluate_performance.py --component production
```

Evaluate only prop firm trading:
```bash
python scripts/evaluate_performance.py --component prop_firm
```

### Custom Time Period

Evaluate for the last 7 days:
```bash
python scripts/evaluate_performance.py --days 7
```

### JSON Output

Get results in JSON format:
```bash
python scripts/evaluate_performance.py --json
```

### Combined Options

Evaluate production trading for last 14 days with JSON output:
```bash
python scripts/evaluate_performance.py --component production --days 14 --json
```

## Output

### Signal Generator Metrics

- **Average Generation Time**: Target <0.3s
- **Cache Hit Rate**: Target >80%
- **Skip Rate**: Target 30-50%
- **Average API Latency**: Per data source
- **Error Counts**: By source and type

### Production Trading Metrics

- **Total/Completed/Pending Trades**: Trade counts
- **Win Rate**: Percentage of winning trades
- **Total P&L**: Dollar amount
- **Profit Factor**: Ratio of gross profit to gross loss
- **Return Percentage**: Return on capital
- **Performance by Asset Class**: Stocks vs Crypto
- **Performance by Signal Type**: Long vs Short

### Prop Firm Trading Metrics

- **All Production Metrics**: Plus compliance tracking
- **Max Drawdown**: Current drawdown vs limit
- **Daily Loss Breaches**: Count of daily loss limit violations
- **Drawdown Breaches**: Count of max drawdown violations
- **Trading Halted Status**: Whether trading is currently halted
- **Risk Limit Compliance**: Status vs configured limits

## Performance Grades

Each component receives a performance grade:

- **A (Excellent)**: All metrics within target ranges
- **B (Good)**: Most metrics within target ranges
- **C (Fair)**: Some metrics need improvement
- **D (Needs Improvement)**: Multiple metrics below targets

## Recommendations

The script provides actionable recommendations based on current performance:

- **Signal Generator**: Optimization suggestions for cache, skip rates, and API calls
- **Production Trading**: Suggestions for improving win rates, profit factors, and returns
- **Prop Firm Trading**: Compliance-focused recommendations and risk management suggestions

## Report Files

Reports are automatically saved to `argo/reports/performance_evaluation_YYYYMMDD_HHMMSS.json` with complete metrics and analysis.

## Examples

### Quick Signal Generator Check
```bash
python scripts/evaluate_performance.py --component signal --days 1
```

### Full System Evaluation
```bash
python scripts/evaluate_performance.py --days 30
```

### Prop Firm Compliance Check
```bash
python scripts/evaluate_performance.py --component prop_firm --days 7
```

### Export for Analysis
```bash
python scripts/evaluate_performance.py --json > performance_report.json
```

## Integration

This script can be integrated into:

- **Monitoring Dashboards**: Run periodically and display results
- **CI/CD Pipelines**: Automated performance checks
- **Alerting Systems**: Trigger alerts on poor performance grades
- **Reporting Systems**: Generate regular performance reports

## Notes

- **Environment Detection**: The script automatically detects the current environment (dev/production)
- **Account Verification**: Verifies which Alpaca account is being used
- **Prop Firm Mode**: Checks if prop firm mode is enabled before evaluating
- **Data Availability**: Metrics depend on actual trading activity and signal generation

## Troubleshooting

### No Data Available

If metrics show zeros:
- Signal generator may not be running
- No trades executed in the evaluation period
- Performance metrics not being collected

### Environment Warnings

If you see environment warnings:
- Verify you're running in the correct environment
- Check that the correct Alpaca account is configured
- Ensure prop firm mode is enabled if evaluating prop firm trading

### Missing Dependencies

If you see import errors:
- Ensure you're running from the `argo` directory
- Check that all required modules are installed
- Verify Redis is available (optional, uses in-memory fallback)
