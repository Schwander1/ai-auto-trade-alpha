# Conversation Logging Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** Conversation logging system (LOCAL DEVELOPMENT ONLY)

---

## Overview

This rule governs the automatic conversation logging system that captures user-AI conversations for context retention and decision tracking. **This system is LOCAL DEVELOPMENT ONLY and never runs in production.**

**Note:** This rule is separate from:
- **[14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md)** - System monitoring and observability
- **[08_DOCUMENTATION.md](08_DOCUMENTATION.md)** - Documentation standards
- **[05_ENVIRONMENT.md](05_ENVIRONMENT.md)** - Environment detection

This rule specifically focuses on **conversation logging for AI context retention**.

---

## Core Principle: Local-Only, Fully Automated

### Environment Restriction
- **Development Only:** System only runs in development environment
- **Production Disabled:** Automatically exits in production (never runs on prod servers)
- **Environment Detection:** Uses `argo/argo/core/environment.py` → `detect_environment()`

### Automation
- **Fully Automated:** Zero manual steps after initial setup
- **Background Service:** Runs continuously in development
- **Auto-Cleanup:** Automatic deletion of old logs
- **Auto-Discovery:** Automatically finds Cursor conversation storage

---

## What Gets Logged

### Full Conversations
- **Location:** `conversation_logs/sessions/YYYY-MM-DD/session_HHMMSS.md`
- **Retention:** 3 days
- **Content:** Complete conversation text with metadata
- **Purpose:** Full context for AI assistant reference

### Decision Summaries
- **Location:** `conversation_logs/decisions/YYYY-MM-DD/decision_HHMMSS.md`
- **Retention:** 30 days
- **Content:** Extracted key decisions and important changes
- **Purpose:** Quick reference for important decisions

### Searchable Index
- **Location:** `conversation_logs/index.json`
- **Retention:** While logs exist
- **Content:** Metadata and file references
- **Purpose:** Quick search and lookup

---

## Environment Detection

### Automatic Detection

**Component:** `scripts/conversation_logger_service.py` → `should_run()`

**Process:**
1. Import `argo.core.environment.detect_environment()`
2. Check if environment == 'production'
3. If production: Exit gracefully (no error)
4. If development: Continue running

**Rule:** Service must check environment before starting
- Never runs in production
- Logs environment detection result
- Exits gracefully if production detected

---

## Deployment Exclusions

### Files That MUST NOT Be Deployed

**Conversation Logs Directory:**
- `conversation_logs/` - Entire directory (LOCAL ONLY)

**Conversation Logging Scripts:**
- `scripts/conversation_logger_service.py` - Background service (LOCAL ONLY)
- `scripts/cleanup_conversation_logs.py` - Cleanup script (LOCAL ONLY)
- `scripts/setup_conversation_logging.sh` - Setup script (LOCAL ONLY)

**Rule:** All conversation logging files are LOCAL ONLY
- Excluded from `.deployignore`
- Listed in `scripts/deployment-manifest.json` → `local_only.patterns`
- Never deployed to production servers

---

## Privacy & Security

### Git Exclusion

**Rule:** Conversation logs must be excluded from version control

**Implementation:**
- `conversation_logs/.gitignore` - Excludes all log files
- `.gitignore` (root) - Excludes `conversation_logs/` directory
- Only `conversation_logs/.gitignore` and `conversation_logs/README.md` are committed

### Data Protection

**Rule:** Conversation logs contain sensitive information and must be protected

**Requirements:**
- Never committed to version control
- Never deployed to production
- Auto-cleanup after retention period
- Local storage only

---

## Retention Policy

### Conversation Sessions
- **Retention:** 3 days
- **Cleanup:** Daily at 2 AM (cron job)
- **Script:** `scripts/cleanup_conversation_logs.py`
- **Location:** `conversation_logs/sessions/`

### Decision Summaries
- **Retention:** 30 days
- **Cleanup:** Daily at 2 AM (cron job)
- **Script:** `scripts/cleanup_conversation_logs.py`
- **Location:** `conversation_logs/decisions/`

**Rule:** Retention policy is automatic and enforced
- No manual cleanup required
- Old logs automatically deleted
- Index automatically updated

---

## Service Management

### Background Service

**Component:** `scripts/conversation_logger_service.py`

**Behavior:**
- Runs continuously in development
- **Cursor-Aware:** Only monitors when Cursor is running
- Monitors Cursor conversation storage when active
- Logs new conversations automatically
- Updates searchable index
- **Auto-Resume:** Automatically resumes when Cursor starts

**Lifecycle:**
- **Startup:** Checks environment → exits if production
- **Cursor Check:** Verifies Cursor is running before monitoring
- **Waiting:** If Cursor not running, waits and checks periodically (every 30 seconds)
- **Running:** Monitors and logs conversations (only when Cursor is active)
- **Paused:** When Cursor stops, pauses monitoring and waits for resume
- **Resume:** Automatically resumes when Cursor starts again
- **Shutdown:** Graceful exit on SIGTERM/SIGINT

**Cursor Detection:**
- Checks if Cursor process is running before monitoring
- Uses `pgrep` to detect Cursor process on macOS
- Falls back to `ps aux` if `pgrep` unavailable
- Waits up to 5 minutes for Cursor to start on service startup
- Checks every 30 seconds when Cursor is not running

**Rule:** Service must be environment-aware and Cursor-aware
- Only runs in development
- Only monitors when Cursor is running
- Exits gracefully in production
- Handles errors without crashing
- Automatically resumes when Cursor starts
- Handles laptop sleep/wake gracefully

### Cleanup Service

**Component:** `scripts/cleanup_conversation_logs.py`

**Behavior:**
- Runs daily via cron (2 AM)
- Removes old conversations (3 days)
- Removes old decisions (30 days)
- Updates searchable index
- **Independent:** Runs regardless of Cursor status (cleans up existing logs)

**Rule:** Cleanup must be environment-aware
- Only runs in development
- Exits gracefully in production
- Logs cleanup actions
- Does not require Cursor to be running

---

## Setup & Installation

### One-Time Setup

**Script:** `scripts/setup_conversation_logging.sh`

**Process:**
1. Verify development environment
2. Create directory structure
3. Make scripts executable
4. Test scripts
5. Setup background service (macOS launchd)
6. Setup cron job for cleanup
7. Verify setup

**Rule:** Setup must verify environment
- Only runs in development
- Exits if production detected
- Provides clear error messages

---

## File Structure

### Directory Structure

```
conversation_logs/
├── sessions/              # Full conversations (3-day retention)
│   └── YYYY-MM-DD/
│       └── session_HHMMSS.md
├── decisions/             # Decision summaries (30-day retention)
│   └── YYYY-MM-DD/
│       └── decision_HHMMSS.md
├── index.json             # Searchable index (auto-generated)
├── .gitignore             # Privacy protection
└── README.md              # Usage documentation
```

**Rule:** Directory structure must be maintained
- Date-based organization
- Automatic directory creation
- Clean structure for easy navigation

---

## Integration with Existing Systems

### Environment Detection

**Integration:** Uses `argo/argo/core/environment.py`

**Rule:** Must use existing environment detection
- No duplicate detection logic
- Consistent with other systems
- Respects environment configuration

### Deployment Exclusions

**Integration:** Uses `.deployignore` and `scripts/deployment-manifest.json`

**Rule:** Must be properly excluded from deployment
- Listed in `.deployignore`
- Listed in `deployment-manifest.json` → `local_only.patterns`
- Verified by deployment scripts

### Git Exclusions

**Integration:** Uses `.gitignore` and `conversation_logs/.gitignore`

**Rule:** Must be properly excluded from git
- Root `.gitignore` excludes `conversation_logs/`
- `conversation_logs/.gitignore` excludes all log files
- Only documentation files committed

---

## Best Practices

### DO
- ✅ Always check environment before running
- ✅ Check if Cursor is running before monitoring
- ✅ Wait for Cursor to start if not running
- ✅ Auto-resume when Cursor starts
- ✅ Exit gracefully in production (no errors)
- ✅ Log environment detection results
- ✅ Use existing environment detection system
- ✅ Follow retention policy strictly
- ✅ Update searchable index automatically
- ✅ Handle errors gracefully
- ✅ Provide clear logging messages
- ✅ Handle laptop sleep/wake gracefully

### DON'T
- ❌ Run in production environment
- ❌ Monitor when Cursor is not running (waste resources)
- ❌ Commit conversation logs to git
- ❌ Deploy conversation logging to production
- ❌ Skip environment detection
- ❌ Skip Cursor detection
- ❌ Hardcode environment checks
- ❌ Store logs longer than retention period
- ❌ Ignore cleanup failures
- ❌ Create duplicate environment detection logic
- ❌ Assume Cursor is always running

---

## Troubleshooting

### Service Not Running

**Check:**
1. Verify environment: `python3 -c "from argo.core.environment import detect_environment; print(detect_environment())"`
2. Check service status: `launchctl list | grep conversation-logger`
3. Check logs: `tail -f conversation_logs/service.log`
4. Check if Cursor is running: `pgrep -f Cursor`

**Fix:**
- Ensure development environment
- Ensure Cursor is running (service waits for Cursor)
- Restart service: `launchctl load ~/Library/LaunchAgents/com.argo.conversation-logger.plist`

### Service Waiting for Cursor

**Symptom:** Service logs show "Cursor is not running - pausing monitoring"

**This is Normal:**
- Service automatically pauses when Cursor is not running
- Service will automatically resume when Cursor starts
- No action needed - service is working correctly

**To Verify:**
- Check logs: `tail -f conversation_logs/service.log`
- Look for "Cursor detected - resuming monitoring" message

### Cleanup Not Running

**Check:**
1. Verify cron job: `crontab -l | grep conversation-logs`
2. Check cleanup logs: `tail -f conversation_logs/cleanup.log`
3. Run manually: `python3 scripts/cleanup_conversation_logs.py`

**Fix:**
- Re-run setup script
- Verify cron job installation
- Check environment detection

### Environment Detection Issues

**Check:**
1. Verify environment detection: `python3 -c "from argo.core.environment import detect_environment, get_environment_info; import json; print(json.dumps(get_environment_info(), indent=2))"`
2. Check `ARGO_ENVIRONMENT` variable
3. Verify `argo/argo/core/environment.py` exists

**Fix:**
- Ensure environment detection module is available
- Check environment variable settings
- Verify file paths

---

## Related Rules

- **[05_ENVIRONMENT.md](05_ENVIRONMENT.md)** - Environment detection details
- **[04_DEPLOYMENT.md](04_DEPLOYMENT.md)** - Deployment exclusions
- **[07_SECURITY.md](07_SECURITY.md)** - Privacy and security practices
- **[14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md)** - System monitoring
- **[18_VERSIONING_ARCHIVING.md](18_VERSIONING_ARCHIVING.md)** - File versioning (conversation logs excluded)

---

## Compliance Checklist

When implementing or modifying conversation logging:

- [ ] Environment detection integrated
- [ ] Production exit implemented
- [ ] Deployment exclusions added
- [ ] Git exclusions added
- [ ] Retention policy enforced
- [ ] Cleanup service configured
- [ ] Background service configured
- [ ] Error handling implemented
- [ ] Logging messages clear
- [ ] Documentation updated

---

**Note:** This system is designed for local development context retention only. It never runs in production and all logs are excluded from version control and deployment.

