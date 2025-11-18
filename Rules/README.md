# Rules Directory

**Purpose:** Centralized, organized rules for the workspace, divided by function for easy maintenance and reference. Note: This workspace contains two separate, independent entities (Argo Capital and Alpine Analytics LLC) with no cross-references.

**Last Updated:** November 18, 2025  
**Total Rules Files:** 36  
**Current System State:** v3.0 - Unified Architecture - Single signal generator with multi-executor trading

**Note:** For current system status, see [SYSTEM_STATUS.md](../SYSTEM_STATUS.md) (single source of truth)

---

## 📋 Quick Index

### Core Development Rules
- **[01_DEVELOPMENT.md](01_DEVELOPMENT.md)** - Development practices, coding standards, naming conventions
- **[02_CODE_QUALITY.md](02_CODE_QUALITY.md)** - Code quality standards, review process, refactoring guidelines
- **[03_TESTING.md](03_TESTING.md)** - Testing requirements, coverage standards, test organization
- **[19_CONTINUOUS_OPTIMIZATION.md](19_CONTINUOUS_OPTIMIZATION.md)** - Continuous optimization and world-class excellence mindset

### Infrastructure & Operations
- **[04_DEPLOYMENT.md](04_DEPLOYMENT.md)** - Deployment safety gates, procedures, rollback
- **[05_ENVIRONMENT.md](05_ENVIRONMENT.md)** - Environment detection, configuration, dev/prod differences
- **[06_CONFIGURATION.md](06_CONFIGURATION.md)** - Configuration management, secrets, settings
- **[26_API_DESIGN.md](26_API_DESIGN.md)** - API design standards, versioning, documentation
- **[27_DATABASE_MIGRATIONS.md](27_DATABASE_MIGRATIONS.md)** - Database migration procedures, schema changes
- **[28_PERFORMANCE.md](28_PERFORMANCE.md)** - Performance optimization, caching, budgets
- **[29_ERROR_HANDLING.md](29_ERROR_HANDLING.md)** - Error handling patterns, resilience, recovery
- **[30_CODE_REVIEW.md](30_CODE_REVIEW.md)** - Code review process, PR templates, guidelines
- **[31_FEATURE_FLAGS.md](31_FEATURE_FLAGS.md)** - Feature flag management, A/B testing
- **[32_DATA_LIFECYCLE.md](32_DATA_LIFECYCLE.md)** - Data retention policies, archiving, purging
- **[33_DISASTER_RECOVERY.md](33_DISASTER_RECOVERY.md)** - Disaster recovery, backup procedures, business continuity

### Security & Compliance
- **[07_SECURITY.md](07_SECURITY.md)** - Security best practices, vulnerability prevention, compliance
- **[36_RBAC_AUTHORIZATION.md](36_RBAC_AUTHORIZATION.md)** - Role-Based Access Control (RBAC) system

### Documentation & Organization
- **[08_DOCUMENTATION.md](08_DOCUMENTATION.md)** - Documentation standards, formatting, structure
- **[09_WORKSPACE.md](09_WORKSPACE.md)** - Workspace organization, file structure, cleanup rules

### Project-Specific Rules
- **[10_MONOREPO.md](10_MONOREPO.md)** - Workspace structure, entity separation (NO shared code)
- **[11_FRONTEND.md](11_FRONTEND.md)** - Alpine Analytics LLC Frontend rules (Next.js, TypeScript, React)
- **[12A_ARGO_BACKEND.md](12A_ARGO_BACKEND.md)** - Argo Capital Backend rules (Python, FastAPI)
- **[12B_ALPINE_BACKEND.md](12B_ALPINE_BACKEND.md)** - Alpine Analytics LLC Backend rules (Python, FastAPI)

### Trading & Operations Rules
- **[13_TRADING_OPERATIONS.md](13_TRADING_OPERATIONS.md)** - Trading operations, signal generation, risk management, position monitoring, prop firm trading (Argo Capital only)
- **[25_DATA_SOURCES.md](25_DATA_SOURCES.md)** - Data source integration, optimization, and configuration
- **[14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md)** - Monitoring, logging, metrics, health checks
- **[15_BACKTESTING.md](15_BACKTESTING.md)** - Backtesting framework, strategy testing, parameter optimization
- **[16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md)** - Development vs Production differences, automatic switching, deployment consistency

### Documentation & Optimization Rules
- **[17_SYSTEM_DOCUMENTATION.md](17_SYSTEM_DOCUMENTATION.md)** - SystemDocs management, update process, system knowledge
- **[18_VERSIONING_ARCHIVING.md](18_VERSIONING_ARCHIVING.md)** - File versioning and automatic archiving system
- **[19_CONTINUOUS_OPTIMIZATION.md](19_CONTINUOUS_OPTIMIZATION.md)** - Continuous optimization and world-class excellence mindset
- **[28_PERFORMANCE.md](28_PERFORMANCE.md)** - Performance optimization rules (v2.0 - All 15 optimizations documented)
- **[20_INTELLIGENT_CODE_ORGANIZATION.md](20_INTELLIGENT_CODE_ORGANIZATION.md)** - Feature-based code organization, automatic enforcement
- **[21_DEPENDENCY_IMPACT_ANALYSIS.md](21_DEPENDENCY_IMPACT_ANALYSIS.md)** - Dependency tracking and impact analysis (mandatory)
- **[22_TRADE_SECRET_IP_PROTECTION.md](22_TRADE_SECRET_IP_PROTECTION.md)** - Trade secret and IP protection (mandatory)
- **[23_CONVERSATION_LOGGING.md](23_CONVERSATION_LOGGING.md)** - Conversation logging system (LOCAL DEVELOPMENT ONLY)

### Strategic & Leadership Rules
- **[24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md)** - Vision, mission, strategic goals, and decision-making framework

### Data Sources Rules
- **[25_DATA_SOURCES.md](25_DATA_SOURCES.md)** - Data source integration, optimization, and configuration rules

### Development Tools Rules
- **[34_CURSOR_PROFILES.md](34_CURSOR_PROFILES.md)** - Cursor Pro profiles usage and guidelines
- **[35_AGENTIC_FEATURES.md](35_AGENTIC_FEATURES.md)** - Agentic AI features (Copilot CLI, Claude API) usage and automation

---

## 🎯 How to Use

### Adding a New Rule

1. **Identify the category** - Which file does it belong to?
2. **Add to appropriate file** - Use clear headings and examples
3. **Update this README** - If adding a new category, add it here
4. **Reference in code** - When implementing, reference the rule file

### Example: Adding a Rule

```markdown
# In Rules/07_SECURITY.md

## New Security Rule

**Rule:** Never log sensitive data in production

**Why:** Prevents credential exposure in logs

**Implementation:**
- Use environment-aware logging
- Sanitize all user inputs before logging
- Use structured logging with redaction
```

### Modifying Existing Rules

1. **Find the rule** - Use this index to locate the file
2. **Update the rule** - Make changes with clear explanations
3. **Update version** - Note the change date in the file header
4. **Document impact** - If breaking, note migration path

---

## 📚 Rule Categories Explained

### Development Rules (01-03)
Core coding practices that apply to all projects. These are the foundation of code quality.

### Infrastructure Rules (04-06)
Operational rules for deployment, environments, and configuration. Critical for production stability.

### Security Rules (07, 36)
Security-first practices. These are non-negotiable and must be followed.
- **07_SECURITY.md** - General security rules and best practices
- **36_RBAC_AUTHORIZATION.md** - RBAC system and authorization rules

### Organization Rules (08-09)
How we structure code, documentation, and workspace. Ensures maintainability.

### Project Rules (10-12)
Specific rules for workspace structure, frontend, and backend. Entity-specific standards (Argo Capital and Alpine Analytics LLC are separate).

### Trading & Operations Rules (13-16)
Trading-specific rules for signal generation, risk management, monitoring, backtesting, and dev/prod differences. Critical for trading system operations.

### API & Infrastructure Rules (26-30)
API design, database migrations, performance optimization, error handling, and code review processes. Essential for building reliable, scalable systems.

### Operations & Lifecycle Rules (31-33)
Feature flags, data lifecycle management, and disaster recovery. Critical for operational excellence and business continuity.

### Development Tools Rules (34)
Cursor Pro profiles usage and guidelines. Optimizes AI assistance and development productivity.

---

## 🔄 Rule Priority

1. **Security Rules (07)** - Highest priority, non-negotiable
2. **Deployment Rules (04)** - Production safety gates
3. **Code Quality Rules (02)** - Maintainability and reliability
4. **Development Rules (01)** - Consistency and best practices
5. **Project-Specific Rules (10-12)** - Project-specific standards

---

## 📝 Rule Format Standard

Each rule file follows this structure:

```markdown
# [Category] Rules

**Last Updated:** [Date]
**Version:** [Version]

## Overview
Brief description of what this category covers.

## [Section Name]
### [Subsection]
**Rule:** [What the rule is]
**Why:** [Why it matters]
**Implementation:** [How to follow it]
**Example:** [Code example]
```

---

## 🚀 Quick Reference

### Most Common Rules

- **Deployment:** See [04_DEPLOYMENT.md](04_DEPLOYMENT.md) - 11 safety gates (includes 100% health confirmation)
- **Security:** See [07_SECURITY.md](07_SECURITY.md) - Never commit secrets
- **RBAC:** See [36_RBAC_AUTHORIZATION.md](36_RBAC_AUTHORIZATION.md) - Role-Based Access Control
- **Code Quality:** See [02_CODE_QUALITY.md](02_CODE_QUALITY.md) - SOLID principles
- **Testing:** See [03_TESTING.md](03_TESTING.md) - 95%+ coverage required
- **Naming:** See [01_DEVELOPMENT.md](01_DEVELOPMENT.md) - Language-specific conventions
- **API Design:** See [26_API_DESIGN.md](26_API_DESIGN.md) - API versioning, error responses
- **Database Migrations:** See [27_DATABASE_MIGRATIONS.md](27_DATABASE_MIGRATIONS.md) - Migration procedures
- **Performance:** See [28_PERFORMANCE.md](28_PERFORMANCE.md) - Optimization, caching, budgets
- **Error Handling:** See [29_ERROR_HANDLING.md](29_ERROR_HANDLING.md) - Resilience patterns
- **Code Review:** See [30_CODE_REVIEW.md](30_CODE_REVIEW.md) - PR process, review guidelines
- **Optimization:** See [19_CONTINUOUS_OPTIMIZATION.md](19_CONTINUOUS_OPTIMIZATION.md) - World-class excellence mindset
- **Trading:** See [13_TRADING_OPERATIONS.md](13_TRADING_OPERATIONS.md) - 7-layer risk management
- **Monitoring:** See [14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md) - Health checks, tracing
- **Backtesting:** See [15_BACKTESTING.md](15_BACKTESTING.md) - Strategy testing
- **Dev vs Prod:** See [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) - Automatic switching, deployment consistency
- **Code Organization:** See [20_INTELLIGENT_CODE_ORGANIZATION.md](20_INTELLIGENT_CODE_ORGANIZATION.md) - Feature-based organization
- **Dependency Tracking:** See [21_DEPENDENCY_IMPACT_ANALYSIS.md](21_DEPENDENCY_IMPACT_ANALYSIS.md) - Impact analysis
- **IP Protection:** See [22_TRADE_SECRET_IP_PROTECTION.md](22_TRADE_SECRET_IP_PROTECTION.md) - Trade secret protection
- **Conversation Logging:** See [23_CONVERSATION_LOGGING.md](23_CONVERSATION_LOGGING.md) - Local-only conversation logging
- **Vision & Goals:** See [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md) - Strategic direction and goals
- **Entity Separation:** See [10_MONOREPO.md](10_MONOREPO.md) - Complete entity separation
- **Cursor Profiles:** See [34_CURSOR_PROFILES.md](34_CURSOR_PROFILES.md) - Profile usage guidelines

---

## 📖 Related Documentation

- **System Guides:** `docs/SystemDocs/*COMPLETE_GUIDE.md`
- **Deployment Guide:** `docs/SystemDocs/ENVIRONMENT_DEPLOYMENT_COMPLETE_GUIDE.md`
- **Security Guide:** `docs/SystemDocs/SECURITY_GUIDE.md`
- **Configuration Guide:** `docs/SystemDocs/CONFIGURATION_MANAGEMENT_COMPLETE_GUIDE.md`

---

## 🔍 Finding Rules

### By Topic
- **"How do I name variables?"** → [01_DEVELOPMENT.md](01_DEVELOPMENT.md)
- **"What are the deployment gates?"** → [04_DEPLOYMENT.md](04_DEPLOYMENT.md)
- **"How do I handle secrets?"** → [07_SECURITY.md](07_SECURITY.md)
- **"How do I implement RBAC?"** → [36_RBAC_AUTHORIZATION.md](36_RBAC_AUTHORIZATION.md)
- **"What's the test coverage requirement?"** → [03_TESTING.md](03_TESTING.md)
- **"How do I structure files?"** → [09_WORKSPACE.md](09_WORKSPACE.md)
- **"How do I design APIs?"** → [26_API_DESIGN.md](26_API_DESIGN.md)
- **"How do I create database migrations?"** → [27_DATABASE_MIGRATIONS.md](27_DATABASE_MIGRATIONS.md)
- **"How do I optimize performance?"** → [28_PERFORMANCE.md](28_PERFORMANCE.md)
- **"How do I handle errors?"** → [29_ERROR_HANDLING.md](29_ERROR_HANDLING.md)
- **"What's the code review process?"** → [30_CODE_REVIEW.md](30_CODE_REVIEW.md)
- **"How do I use feature flags?"** → [31_FEATURE_FLAGS.md](31_FEATURE_FLAGS.md)
- **"What are data retention policies?"** → [32_DATA_LIFECYCLE.md](32_DATA_LIFECYCLE.md)
- **"What's the disaster recovery plan?"** → [33_DISASTER_RECOVERY.md](33_DISASTER_RECOVERY.md)
- **"Which Cursor profile should I use?"** → [34_CURSOR_PROFILES.md](34_CURSOR_PROFILES.md)
- **"How do I use agentic features?"** → [35_AGENTIC_FEATURES.md](35_AGENTIC_FEATURES.md)

### By Project
- **Frontend (Alpine Analytics LLC):** → [11_FRONTEND.md](11_FRONTEND.md)
- **Backend (Argo Capital):** → [12A_ARGO_BACKEND.md](12A_ARGO_BACKEND.md)
- **Backend (Alpine Analytics LLC):** → [12B_ALPINE_BACKEND.md](12B_ALPINE_BACKEND.md)
- **Workspace Structure:** → [10_MONOREPO.md](10_MONOREPO.md) - Entity separation

### By Trading Operations
- **Trading Operations:** → [13_TRADING_OPERATIONS.md](13_TRADING_OPERATIONS.md)
- **Monitoring & Health:** → [14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md)
- **Backtesting:** → [15_BACKTESTING.md](15_BACKTESTING.md)
- **Dev vs Prod Differences:** → [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md)

---

## ✅ Rule Compliance

All code should comply with these rules. When in doubt:
1. Check the relevant rule file
2. Follow the examples provided
3. Ask for clarification if needed
4. Update rules if you find gaps

---

**Note:** These rules are living documents. They evolve as the system grows. Always check the "Last Updated" date to ensure you're following the latest standards.

