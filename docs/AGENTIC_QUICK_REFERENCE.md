# Agentic Features - Quick Reference Card

**Last Updated:** January 15, 2025

---

## 🚀 Quick Commands

### Package.json Scripts (Recommended)

```bash
# Automated Deployment (with 11 safety gates)
pnpm agentic:deploy:auto argo production

# Troubleshooting Automation
pnpm agentic:troubleshoot health_check
pnpm agentic:troubleshoot api_failure
pnpm agentic:troubleshoot trading_paused

# Weekly Code Quality Review
pnpm agentic:code-review argo/argo/core

# Test Coverage Analysis
pnpm agentic:test-coverage argo/argo/core

# Monthly Documentation Update
pnpm agentic:docs-update

# Usage Tracking
pnpm agentic:usage

# Monitoring
pnpm agentic:monitor

# Rate Limits
pnpm agentic:limits

# Legacy Commands (still work)
pnpm agentic:deploy "Deploy Argo to production"
pnpm agentic:refactor "Refactor functions over 50 lines"
```

### Direct Scripts (Automated)

```bash
# Automated Deployment (Recommended)
./scripts/agentic/automated-deployment.sh argo production

# Automated Troubleshooting
./scripts/agentic/automated-troubleshooting.sh health_check
./scripts/agentic/automated-troubleshooting.sh api_failure
./scripts/agentic/automated-troubleshooting.sh trading_paused
./scripts/agentic/automated-troubleshooting.sh signal_generation
./scripts/agentic/automated-troubleshooting.sh deployment

# Weekly Code Review
./scripts/agentic/weekly-code-review.sh argo/argo/core

# Test Coverage Analysis
./scripts/agentic/test-coverage-analysis.sh argo/argo/core

# Monthly Documentation Update
./scripts/agentic/monthly-docs-update.sh

# Manual Commands (still work)
./scripts/agentic/copilot-with-rules.sh "Deploy Argo to production"
./scripts/agentic/copilot-with-rules.sh "Refactor functions over 50 lines"
```

### Templates

```bash
# Deployment Template
./scripts/agentic/templates/deployment-template.sh argo production

# Refactoring Template
./scripts/agentic/templates/refactoring-template.sh argo/argo/core/

# Troubleshooting Template
./scripts/agentic/templates/troubleshooting-template.sh "Service returning 500 errors"
```

---

## 🎯 Common Use Cases

### Deploy to Production (Automated)
```bash
# Recommended: Use automated deployment script
pnpm agentic:deploy:auto argo production

# Or use direct script
./scripts/agentic/automated-deployment.sh argo production
```

### Troubleshoot Issues (Automated)
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

### Weekly Code Quality Review
```bash
pnpm agentic:code-review argo/argo/core
```

### Test Coverage Analysis
```bash
pnpm agentic:test-coverage argo/argo/core
```

### Monthly Documentation Update
```bash
pnpm agentic:docs-update
```

### Refactor Code (Manual)
```bash
./scripts/agentic/copilot-with-rules.sh "Refactor signal_generation_service.py's 224-line function into smaller functions"
```

### Understand Codebase
```bash
./scripts/agentic/copilot-with-rules.sh "Explain how the 7-layer risk management system works"
```

---

## 📊 Monitoring Commands

```bash
# View usage report (last 30 days)
pnpm agentic:usage

# View monitoring report (last 7 days)
pnpm agentic:monitor

# Check rate limits
pnpm agentic:limits

# Custom time periods
python scripts/agentic/usage_tracker.py report 7
python scripts/agentic/monitor.py report 30
```

---

## 🔧 Setup (One-Time)

```bash
# 1. Install Copilot CLI
npm install -g @githubnext/github-copilot-cli
copilot auth

# 2. Set API key
export ANTHROPIC_API_KEY="your-key-here"

# 3. Install Python dependencies
pip install anthropic

# 4. Test
./scripts/agentic/copilot-with-rules.sh "test"
```

---

## 💰 Cost Tracking

**Monthly Costs:**
- GitHub Copilot Pro: $10/month
- Anthropic API: ~$10-30/month
- Cursor Pro: $20/month (already have)
- **Total: $40-60/month**

**Check Costs:**
```bash
pnpm agentic:usage
```

---

## 📚 Documentation

- **Setup Guide:** `docs/AGENTIC_SETUP_GUIDE.md`
- **Rules:** `Rules/35_AGENTIC_FEATURES.md`
- **Scripts:** `scripts/agentic/README.md`
- **Implementation:** `docs/AGENTIC_IMPLEMENTATION_COMPLETE.md`

---

## ⚡ Cursor Pro Shortcuts

- `Cmd+I` - Composer Mode (multi-file refactoring)
- `Cmd+Shift+A` - Agent Mode (autonomous tasks)
- `Cmd+L` - Codebase Chat (understanding)

---

**Tip:** Always use `./scripts/agentic/copilot-with-rules.sh` or `pnpm agentic:*` commands to ensure all rules are automatically included!

