# Deployment Guide v5.0

**Date:** January 15, 2025  
**Version:** 5.0  
**Status:** ✅ Complete

---

## Overview

This guide covers deployment procedures for v5.0, including all new features, optimizations, and enhancements.

---

## Pre-Deployment Checklist

### Dependencies

- [x] Python 3.8+
- [x] All v5.0 dependencies installed:
  - `pyarrow>=14.0.0` (Parquet support)
  - `scikit-learn>=1.3.0` (ML calibration)
  - `websockets>=12.0` (WebSocket streams)
  - `boto3>=1.34.0` (S3 integration)
  - `pandas>=2.0.0` (Data processing)

### Configuration

- [x] AWS credentials configured (for S3 backups)
- [x] S3 bucket name set (BACKUP_BUCKET_NAME or AWS_BUCKET_NAME)
- [x] Redis configured (optional, for distributed caching)

---

## Deployment Steps

### Step 1: Install Dependencies

```bash
cd argo
source venv/bin/activate
pip install -r requirements.txt
```

**Verify:**
```bash
python -c "import pandas, pyarrow, sklearn, boto3; print('✅ All dependencies installed')"
```

### Step 2: Configure AWS (Production)

**Set Environment Variables:**
```bash
export BACKUP_BUCKET_NAME="your-backup-bucket-name"
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"
```

### Step 3: Create S3 Lifecycle Policy

```bash
python argo/compliance/s3_lifecycle_policy.py create
```

### Step 4: Initialize Database Optimizations

```bash
python -c "from argo.core.database_optimizer import DatabaseOptimizer; DatabaseOptimizer()"
```

### Step 5: Run Health Checks

```bash
# Complete health check
python argo/scripts/health_check_complete.py

# v5.0 optimizations check
python argo/scripts/health_check_v5_optimizations.py

# Unified health check
python argo/scripts/health_check_unified.py --level 3
```

**Expected:** All checks PASS

### Step 6: Test Backtesting Enhancements

```bash
# Run out-of-sample backtest
python argo/scripts/run_out_of_sample_backtest.py AAPL
```

---

## Post-Deployment

### Monitoring

1. **Monitor Signal Generation:**
   - Check confidence calibration logs
   - Verify outcome tracking updates
   - Monitor performance metrics

2. **Monitor Storage:**
   - Check Parquet backup creation
   - Verify S3 lifecycle transitions
   - Monitor storage costs

3. **Monitor Database:**
   - Refresh materialized views periodically
   - Monitor query performance
   - Check index usage

### Maintenance

**Daily:**
- Automatic Parquet backups (via cron)
- Outcome tracking (automatic)

**Weekly:**
- Refresh materialized views
- Review performance metrics
- Check health status

**Monthly:**
- Review storage costs
- Analyze regime changes
- Update calibration models

---

## Related Documentation

- **Production Deployment:** See `../../V5.0_PRODUCTION_DEPLOYMENT_GUIDE.md`
- **System Architecture:** See `01_COMPLETE_SYSTEM_ARCHITECTURE.md`
- **Monitoring:** See `../v4.0/04_SYSTEM_MONITORING_COMPLETE_GUIDE.md`

---

**This guide reflects v5.0 deployment procedures.**

