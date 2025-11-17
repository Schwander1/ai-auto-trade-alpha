# Complete Agentic Features Guide

**Date:** January 15, 2025  
**Version:** 1.0  
**Status:** Complete Implementation Guide

---

## Executive Summary

This document provides a comprehensive guide to the agentic development stack implemented in the argo-alpine workspace. It covers GitHub Copilot CLI, Anthropic Claude API, and Cursor Pro integration for automated workflows, deployments, and code refactoring.

**Strategic Context:** Agentic features align with efficiency and automation goals defined in `Rules/24_VISION_MISSION_GOALS.md`.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture & Components](#architecture--components)
3. [How It Works](#how-it-works)
4. [Setup Guide](#setup-guide)
5. [Usage Guide](#usage-guide)
6. [Rule Enforcement](#rule-enforcement)
7. [Cost Management](#cost-management)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Quick Reference](#quick-reference)

---

## System Overview

### Purpose

The agentic development stack automates development workflows, deployments, and code refactoring using AI-powered tools while ensuring all 35+ development rules are automatically enforced.

### Key Features

- **Automatic Rule Enforcement:** All commands automatically include Rules/ directory references
- **Deployment Automation:** Automated deployments with all 11 safety gates
- **Code Refactoring:** Automated refactoring of functions over 50 lines
- **Cost Optimization:** Caching, rate limiting, and usage tracking
- **Monitoring:** Usage tracking, cost monitoring, and performance metrics

### Available Tools

1. **GitHub Copilot CLI** ($10/month)
   - Deployment automation
   - Terminal workflows
   - Rule-aware command execution

2. **Anthropic Claude API** (pay-as-you-go, ~$10-30/month)
   - Deep codebase understanding
   - Complex refactoring
   - Code generation

3. **Cursor Pro** ($20/month, already configured ✅)
   - Agent Mode (autonomous tasks)
   - Composer Mode (multi-file refactoring)
   - Codebase Chat
   - Bugbot (automatic PR reviews)

**Total Cost:** $40-60/month

---

## Architecture & Components

### Component Structure

```
Agentic Development Stack
├── GitHub Copilot CLI
│   ├── copilot-with-rules.sh (Wrapper)
│   ├── Automatic rule inclusion
│   └── Context-aware rule selection
├── Anthropic Claude API
│   ├── cached_claude.py (Cached wrapper)
│   ├── usage_tracker.py (Cost tracking)
│   └── rate_limiter.py (Usage limits)
├── Monitoring
│   ├── monitor.py (Usage monitoring)
│   └── Prometheus integration (optional)
└── Templates
    ├── deployment-template.sh
    ├── refactoring-template.sh
    └── troubleshooting-template.sh
```

### Scripts Location

**Location:** `scripts/agentic/`

- `copilot-with-rules.sh` - Rule-aware Copilot CLI wrapper
- `usage_tracker.py` - API usage and cost tracking
- `cached_claude.py` - Cached Claude API wrapper
- `rate_limiter.py` - Rate limiting and usage caps
- `monitor.py` - Usage monitoring and metrics
- `test_setup.sh` - Setup verification script

### Integration Points

- **Package.json:** 5 agentic scripts (`agentic:deploy`, `agentic:refactor`, etc.)
- **GitHub Actions:** `.github/workflows/deploy-argo-agentic.yml`
- **Rules:** `Rules/35_AGENTIC_FEATURES.md`
- **Documentation:** `docs/AGENTIC_SETUP_GUIDE.md`

---

## How It Works

### Rule Enforcement Flow

1. **User Issues Command:**
   ```bash
   ./scripts/agentic/copilot-with-rules.sh "Deploy Argo to production"
   ```

2. **Wrapper Script:**
   - Detects context (deployment, refactoring, etc.)
   - Automatically includes relevant rules
   - Adds Rules/ directory references
   - Constructs full command with rules

3. **Copilot CLI:**
   - Receives command with rule context
   - Executes with full rule awareness
   - Follows all 11 safety gates (for deployments)
   - Returns results

4. **Monitoring:**
   - Usage tracked automatically
   - Costs logged
   - Metrics recorded

### Context-Aware Rule Inclusion

The wrapper script automatically detects context and includes relevant rules:

- **Deployment:** Rules/04_DEPLOYMENT.md (11 safety gates)
- **Refactoring:** Rules/02_CODE_QUALITY.md, Rules/01_DEVELOPMENT.md
- **Testing:** Rules/03_TESTING.md
- **Security:** Rules/07_SECURITY.md
- **Frontend:** Rules/11_FRONTEND.md
- **Backend:** Rules/12A_ARGO_BACKEND.md or Rules/12B_ALPINE_BACKEND.md

---

## Setup Guide

### Prerequisites

- Node.js 20.x or later
- Python 3.8 or later
- GitHub account with Copilot Pro subscription
- Anthropic API key (optional, for Claude API)

### Step 1: Install GitHub Copilot CLI

```bash
# Install globally
npm install -g @githubnext/github-copilot-cli

# Verify installation
copilot --version
```

### Step 2: Authenticate Copilot CLI

```bash
# Authenticate with GitHub
copilot auth

# Follow the prompts:
# 1. Browser opens automatically
# 2. Sign in to GitHub
# 3. Authorize Copilot CLI
# 4. Copy token back to terminal
# 5. Press Enter
```

### Step 3: Set Up Anthropic API (Optional)

```bash
# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Install Anthropic SDK (optional)
pip install anthropic
```

### Step 4: Make PATH Permanent (Recommended)

Add to `~/.zshrc`:

```bash
export PATH="/Users/dylanneuenschwander/.nvm/versions/node/v20.11.0/bin:$PATH"
```

Then reload:
```bash
source ~/.zshrc
```

### Step 5: Verify Setup

```bash
# Test setup
./scripts/agentic/test_setup.sh

# Expected output:
# ✅ All tests passed!
```

**See:** `docs/AGENTIC_SETUP_GUIDE.md` for detailed setup instructions

---

## Usage Guide

### Deployment Automation

**Basic Usage:**
```bash
./scripts/agentic/copilot-with-rules.sh "Deploy Argo to production"
```

**What Happens:**
1. All 11 safety gates executed automatically
2. Rules/04_DEPLOYMENT.md automatically referenced
3. Health checks mandatory
4. Automatic rollback on failure

**Package.json Script:**
```bash
pnpm agentic:deploy "Deploy Argo to production"
```

### Code Refactoring

**Basic Usage:**
```bash
./scripts/agentic/copilot-with-rules.sh "Refactor functions over 50 lines in argo/argo/core/"
```

**What Happens:**
1. Functions over 50 lines identified
2. Rules/02_CODE_QUALITY.md automatically referenced
3. Refactoring follows all 35+ rules
4. Tests updated (95% coverage required)

**Package.json Script:**
```bash
pnpm agentic:refactor "Refactor functions over 50 lines"
```

### Troubleshooting

**Basic Usage:**
```bash
./scripts/agentic/copilot-with-rules.sh "Diagnose why health checks are failing"
```

**What Happens:**
1. System analyzed
2. Logs checked
3. Root cause identified
4. Fix suggested based on Rules/29_ERROR_HANDLING.md

### Usage Tracking

**View Usage Report:**
```bash
pnpm agentic:usage
# Or: python scripts/agentic/usage_tracker.py report
```

**View Monitoring Report:**
```bash
pnpm agentic:monitor
# Or: python scripts/agentic/monitor.py report
```

**Check Rate Limits:**
```bash
pnpm agentic:limits
# Or: python scripts/agentic/rate_limiter.py status
```

---

## Rule Enforcement

### Automatic Rule Inclusion

All agentic commands automatically include references to the Rules/ directory:

**Base Rules Context:**
- Rules/ directory (all 35+ rules)
- Rules/04_DEPLOYMENT.md (for deployments)
- Rules/02_CODE_QUALITY.md (for refactoring)
- Rules/01_DEVELOPMENT.md (for development)

**Context-Specific Rules:**
- Deployment: All 11 safety gates
- Refactoring: Code quality standards
- Testing: Testing requirements
- Security: Security practices

### Manual Rule Reference

If using Copilot CLI directly (not recommended):

```bash
# ✅ Good - Includes rule reference
copilot "Deploy Argo to production following all rules in Rules/04_DEPLOYMENT.md"

# ❌ Bad - No rule reference
copilot "Deploy Argo to production"
```

**Recommendation:** Always use `./scripts/agentic/copilot-with-rules.sh` wrapper

---

## Cost Management

### Cost Breakdown

**Monthly Costs:**
- GitHub Copilot Pro: $10/month
- Anthropic API: ~$10-30/month (pay-as-you-go)
- Cursor Pro: $20/month (already have)
- **Total: $40-60/month**

### Cost Optimization

1. **Caching:**
   - `cached_claude.py` caches API responses
   - Reduces redundant API calls
   - Automatic cache invalidation

2. **Rate Limiting:**
   - Daily limits: 100 requests
   - Monthly limits: 2000 requests
   - Cost limits: $10/day, $50/month
   - Automatic blocking when limits reached

3. **Usage Tracking:**
   - All API calls logged
   - Cost per operation tracked
   - Usage reports available

### Monitoring Costs

**View Usage:**
```bash
pnpm agentic:usage
```

**View Limits:**
```bash
pnpm agentic:limits
```

**View Monitoring:**
```bash
pnpm agentic:monitor
```

---

## Troubleshooting

### Issue: Copilot CLI Not Found

**Solution:**
```bash
# Check if installed
which copilot

# If not found, reinstall
npm install -g @githubnext/github-copilot-cli

# Add to PATH
export PATH="/Users/dylanneuenschwander/.nvm/versions/node/v20.11.0/bin:$PATH"
```

### Issue: Authentication Fails

**Solution:**
```bash
# Reset authentication
copilot auth --reset

# Try again
copilot auth
```

### Issue: Rules Not Enforced

**Solution:**
- Always use `./scripts/agentic/copilot-with-rules.sh` wrapper
- Don't use `copilot` command directly
- Verify wrapper script is executable: `chmod +x scripts/agentic/copilot-with-rules.sh`

### Issue: High API Costs

**Solution:**
- Check usage: `pnpm agentic:usage`
- Review rate limits: `pnpm agentic:limits`
- Enable caching (automatic in `cached_claude.py`)
- Adjust rate limits in `rate_limiter.py`

### Issue: Agentic Deployment Fails

**Solution:**
- Check Copilot CLI authentication: `copilot diagnostic`
- Verify wrapper script: `./scripts/agentic/test_setup.sh`
- Check logs: `logs/agentic_usage.jsonl`
- Fallback to traditional deployment if needed

---

## Best Practices

### DO ✅

- Always use `./scripts/agentic/copilot-with-rules.sh` wrapper
- Use package.json scripts for convenience
- Monitor usage regularly
- Set appropriate rate limits
- Review costs monthly
- Test agentic commands before production use

### DON'T ❌

- Use `copilot` command directly (bypasses rule enforcement)
- Skip rule references in commands
- Ignore rate limits
- Deploy without testing agentic commands first
- Use agentic features without monitoring costs

### Recommended Workflow

1. **Development:**
   - Use Cursor Pro for code editing
   - Use agentic features for refactoring
   - Monitor usage and costs

2. **Deployment:**
   - Use agentic deployment for production
   - Verify all safety gates pass
   - Monitor deployment health

3. **Maintenance:**
   - Review usage reports weekly
   - Adjust rate limits as needed
   - Update rules as system evolves

---

## Quick Reference

### Commands

```bash
# Deployment
./scripts/agentic/copilot-with-rules.sh "Deploy Argo to production"
pnpm agentic:deploy "Deploy Argo to production"

# Refactoring
./scripts/agentic/copilot-with-rules.sh "Refactor functions over 50 lines"
pnpm agentic:refactor "Refactor code"

# Monitoring
pnpm agentic:usage
pnpm agentic:monitor
pnpm agentic:limits

# Testing
./scripts/agentic/test_setup.sh
```

### Key Files

- **Wrapper Script:** `scripts/agentic/copilot-with-rules.sh`
- **Rules:** `Rules/35_AGENTIC_FEATURES.md`
- **Setup Guide:** `docs/AGENTIC_SETUP_GUIDE.md`
- **Quick Reference:** `docs/AGENTIC_QUICK_REFERENCE.md`

### Documentation

- **Setup:** `docs/AGENTIC_SETUP_GUIDE.md`
- **Quick Reference:** `docs/AGENTIC_QUICK_REFERENCE.md`
- **Rules:** `Rules/35_AGENTIC_FEATURES.md`
- **Implementation:** `docs/AGENTIC_IMPLEMENTATION_COMPLETE.md`

---

## Related Guides

- **Deployment:** `MONOREPO_DEPLOYMENT_GUIDE.md` - Deployment procedures
- **Local Development:** `LOCAL_DEVELOPMENT_GUIDE.md` - Local setup
- **Troubleshooting:** `TROUBLESHOOTING_RECOVERY_COMPLETE_GUIDE.md` - Issue resolution
- **System Architecture:** `COMPLETE_SYSTEM_ARCHITECTURE.md` - System overview

---

**Last Updated:** January 15, 2025  
**Version:** 1.0

