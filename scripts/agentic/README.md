# Agentic Features Scripts

**Purpose:** Scripts and tools for agentic AI features (GitHub Copilot CLI, Anthropic Claude API)

---

## Overview

This directory contains all scripts and tools for using agentic AI features in the argo-alpine workspace.

---

## Scripts

### `copilot-with-rules.sh`
Wrapper script for Copilot CLI that automatically includes Rules/ directory references.

**Usage:**
```bash
./scripts/agentic/copilot-with-rules.sh "your command"
```

**Features:**
- Automatically includes relevant rules based on command context
- Detects deployment, refactoring, testing, security contexts
- Ensures all 25+ rules are followed

### `usage_tracker.py`
Track Anthropic API usage and costs.

**Usage:**
```bash
python scripts/agentic/usage_tracker.py report [days]
python scripts/agentic/usage_tracker.py log <model> <input_tokens> <output_tokens> <operation>
```

**Features:**
- Tracks API requests, tokens, and costs
- Generates usage reports
- Cost estimation and warnings

### `cached_claude.py`
Cached wrapper for Anthropic Claude API to reduce costs.

**Usage:**
```python
from scripts.agentic.cached_claude import CachedClaude

claude = CachedClaude()
response = claude.call("your prompt", model="claude-3-5-sonnet-20241022")
```

**Features:**
- Automatic caching of API responses
- Configurable cache TTL
- Cost reduction through caching

### `rate_limiter.py`
Rate limiting and usage caps for Anthropic API.

**Usage:**
```bash
python scripts/agentic/rate_limiter.py check
python scripts/agentic/rate_limiter.py status
```

**Features:**
- Daily and monthly request limits
- Daily and monthly cost limits
- Automatic limit checking

### `monitor.py`
Monitor agentic feature usage and performance.

**Usage:**
```bash
python scripts/agentic/monitor.py report [days]
python scripts/agentic/monitor.py stats [days]
```

**Features:**
- Tracks operation success rates
- Monitors operation durations
- Exports metrics to Prometheus (if available)

---

## Templates

### `templates/deployment-template.sh`
Template for agentic deployments.

**Usage:**
```bash
./scripts/agentic/templates/deployment-template.sh <project> <environment>
```

### `templates/refactoring-template.sh`
Template for agentic refactoring.

**Usage:**
```bash
./scripts/agentic/templates/refactoring-template.sh <target> [scope]
```

### `templates/troubleshooting-template.sh`
Template for agentic troubleshooting.

**Usage:**
```bash
./scripts/agentic/templates/troubleshooting-template.sh <issue_description>
```

---

## Quick Reference

### Common Commands

```bash
# Deployment
./scripts/agentic/copilot-with-rules.sh "Deploy Argo to production"

# Refactoring
./scripts/agentic/copilot-with-rules.sh "Refactor functions over 50 lines in argo/argo/core/"

# Usage tracking
python scripts/agentic/usage_tracker.py report

# Rate limits
python scripts/agentic/rate_limiter.py status

# Monitoring
python scripts/agentic/monitor.py report
```

### Using Package.json Scripts

```bash
pnpm agentic:deploy "Deploy Argo to production"
pnpm agentic:refactor "Refactor functions over 50 lines"
pnpm agentic:usage
pnpm agentic:monitor
pnpm agentic:limits
```

---

## Related Documentation

- **Rules:** `Rules/35_AGENTIC_FEATURES.md` - Complete agentic features rules
- **Setup Guide:** `docs/AGENTIC_SETUP_GUIDE.md` - Setup instructions
- **Deployment:** `Rules/04_DEPLOYMENT.md` - 11 safety gates

---

**Note:** All scripts automatically enforce rules from the Rules/ directory. Use wrapper scripts to ensure compliance.

