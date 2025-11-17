# Cursor Pro Profiles Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** All development work

---

## Overview

Rules and guidelines for using Cursor Pro profiles to optimize AI assistance, maintain entity separation, and improve development productivity.

**Strategic Context:** Profile usage aligns with development efficiency goals defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md).

**See Also:** [docs/CURSOR_PROFILES_STRATEGY.md](../docs/CURSOR_PROFILES_STRATEGY.md) for complete strategy, [.cursor/PROFILE_DETECTION.md](../.cursor/PROFILE_DETECTION.md) for detection guide.

---

## Profile Usage Rules

### When to Use Profiles

**Rule:** Always use appropriate profile for your work

**Profile Selection:**
- **Argo Trading Profile:** When working on `argo/` directory
- **Alpine Full-Stack Profile:** When working on `alpine-backend/` or `alpine-frontend/`
- **Security-Sensitive Profile:** When working on trade secrets or IP-protected code
- **Monorepo Refactoring Profile:** When refactoring across services
- **Dev Workflow Profile:** For fast iteration and bug fixes

### Profile Switching

**Rule:** Switch profiles when changing context

**Switch When:**
- Moving from Argo to Alpine work (or vice versa)
- Starting work on trade secret code
- Beginning cross-service refactoring
- Changing from feature work to bug fixes

**How to Switch:**
- **Keyboard:** `Cmd+Shift+P` → "Profile: Switch"
- **Status Bar:** Click profile name (bottom-right)
- **Command Palette:** Type "Profile: Switch"

---

## Entity Separation

### Profile-Based Separation

**Rule:** Profiles enforce entity separation

**Argo Trading Profile:**
- Excludes `alpine-backend/**` and `alpine-frontend/**`
- Focuses on trading system only
- Prevents accidental cross-entity references

**Alpine Full-Stack Profile:**
- Excludes `argo/**`
- Focuses on web application only
- Prevents accidental cross-entity references

**Enforcement:**
- AI assistant automatically applies entity separation
- File exclusions prevent context pollution
- Rules prevent cross-entity imports

---

## Security & IP Protection

### Security-Sensitive Profile

**Rule:** Always use Security-Sensitive Profile for trade secret work

**When to Use:**
- Working on proprietary algorithms
- Modifying trade secret code
- Updating patent-pending technology
- Refactoring IP-protected features

**Files Requiring Security-Sensitive Profile:**
- `argo/argo/core/signal_generation_service.py`
- `argo/argo/core/signal_tracker.py`
- `argo/argo/core/weighted_consensus_engine.py`
- `argo/argo/core/regime_detector.py`
- Any file with "TRADE SECRET" or "PATENT-PENDING" markers

**Benefits:**
- IP protection rules prioritized
- Reduced context exposure
- Security-first mindset
- Proper trade secret marking enforced

---

## AI Assistant Integration

### Auto-Detection

**Rule:** AI assistant automatically detects and recommends profiles

**Detection Process:**
1. AI analyzes open files and paths
2. Detects task type from request
3. Recommends appropriate profile
4. Adjusts responses based on profile

**You:**
- Review AI recommendation
- Switch profile if needed
- Continue working

### Context-Aware Responses

**Rule:** AI adjusts responses based on profile

**Profile-Specific Behavior:**
- **Argo Trading:** Applies trading-specific rules, excludes Alpine context
- **Alpine Full-Stack:** Applies frontend/backend rules, excludes Argo context
- **Security-Sensitive:** Prioritizes IP protection, enforces trade secret marking
- **Monorepo Refactoring:** Considers cross-service impact, applies all rules
- **Dev Workflow:** Focuses on speed and iteration

---

## Profile Configuration

### Profile Files

**Rule:** Use profile JSON files from `.cursor/profiles/`

**Available Profiles:**
- `argo-trading.json` - Argo Trading Profile
- `alpine-fullstack.json` - Alpine Full-Stack Profile
- `security-sensitive.json` - Security-Sensitive Profile
- `monorepo-refactoring.json` - Monorepo Refactoring Profile
- `dev-workflow.json` - Dev Workflow Profile

**Setup:** See [docs/CURSOR_PROFILES_QUICK_START.md](../docs/CURSOR_PROFILES_QUICK_START.md)

### Profile Settings

**Rule:** Only use valid Cursor Pro settings

**Valid Settings:**
- Model selection
- Context window size
- Feature toggles (composer, agent, codebase)
- File exclusions
- Search exclusions

**Invalid Settings (Removed):**
- `cursor.codebase.paths` - Not supported
- `cursor.rules.include` - Rules load automatically
- `cursor.composer.monorepoMode` - Not a valid setting

---

## Best Practices

### DO

✅ **DO:**
- Use appropriate profile for your work
- Switch profiles when changing context
- Trust AI profile recommendations
- Use Security-Sensitive Profile for trade secrets
- Keep profiles updated

### DON'T

❌ **DON'T:**
- Use wrong profile for context (e.g., Argo profile for Alpine work)
- Ignore AI profile recommendations
- Work on trade secrets without Security-Sensitive Profile
- Mix entity contexts (profiles prevent this)
- Modify profile settings unnecessarily

---

## Profile Maintenance

### Regular Updates

**Rule:** Review and update profiles quarterly

**Review Checklist:**
- [ ] Profile settings still valid
- [ ] File exclusions still appropriate
- [ ] New rules added to relevant profiles
- [ ] Performance optimized
- [ ] Documentation updated

### Team Synchronization

**Rule:** Keep profiles synchronized across team

**Process:**
1. Update profile JSON files
2. Commit to version control
3. Team members update local profiles
4. Document changes

---

## Related Rules

- **Monorepo:** [10_MONOREPO.md](10_MONOREPO.md) - Entity separation
- **IP Protection:** [22_TRADE_SECRET_IP_PROTECTION.md](22_TRADE_SECRET_IP_PROTECTION.md) - Trade secret protection
- **Development:** [01_DEVELOPMENT.md](01_DEVELOPMENT.md) - Development practices

---

**Note:** Cursor Pro profiles optimize AI assistance and enforce entity separation. Always use the appropriate profile for your work context. The AI assistant will automatically detect and recommend profiles - trust the recommendations and switch when needed.

