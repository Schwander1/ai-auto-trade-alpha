# Dependency & Impact Analysis Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** All code changes

---

## Overview

This rule ensures that when making changes, we understand **what affects what** - tracking dependencies and analyzing impacts before, during, and after code modifications. This is **standard practice** for all code changes.

**Core Principle:** **Know the Impact** - Before changing anything, understand what it affects and how.

**Enforcement:** Impact analysis is **mandatory** before making changes. Code changes without impact analysis will be rejected.

---

## Dependency Tracking

### What to Track

**Code Dependencies:**
- Which modules import this code?
- Which functions call this function?
- Which classes inherit from this class?
- Which features depend on this component?

**Data Dependencies:**
- Which components read this data?
- Which components write this data?
- Which processes depend on this data structure?

**Configuration Dependencies:**
- Which components use this configuration?
- What happens if this config changes?
- Which environments use this config?

**Integration Dependencies:**
- Which external services depend on this?
- Which APIs are affected?
- Which databases are involved?

### Dependency Discovery

**Before Making Changes:**

1. **Search for Imports:**
   ```bash
   # Find all files importing this module
   grep -r "from argo.risk_management" argo/
   grep -r "import.*RiskManager" argo/
   ```

2. **Search for Usage:**
   ```bash
   # Find all usages of this function/class
   grep -r "calculate_position_size" argo/
   grep -r "RiskManager" argo/
   ```

3. **Check SystemDocs:**
   - Review `docs/SystemDocs/COMPLETE_SYSTEM_ARCHITECTURE.md`
   - Check component relationships
   - Understand data flows

4. **Check Related Rules:**
   - Review relevant rule files
   - Understand dependencies between rules
   - Check for cross-references

---

## Impact Analysis Process

### Step 1: Identify Direct Dependencies

**Questions to Ask:**
- What directly imports/uses this code?
- What directly calls this function?
- What directly depends on this configuration?

**Tools:**
- `grep` for imports and usage
- IDE "Find Usages" functionality
- Code analysis tools

**Documentation:** List all direct dependencies.

### Step 2: Identify Indirect Dependencies

**Questions to Ask:**
- What depends on things that depend on this?
- What processes flow through this component?
- What features are built on top of this?

**Tools:**
- System architecture documentation
- Dependency graphs
- System flow diagrams

**Documentation:** List all indirect dependencies.

### Step 3: Identify Cross-Project Dependencies

**Questions to Ask:**
- Does this affect other projects (Argo/Alpine)?
- Does this affect shared packages?
- Does this affect deployment?

**Check:**
- Entity separation (Rule 10) - NO cross-entity dependencies
- Project-specific dependencies only
- Deployment impacts

**Documentation:** List all cross-project impacts (should be NONE for separate entities).

### Step 4: Identify Environment Dependencies

**Questions to Ask:**
- Does this behave differently in dev vs prod?
- Does this affect environment detection?
- Does this require environment-specific changes?

**Check:**
- Rule 16: Dev vs Prod Differences
- Environment detection logic
- Configuration differences

**Documentation:** List all environment-specific impacts.

### Step 5: Document Impact

**Create Impact Analysis:**
- List all affected components
- List all affected features
- List all affected environments
- List all affected tests
- List all affected documentation

---

## Change Impact Checklist (MANDATORY)

### Before Making Changes

- [ ] **Identify all direct dependencies**
- [ ] **Identify all indirect dependencies**
- [ ] **Identify cross-project impacts** (should be NONE for separate entities)
- [ ] **Identify environment-specific impacts**
- [ ] **Review SystemDocs for context**
- [ ] **Review related rules**
- [ ] **Document impact analysis**

### During Changes

- [ ] **Update all affected imports**
- [ ] **Update all affected function calls**
- [ ] **Update all affected configurations**
- [ ] **Update all affected tests**
- [ ] **Update all affected documentation**
- [ ] **Test all affected components**

### After Changes

- [ ] **Verify all dependencies still work**
- [ ] **Run tests for all affected components**
- [ ] **Update SystemDocs if architecture changed**
- [ ] **Update rules if standards changed**
- [ ] **Document what changed and why**

---

## Common Impact Scenarios

### Scenario 1: Changing a Function Signature

**Impact:**
- All callers must be updated
- All tests must be updated
- Documentation must be updated

**Process:**
1. Find all callers: `grep -r "function_name("`
2. Update all callers
3. Update all tests
4. Update documentation

### Scenario 2: Changing a Configuration Structure

**Impact:**
- All code reading this config
- All environments using this config
- All documentation referencing config

**Process:**
1. Find all config readers: `grep -r "config.get("`
2. Update all readers
3. Update all environment configs
4. Update documentation

### Scenario 3: Changing a Data Model

**Impact:**
- All code using this model
- Database migrations
- API responses
- Frontend components

**Process:**
1. Find all model usage
2. Create migration
3. Update all code
4. Update API docs
5. Update frontend

### Scenario 4: Changing a Shared Package

**Impact:**
- ALL projects using this package
- All must be tested
- All must be updated

**Note:** With entity separation (Rule 10), there should be NO shared packages between Argo and Alpine.

**Process:**
1. Identify all projects using package (if any)
2. Test all projects
3. Update all projects
4. Deploy all projects (if needed)

---

## Dependency Documentation

### Code Comments

**Document Dependencies in Code:**
```python
# This function is used by:
# - argo/trading/paper_trading_engine.py (position sizing)
# - argo/risk_management/risk_manager.py (validation)
# - argo/backtesting/profit_backtester.py (simulation)
def calculate_position_size(...):
    ...
```

### Module Documentation

**Document Module Dependencies:**
```python
"""
Risk Management Module

Dependencies:
- argo/core/config.py (configuration)
- argo/trading/paper_trading_engine.py (position data)

Used By:
- argo/trading/paper_trading_engine.py
- argo/signal_generation/signal_generation_service.py
- argo/backtesting/profit_backtester.py
"""
```

### SystemDocs Updates

**When Architecture Changes:**
- Update `docs/SystemDocs/COMPLETE_SYSTEM_ARCHITECTURE.md`
- Update component relationship diagrams
- Update data flow diagrams
- Document new dependencies

---

## Impact Analysis Tools

### Code Search

```bash
# Find all imports
grep -r "from argo.module" argo/

# Find all usages
grep -r "function_name" argo/

# Find all references
grep -r "CLASS_NAME" argo/
```

### Dependency Graphs

**Generate Dependency Graph:**
```bash
# Python dependency graph
pip install pydeps
pydeps argo/ --show-deps

# TypeScript dependency graph
npm install -g madge
madge --image deps.svg alpine-frontend/
```

### IDE Tools

- **VS Code:** "Find All References"
- **PyCharm:** "Find Usages"
- **IntelliJ:** "Find Usages"

---

## Best Practices

### DO
- ✅ Always analyze impact before changes
- ✅ Document dependencies in code
- ✅ Update SystemDocs when architecture changes
- ✅ Test all affected components
- ✅ Update all affected documentation
- ✅ Consider environment-specific impacts
- ✅ Verify entity separation (no cross-entity dependencies)

### DON'T
- ❌ Make changes without impact analysis
- ❌ Ignore indirect dependencies
- ❌ Skip updating documentation
- ❌ Forget to test affected components
- ❌ Create cross-entity dependencies
- ❌ Ignore environment differences

---

## Related Rules

- [20_INTELLIGENT_CODE_ORGANIZATION.md](20_INTELLIGENT_CODE_ORGANIZATION.md) - Code organization (affects dependencies)
- [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) - Environment-specific impacts
- [10_MONOREPO.md](10_MONOREPO.md) - Entity separation (no cross-entity dependencies)
- [04_DEPLOYMENT.md](04_DEPLOYMENT.md) - Deployment impacts
- [17_SYSTEM_DOCUMENTATION.md](17_SYSTEM_DOCUMENTATION.md) - SystemDocs updates

---

**Note:** Understanding dependencies and impacts is **critical** for maintaining system stability and preventing breaking changes. Always analyze impact before making changes. Impact analysis is **mandatory** - code changes without impact analysis will be rejected.

