# Versioning & Archiving Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** File versioning and archive management

---

## Overview

This rule governs the versioning of important files and the automatic archiving of older versions to maintain a clean workspace while preserving complete tracking history. **Older versions are automatically moved to archive folders** to prevent workspace clutter.

**Note:** This rule is separate from:
- **[09_WORKSPACE.md](09_WORKSPACE.md)** - General workspace organization and cleanup
- **[08_DOCUMENTATION.md](08_DOCUMENTATION.md)** - Documentation standards (includes versioning format for docs)
- **[17_SYSTEM_DOCUMENTATION.md](17_SYSTEM_DOCUMENTATION.md)** - SystemDocs management

This rule specifically focuses on **automatic versioning and archiving** of files.

---

## Core Principle: Clean Workspace, Complete History

### Workspace Visibility
- **Current versions only** in main workspace directories
- **No version clutter** when expanding folders
- **Clean, organized** file structure

### Complete Tracking
- **All versions preserved** in archive
- **Full history maintained** for reference
- **Easy retrieval** when needed

---

## What Gets Versioned

### Files That Should Be Versioned

#### 1. Documentation Files
- **Investor Docs:** `docs/InvestorDocs/v*.md`
- **System Docs:** Major guides in `docs/SystemDocs/`
- **Technical Docs:** `docs/TechnicalDocs/v*.md`
- **Rule Files:** `Rules/*.md` (when major changes)

#### 2. Configuration Files
- **Main Config:** `argo/config.json` (when structure changes)
- **Environment Configs:** `.env.example` files (when schema changes)
- **Deployment Configs:** Major deployment configuration changes

#### 3. Important Scripts
- **Deployment Scripts:** `scripts/deploy-*.sh` (when logic changes)
- **Setup Scripts:** `scripts/setup-*.sh` (when process changes)
- **Migration Scripts:** Database or system migration scripts

#### 4. Architecture Documents
- **System Architecture:** `docs/SystemDocs/COMPLETE_SYSTEM_ARCHITECTURE.md`
- **Status Reports:** Major status reports

### Files That Should NOT Be Versioned

- **Source Code:** Use Git for versioning
- **Test Files:** Use Git for versioning
- **Build Artifacts:** Never versioned
- **Temporary Files:** Never versioned
- **Log Files:** Never versioned
- **Database Files:** Never versioned
- **Conversation Logs:** Never versioned (excluded from git, see [23_CONVERSATION_LOGGING.md](23_CONVERSATION_LOGGING.md))

---

## Versioning Format

### Version Numbering

#### Format: `v{major}.{minor}_{number}_{name}.{ext}`

**Components:**
- **Major:** Breaking changes or major rewrites
- **Minor:** Significant additions or improvements
- **Number:** Sequential number for same major.minor
- **Name:** Descriptive name (optional for some files)

#### Examples

**Documentation:**
- `v1.0_01_executive_summary.md`
- `v2.0_01_executive_summary.md`
- `v2.1_01_executive_summary.md`

**Configuration:**
- `config.v1.0.json`
- `config.v2.0.json`

**Scripts:**
- `deploy-argo.v1.0.sh`
- `deploy-argo.v2.0.sh`

**System Docs:**
- `COMPLETE_SYSTEM_ARCHITECTURE.v1.0.md`
- `COMPLETE_SYSTEM_ARCHITECTURE.v2.0.md`

### Current Version Naming

**Rule:** Current version uses **base name only** (no version suffix)

**Examples:**
- Current: `executive_summary.md`
- Archived: `v1.0_01_executive_summary.md`, `v2.0_01_executive_summary.md`

- Current: `config.json`
- Archived: `config.v1.0.json`, `config.v2.0.json`

---

## Archive Structure

### Archive Directory Layout

```
archive/
├── docs/
│   ├── InvestorDocs/
│   │   ├── v1.0/
│   │   │   ├── v1.0_01_executive_summary.md
│   │   │   ├── v1.0_02_business_model.md
│   │   │   └── ...
│   │   └── v2.0/
│   │       ├── v2.0_01_executive_summary.md
│   │       └── ...
│   ├── SystemDocs/
│   │   ├── COMPLETE_SYSTEM_ARCHITECTURE.v1.0.md
│   │   ├── COMPLETE_SYSTEM_ARCHITECTURE.v2.0.md
│   │   └── ...
│   └── TechnicalDocs/
│       └── ...
├── configs/
│   ├── config.v1.0.json
│   ├── config.v2.0.json
│   └── ...
├── scripts/
│   ├── deploy-argo.v1.0.sh
│   ├── deploy-argo.v2.0.sh
│   └── ...
└── backup-files/
    └── (existing backup files)
```

### Archive Organization Rules

#### By Type
- **docs/:** All documentation versions
- **configs/:** Configuration file versions
- **scripts/:** Script versions
- **backup-files/:** Existing backup files (legacy)

#### By Version
- **Grouped by major.minor:** `v1.0/`, `v2.0/`, etc.
- **Flat structure:** For files with simple versioning

---

## Automatic Archiving Process

### When Versioning Occurs

#### 1. Documentation Updates
- **Trigger:** When major documentation is updated
- **Action:** Archive previous version before update
- **Example:** Updating `executive_summary.md` → Archive current as `v2.0_01_executive_summary.md`

#### 2. Configuration Changes
- **Trigger:** When configuration structure changes significantly
- **Action:** Archive previous version before update
- **Example:** Updating `config.json` → Archive current as `config.v2.0.json`

#### 3. Script Changes
- **Trigger:** When deployment or setup scripts change significantly
- **Action:** Archive previous version before update
- **Example:** Updating `deploy-argo.sh` → Archive current as `deploy-argo.v2.0.sh`

#### 4. System Documentation Updates
- **Trigger:** When SystemDocs are updated (per Rule 17)
- **Action:** Archive previous version before update
- **Example:** Updating `COMPLETE_SYSTEM_ARCHITECTURE.md` → Archive as `COMPLETE_SYSTEM_ARCHITECTURE.v2.0.md`

### Archiving Steps

#### Step 1: Identify Current Version
1. Check if file exists in workspace
2. Determine current version number (if versioned)
3. If no version, treat as v1.0

#### Step 2: Create Archive Copy
1. Create archive directory structure if needed
2. Copy current file to archive with version number
3. Use appropriate archive location:
   - Docs → `archive/docs/{type}/v{major}.{minor}/`
   - Configs → `archive/configs/`
   - Scripts → `archive/scripts/`

#### Step 3: Update Current File
1. Update file in workspace (remove version suffix)
2. Keep base name only
3. Update version metadata in file header if present

#### Step 4: Update Archive Index (Optional)
1. Create/update `archive/INDEX.md` if needed
2. Document what was archived and when
3. Link to archived versions

---

## Version Tracking

### Version Metadata

#### In File Headers
For versioned files, include version metadata:

```markdown
**Last Updated:** January 15, 2025  
**Version:** 2.0  
**Status:** Current
```

#### Archive Index
Maintain `archive/INDEX.md` (optional) with:
- List of archived files
- Version numbers
- Archive dates
- Brief change descriptions

### Version History

#### Tracking Method
- **Git:** Primary version control (for code)
- **Archive:** Secondary version control (for docs/configs)
- **Metadata:** Version info in file headers

#### Retrieval
- **Find version:** Check `archive/` directory
- **Restore version:** Copy from archive to workspace
- **Compare versions:** Use diff tools

---

## Workspace Cleanliness

### Current Files Only

**Rule:** Main workspace directories contain **current versions only**

**Examples:**
```
docs/InvestorDocs/
├── v2.0_01_executive_summary.md  ✅ Current
├── v2.0_02_business_model.md     ✅ Current
└── (no old versions)              ✅ Clean

archive/docs/InvestorDocs/
├── v1.0/
│   ├── v1.0_01_executive_summary.md  ✅ Archived
│   └── v1.0_02_business_model.md     ✅ Archived
└── v2.0/
    └── (when v3.0 is created)
```

### Automatic Cleanup

#### When Creating New Version
1. **Archive old version** before creating new
2. **Remove version suffix** from current file
3. **Keep workspace clean** automatically

#### Automatic Workspace Cleanup

**Rule:** Automatically clean workspace of unnecessary files when requested.

**What Gets Cleaned:**
1. **Old Backup Directories**
   - Remove old `backups/backup_*` directories (keep `BACKUP_README.md`)
   - Archive old backups older than 30 days (optional, with approval)

2. **Historical Markdown Files (AUTOMATIC)**
   - **Root-level historical files:**
     - `*_SUMMARY.md` (implementation summaries, completion summaries)
     - `*_COMPLETE.md` (historical completion reports)
     - `*_STATUS.md` (historical status reports)
     - **Action:** Archive to `archive/docs/root/` with date prefix, then remove
   
   - **Rules directory historical files:**
     - `*_SUMMARY.md` (organization summaries, review summaries)
     - `*_REPORT.md` (final organization reports, historical reports)
     - **Action:** Archive to `archive/docs/Rules/` with date prefix, then remove
   
   - **Project-level historical completion files:**
     - `*_COMPLETE.md` (implementation complete, setup complete)
     - `*_FINAL.md` (test coverage final, etc.)
     - **Action:** Archive to `archive/docs/{project}/` with date prefix, then remove
   
   - These are historical snapshots, not current documentation
   - **Automatic:** Cleanup happens automatically when detected

3. **Log Files**
   - Remove `.log` files from `logs/` and project `logs/` directories
   - Logs regenerate automatically as needed
   - Keep log directories (they'll be recreated)

4. **Old Integration/Work Files**
   - Remove old integration scripts (e.g., `*_integration_clean.py`)
   - Remove old work files (e.g., `*_routes_to_add.txt`)
   - Remove old test files that are no longer used
   - **Check for references first** before removing

5. **Temporary Files**
   - Remove `*.tmp`, `*.bak`, `*.old` files
   - Remove OS-specific files (`.DS_Store`, `Thumbs.db`)
   - Remove editor backup files (`*~`)

**What NEVER Gets Removed:**
- Source code files (`.py`, `.ts`, `.tsx`, `.js`, `.jsx`)
- Configuration files (`.json`, `.yaml`, `.toml`, `.env.example`)
- Current documentation (`.md` files in `docs/`)
- Scripts in `scripts/` directory
- Test files in proper test directories
- Git-related files
- CI/CD configs

#### Cleanup Process

**When User Requests Cleanup:**
1. **Analyze workspace** for unnecessary files
2. **Check for references** before removing code files
3. **Remove unnecessary files** automatically
4. **Verify no breaking changes** after cleanup
5. **Report what was removed**

**Safety Checks:**
- Never remove files that are imported/referenced
- Never remove active configuration files
- Never remove current documentation
- Always verify before removing code files

#### Periodic Cleanup

**Automatic Detection:**
- **Check for orphaned versions:** Files with version suffixes in workspace
- **Move to archive:** If found, move to appropriate archive location
- **Update references:** If needed

**Suggested Cleanup Triggers:**
- Before major commits
- When workspace becomes cluttered (>100 files in root)
- When user requests cleanup
- Weekly automated scan (suggest to user)

---

## Version Numbering Guidelines

### When to Increment Major Version

- **Breaking changes:** Incompatible with previous version
- **Major rewrites:** Complete restructure
- **Significant feature additions:** Major new functionality
- **Format changes:** File format or structure changes

### When to Increment Minor Version

- **Significant additions:** New sections or features
- **Important updates:** Substantial content changes
- **Improvements:** Major improvements to existing content

### When to Increment Number

- **Minor updates:** Small changes, corrections
- **Bug fixes:** Fixing errors
- **Clarifications:** Improving clarity

---

## Archive Management

### Archive Maintenance

#### Regular Review
- **Check archive size:** Ensure not growing too large
- **Verify organization:** Ensure files in correct locations
- **Update index:** Keep archive index current

#### Archive Cleanup (Rare)
- **Very old versions:** Consider compressing or removing very old versions (after 1+ year)
- **User approval required:** Never delete archives without explicit approval
- **Backup first:** Always backup before cleanup

### Archive Access

#### Finding Archived Versions
1. **Check archive directory:** `archive/docs/`, `archive/configs/`, etc.
2. **Search by version:** Look for version number
3. **Check index:** If `archive/INDEX.md` exists

#### Restoring Archived Versions
1. **Copy from archive:** Copy archived file to workspace
2. **Rename if needed:** Remove version suffix if making current
3. **Update references:** Update any references to the file

---

## Implementation Rules

### Automatic Archiving

**Rule:** When updating a versioned file, **automatically archive** the previous version.

**Process:**
1. Before updating, check if file exists
2. If exists, copy to archive with version number
3. Update file in workspace
4. Remove version suffix from current file

### Manual Archiving

**Rule:** When user requests versioning, follow the same process.

**Process:**
1. User requests: "version this file" or "create new version"
2. Archive current version
3. Create new version or update current

### Version Detection

**Rule:** Detect versioned files by:
- Version suffix in filename: `v1.0_`, `v2.0_`, etc.
- Version metadata in file header
- Archive location

---

## Best Practices

### DO
- ✅ Archive before major updates
- ✅ Use consistent version numbering
- ✅ Keep workspace clean (current versions only)
- ✅ Maintain complete history in archive
- ✅ Update version metadata in files
- ✅ Organize archives by type and version

### DON'T
- ❌ Leave old versions in workspace
- ❌ Use inconsistent version formats
- ❌ Delete archives without approval
- ❌ Version source code files (use Git)
- ❌ Version temporary or build files
- ❌ Create version clutter in workspace

---

## Related Rules

- **[09_WORKSPACE.md](09_WORKSPACE.md)** - General workspace organization (archive location mentioned)
- **[08_DOCUMENTATION.md](08_DOCUMENTATION.md)** - Documentation standards (versioning format for docs)
- **[17_SYSTEM_DOCUMENTATION.md](17_SYSTEM_DOCUMENTATION.md)** - SystemDocs management (may trigger versioning)

---

## Quick Reference

### Archive Locations
- **Documentation:** `archive/docs/{type}/v{major}.{minor}/`
- **Configurations:** `archive/configs/`
- **Scripts:** `archive/scripts/`
- **Backup Files:** `archive/backup-files/`

### Version Format
- **Documentation:** `v{major}.{minor}_{number}_{name}.md`
- **Configs/Scripts:** `{name}.v{major}.{minor}.{ext}`

### Current Version
- **No version suffix:** Base name only
- **Example:** `executive_summary.md` (not `v2.0_01_executive_summary.md`)

### Archiving Process
1. Identify current version
2. Copy to archive with version number
3. Update file in workspace
4. Remove version suffix

---

**Remember:** Keep workspace clean with current versions only. All history preserved in archive for complete tracking.

