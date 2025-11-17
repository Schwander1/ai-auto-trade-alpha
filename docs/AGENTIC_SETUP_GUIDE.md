# Agentic Development Stack Setup Guide

**Date:** January 15, 2025  
**Version:** 1.0  
**Status:** Complete Setup Instructions

---

## Overview

This guide sets up the complete agentic development stack for argo-alpine workspace:

- **GitHub Copilot Pro** ($10/month) - Deployment automation & terminal workflows
- **Anthropic Claude API** (pay-as-you-go) - Deep codebase understanding & refactoring
- **Cursor Pro** ($20/month) - Already configured ✅

**Total Cost:** $30/month + $10-30/month API usage = $40-60/month

---

## Step 1: Install GitHub Copilot Pro

### 1.1 Sign Up for Copilot Pro

1. Go to: https://github.com/features/copilot
2. Click "Get Copilot Pro"
3. Select **Pro** plan ($10/month or $100/year)
4. Complete payment setup

### 1.2 Install Copilot CLI

```bash
# Install globally
npm install -g @githubnext/github-copilot-cli

# Verify installation
copilot --version
```

### 1.3 Authenticate

```bash
# Authenticate with GitHub
copilot auth

# Follow the prompts to:
# 1. Open browser
# 2. Authorize Copilot CLI
# 3. Copy token back to terminal
```

### 1.4 Test Installation

```bash
# Test with a simple command
copilot "What files are in the current directory?"

# Should return a helpful response
```

---

## Step 2: Configure Anthropic API Key

### 2.1 Set Environment Variable

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Anthropic API Key (already have)
export ANTHROPIC_API_KEY="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"

# Reload shell
source ~/.zshrc  # or source ~/.bashrc
```

### 2.2 Verify API Key Works

```bash
# Test API key
python3 -c "
from anthropic import Anthropic
import os
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
print('✅ API key is valid!')
"
```

### 2.3 Add to Workspace .env (Optional)

Create or update `.env.local` in workspace root:

```bash
# .env.local
ANTHROPIC_API_KEY=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
```

---

## Step 3: Install Python Dependencies

```bash
# Install Anthropic SDK
pip install anthropic

# Or if using requirements.txt
pip install -r requirements.txt
```

---

## Step 4: Test Your Setup

### 4.1 Test Copilot CLI

```bash
# Test deployment automation
./scripts/agentic/copilot-with-rules.sh "Show me the deployment workflow for Argo to production"

# Test code understanding
./scripts/agentic/copilot-with-rules.sh "Explain how the 7-layer risk management system works in argo/argo/core/"

# Test troubleshooting
./scripts/agentic/copilot-with-rules.sh "What are common issues in the signal generation service?"
```

### 4.2 Test Anthropic API

```bash
# Test with Python
python3 << EOF
from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[{
        "role": "user",
        "content": "Hello! Can you help me refactor code?"
    }]
)
print("✅ API working! Response:", response.content[0].text[:50])
EOF
```

### 4.3 Test Cursor Pro (Already Configured)

- Press `Cmd+I` - Composer should open
- Press `Cmd+Shift+A` - Agent Mode should open
- Press `Cmd+L` - Codebase Chat should open

---

## Step 5: Quick Start Commands

### 5.1 Using Package.json Scripts

```bash
# Deployment
pnpm agentic:deploy "Deploy Argo to production"

# Refactoring
pnpm agentic:refactor "Refactor functions over 50 lines in argo/argo/core/"

# Usage tracking
pnpm agentic:usage

# Monitoring
pnpm agentic:monitor

# Rate limits
pnpm agentic:limits
```

### 5.2 Using Direct Scripts

```bash
# Deployment
./scripts/agentic/copilot-with-rules.sh "Deploy Argo to production"

# Using templates
./scripts/agentic/templates/deployment-template.sh argo production
./scripts/agentic/templates/refactoring-template.sh argo/argo/core/
./scripts/agentic/templates/troubleshooting-template.sh "Service returning 500 errors"
```

---

## Step 6: Monitor Usage & Costs

### 6.1 Anthropic API Usage

```bash
# View usage report
python scripts/agentic/usage_tracker.py report

# View last 7 days
python scripts/agentic/usage_tracker.py report 7

# Or use pnpm script
pnpm agentic:usage
```

### 6.2 Check Rate Limits

```bash
# Check current limits
python scripts/agentic/rate_limiter.py status

# Or use pnpm script
pnpm agentic:limits
```

### 6.3 Monitor Operations

```bash
# View monitoring report
python scripts/agentic/monitor.py report

# Or use pnpm script
pnpm agentic:monitor
```

### 6.4 Cost Estimates

**Anthropic API:**
- Claude 3.5 Sonnet: ~$3-15 per 1M input tokens, ~$15 per 1M output tokens
- Typical refactoring session: ~100K-500K tokens = $1-10
- Monthly estimate: $10-30 for development work

**GitHub Copilot:**
- 300 premium requests/month (Pro plan)
- Unlimited basic completions

---

## Step 7: Common Workflows

### 7.1 Automated Deployment (Recommended)

```bash
# Automated deployment with all 11 safety gates (RECOMMENDED)
pnpm agentic:deploy:auto argo production

# Or use direct script
./scripts/agentic/automated-deployment.sh argo production

# Deploy Alpine
pnpm agentic:deploy:auto alpine production
```

### 7.2 Automated Troubleshooting

```bash
# Health check failures
pnpm agentic:troubleshoot health_check

# API failures
pnpm agentic:troubleshoot api_failure

# Trading paused
pnpm agentic:troubleshoot trading_paused

# Signal generation issues
pnpm agentic:troubleshoot signal_generation

# Deployment failures
pnpm agentic:troubleshoot deployment
```

### 7.3 Weekly Code Quality Review

```bash
# Automated code quality review
pnpm agentic:code-review argo/argo/core

# Or use direct script
./scripts/agentic/weekly-code-review.sh argo/argo/core
```

### 7.4 Test Coverage Analysis

```bash
# Analyze test coverage gaps
pnpm agentic:test-coverage argo/argo/core

# Or use direct script
./scripts/agentic/test-coverage-analysis.sh argo/argo/core
```

### 7.5 Monthly Documentation Update

```bash
# Update documentation
pnpm agentic:docs-update

# Or use direct script
./scripts/agentic/monthly-docs-update.sh
```

### 7.6 Autonomous Refactoring (Manual)

```bash
# Refactor functions over 50 lines
./scripts/agentic/copilot-with-rules.sh "Refactor the 8 functions over 50 lines in argo/argo/core/ following our 25+ rules"

# Or use Cursor Agent Mode (Cmd+Shift+A)
"Refactor signal_generation_service.py's 224-line function into smaller functions following Rules/02_CODE_QUALITY.md"
```

---

## Troubleshooting

### Issue: Copilot CLI not found

```bash
# Reinstall
npm install -g @githubnext/github-copilot-cli

# Check PATH
which copilot
```

### Issue: Anthropic API key not working

```bash
# Verify key is set
echo $ANTHROPIC_API_KEY

# Test with curl
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"test"}]}'
```

### Issue: Copilot authentication fails

```bash
# Re-authenticate
copilot auth --reset
copilot auth
```

### Issue: Python scripts not executable

```bash
# Make scripts executable
chmod +x scripts/agentic/*.py
chmod +x scripts/agentic/*.sh
chmod +x scripts/agentic/templates/*.sh
```

---

## Next Steps

1. ✅ Complete Step 1: Install GitHub Copilot Pro
2. ✅ Complete Step 2: Configure Anthropic API Key
3. ✅ Complete Step 3: Install Python Dependencies
4. ✅ Complete Step 4: Test Your Setup
5. ✅ Start using agentic features!

---

## Quick Reference

### Common Commands

```bash
# Deployment
./scripts/agentic/copilot-with-rules.sh "Deploy Argo to production"
./scripts/agentic/copilot-with-rules.sh "Deploy Alpine to production"

# Refactoring
./scripts/agentic/copilot-with-rules.sh "Refactor functions over 50 lines in argo/argo/core/"

# Troubleshooting
./scripts/agentic/copilot-with-rules.sh "Diagnose why health checks are failing"

# Usage Tracking
pnpm agentic:usage

# Cost Monitoring
python scripts/agentic/usage_tracker.py report

# Rate Limits
pnpm agentic:limits
```

### Cursor Pro Shortcuts
- `Cmd+I` - Composer Mode (multi-file refactoring)
- `Cmd+Shift+A` - Agent Mode (autonomous tasks)
- `Cmd+L` - Codebase Chat (understanding)

---

## Related Documentation

- **Rules:** [Rules/35_AGENTIC_FEATURES.md](../Rules/35_AGENTIC_FEATURES.md) - Complete agentic features rules
- **Deployment:** [Rules/04_DEPLOYMENT.md](../Rules/04_DEPLOYMENT.md) - 11 safety gates
- **Code Quality:** [Rules/02_CODE_QUALITY.md](../Rules/02_CODE_QUALITY.md) - Refactoring guidelines
- **Cursor Pro:** [docs/CURSOR_PRO_QUICK_REFERENCE.md](CURSOR_PRO_QUICK_REFERENCE.md) - Cursor Pro features

---

**Setup Complete!** 🎉

You now have a fully agentic development stack ready to automate your workflows!

