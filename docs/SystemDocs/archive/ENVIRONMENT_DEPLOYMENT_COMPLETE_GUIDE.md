# Complete Environment & Deployment Guide

**Date:** November 14, 2025  
**Version:** 3.0  
**Status:** Complete Implementation Guide

---

## Executive Summary

This document provides a comprehensive guide to environment management and deployment in the Argo-Alpine system. It explains how environments work, how to deploy safely, what to exclude, and how to prevent deployment-related issues.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Environment Architecture](#environment-architecture)
3. [Deployment Process](#deployment-process)
4. [What to Exclude](#what-to-exclude)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

---

## System Overview

### Purpose

Environment and deployment management ensures **safe, consistent deployments** across dev and production while preventing deployment-related issues.

### Key Features

- **Environment Detection**: Automatic dev/prod detection
- **Dual Account System**: Separate Alpaca accounts per environment
- **Deployment Exclusions**: Prevents local files from production
- **Safe Deployment**: Validation before deployment
- **Rollback Capability**: Quick recovery from issues

---

## Environment Architecture

### Environment Types

**Development**:
- Local workspace
- Dev Alpaca paper trading account
- Local config.json (acceptable)
- Testing and development

**Production**:
- AWS server
- Production Alpaca paper trading account
- AWS Secrets Manager (primary)
- Live trading and signal generation

---

### Environment Detection

**Process**:
1. Check `ENV` environment variable
2. Check file path (contains "production"?)
3. Check hostname
4. Default to "development"

**Code**: `argo/argo/core/environment.py`

**Priority**:
1. `ENV` environment variable (highest)
2. File path detection
3. Hostname detection
4. Default to development (lowest)

---

### Account Selection

**Development**:
- Uses `alpaca.dev` from config.json
- Account: Dev Trading Account
- API Keys: From config.json or AWS Secrets Manager

**Production**:
- Uses `alpaca.production` from AWS Secrets Manager
- Account: Production Trading Account
- API Keys: From AWS Secrets Manager only

**Fallback**: If AWS Secrets Manager unavailable, falls back to config.json

---

## Deployment Process

### Pre-Deployment Checklist

**1. Local Testing**:
- Run health checks
- Run integration tests
- Verify all components working
- Test configuration changes

**2. Code Review**:
- Review all changes
- Verify no hardcoded secrets
- Check deployment exclusions
- Validate configuration

**3. Backup**:
- Backup current production system
- Backup configuration
- Backup database

**4. Validation**:
- Run deployment validation script
- Verify exclusions
- Check environment detection

---

### Deployment Steps

**Step 1: Prepare Deployment**
```bash
# Verify local system health
python argo/scripts/health_check_unified.py --level 3

# Run integration tests
python argo/scripts/test_full_system_integration.py

# Verify deployment exclusions
./scripts/verify-deployment-exclusions.sh
```

**Step 2: Deploy to Production**

**Argo (Blue-Green - Recommended):**
```bash
# Zero-downtime blue-green deployment
./scripts/deploy-argo-blue-green.sh

# Or test first (safe, doesn't switch traffic)
./scripts/test-argo-blue-green.sh
```

**Argo (Legacy Direct - Deprecated):**
```bash
# Legacy deployment (causes downtime, not recommended)
./scripts/deploy-argo.sh
```

**Alpine (Blue-Green):**
```bash
# Zero-downtime blue-green deployment
./scripts/deploy-alpine.sh
```

**Step 3: Verify Deployment**
```bash
# SSH to production
ssh user@prod

# Verify environment
cd /root/argo-production
python -c "from argo.core.environment import detect_environment; print(detect_environment())"

# Run health check
python argo/scripts/health_check_unified.py --level 3

# Verify Alpaca account
python argo/scripts/check_account_status.py
```

**Step 4: Monitor**
```bash
# Monitor logs
tail -f argo/logs/trading/*.log
tail -f argo/logs/signals.log

# Monitor health
watch -n 60 'python argo/scripts/health_check_unified.py --level 2'
```

---

## What to Exclude

### Files to Exclude from Production

**Local Development Files**:
- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python files
- `.pytest_cache/` - Test cache
- `.mypy_cache/` - Type checking cache

**Backup Files**:
- `*.backup` - Backup files
- `*.backup*` - Backup file variants
- `backups/` - Backup directories

**Local Data**:
- `data/signals.db` - Local database (production has its own)
- `data/historical/*.csv` - Local historical data
- `logs/` - Local logs (production has its own)

**Development Tools**:
- `.vscode/` - VS Code settings
- `.idea/` - IDE settings
- `*.swp` - Editor swap files
- `.DS_Store` - macOS files

**Test Files**:
- `tests/` - Test files (optional, can exclude)
- `*_test.py` - Test files
- `test_*.py` - Test files

**Documentation** (Optional):
- `docs/` - Documentation (can exclude if not needed)
- `README.md` - Readme files

---

### Deployment Exclusion File

**File**: `.deployignore`

**Format**: Similar to `.gitignore`, one pattern per line

**Example**:
```
# Virtual environments
venv/
__pycache__/
*.pyc

# Backup files
*.backup
*.backup*
backups/

# Local data
data/signals.db
data/historical/
logs/

# Development tools
.vscode/
.idea/
*.swp
.DS_Store

# Test files (optional)
tests/
*_test.py
test_*.py
```

---

## Troubleshooting

### Issue: Wrong environment after deployment

**Symptoms**: Production using dev account, or vice versa

**Solutions**:
1. Check environment detection on production server
2. Verify file path contains "production"
3. Set `ENV=production` environment variable
4. Check hostname

---

### Issue: Local files deployed to production

**Symptoms**: Local config, data, or cache files in production

**Solutions**:
1. Check `.deployignore` file
2. Verify deployment script uses exclusions
3. Clean production server manually
4. Update `.deployignore` if needed

---

### Issue: Deployment breaks production

**Symptoms**: Production system not working after deployment

**Solutions**:
1. Rollback to previous version
2. Check deployment logs
3. Verify configuration
4. Run health checks
5. Fix issues and redeploy

---

### Issue: AWS Secrets Manager not working

**Symptoms**: Production falls back to config.json

**Solutions**:
1. Verify AWS credentials on production
2. Check IAM permissions
3. Verify secret names
4. Test secret retrieval
5. Update secrets if needed

---

## Best Practices

### 1. Test Locally First

**Why**: Catch issues before production

**How**: Full testing in dev before deployment

**Benefit**: Prevents production issues

---

### 2. Use Deployment Exclusions

**Why**: Prevents local files in production

**How**: Maintain `.deployignore`, verify exclusions

**Benefit**: Clean production deployments

---

### 3. Validate Before Deploying

**Why**: Ensures deployment will work

**How**: Run validation scripts, health checks

**Benefit**: Prevents deployment failures

---

### 4. Backup Before Deploying

**Why**: Quick recovery if needed

**How**: Backup production system before changes

**Benefit**: Fast rollback capability

---

### 5. Monitor After Deployment

**Why**: Early detection of issues

**How**: Monitor logs, health checks, metrics

**Benefit**: Fast issue detection

---

### 6. Gradual Rollouts

**Why**: Minimize impact of issues

**How**: Deploy changes gradually, monitor closely

**Benefit**: Limits impact of problems

---

### 7. Document Deployments

**Why**: Track what changed and when

**How**: Document all deployments, changes, results

**Benefit**: Easier troubleshooting

---

## Quick Reference: Deployment

### Deployment Commands

```bash
# Pre-deployment validation
python argo/scripts/health_check_unified.py --level 3
./scripts/verify-deployment-exclusions.sh

# Deploy
./scripts/deploy-argo.sh

# Post-deployment verification
ssh user@prod "cd /root/argo-production && python argo/scripts/health_check_unified.py --level 3"
```

### Environment Variables

```bash
# Set environment explicitly
export ENV=production  # or development

# Set config path
export ARGO_CONFIG_PATH=/path/to/config.json
```

---

## Conclusion

Environment and deployment management is **critical for system reliability**. Proper deployment procedures ensure safe, consistent deployments across environments.

**Key Takeaways**:
1. Test locally before deploying
2. Use deployment exclusions
3. Validate before deploying
4. Backup before changes
5. Monitor after deployment

**Remember**: Safe deployment procedures prevent production issues.

---

**For Questions**:  
Deployment: deploy@alpineanalytics.com  
**Technical Support**: tech@alpineanalytics.com

