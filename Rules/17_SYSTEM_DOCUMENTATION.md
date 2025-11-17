# System Documentation Rules

**Last Updated:** November 17, 2025
**Version:** 2.0
**Applies To:** SystemDocs directory management

---

## Overview

This rule governs the management and maintenance of the `docs/SystemDocs/` directory, which contains comprehensive guides and documentation for the systems in this workspace. This rule ensures SystemDocs are kept up-to-date with the most current system implementation, but **only when explicitly requested**.

**Note:** This workspace contains two separate, independent entities (Argo Capital and Alpine Analytics LLC). SystemDocs should document each entity separately with no cross-references.

**Note:** This rule is separate from `08_DOCUMENTATION.md`, which covers general documentation standards (code comments, API docs, README files). This rule specifically focuses on SystemDocs management.

---

## SystemDocs Location & Structure

### Primary Location
- **Path:** `docs/SystemDocs/`
- **Index:** `docs/SystemDocs/COMPLETE_GUIDES_INDEX.md`
- **Purpose:** Comprehensive operational and technical guides

### Key Documents

#### Complete Guides (Primary References)
1. **`BACKTESTING_COMPLETE_GUIDE.md`** - Backtesting framework guide
2. **`RISK_MANAGEMENT_COMPLETE_GUIDE.md`** - 7-layer risk management system
3. **`SIGNAL_GENERATION_COMPLETE_GUIDE.md`** - Weighted Consensus v6.0 algorithm (v6.0)
4. **`TRADING_EXECUTION_COMPLETE_GUIDE.md`** - Order execution and position sizing
5. **`SYSTEM_MONITORING_COMPLETE_GUIDE.md`** - Health checks and monitoring
6. **`TROUBLESHOOTING_RECOVERY_COMPLETE_GUIDE.md`** - Diagnostic and recovery procedures
7. **`CONFIGURATION_MANAGEMENT_COMPLETE_GUIDE.md`** - Configuration structure and management
8. **`ENVIRONMENT_DEPLOYMENT_COMPLETE_GUIDE.md`** - Deployment and environment management

#### Architecture & Status Documents
- **`COMPLETE_SYSTEM_ARCHITECTURE.md`** - Full system architecture overview
- **`FINAL_SYSTEM_STATUS_REPORT.md`** - Current system status
- **`COMPLETE_GUIDES_INDEX.md`** - Index of all guides

---

## Critical Rule: Update Only When Asked

### ⚠️ NEVER Update SystemDocs Automatically

**Rule:** SystemDocs are **ONLY** updated when the user explicitly requests it.

**Why:**
- SystemDocs represent the authoritative state of the system
- Automatic updates could introduce errors or inconsistencies
- User must verify accuracy before documentation changes
- Prevents documentation drift from code changes

**When to Update:**
- ✅ User explicitly says: "update system docs", "refresh system documentation", "make system docs current"
- ✅ User asks: "ensure system docs are up to date"
- ✅ User requests: "update [specific guide] with current system"

**When NOT to Update:**
- ❌ After code changes (unless explicitly asked)
- ❌ After feature additions (unless explicitly asked)
- ❌ During refactoring (unless explicitly asked)
- ❌ Automatically as part of other tasks

---

## System Knowledge Requirements

### Full System Setup Knowledge

When working with SystemDocs, you must know:

#### 1. Core Components

**Argo Capital (Signal Generation)**
- **Location:** `argo/`
- **Main Service:** `argo/core/signal_generation_service.py`
- **Consensus Engine:** `argo/core/weighted_consensus_engine.py`
- **Trading Engine:** `argo/core/paper_trading_engine.py`
- **Backtesting:** `argo/backtest/`
- **Config:** `argo/config.json`

**Alpine Analytics (Distribution)**
- **Backend:** `alpine-backend/backend/`
- **Frontend:** `alpine-frontend/`
- **Database:** PostgreSQL (production), SQLite (local)
- **API:** FastAPI endpoints

#### 2. Environment Setup

**Development:**
- Local machine
- Dev Alpaca paper trading account
- SQLite database
- Local config files

**Production:**
- Argo Server: 178.156.194.174
- Alpine Server: 91.98.153.49
- Production Alpaca paper trading account
- PostgreSQL database
- AWS Secrets Manager

#### 3. Key System Features

- **Signal Generation:** Every 5 seconds, Weighted Consensus v6.0 (v6.0)
- **Data Sources:** Massive (40%), Alpha Vantage (25%), X Sentiment (20%), Sonar AI (15%)
- **Risk Management:** 7-layer protection system
- **Backtesting:** Strategy backtester + Profit backtester
- **Environment Detection:** Automatic dev/prod switching
- **SHA-256 Verification:** Signal integrity verification
- **Position Monitoring:** Real-time position tracking

#### 4. Configuration Structure

- **Trading Config:** `config.json` (dev/prod sections)
- **Risk Parameters:** Position sizing, drawdown limits, correlation groups
- **Signal Parameters:** Consensus threshold, min confidence, source weights
- **Execution Parameters:** Order types, retry logic, position monitoring

---

## SystemDocs Update Process

### When User Requests Update

#### Step 1: Analyze Current System
1. **Review Codebase:**
   - Check core components for changes
   - Verify configuration structure
   - Review recent implementations
   - Check for new features

2. **Check Conversation Logs (if available):**
   - Review `conversation_logs/decisions/` for recent decisions (30-day retention)
   - Check `conversation_logs/sessions/` for full context (3-day retention)
   - See [23_CONVERSATION_LOGGING.md](23_CONVERSATION_LOGGING.md) for details
   - **Note:** Conversation logs are LOCAL ONLY and may not always be available

3. **Compare with SystemDocs:**
   - Read relevant SystemDocs files
   - Identify gaps or outdated information
   - Note missing components or features
   - Check for inconsistencies

#### Step 2: Identify What Needs Updating
1. **Complete Guides:**
   - Which guides are affected?
   - What sections need updates?
   - Are new guides needed?

2. **Architecture Documents:**
   - System architecture changes?
   - New components added?
   - Data flow changes?

3. **Index Files:**
   - Update `COMPLETE_GUIDES_INDEX.md` if needed
   - Add new guides to index
   - Update dependencies

#### Step 3: Update SystemDocs
1. **Follow Guide Format:**
   - Use existing guide structure
   - Maintain consistency
   - Include all required sections

2. **Verify Accuracy:**
   - Cross-reference with code
   - Verify configuration examples
   - Check file paths and locations
   - Ensure examples work

3. **Fill Gaps:**
   - Add missing information
   - Clarify unclear sections
   - Add troubleshooting steps
   - Include best practices

#### Step 4: Optimize
1. **Improve Clarity:**
   - Simplify complex explanations
   - Add diagrams if helpful
   - Include more examples
   - Better organization

2. **Enhance Usability:**
   - Improve quick reference sections
   - Add cross-references
   - Update dependencies
   - Better navigation

---

## Guide Format Standard

### Required Sections (Complete Guides)

1. **Executive Summary** - Overview and purpose
2. **Table of Contents** - Navigation
3. **System Overview** - High-level understanding
4. **Architecture & Components** - Technical details
5. **How It Works** - Step-by-step process
6. **What Affects What** - Correlations and dependencies
7. **Configuration Guide** - How to configure
8. **Troubleshooting** - Common issues and solutions
9. **Best Practices** - Recommendations
10. **Quick Reference** - Quick lookup

### Document Headers

```markdown
# [Title]

**Date:** [Current Date]
**Version:** [Version Number]
**Status:** [Status]

---
```

---

## Gap Filling Strategy

### When Updating SystemDocs

#### 1. Identify Gaps
- **Missing Components:** Components not documented
- **Outdated Information:** Information that doesn't match code
- **Incomplete Sections:** Sections with missing details
- **Missing Examples:** Concepts without examples
- **Unclear Explanations:** Confusing or vague content

#### 2. Fill Gaps
- **Add Missing Information:** Document all components
- **Update Outdated Content:** Match current implementation
- **Complete Sections:** Add all required details
- **Add Examples:** Provide working examples
- **Clarify Explanations:** Make content clear and actionable

#### 3. Optimize Content
- **Improve Organization:** Better structure and flow
- **Enhance Clarity:** Clearer explanations
- **Add Cross-References:** Link related sections
- **Update Dependencies:** Reflect current relationships
- **Improve Navigation:** Better table of contents

---

## Verification Checklist

### Before Completing SystemDocs Update

- [ ] All guides reviewed for accuracy
- [ ] Code cross-referenced with documentation
- [ ] Configuration examples verified
- [ ] File paths and locations correct
- [ ] Examples tested and working
- [ ] No outdated information
- [ ] All components documented
- [ ] Gaps filled
- [ ] Content optimized
- [ ] Index updated (if needed)
- [ ] Format consistent
- [ ] Cross-references correct

---

## SystemDocs Maintenance

### Regular Review (When Asked)

When user requests SystemDocs update, review:

1. **Complete Guides:**
   - Are they current?
   - Do they match implementation?
   - Are examples working?
   - Are gaps filled?

2. **Architecture Documents:**
   - Reflect current architecture?
   - Include all components?
   - Data flows accurate?

3. **Index Files:**
   - All guides listed?
   - Dependencies correct?
   - Navigation clear?

### Documentation Accuracy

**Rule:** SystemDocs must accurately reflect the current system implementation.

**Verification:**
- Cross-reference with code
- Verify configuration examples
- Test code examples
- Check file paths
- Verify component locations

---

## Related Rules

- **[08_DOCUMENTATION.md](08_DOCUMENTATION.md)** - General documentation standards (code comments, API docs, README files)
- **[09_WORKSPACE.md](09_WORKSPACE.md)** - Workspace organization (includes docs/ structure)
- **[04_DEPLOYMENT.md](04_DEPLOYMENT.md)** - Deployment procedures (referenced in deployment guides)
- **[05_ENVIRONMENT.md](05_ENVIRONMENT.md)** - Environment management (referenced in environment guides)

---

## Quick Reference

### SystemDocs Location
- **Path:** `docs/SystemDocs/`
- **Index:** `docs/SystemDocs/COMPLETE_GUIDES_INDEX.md`

### When to Update
- ✅ **ONLY** when user explicitly requests
- ❌ **NEVER** automatically

### Update Process
1. Analyze current system
2. Compare with SystemDocs
3. Identify gaps
4. Update SystemDocs
5. Verify accuracy
6. Optimize content

### Key Documents
- Complete Guides (8 guides)
- Architecture documents
- Status reports
- Index files

---

**Remember:** SystemDocs are authoritative documentation. Only update when explicitly requested, and always verify accuracy against the current system implementation.
