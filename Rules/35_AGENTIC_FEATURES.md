# Agentic Features Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** All development work

---

## Overview

Rules and guidelines for using agentic AI features (GitHub Copilot CLI, Anthropic Claude API, Cursor Pro) to automate development workflows, deployments, and code refactoring.

**Strategic Context:** Agentic features align with efficiency and automation goals defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md).

**See Also:** [docs/AGENTIC_SETUP_GUIDE.md](../docs/AGENTIC_SETUP_GUIDE.md) for setup instructions.

---

## Available Agentic Tools

### 1. Cursor Pro (Automatic ✅)
- **Status:** Already configured and automatic
- **Features:** Agent Mode, Composer, Codebase Chat, Bugbot
- **Rule Enforcement:** Automatically enforces all Rules/ directory
- **Usage:** Press `Cmd+I` (Composer), `Cmd+Shift+A` (Agent), `Cmd+L` (Chat)
- **Cost:** $20/month (already subscribed)

### 2. GitHub Copilot CLI (Manual Trigger)
- **Status:** Requires manual command execution
- **Features:** Deployment automation, terminal workflows
- **Rule Enforcement:** Must reference Rules/ directory in commands
- **Usage:** `copilot "command with rule reference"` or `./scripts/agentic/copilot-with-rules.sh "command"`
- **Cost:** $10/month (Copilot Pro)

### 3. Anthropic Claude API (Manual Trigger)
- **Status:** Requires API key (already have)
- **Features:** Deep codebase understanding, refactoring
- **Rule Enforcement:** Must reference Rules/ directory
- **Usage:** Via Python scripts or CLI tools in `scripts/agentic/`
- **Cost:** Pay-as-you-go (~$10-30/month estimated)

---

## Rule: Always Reference Rules Directory

**Rule:** All agentic commands MUST reference Rules/ directory

**Why:** Ensures all AI tools follow our 25+ development rules

**Implementation:**
- Use `./scripts/agentic/copilot-with-rules.sh` wrapper (automatically includes rules)
- Include "following our rules in Rules/ directory" in manual commands
- Reference specific rule files when relevant
- Ensure tools have access to Rules/ directory

**Example:**
```bash
# ✅ Good - Uses wrapper (automatic rule inclusion)
./scripts/agentic/copilot-with-rules.sh "Deploy Argo to production"

# ✅ Good - Manual with rule reference
copilot "Deploy Argo to production following all rules in Rules/04_DEPLOYMENT.md"

# ❌ Bad - No rule reference
copilot "Deploy Argo to production"
```

---

## Deployment Automation Rules

### Rule: Use Copilot CLI for Deployments

**Rule:** All deployments MUST use Copilot CLI with 11 safety gates

**11 Safety Gates (from Rules/04_DEPLOYMENT.md):**
1. Identify Changes
2. Verify Scope
3. Run Tests
4. Run Linting
5. Build Locally
6. Verify Staging
7. Validate Environment
8. Code Quality Check
9. Pre-Deployment Health
10. Explicit Confirmation
11. Post-Deployment Health (Level 3)

**Command Format:**
```bash
# Recommended: Use wrapper script
./scripts/agentic/copilot-with-rules.sh "Deploy Argo to production"

# Or manual with full specification
copilot "Deploy [project] to production following all 11 safety gates in Rules/04_DEPLOYMENT.md. 
If any gate fails, rollback automatically."
```

**Automatic Enforcement:**
- Copilot CLI will execute all 11 gates
- Automatic rollback on failure
- Health checks mandatory
- All rules automatically included via wrapper

---

## Refactoring Automation Rules

### Rule: Use Agentic Tools for Complex Refactoring

**Rule:** Functions over 50 lines MUST be refactored using agentic tools

**Process:**
1. Identify functions over 50 lines
2. Use Claude API or Cursor Agent Mode
3. Reference Rules/02_CODE_QUALITY.md
4. Ensure all 25+ rules followed
5. Update tests (95% coverage required)

**Command Format:**
```bash
# Using Cursor Agent Mode (Cmd+Shift+A) - Recommended
"Refactor [file] following Rules/02_CODE_QUALITY.md. 
Break functions over 50 lines into smaller functions. 
Ensure all 25+ rules in Rules/ directory are followed."

# Using Copilot CLI
./scripts/agentic/copilot-with-rules.sh "Refactor functions over 50 lines in [directory]"

# Using Claude API directly
python scripts/agentic/refactor_with_claude.py --file [file] --rules Rules/
```

---

## Code Review Automation

### Rule: Bugbot Automatically Reviews PRs

**Rule:** All PRs automatically reviewed by Bugbot

**Status:** ✅ Already automatic

**What Bugbot Checks:**
- All 25+ rules in Rules/ directory
- Security vulnerabilities
- Code quality issues
- Test coverage (95% required)
- Naming conventions
- SOLID principles

**No Action Required:** Bugbot runs automatically on every PR

---

## When to Use Each Tool

### Use Cursor Pro For:
- ✅ Multi-file refactoring (Composer Mode - `Cmd+I`)
- ✅ Complex feature implementation (Agent Mode - `Cmd+Shift+A`)
- ✅ Codebase understanding (Codebase Chat - `Cmd+L`)
- ✅ Quick code suggestions (Inline completions)
- ✅ PR reviews (Bugbot - automatic)

### Use Copilot CLI For:
- ✅ Deployment automation (11 safety gates)
- ✅ Terminal workflows
- ✅ Multi-step operations
- ✅ Production deployments
- ✅ Complex command sequences

### Use Claude API For:
- ✅ Deep codebase analysis
- ✅ Complex refactoring across services
- ✅ Architecture decisions
- ✅ Code generation with full context
- ✅ Large-scale refactoring projects

---

## Automatic Rule Enforcement

### Cursor Pro (Automatic ✅)
- Automatically reads Rules/ directory
- Enforces all rules in Agent Mode, Composer, Chat
- Bugbot automatically reviews PRs
- **No configuration needed**

### Copilot CLI (Semi-Automatic)
- Use `./scripts/agentic/copilot-with-rules.sh` wrapper (automatic rule inclusion)
- Can be configured to always include rules
- **Configuration:** Wrapper script handles this automatically

### Claude API (Semi-Automatic)
- Use scripts in `scripts/agentic/` (automatic rule inclusion)
- Must explicitly reference Rules/ in direct API calls
- **Configuration:** Helper scripts auto-include rules

---

## Cost Management Rules

### Rule: Monitor and Optimize API Usage

**Rule:** Track all agentic API usage and costs

**Implementation:**
- Use `scripts/agentic/usage_tracker.py` to track usage
- Review monthly costs via `pnpm agentic:usage`
- Set usage limits via `scripts/agentic/rate_limiter.py`
- Use caching to reduce API calls

**Cost Targets:**
- Anthropic API: $10-30/month (development work)
- GitHub Copilot: $10/month (fixed)
- Cursor Pro: $20/month (fixed)
- **Total:** $40-60/month

**Optimization:**
- Use cached responses when possible
- Batch similar requests
- Use cheaper models for simple tasks
- Monitor usage patterns

---

## Security Rules

### Rule: Protect API Keys

**Rule:** Never commit API keys to version control

**Implementation:**
- Store API keys in environment variables
- Use AWS Secrets Manager for production
- Never log API keys
- Rotate keys regularly

**See:** [07_SECURITY.md](07_SECURITY.md) for complete security rules

---

## Best Practices

### DO ✅
- Always use `./scripts/agentic/copilot-with-rules.sh` wrapper for Copilot CLI
- Use Cursor Agent Mode for complex tasks
- Monitor API usage and costs
- Reference specific rule files when relevant
- Let Bugbot automatically review PRs
- Use appropriate tool for the task
- Cache API responses when possible

### DON'T ❌
- Use agentic tools without rule references
- Skip safety gates in deployments
- Ignore Bugbot reviews
- Use wrong tool for the task
- Deploy without agentic automation
- Commit API keys
- Exceed usage limits without monitoring

---

## Error Handling & Recovery

### Rule: Implement Fallback Mechanisms

**Rule:** All agentic operations must have fallback mechanisms

**Implementation:**
- If Copilot CLI fails, fall back to manual scripts
- If Claude API fails, use Cursor Agent Mode
- If agentic deployment fails, use standard deployment
- Always log errors for analysis

**Example:**
```bash
# Wrapper script handles fallback automatically
./scripts/agentic/copilot-with-rules.sh "Deploy Argo" || ./scripts/deploy-argo-blue-green.sh
```

---

## Monitoring & Observability

### Rule: Track Agentic Feature Usage

**Rule:** Monitor all agentic operations for optimization

**Metrics to Track:**
- API request counts
- API costs
- Operation success rates
- Operation durations
- Tool usage patterns

**Implementation:**
- Use `scripts/agentic/monitor.py` for tracking
- Export metrics to Prometheus (if configured)
- Review monthly usage reports
- Optimize based on patterns

---

## Related Rules

- **Deployment:** [04_DEPLOYMENT.md](04_DEPLOYMENT.md) - 11 safety gates
- **Code Quality:** [02_CODE_QUALITY.md](02_CODE_QUALITY.md) - Refactoring guidelines
- **Development:** [01_DEVELOPMENT.md](01_DEVELOPMENT.md) - Development practices
- **Security:** [07_SECURITY.md](07_SECURITY.md) - Security best practices
- **Monitoring:** [14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md) - Monitoring rules
- **Cursor Profiles:** [34_CURSOR_PROFILES.md](34_CURSOR_PROFILES.md) - Profile usage

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
```

### Cursor Pro Shortcuts
- `Cmd+I` - Composer Mode (multi-file refactoring)
- `Cmd+Shift+A` - Agent Mode (autonomous tasks)
- `Cmd+L` - Codebase Chat (understanding)

---

**Note:** Agentic features are powerful tools that automate workflows while enforcing all development rules. Always use the wrapper scripts to ensure rule compliance. Monitor usage and costs regularly to optimize efficiency.

