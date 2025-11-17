# Automated Optimization Monitoring Guide

**Date**: 2025-01-XX  
**Status**: ✅ Complete

## Overview

The Automated Optimization Monitor & Rollback System continuously monitors system health after enabling optimizations and automatically rolls back if issues are detected.

## Features

✅ **Automatic Health Checks** - Runs health checks every 60 seconds  
✅ **Performance Monitoring** - Tracks signal generation time, cache hit rate, errors  
✅ **Automatic Rollback** - Disables optimizations if issues detected  
✅ **Detailed Reports** - Generates comprehensive monitoring reports  
✅ **Configurable Thresholds** - Customize rollback conditions  

## Quick Start

### Basic Usage (1 hour monitoring with auto-rollback)

```bash
python3 argo/scripts/auto_monitor_optimizations.py
```

### Monitor for 2 Hours

```bash
python3 argo/scripts/auto_monitor_optimizations.py --duration 7200
```

### Check Every 30 Seconds

```bash
python3 argo/scripts/auto_monitor_optimizations.py --interval 30
```

### Monitor Without Auto-Rollback (Just Alerts)

```bash
python3 argo/scripts/auto_monitor_optimizations.py --no-rollback
```

### Run in Background

```bash
nohup python3 argo/scripts/auto_monitor_optimizations.py > monitoring.log 2>&1 &
```

## Rollback Triggers

The system automatically rolls back optimizations if:

1. **Health Score < 70%** - System health drops below threshold
2. **Error Rate > 10%** - Too many components failing
3. **Signal Generation > 2 seconds** - Performance degradation
4. **3+ Consecutive Failures** - Persistent issues

## Monitoring Metrics

### Health Checks
- Environment detection
- Trading engine connectivity
- Signal generation service
- Data source connectivity
- Database health
- API endpoints
- Configuration loading

### Performance Metrics
- Average signal generation time
- Cache hit rate
- Total errors
- API call latency

## Reports

Reports are automatically saved to:
```
argo/reports/monitoring_report_YYYYMMDD_HHMMSS.json
```

### Report Contents
- Monitoring start/end times
- Duration
- Total health checks performed
- Rollback status
- All health check results
- Performance metrics timeline

## Configuration

### Default Settings
- **Check Interval**: 60 seconds
- **Monitoring Duration**: 3600 seconds (1 hour)
- **Auto-Rollback**: Enabled
- **Max Error Rate**: 10%
- **Min Health Score**: 70%
- **Max Signal Gen Time**: 2.0 seconds
- **Max Consecutive Failures**: 3

### Custom Thresholds

```bash
# Custom error rate threshold (5%)
python3 argo/scripts/auto_monitor_optimizations.py --max-error-rate 0.05

# Custom health score threshold (80%)
python3 argo/scripts/auto_monitor_optimizations.py --min-health-score 0.80
```

## Command Line Options

```
--interval SECONDS        Check interval in seconds (default: 60)
--duration SECONDS        Monitoring duration in seconds (default: 3600)
--no-rollback             Disable automatic rollback
--max-error-rate FLOAT    Max error rate for rollback (default: 0.10)
--min-health-score FLOAT  Min health score (default: 0.70)
```

## Example Output

```
🚀 Starting automated optimization monitoring
   Check interval: 60s
   Monitoring duration: 3600s
   Auto-rollback: True

📊 Health Check #1 (Elapsed: 0s)
   Health Score: 100.00%
   Error Rate: 0.00%
   Avg Signal Gen Time: 0.245s
   Cache Hit Rate: 82.5%
   ✅ System healthy: All checks passed

📊 Health Check #2 (Elapsed: 60s)
   Health Score: 100.00%
   Error Rate: 0.00%
   Avg Signal Gen Time: 0.238s
   Cache Hit Rate: 85.2%
   ✅ System healthy: All checks passed

...

============================================================
MONITORING SUMMARY
============================================================
Duration: 60.0 minutes
Total Checks: 60
Final Status: HEALTHY
✅ System remained healthy - Optimizations active
============================================================
```

## Rollback Example

If issues are detected:

```
⚠️  Rollback condition detected: Health score too low: 45.00%; Error rate too high: 25.00%
🔄 AUTOMATIC ROLLBACK TRIGGERED - Disabling all optimizations
✅ Rollback complete - All optimization flags disabled

============================================================
MONITORING SUMMARY
============================================================
Duration: 5.0 minutes
Total Checks: 5
Final Status: ROLLED_BACK
⚠️  ROLLBACK TRIGGERED - Optimizations disabled
============================================================
```

## Integration with System

### After Enabling Optimizations

1. **Enable all optimizations**:
   ```bash
   python3 -c "
   import sys; sys.path.insert(0, 'argo')
   from argo.core.feature_flags import FeatureFlags
   f = FeatureFlags()
   f.enable('optimized_weights')
   f.enable('regime_based_weights')
   f.enable('confidence_threshold_88')
   f.enable('incremental_confidence')
   f.enable('async_batch_db')
   f.enable('request_coalescing')
   print('✅ All optimizations enabled')
   "
   ```

2. **Start monitoring**:
   ```bash
   python3 argo/scripts/auto_monitor_optimizations.py --duration 7200
   ```

3. **Monitor the output** for any issues

4. **Check the report** after monitoring completes

## Best Practices

1. **Always monitor after enabling optimizations** - At least 1 hour
2. **Start with shorter durations** - Test with 30 minutes first
3. **Review reports** - Check detailed reports for insights
4. **Adjust thresholds** - Customize based on your system
5. **Use background mode** - For long-term monitoring

## Troubleshooting

### Health Check Fails

If health checks fail immediately:
- Check if signal generation service is running
- Verify database connectivity
- Check API endpoints are accessible

### Performance Metrics Not Available

If performance metrics show as unavailable:
- Signal generation service may not be initialized
- Metrics may not be enabled
- This is normal if service hasn't generated signals yet

### False Rollback Triggers

If rollback triggers too easily:
- Adjust thresholds with `--max-error-rate` and `--min-health-score`
- Increase `--interval` to reduce check frequency
- Use `--no-rollback` to monitor without auto-rollback

## Support

For issues or questions:
1. Check monitoring reports in `argo/reports/`
2. Review logs for detailed error messages
3. Verify feature flags are enabled correctly
4. Run manual health check: `python3 argo/scripts/health_check_unified.py --level 3`

---
**Status**: ✅ Ready for Use  
**Compliance**: Rule 14 (Monitoring & Observability), Rule 31 (Feature Flags)

