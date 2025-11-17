# Development vs Production Differences

**Last Updated:** January 15, 2025  
**Version:** 2.0  
**Applies To:** All projects

---

## Overview

Comprehensive guide to differences between development and production environments, automatic environment switching, and ensuring deployment consistency.

---

## Automatic Environment Detection

### Detection Mechanism

**Component:** `argo/argo/core/environment.py` → `detect_environment()`

**Priority Order:**
1. `ARGO_ENVIRONMENT` environment variable (highest priority)
   - Values: `production`, `prod` → returns `production`
   - Values: `development`, `dev` → returns `development`
2. File path detection: `/root/argo-production/config.json` exists
3. Working directory: Contains `/root/argo-production` in path
4. Hostname: Contains "production" or "prod" (case-insensitive)
5. Default: `development` (lowest priority)

**Implementation:** See `argo/argo/core/environment.py` → `detect_environment()`

**Rule:** Environment detection happens automatically on initialization
- No manual configuration needed
- Works in both local and production
- Logs detected environment for verification

---

## Automatic Account Switching

### Alpaca Account Selection

**Component:** `argo/argo/core/paper_trading_engine.py`

#### Development Environment
- **Automatically Uses:** `alpaca.dev` from `config.json`
- **Account Name:** Dev Trading Account
- **Source Priority:**
  1. AWS Secrets Manager: `alpaca-api-key-dev`, `alpaca-secret-key-dev` (if available)
  2. `config.json` → `alpaca.dev.api_key`, `alpaca.dev.secret_key`
  3. Environment variables: `ALPACA_API_KEY`, `ALPACA_SECRET_KEY` (fallback)

**Implementation:** See `argo/argo/core/paper_trading_engine.py` → `__init__()`

#### Production Environment
- **Automatically Uses:** `alpaca.production` from AWS Secrets Manager
- **Account Name:** Production Trading Account
- **Source Priority:**
  1. AWS Secrets Manager: `alpaca-api-key-production`, `alpaca-secret-key-production` (primary)
  2. AWS Secrets Manager (fallback): `alpaca-api-key`, `alpaca-secret-key` (generic)
  3. `config.json` → `alpaca.production.api_key`, `alpaca.production.secret_key` (last resort)

**Implementation:** See `argo/argo/core/paper_trading_engine.py` → `__init__()`

**Rule:** Account selection is automatic based on detected environment
- No code changes needed when deploying
- Same code works in both environments
- Verification: Run `argo/scripts/check_account_status.py`

---

## Configuration Differences

### Development Configuration

**Location:** `argo/config.json` (local file, not committed)

**Structure:**
```json
{
  "alpaca": {
    "dev": {
      "api_key": "PKKTZHTVMTOW7DPPYNOGYPKHWD",
      "secret_key": "56mYiK5MBahHS6wRH7ghC6Mtqt2nxwcTBB9odMjcTMc2",
      "paper": true,
      "account_name": "Dev Trading Account"
    }
  },
  "trading": {
    "auto_execute": true  // Can be false for testing
  }
}
```

**Characteristics:**
- ✅ Can contain actual API keys (local only, not committed)
- ✅ Can disable trading (`auto_execute: false`)
- ✅ Optional signal storage (to save space)
- ✅ Detailed debug logging enabled

### Production Configuration

**Location:** AWS Secrets Manager (primary) + `config.json.example` (template)

**Structure:**
```json
{
  "alpaca": {
    "production": {
      "api_key": "FROM_AWS_SECRETS",
      "secret_key": "FROM_AWS_SECRETS",
      "paper": true,
      "account_name": "Production Trading Account"
    }
  },
  "trading": {
    "auto_execute": true  // Always true in production
  }
}
```

**Characteristics:**
- ✅ Secrets from AWS Secrets Manager only
- ✅ Trading always enabled
- ✅ Required signal storage (for audit)
- ✅ Production-level logging

**Rule:** `config.json` in production should have placeholder values
- Actual secrets come from AWS Secrets Manager
- Template file (`config.json.example`) is committed
- Never commit actual `config.json` with secrets

---

## File Deployment Rules

### Files That MUST Be Deployed (Consistent Across Environments)

**Core Application Code:**
- `argo/argo/**/*.py` - All Python source code
- `alpine-backend/**/*.py` - Backend code
- `alpine-frontend/**/*.{ts,tsx,js,jsx}` - Frontend code
- **⚠️ DEPRECATED:** `packages/shared/` violates entity separation (Rule 10) and should be removed

**Configuration Templates:**
- `argo/config.json.example` - Configuration template
- `.env.example` - Environment variable template

**Environment-Aware Code:**
- `argo/argo/core/environment.py` - Environment detection
- `argo/argo/core/paper_trading_engine.py` - Auto account switching
- `argo/argo/core/signal_generation_service.py` - Environment-aware behavior

**Operational Commands (Recommended):**
- `./commands/deploy all to production` - Deploy all services to production
- `./commands/deploy argo to production` - Deploy Argo to production
- `./commands/deploy alpine to production` - Deploy Alpine to production
- `./commands/health check all production` - Health check all production services
- `./commands/rollback argo production` - Rollback Argo production
- `./commands/status check all production` - Status check all production services
- `./commands/logs view all production` - View production logs
- See [commands/README.md](../commands/README.md) for complete reference

**Operational Scripts (Direct Access):**
- `argo/scripts/check_account_status.py` - Account verification
- `argo/scripts/health_check_unified.py` - Health checks
- `argo/scripts/monitor_aws_secrets_health.py` - Secrets monitoring
- `scripts/deploy-argo-blue-green.sh` - Blue-green deployment (zero-downtime, recommended)
- `scripts/deploy-argo.sh` - Legacy direct deployment (deprecated, causes downtime)
- `scripts/rollback-argo-blue-green.sh` - Rollback script
- `scripts/test-argo-blue-green.sh` - Test deployment script

### Files That MUST NOT Be Deployed (Local Only)

**Local Development Files:**
- `scripts/local_*.sh` - Local setup scripts
- `scripts/local_*.py` - Local utility scripts
- `scripts/setup_local_dev.sh` - Local development setup
- `scripts/start-all.sh` - Local service starter
- `argo/scripts/execute_test_trade.py` - Test trade script
- `argo/scripts/enable_full_trading.py` - Local trading enabler

**Local Configuration:**
- `argo/config.json` - Actual config with secrets (local only)
- `.env.local` - Local environment variables
- `*.local.json` - Local JSON configs

**Test Files:**
- `tests/` - Test directories
- `*_test.py` - Test files
- `__tests__/` - Test directories

**Build Artifacts:**
- `venv/` - Python virtual environments
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python files
- `node_modules/` - Node dependencies
- `.next/` - Next.js build output
- `*.log` - Log files
- `*.db` - Local databases
- `backups/` - Backup directories

**Rule:** Local-only files are automatically excluded via `.deployignore`
- Deployment scripts verify exclusions
- Never manually copy local files to production

---

## Behavior Differences

### Signal Generation

#### Development
- **Frequency:** Same as production (every 5 seconds)
- **Storage:** Optional (can disable to save space)
- **Logging:** Detailed debug logging
- **Purpose:** Testing and development

#### Production
- **Frequency:** Every 5 seconds (as configured)
- **Storage:** Required (for audit and compliance)
- **Logging:** Production-level logging (INFO and above)
- **Purpose:** Live signal generation for customers

**Rule:** Signal generation logic is identical in both environments
- Only storage and logging differ
- Same Weighted Consensus algorithm
- Same data sources and weights

### Trading Execution

#### Development
- **Auto-Execute:** Can be disabled (`auto_execute: false`)
- **Account:** Dev paper trading account
- **Purpose:** Strategy testing, risk management testing
- **Can Stop:** Can be stopped/started for testing
- **Cursor-Aware:** Automatically pauses when Cursor is closed or computer is asleep
- **Auto-Resume:** Automatically resumes when Cursor starts or computer wakes up
- **Behavior:** Only trades when actively working (Cursor running + computer awake)

#### Production
- **Auto-Execute:** Always enabled (`auto_execute: true`)
- **Account:** Production paper trading account
- **Purpose:** Live trading
- **Always Running:** Runs continuously when deployed (24/7)
- **No Pausing:** Never pauses for Cursor/computer state (always active)

**Rule:** Trading logic is identical in both environments
- Only account and enable/disable differ
- Same risk management rules
- Same position sizing logic
- **Development:** Cursor/computer-aware (pauses when inactive)
- **Production:** Always active (never pauses)

### Signal Storage

#### Development
- **Database:** Local SQLite (optional)
- **Storage:** Can be disabled to save space
- **Retention:** Short-term (for testing)
- **Purpose:** Testing and debugging

#### Production
- **Database:** PostgreSQL (required)
- **Storage:** Required (immutable logs)
- **Retention:** 7 years (compliance)
- **Purpose:** Audit trail, compliance, customer delivery

**Rule:** Production must store all signals
- Development can skip storage for space
- Same signal format in both environments
- SHA-256 hashes required in production

### Logging

#### Development
- **Level:** DEBUG (detailed information)
- **Location:** Local files (`argo/logs/*.log`)
- **Retention:** 7 days
- **Purpose:** Debugging and development

#### Production
- **Level:** INFO and above (production-level)
- **Location:** Centralized logging (if available)
- **Retention:** 30 days
- **Purpose:** Operations and monitoring

**Rule:** Logging level automatically adjusts based on environment
- Development: DEBUG for detailed debugging
- Production: INFO+ for operational visibility

---

## Deployment Consistency Rules

### Code Consistency

**Rule:** Code must be identical between dev and prod
- Same source code deployed to both
- No environment-specific code branches
- Environment detection handles differences

**Exception:** Configuration values only
- API keys differ (dev vs prod accounts)
- Logging levels differ (DEBUG vs INFO)
- Storage settings differ (optional vs required)

### Configuration Consistency

**Rule:** Configuration structure must be consistent
- Same `config.json` structure in both environments
- Same parameter names and types
- Only values differ (secrets, flags)

**Template:** `config.json.example` defines structure
- Committed to version control
- Used as template for both environments
- Documents all configuration options

### Deployment Process

**Rule:** Deployment must maintain consistency

**Before Deployment:**
1. ✅ Code tested in development
2. ✅ Configuration validated
3. ✅ Environment detection verified
4. ✅ Account selection verified

**During Deployment:**
1. ✅ Same code deployed (no modifications)
2. ✅ Configuration template deployed
3. ✅ Secrets loaded from AWS Secrets Manager
4. ✅ Environment automatically detected

**After Deployment:**
1. ✅ Verify correct environment detected
2. ✅ Verify correct account selected
3. ✅ Verify configuration loaded correctly
4. ✅ Run health checks

---

## Verification & Testing

### Pre-Deployment Verification

**Local Verification:**
```bash
# 1. Verify environment detection
python -c "from argo.core.environment import detect_environment; print(detect_environment())"
# Should output: development

# 2. Verify account selection
python argo/scripts/check_account_status.py
# Should show: Dev Trading Account

# 3. Verify configuration
python -c "from argo.core.weighted_consensus_engine import WeightedConsensusEngine; e = WeightedConsensusEngine(); print('Config loaded:', e.config is not None)"
```

**Production Verification (After Deployment):**
```bash
# 1. Verify environment detection
python -c "from argo.core.environment import detect_environment; print(detect_environment())"
# Should output: production

# 2. Verify account selection
python argo/scripts/check_account_status.py
# Should show: Production Trading Account

# 3. Verify AWS Secrets Manager
python argo/scripts/monitor_aws_secrets_health.py
# Should show: All secrets accessible
```

### Consistency Checks

**Rule:** Run consistency checks before deployment

**Checklist:**
- [ ] Code is identical (no environment-specific branches)
- [ ] Configuration structure matches template
- [ ] Environment detection works correctly
- [ ] Account selection works correctly
- [ ] All required secrets in AWS Secrets Manager
- [ ] Local-only files excluded from deployment
- [ ] Health checks pass in both environments

---

## Common Issues & Solutions

### Issue: Wrong Account Selected

**Symptom:** Trading on wrong Alpaca account

**Causes:**
- Environment not detected correctly
- `ARGO_ENVIRONMENT` variable not set
- Wrong secrets in AWS Secrets Manager

**Solution:**
1. Check environment detection: `python -c "from argo.core.environment import detect_environment, get_environment_info; import json; print(json.dumps(get_environment_info(), indent=2))"`
2. Verify `ARGO_ENVIRONMENT` variable (production only)
3. Check AWS Secrets Manager secrets
4. Run `argo/scripts/check_account_status.py` to verify

### Issue: Configuration Not Loading

**Symptom:** Configuration errors, missing values

**Causes:**
- `config.json` missing (dev) or AWS Secrets not configured (prod)
- Wrong configuration structure
- Missing required fields

**Solution:**
1. Development: Ensure `argo/config.json` exists
2. Production: Verify AWS Secrets Manager setup
3. Check `config.json.example` for structure
4. Validate configuration on load

### Issue: Local Files Deployed to Production

**Symptom:** Local-only files in production

**Causes:**
- `.deployignore` not working
- Manual file copy
- Deployment script issue

**Solution:**
1. Check `.deployignore` file
2. Verify deployment script exclusions
3. Run `scripts/verify-deployment-exclusions.sh`
4. Remove local files from production manually if needed

---

## Best Practices

### DO
- ✅ Always test in development first
- ✅ Verify environment detection before deployment
- ✅ Use `config.json.example` as template
- ✅ Store production secrets in AWS Secrets Manager only
- ✅ Verify account selection after deployment
- ✅ Run health checks in both environments
- ✅ Keep code identical between environments
- ✅ Document environment-specific behavior

### DON'T
- ❌ Hardcode environment-specific values in code
- ❌ Create separate code branches for dev/prod
- ❌ Commit actual `config.json` with secrets
- ❌ Deploy local-only files to production
- ❌ Skip environment verification
- ❌ Assume environment detection works without testing
- ❌ Mix dev and prod credentials
- ❌ Deploy without verifying account selection

---

## Related Rules

- [05_ENVIRONMENT.md](05_ENVIRONMENT.md) - Environment detection details
- [06_CONFIGURATION.md](06_CONFIGURATION.md) - Configuration management
- [04_DEPLOYMENT.md](04_DEPLOYMENT.md) - Deployment procedures
- [07_SECURITY.md](07_SECURITY.md) - Secrets management
- [13_TRADING_OPERATIONS.md](13_TRADING_OPERATIONS.md) - Trading behavior differences

