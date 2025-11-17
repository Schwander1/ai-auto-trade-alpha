# Environment Rules

**Last Updated:** January 15, 2025  
**Version:** 2.0  
**Applies To:** All projects

---

## Overview

Environment detection, configuration, and dev/prod differences to ensure correct behavior across all environments.

---

## Environment Types

### Development
- **Location:** Local workspace
- **Alpaca Account:** Dev paper trading account
- **Config:** Local `config.json` (acceptable)
- **Purpose:** Testing and development
- **Trading:** Can be enabled/disabled

### Production
- **Location:** AWS server
- **Alpaca Account:** Production paper trading account
- **Config:** AWS Secrets Manager (primary)
- **Purpose:** Live trading and signal generation
- **Trading:** Always enabled (when deployed)

---

## Environment Detection

**See:** [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) for complete environment detection details

### Detection Process

**Component:** `argo/argo/core/environment.py` → `detect_environment()`

**Priority Order:**
1. `ARGO_ENVIRONMENT` environment variable (highest priority)
2. File path: `/root/argo-production/config.json` exists
3. Working directory: Contains `/root/argo-production`
4. Hostname: Contains "production" or "prod"
5. Default: `development` (lowest priority)

**Rule:** Environment detection is automatic and happens on initialization
- No manual configuration needed
- Works in both local and production
- Logs detected environment for verification

---

## Account Selection

**See:** [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) for complete account switching details

### Automatic Account Switching

**Rule:** Account selection is automatic based on detected environment
- Development: Automatically uses `alpaca.dev` account
- Production: Automatically uses `alpaca.production` account
- No code changes needed when deploying
- Verification: Run `argo/scripts/check_account_status.py`

---

## Configuration Sources

**See:** [06_CONFIGURATION.md](06_CONFIGURATION.md) for complete configuration management

### Priority Order

1. **AWS Secrets Manager** (production, environment-specific)
2. **Environment Variables** (fallback)
3. **config.json** (development/local)

**Rule:** Configuration source selection is automatic based on environment
- Production: AWS Secrets Manager (primary)
- Development: `config.json` (local file)

---

## Environment-Specific Behavior

**See:** [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) for complete behavior differences

### Key Differences Summary

**Development:**
- Optional signal storage (to save space)
- Trading can be disabled for testing
- Detailed debug logging
- Local SQLite database (optional)
- **Cursor-Aware Trading:** Automatically pauses when Cursor is closed or computer is asleep

**Production:**
- Required signal storage (for audit)
- Trading always enabled
- Production-level logging
- PostgreSQL database (required)
- **Always Active:** Never pauses (runs 24/7)

---

## Environment Variables

### Required Variables

#### Argo (Production)
- `ENV=production`
- `ALPACA_API_KEY` (from AWS Secrets Manager)
- `ALPACA_SECRET_KEY` (from AWS Secrets Manager)
- `AWS_REGION` (for Secrets Manager)

#### Alpine (Production)
- `ENV=production`
- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `AWS_REGION`

### Optional Variables
- `LOG_LEVEL` (default: INFO)
- `DEBUG` (default: false)
- `API_PORT` (default: 8000)

---

## Environment Validation

### Pre-Deployment Check

```bash
# Validate environment setup
./scripts/check-env.sh [argo|alpine]

# Check specific environment
ENV=production python scripts/validate_environment.py
```

### Validation Checklist
- [ ] Environment detected correctly
- [ ] Correct Alpaca account selected
- [ ] AWS Secrets Manager accessible (production)
- [ ] All required variables present
- [ ] Configuration loaded successfully

---

## Environment Differences

**See:** [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) for complete file and behavior differences

### Quick Reference

**Files:** See [04_DEPLOYMENT.md](04_DEPLOYMENT.md) for deployment exclusions

**Behavior:** See [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) for detailed differences

---

## Environment Setup

### Development Setup

```bash
# 1. Clone repository
git clone <repo>

# 2. Install dependencies
cd argo && pip install -r requirements.txt
cd ../alpine-backend && pip install -r requirements.txt
cd ../alpine-frontend && npm install

# 3. Configure local environment
cp argo/config.json.example argo/config.json
# Edit config.json with dev credentials

# 4. Run locally
python argo/main.py
```

### Production Setup

```bash
# 1. SSH to production server
ssh user@production-server

# 2. Configure AWS Secrets Manager
./scripts/setup_aws_secrets_manager.sh

# 3. Set environment variable
export ENV=production

# 4. Deploy
./commands/deploy argo to production  # Recommended (uses blue-green, zero-downtime)
# Or: ./scripts/deploy-argo-blue-green.sh  # Direct script access
# Legacy: ./scripts/deploy-argo.sh  # Deprecated (causes downtime)
```

---

## Environment Troubleshooting

### Common Issues

#### Wrong Account Selected
- **Symptom:** Trading on wrong Alpaca account
- **Fix:** Check `ENV` variable and environment detection
- **Verify:** Run `argo/scripts/check_account_status.py`

#### Secrets Not Loading
- **Symptom:** API keys not found
- **Fix:** Check AWS Secrets Manager access
- **Verify:** Run `argo/scripts/monitor_aws_secrets_health.py`

#### Config Not Found
- **Symptom:** Configuration errors
- **Fix:** Ensure `config.json` exists (dev) or AWS Secrets configured (prod)
- **Verify:** Check environment detection logic

---

## Best Practices

### DO
- ✅ Always set `ENV` variable explicitly in production
- ✅ Use AWS Secrets Manager for production secrets
- ✅ Validate environment before deployment
- ✅ Test environment detection locally
- ✅ Document environment-specific behavior

### DON'T
- ❌ Hardcode environment-specific values
- ❌ Commit secrets to version control
- ❌ Use production credentials in development
- ❌ Skip environment validation
- ❌ Assume environment detection works correctly

---

## Related Rules

- [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) - Complete dev vs prod differences
- [04_DEPLOYMENT.md](04_DEPLOYMENT.md) - Deployment procedures
- [06_CONFIGURATION.md](06_CONFIGURATION.md) - Configuration management
- [07_SECURITY.md](07_SECURITY.md) - Security practices

