# Performance Evaluation - Quick Reference

## Quick Commands

```bash
# Full evaluation (all components, 30 days)
cd argo && python3 scripts/evaluate_performance.py

# Signal generator only
python3 scripts/evaluate_performance.py --component signal

# Production trading only
python3 scripts/evaluate_performance.py --component production

# Prop firm trading only
python3 scripts/evaluate_performance.py --component prop_firm

# Last 7 days
python3 scripts/evaluate_performance.py --days 7

# JSON output
python3 scripts/evaluate_performance.py --json

# Save to file
python3 scripts/evaluate_performance.py --json > report.json
```

## Performance Targets

### Signal Generator
- Generation Time: **<0.3s** (target)
- Cache Hit Rate: **>80%** (target)
- Skip Rate: **30-50%** (optimal)

### Production Trading
- Win Rate: **>45%** (target)
- Profit Factor: **>1.5** (target)
- Return: **>10%** (target)

### Prop Firm Trading
- Win Rate: **>45%** (target)
- Profit Factor: **>1.5** (target)
- Max Drawdown: **<2.0%** (limit)
- Daily Loss: **<4.5%** (limit)
- Compliance: **Zero breaches** (critical)

## Performance Grades

- **A (Excellent)**: All metrics exceed targets
- **B (Good)**: Most metrics meet targets
- **C (Fair)**: Some metrics need improvement
- **D (Needs Improvement)**: Multiple metrics below targets

## Report Location

Reports saved to: `argo/reports/performance_evaluation_YYYYMMDD_HHMMSS.json`

## Troubleshooting

**No data?** → Services may not be running or no trades executed
**Environment warning?** → Check ARGO_ENVIRONMENT variable
**Prop firm not enabled?** → Set `prop_firm.enabled = true` in config.json
