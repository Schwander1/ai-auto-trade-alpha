# Workspace Organization Rules

**Last Updated:** January 15, 2025  
**Version:** 2.0  
**Applies To:** All projects

---

## Overview

Workspace organization, file structure, and cleanup rules to maintain a clean, organized codebase.

---

## File Structure

### Root Directory Structure

```
argo-alpine-workspace/
├── argo/                    # Argo Capital (Trading Engine)
├── alpine-backend/          # Alpine Analytics Backend
├── alpine-frontend/         # Alpine Analytics Frontend
├── packages/                # Shared code
│   └── shared/             # Shared utilities
├── docs/                    # All documentation
│   ├── InvestorDocs/       # Investor documentation
│   ├── TechnicalDocs/      # Technical documentation
│   └── SystemDocs/         # System documentation
├── scripts/                 # Utility scripts
├── infrastructure/          # Infrastructure configs
│   └── monitoring/         # Prometheus, Grafana
├── tests/                   # Integration/E2E tests
├── pdfs/                    # Generated PDFs
├── Rules/                   # Development rules (this folder)
├── .github/                 # GitHub workflows
├── .husky/                  # Git hooks
└── [root config files]      # package.json, turbo.json, etc.
```

---

## File Naming Conventions

### Scripts
- **Format:** `kebab-case.sh` or `kebab-case.py`
- **Examples:**
  - `deploy-argo-blue-green.sh` (recommended)
  - `deploy-argo.sh` (legacy, deprecated)
  - `check-env.sh`
  - `setup-local-dev.sh`

### Documentation
- **Format:** `UPPERCASE_WITH_UNDERSCORES.md` or `v1.0_01_*.md`
- **Examples:**
  - `BACKTESTING_COMPLETE_GUIDE.md`
  - `v2.0_01_executive_summary.md`

### Configuration Files
- **Format:** `.filename` or `filename.config.ext`
- **Examples:**
  - `.env.example`
  - `config.json`
  - `tsconfig.json`

### Test Files
- **Python:** `test_*.py` or `*_test.py`
- **TypeScript:** `*.test.ts`, `*.test.tsx`, `*.spec.ts`

---

## Workspace Cleanup

**See:** [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) for deployment file exclusions

### Files to Always Remove

#### Build Artifacts
- `*.pyc`, `__pycache__/`, `*.pyo`
- `node_modules/` (keep package.json, remove actual modules)
- `.next/`, `dist/`, `build/`
- `*.log`, `*.tmp`, `*.swp`, `*.bak`

#### OS-Specific Files
- `.DS_Store` (macOS)
- `Thumbs.db` (Windows)
- `.idea/`, `.vscode/` (except configs)

#### Temporary Files
- `*.backup`
- `*.old`
- `*~` (editor backup files)

#### Historical Markdown Files (Automatic Cleanup)
**Rule:** Automatically archive or remove historical markdown files that are no longer current documentation.

**What Gets Cleaned:**
1. **Root-Level Historical Files**
   - `*_SUMMARY.md` (implementation summaries, completion summaries)
   - `*_COMPLETE.md` (historical completion reports)
   - `*_STATUS.md` (historical status reports)
   - These are historical snapshots, not current documentation
   - **Action:** Archive to `archive/docs/root/` with date prefix

2. **Rules Directory Historical Files**
   - `*_SUMMARY.md` (organization summaries, review summaries)
   - `*_REPORT.md` (final organization reports, historical reports)
   - These are historical organization artifacts
   - **Action:** Archive to `archive/docs/Rules/` with date prefix

3. **Project-Level Historical Completion Files**
   - `*_COMPLETE.md` (implementation complete, setup complete)
   - `*_FINAL.md` (test coverage final, etc.)
   - Historical completion reports in project directories
   - **Action:** Archive to `archive/docs/{project}/` with date prefix

**What NEVER Gets Removed:**
- Current documentation in `docs/` directories
- `README.md` files (project documentation)
- Active rule files in `Rules/` (numbered rules like `01_*.md`)
- Documentation in proper `docs/` subdirectories
- Files referenced in current documentation

**Automatic Cleanup Process:**
1. **Scan for historical markdown files** (root, Rules/, project directories)
2. **Check if file is referenced** in current documentation
3. **Archive historical files** to appropriate archive location
4. **Remove from workspace** after archiving
5. **Update archive index** if needed

### Files to Always Keep

#### Source Code
- All `.py`, `.ts`, `.tsx`, `.js`, `.jsx` files
- All configuration files (`.json`, `.yaml`, `.toml`)
- All documentation files (`.md`)

#### Configuration
- `.env.example` (not `.env`)
- `config.json.example` (not `config.json`)
- `.gitignore`, `.gitattributes`

#### CI/CD
- `.github/` workflows
- `.husky/` git hooks
- Deployment scripts

---

## Organization Enforcement

### Automatic Organization

#### Before Adding New Files
1. **Check if similar functionality exists**
2. **Place in correct directory** per structure above
3. **Follow naming conventions**
4. **Update relevant documentation**

#### When Detecting Issues
1. **Suggest correct location** if misplaced
2. **Warn about duplicate functionality**
3. **Enforce naming conventions**
4. **Update documentation** if structure changes

---

## Cleanup Process

### Analysis Phase
1. **Scan entire workspace**
2. **Identify duplicates** (content-based)
3. **List unnecessary files**
4. **Map current structure vs. ideal structure**

### Execution Phase
1. **Remove approved unnecessary files**
2. **Move files to correct locations**
3. **Update import paths** if needed
4. **Update documentation references**

### Verification Phase
1. **Verify no broken imports**
2. **Confirm structure matches standards**
3. **Update .gitignore** if needed
4. **Document changes made**

---

## Cleanup Triggers

### When to Cleanup
- **Before major commits**
- **When user requests cleanup**
- **When detecting workspace bloat** (>100 files in root)
- **Weekly automated scan** (suggest to user)

---

## Duplicate Detection

### Content-Based Detection
- **Rule:** Use content hashing to identify true duplicates
- **Action:** Not just same name, but same content
- **Tool:** Use file hashing (MD5, SHA-256)

### Handling Duplicates
1. **Identify duplicates**
2. **Keep the canonical version**
3. **Update all references**
4. **Remove duplicates**

---

## Archive Organization

**See:** [18_VERSIONING_ARCHIVING.md](18_VERSIONING_ARCHIVING.md) for complete versioning and archiving rules.

### Backup Files
- **Location:** `archive/backup-files/`
- **Format:** Organized by date or purpose
- **Action:** Move old backup files here

### Versioned Files
- **Location:** `archive/docs/`, `archive/configs/`, `archive/scripts/`
- **Format:** Organized by type and version
- **Action:** Automatic archiving of older versions (see Rule 18)

---

## Root Directory Cleanliness

### Keep in Root
- **Essential configs only:**
  - `package.json`
  - `turbo.json`
  - `README.md`
  - `.gitignore`
  - `.cursorrules/` (or `Rules/`)

### Move to Subdirectories
- **Scripts:** → `scripts/`
- **Documentation:** → `docs/`
- **Tests:** → `tests/`
- **Configs:** → Project-specific directories

---

## Best Practices

### DO
- ✅ Follow the file structure
- ✅ Use consistent naming conventions
- ✅ Keep root directory clean
- ✅ Organize files logically
- ✅ Remove unnecessary files regularly
- ✅ Update documentation when structure changes

### DON'T
- ❌ Create files in root unnecessarily
- ❌ Use inconsistent naming
- ❌ Leave temporary files
- ❌ Commit build artifacts
- ❌ Create duplicate functionality
- ❌ Ignore organization rules

---

## Related Rules

- [01_DEVELOPMENT.md](01_DEVELOPMENT.md) - Development practices
- [08_DOCUMENTATION.md](08_DOCUMENTATION.md) - Documentation standards
- [10_MONOREPO.md](10_MONOREPO.md) - Monorepo structure

