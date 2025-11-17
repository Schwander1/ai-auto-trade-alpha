# Monorepo Structure Rules

**Last Updated:** January 15, 2025  
**Version:** 3.0  
**Applies To:** Workspace structure only

---

## Overview

This workspace contains **TWO COMPLETELY SEPARATE AND INDEPENDENT ENTITIES** that share NO code, NO dependencies, and NO relationships. They exist in the same workspace for development convenience only.

**CRITICAL:** Argo Capital and Alpine Analytics LLC are **separate legal entities** with **no business relationship**. Code, documentation, and references must NEVER cross between them.

---

## Entity Separation (MANDATORY)

### Argo Capital
- **Entity:** Argo Capital (Independent Trading Company)
- **Path:** `argo/`
- **Type:** Trading Engine (Python/FastAPI)
- **Purpose:** Proprietary trading system
- **Deployment:** Independent
- **Code:** Completely separate, no shared code
- **Dependencies:** NO dependencies on Alpine Analytics
- **Documentation:** Independent documentation only

### Alpine Analytics LLC
- **Entity:** Alpine Analytics LLC (Independent Analytics Company)
- **Backend Path:** `alpine-backend/`
- **Frontend Path:** `alpine-frontend/`
- **Type:** Analytics Platform (Python/FastAPI + Next.js)
- **Purpose:** Signal distribution platform
- **Deployment:** Independent (backend + frontend coupled)
- **Code:** Completely separate, no shared code
- **Dependencies:** NO dependencies on Argo Capital
- **Documentation:** Independent documentation only

---

## Separation Rules (MANDATORY - NO EXCEPTIONS)

### Code Separation
- **Rule:** NO shared code between Argo and Alpine
- **Rule:** NO imports between Argo and Alpine
- **Rule:** NO cross-references in code
- **Rule:** NO shared utilities
- **Rule:** NO shared packages
- **Rule:** NO shared libraries

### Documentation Separation
- **Rule:** NO references to Argo in Alpine documentation
- **Rule:** NO references to Alpine in Argo documentation
- **Rule:** NO combined system documentation
- **Rule:** Each entity documented independently
- **Rule:** NO "Argo-Alpine" combined references

### Deployment Separation
- **Rule:** Deploy Argo independently
- **Rule:** Deploy Alpine independently
- **Rule:** NO combined deployment
- **Rule:** NO shared infrastructure (except workspace)
- **Rule:** NO shared deployment scripts

### Configuration Separation
- **Rule:** NO shared configuration files
- **Rule:** NO shared environment variables
- **Rule:** NO shared secrets
- **Rule:** Each entity manages its own configuration

---

## Project Detection

When files are modified, automatically detect entity context:

- Files in `argo/**` → Argo Capital (independent entity)
- Files in `alpine-backend/**` → Alpine Analytics LLC (backend)
- Files in `alpine-frontend/**` → Alpine Analytics LLC (frontend)

**Rule:** NEVER treat Argo and Alpine as related projects.

**Rule:** NEVER create shared code between entities.

---

## Alpine Analytics Coupling

### Alpine Backend + Frontend
- **Rule:** Alpine backend and frontend are coupled (same entity)
- **Rule:** Deploy both together as "alpine-analytics"
- **Rule:** Test both when either changes
- **Reason:** Same entity, tightly integrated
- **Note:** This is the ONLY coupling allowed in the workspace

---

## Workspace Organization

```
workspace/
├── argo/                    # Argo Capital (INDEPENDENT ENTITY)
│   └── [Argo code - NO Alpine references]
├── alpine-backend/          # Alpine Analytics LLC (INDEPENDENT ENTITY)
│   └── [Alpine code - NO Argo references]
├── alpine-frontend/         # Alpine Analytics LLC (INDEPENDENT ENTITY)
│   └── [Alpine code - NO Argo references]
└── [Workspace-level files only - NO shared code]
```

**Rule:** NO shared code directories between entities.

**Rule:** NO `packages/shared/` directory (if it exists, it must be removed or split).

---

## Code Review Requirements

### Before Committing Code

**Check for Cross-Entity References:**
- [ ] NO imports from other entity
- [ ] NO references to other entity in comments
- [ ] NO shared utilities
- [ ] NO combined documentation

### Automated Checks

**Rule:** Code review MUST verify:
- No cross-entity imports
- No cross-entity references
- No shared code
- Independent documentation

---

## Best Practices

### DO
- ✅ Keep entities completely separate
- ✅ Deploy entities independently
- ✅ Document entities separately
- ✅ Test entities independently
- ✅ Maintain independent codebases
- ✅ Use entity-specific naming

### DON'T
- ❌ Create shared code between entities
- ❌ Reference one entity in the other's code
- ❌ Create combined documentation
- ❌ Deploy entities together
- ❌ Create cross-entity dependencies
- ❌ Use "Argo-Alpine" combined naming
- ❌ Share utilities or libraries
- ❌ Create shared packages

---

## Violation Detection

### If Cross-Entity Reference Detected

**Immediate Actions:**
1. **STOP** - Do not commit
2. **IDENTIFY** - Find all cross-references
3. **REMOVE** - Remove all cross-references
4. **VERIFY** - Verify complete separation
5. **DOCUMENT** - Document why separation is required

---

## Related Rules

- [04_DEPLOYMENT.md](04_DEPLOYMENT.md) - Independent deployment procedures
- [09_WORKSPACE.md](09_WORKSPACE.md) - Workspace organization
- [22_TRADE_SECRET_IP_PROTECTION.md](22_TRADE_SECRET_IP_PROTECTION.md) - IP protection (entity separation protects IP)

---

**Note:** Entity separation is **CRITICAL** for legal, IP, and business reasons. These are separate companies with separate IP portfolios. Any violation of separation rules must be immediately corrected.
