# Deployment Rules

**Last Updated:** January 15, 2025  
**Version:** 3.0  
**Applies To:** All projects

---

## Overview

Deployment safety gates, procedures, and rollback strategies to ensure safe, reliable production deployments.

**Strategic Context:** Scalability and reliability goals align with strategic targets defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md) Goals 2, 4, and 7.

**See Also:** [30_CODE_REVIEW.md](30_CODE_REVIEW.md) for PR review process, [31_FEATURE_FLAGS.md](31_FEATURE_FLAGS.md) for feature flag deployment, [33_DISASTER_RECOVERY.md](33_DISASTER_RECOVERY.md) for disaster recovery procedures.

---

## Deployment Safety Gates (MANDATORY)

### All 11 Gates MUST Pass

1. ✅ **Identify Changes** - Detect which project(s) modified
2. ✅ **Verify Scope** - Ensure single project or coupled projects
3. ✅ **Run Tests** - `pnpm --filter=[project] test` must pass
4. ✅ **Run Linting** - `pnpm --filter=[project] lint` must pass
5. ✅ **Build Locally** - `pnpm --filter=[project] build` must succeed
6. ✅ **Verify Staging** - Confirm staging deployment is healthy
7. ✅ **Validate Environment** - Run `scripts/check-env.sh [project]`
8. ✅ **Code Quality** - NO console.log, debugger, TODO, FIXME in diffs
9. ✅ **Pre-Deployment Health** - Verify production systems healthy
10. ✅ **Explicit Confirmation** - Require exact phrase: "deploy fully to production"
11. ✅ **100% Health Confirmation** - MANDATORY post-deployment health check (Level 3 comprehensive) - ALL checks MUST pass

---

## Project Structure

### Projects
- `argo/` → Argo Capital (Alpaca Markets Integration)
- `alpine-backend/` → Alpine Analytics Backend
- `alpine-frontend/` → Alpine Analytics Frontend
- `packages/` → Shared code (affects all projects)

---

## Project Isolation Rules

### Never Mix Projects
- **Rule:** NEVER mix `argo/` and `alpine-*/` changes in single commit
- **Action:** Deploy projects separately

### Coupled Projects
- **Rule:** `alpine-backend/` and `alpine-frontend/` deploy together as "alpine-analytics"
- **Action:** Always test both when either changes

### Shared Package Changes
- **Rule:** Changes to `packages/` require testing ALL projects
- **Action:** All projects must pass tests before deployment
- **Warning:** Warn if package version not updated

---

## Deployment Commands

**See:** [commands/README.md](../commands/README.md) for complete command reference

### Production Deployment (Recommended)
```bash
# Deploy all services to production
./commands/deploy all to production

# Deploy specific project
./commands/deploy argo to production
./commands/deploy alpine to production
```

### Health Checks
```bash
# Production health checks
./commands/health check all production
./commands/health check argo production
./commands/health check alpine production

# Local health checks
./commands/health check all
./commands/health check argo
```

### Emergency Rollback
```bash
# Rollback production deployment
./commands/rollback argo production
./commands/rollback alpine production
./commands/rollback all production
```

### Legacy Commands (Still Supported)
```bash
# Direct script access (for advanced use)
./scripts/deploy-argo-blue-green.sh
./scripts/deploy-alpine.sh
./scripts/rollback-argo-blue-green.sh
```

---

## Deployment Workflow

### When User Says "deploy fully to production"

Execute complete 11-step workflow automatically:

1. **Auto-detect project** from git changes
2. **Validate changes** (lint, test, build)
3. **Verify environment** setup
4. **Scan code quality** (no debug code)
5. **Validate staging** deployment
6. **Check production** environment
7. **Require exact confirmation** ("deploy fully to production")
8. **Execute deployment**
9. **Post-deployment health** checks (Level 3 comprehensive)
10. **100% health confirmation** - MANDATORY (Gate 11)
11. **Completion notification** (only after 100% health confirmed)

---

## Environment Variables

### Argo Capital (`argo/.env.production`)
- `ALPACA_API_KEY`
- `STRIPE_SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`

### Alpine Analytics
- **Backend** (`alpine-backend/.env.production`):
  - `ANALYTICS_API_KEY`
  - `RESEND_API_KEY`
  - `DATABASE_URL`
  - `REDIS_URL`
- **Frontend** (`alpine-frontend/.env.production`):
  - `NEXT_PUBLIC_API_URL`
  - `NEXT_PUBLIC_WS_URL`

---

## Deployment Exclusions

**See:** [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) for complete file deployment rules

### Local-Only Files (Never Deploy)
- `scripts/local_*.sh`, `scripts/local_*.py`
- `argo/scripts/execute_test_trade.py`
- `argo/scripts/enable_full_trading.py`
- `*.local.json`, `.env.local`
- `tests/`, `*_test.py`
- `argo/config.json` (actual file with secrets)

### Production-Useful Files (Should Deploy)
- `argo/scripts/check_account_status.py`
- `argo/scripts/health_check_unified.py`
- `argo/scripts/monitor_aws_secrets_health.py`
- `scripts/deploy-*.sh`, `scripts/health-check.sh`

### Never Deploy (Build Artifacts)
- `venv/`, `__pycache__/`, `*.pyc`
- `node_modules/`, `.next/`
- `*.log`, `*.db`, `backups/`

**Rule:** All exclusions are defined in `.deployignore`
- Deployment scripts automatically exclude these files
- Never manually copy local files to production

---

## Deployment Targets

### Argo Production
- **Server:** 178.156.194.174
- **Path:** `/root/argo-production`
- **Description:** Argo Trading Engine production server

### Alpine Production
- **Server:** 91.98.153.49
- **Path:** `/root/alpine-production`
- **Description:** Alpine Analytics production server

---

## Pre-Deployment Checklist

### Code Quality
- [ ] No `console.log` statements
- [ ] No `debugger` statements
- [ ] No `TODO` or `FIXME` comments
- [ ] All tests passing
- [ ] All linters passing
- [ ] Build succeeds locally

### Environment
- [ ] Environment variables validated
- [ ] Secrets configured in AWS Secrets Manager
- [ ] Database migrations ready
- [ ] Dependencies up to date

### Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] E2E tests passing (if applicable)
- [ ] Manual testing completed

### Documentation
- [ ] README updated (if needed)
- [ ] API documentation updated (if needed)
- [ ] Changelog updated

---

## Post-Deployment Health Confirmation (MANDATORY - GATE 11)

### 100% Health Requirement

**Rule:** After every deployment, **100% health confirmation is REQUIRED** before considering deployment complete. This is **Gate 11** and is **MANDATORY**.

**What "100% Health" Means:**
- All health checks passing (Level 3 comprehensive)
- All services running correctly
- No critical errors in logs
- All API endpoints responding
- Database connections healthy
- All integrations operational
- Performance metrics within acceptable ranges

### Mandatory Health Check Process

**Step 1: Immediate Post-Deployment (Within 5 minutes)**
```bash
# Run comprehensive health check (Level 3)
python argo/scripts/health_check_unified.py --level 3

# For Alpine
curl http://localhost:8001/health
# Production: curl http://91.98.153.49:8001/health

# Verify all checks pass
# If ANY check fails, deployment is NOT complete
```

**Step 2: Extended Verification (Within 15 minutes)**
- Monitor logs for errors
- Verify all services stable
- Check performance metrics
- Validate user-facing functionality

**Step 3: Health Confirmation Report**
- Document all health check results
- Confirm 100% pass rate
- Sign off on deployment completion

### Health Check Failure Protocol

**If health checks fail:**
1. **STOP** - Do not consider deployment complete
2. **INVESTIGATE** - Identify root cause
3. **FIX** - Resolve issues or rollback
4. **RE-CHECK** - Run health checks again
5. **CONFIRM** - Only mark complete when 100% healthy

### Environment-Specific Health Checks

**Development:**
- Level 2 health check sufficient for local testing
- Level 3 required before deployment to production

**Production:**
- Level 3 comprehensive health check MANDATORY
- All checks must pass
- Extended monitoring for 1 hour post-deployment

### Health Check Commands

```bash
# Development (Level 2)
python argo/scripts/health_check_unified.py --level 2

# Production (Level 3 - MANDATORY)
python argo/scripts/health_check_unified.py --level 3

# Alpine Backend
curl http://localhost:8001/health
curl http://91.98.153.49:8001/health  # Production

# Argo API
curl http://localhost:8000/health
curl http://178.156.194.174:8000/health  # Production
```

### Deployment Completion Criteria

**Deployment is ONLY complete when:**
- ✅ All 11 pre-deployment gates passed
- ✅ Deployment executed successfully
- ✅ **100% health checks passing (Level 3)**
- ✅ All services operational
- ✅ No critical errors
- ✅ Health confirmation documented

---

## Post-Deployment Checklist

### Verification
- [ ] **100% health checks passing (Level 3)** - MANDATORY
- [ ] Services running correctly
- [ ] No errors in logs
- [ ] Monitoring alerts configured
- [ ] Rollback plan ready

### Monitoring
- [ ] Check application logs
- [ ] Check error rates
- [ ] Check performance metrics
- [ ] Verify user-facing functionality

---

## Rollback Procedures

### When to Rollback
- Health checks failing
- Error rates spiking
- Critical functionality broken
- Data integrity issues

### Rollback Steps
1. **Identify last known good version**
2. **Stop current deployment**
3. **Restore previous version**
4. **Verify health checks**
5. **Monitor for stability**
6. **Document rollback reason**

### Rollback Commands
```bash
# Rollback Argo
./scripts/rollback.sh argo v1.2.3

# Rollback Alpine
./scripts/rollback.sh alpine v2.1.2
```

---

## Zero-Downtime Deployment

### Blue/Green Deployment (Alpine & Argo)
- **Strategy:** Deploy to new environment, switch traffic
- **Benefit:** Zero downtime, easy rollback
- **Implementation:** 
  - **Alpine:** Docker Compose blue/green setup
  - **Argo:** Process-based blue/green with port swapping

### Argo Blue-Green Deployment
- **Environments:** `/root/argo-production-blue` and `/root/argo-production-green`
- **Ports:** Blue/Green on 8000 (active), inactive on 8001 (for rollback)
- **Script:** `scripts/deploy-argo-blue-green.sh`
- **Features:**
  - Zero downtime deployments
  - Automatic health checks (Gate 11)
  - Instant rollback capability
  - Legacy migration support

### Canary Releases (Future Enhancement)
- **Strategy:** Gradual rollout to subset of traffic
- **Benefit:** Risk mitigation, gradual validation
- **Implementation:** Feature flags or traffic splitting

---

## Deployment Best Practices

### DO
- ✅ Always run full test suite before deployment
- ✅ Deploy during low-traffic periods
- ✅ Have rollback plan ready
- ✅ Monitor closely after deployment
- ✅ Deploy incrementally (small changes)
- ✅ Use feature flags for risky changes
- ✅ Document deployment process

### DON'T
- ❌ Deploy on Fridays (unless emergency)
- ❌ Deploy without testing
- ❌ Deploy multiple major changes at once
- ❌ Skip health checks
- ❌ **Skip 100% health confirmation (Gate 11)**
- ❌ Consider deployment complete without 100% health
- ❌ Deploy without rollback plan
- ❌ Ignore monitoring alerts

---

## Related Rules

- [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) - Deployment consistency and file exclusions
- [05_ENVIRONMENT.md](05_ENVIRONMENT.md) - Environment management
- [06_CONFIGURATION.md](06_CONFIGURATION.md) - Configuration management
- [07_SECURITY.md](07_SECURITY.md) - Security practices
- [10_MONOREPO.md](10_MONOREPO.md) - Monorepo structure
- [14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md) - Post-deployment monitoring

