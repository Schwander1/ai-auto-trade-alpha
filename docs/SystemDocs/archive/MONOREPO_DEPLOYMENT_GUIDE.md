# Monorepo Deployment Guide

## Overview

This monorepo contains two independent projects with shared code:

- **Argo Capital** (`argo/`) - Alpaca Markets Integration
- **Alpine Analytics** (`alpine-backend/` + `alpine-frontend/`) - Analytics Platform

## Quick Start

### Deploy to Production

**Traditional Deployment:**
```bash
# Argo (Blue-Green Zero-Downtime - Recommended)
./scripts/deploy-argo-blue-green.sh

# Argo (Legacy Direct - Deprecated, causes downtime)
./scripts/deploy-argo.sh

# Alpine (Blue-Green Zero-Downtime)
./scripts/deploy-alpine.sh
# Or: pnpm deploy:alpine
```

**Agentic Deployment (Recommended):**
```bash
# Automated deployment with rule enforcement
./scripts/agentic/copilot-with-rules.sh "Deploy Argo to production"

# Or use package.json script
pnpm agentic:deploy "Deploy Argo to production"
```

**Benefits of Agentic Deployment:**
- Automatic rule enforcement (all 35+ rules)
- Automatic execution of all 11 safety gates
- Automatic rollback on failure
- Context-aware rule inclusion
- Cost tracking and monitoring

**See:** `docs/AGENTIC_SETUP_GUIDE.md` for setup instructions

### Check Environment

```bash
# Validate environment variables
pnpm check-env argo
pnpm check-env alpine
```

### Health Checks

```bash
# Check production health
pnpm health argo production
pnpm health alpine production

# Check staging health
pnpm health argo staging
pnpm health alpine staging
```

### Emergency Rollback

```bash
# Rollback to previous version
pnpm rollback argo v1.2.3
pnpm rollback alpine v2.1.2
```

## Deployment Safety Gates

All 10 gates must pass before production deployment:

1. ✅ Identify Changes
2. ✅ Verify Scope
3. ✅ Run Tests
4. ✅ Run Linting
5. ✅ Build Locally
6. ✅ Verify Staging
7. ✅ Validate Environment
8. ✅ Code Quality Scan
9. ✅ Pre-Deployment Health
10. ✅ Explicit Confirmation

## Project Structure

```
argo-alpine/
├── argo/                    # Argo Capital
├── alpine-backend/          # Alpine Analytics Backend
├── alpine-frontend/         # Alpine Analytics Frontend
├── packages/                # Shared code
└── scripts/                 # Deployment automation
```

## Environment Variables

See `scripts/check-env.sh` for required variables per project.

