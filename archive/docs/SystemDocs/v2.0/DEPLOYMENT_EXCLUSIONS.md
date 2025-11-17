# Deployment Exclusions Guide

## Overview

This document explains which files should **NOT** be deployed to production and how the exclusion system works.

## Local-Only Files (Never Deploy)

### Test Trade Scripts
- `argo/scripts/execute_test_trade.py` - Test trade execution (local testing only)
- `argo/scripts/enable_full_trading.py` - Enable trading (local-first, could be useful in prod but kept local)

### Local Setup Scripts
- `scripts/local_setup.sh` - Local environment setup
- `scripts/local_health_check.sh` - Local health validation
- `scripts/local_security_audit.sh` - Local security audit
- `scripts/setup_local_dev.sh` - Local development setup
- `scripts/start-all.sh` - Start all local services

### Test Files
- `*_test.py` - Python test files
- `tests/` - Test directories
- `test_*.py` - Test scripts

### Development Configs
- `*.local.json` - Local configuration files
- `.env.local` - Local environment variables
- `docs/LOCAL_*.md` - Local documentation

## Production-Useful Files (Should Deploy)

These files ARE useful in production and should be deployed:

### Operational Scripts
- `argo/scripts/check_account_status.py` - Check which Alpaca account is active
- `argo/scripts/monitor_aws_secrets_health.py` - Monitor AWS Secrets Manager
- `argo/scripts/add_alpaca_secrets_to_aws.py` - Add secrets to AWS (one-time setup)
- `argo/scripts/setup_aws_secrets_manager.sh` - Setup AWS Secrets Manager
- `argo/scripts/test_end_to_end.py` - End-to-end testing (useful in production)
- `argo/scripts/generate_docs.sh` - Generate documentation

### Health & Monitoring
- `scripts/health-check.sh` - Production health checks
- `scripts/full-health-check.sh` - Comprehensive health checks
- `scripts/security-audit.sh` - Security auditing
- `scripts/security-monitor.sh` - Security monitoring

### Deployment Scripts
- `scripts/deploy-argo.sh` - Deploy Argo to production
- `scripts/deploy-alpine.sh` - Deploy Alpine to production

## Environment-Aware Files (Deploy, But Adapt)

These files detect their environment and work in both local and production:

- `argo/argo/core/paper_trading_engine.py` - Detects dev/prod environment
- `argo/argo/core/signal_generation_service.py` - Environment-aware
- `argo/argo/core/environment.py` - Environment detection
- `argo/scripts/health_check_unified.py` - Works in both environments
- `scripts/security_audit_complete.py` - Environment-aware
- `scripts/system_audit_complete.py` - Environment-aware

## How Exclusions Work

### 1. `.deployignore` File

Similar to `.gitignore`, but for deployment. Lists patterns of files to exclude.

### 2. `deployment-manifest.json`

Defines what should and shouldn't be deployed, with explanations.

### 3. Deployment Scripts

`scripts/deploy-argo.sh` and `scripts/deploy-alpine.sh` use rsync with exclusion patterns.

### 4. Verification Script

Run `scripts/verify-deployment-exclusions.sh` before deployment to verify exclusions are correct.

## Usage

### Before Deployment

```bash
# Verify exclusions are correct
./scripts/verify-deployment-exclusions.sh

# Deploy (exclusions are automatic)
./scripts/deploy-argo.sh
```

### Adding New Local-Only Files

1. Add pattern to `.deployignore`
2. Add to `deployment-manifest.json` under `local_only.patterns`
3. Update `scripts/deploy-argo.sh` exclusion list
4. Run verification script

### Adding New Production Files

1. Ensure file is NOT in `.deployignore`
2. Add to `deployment-manifest.json` under `production_useful.files` if it's a script
3. Verify it gets deployed

## Examples

### ✅ Correct: Local-only script
```bash
# File: scripts/local_setup.sh
# Status: In .deployignore, excluded from deployment
# Result: Stays local, never deployed
```

### ✅ Correct: Production script
```bash
# File: argo/scripts/check_account_status.py
# Status: NOT in .deployignore, included in deployment
# Result: Deployed to production, useful for operations
```

### ❌ Incorrect: Local script deployed
```bash
# File: argo/scripts/execute_test_trade.py
# Status: Should be excluded but wasn't
# Result: Deployed to production (WRONG!)
# Fix: Add to .deployignore and deployment script exclusions
```

## Verification

After deployment, verify local-only files are NOT on production:

```bash
ssh root@178.156.194.174 "cd /root/argo-production && ls -la scripts/execute_test_trade.py"
# Should return: No such file or directory
```

## Summary

- **Local-only**: Test trade scripts, local setup, test files → Never deploy
- **Production-useful**: Operational scripts, health checks, monitoring → Always deploy
- **Environment-aware**: Core code that adapts → Deploy, but behaves differently

Always verify exclusions before deployment!

