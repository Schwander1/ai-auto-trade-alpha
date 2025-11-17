# Cursor Pro Profiles - Quick Start Guide

**Last Updated:** January 15, 2025  
**Version:** 1.0

---

## 🚀 5-Minute Setup

### Step 1: Create Profiles (3 minutes)

1. Open Cursor Settings: `Cmd+,` (Mac) or `Ctrl+,` (Windows/Linux)
2. Navigate to **Profiles** section
3. Create each profile:

   **Profile 1: Argo Trading**
   - Click "Create New Profile"
   - Name: `Argo Trading`
   - Copy JSON from: `.cursor/profiles/argo-trading.json`
   - Paste and save

   **Profile 2: Alpine Full-Stack**
   - Click "Create New Profile"
   - Name: `Alpine Full-Stack`
   - Copy JSON from: `.cursor/profiles/alpine-fullstack.json`
   - Paste and save

   **Profile 3: Security-Sensitive**
   - Click "Create New Profile"
   - Name: `Security-Sensitive`
   - Copy JSON from: `.cursor/profiles/security-sensitive.json`
   - Paste and save

   **Profile 4: Monorepo Refactoring**
   - Click "Create New Profile"
   - Name: `Monorepo Refactoring`
   - Copy JSON from: `.cursor/profiles/monorepo-refactoring.json`
   - Paste and save

   **Profile 5: Dev Workflow**
   - Click "Create New Profile"
   - Name: `Dev Workflow`
   - Copy JSON from: `.cursor/profiles/dev-workflow.json`
   - Paste and save

### Step 2: Set Default Profile (30 seconds)

1. In Profiles settings, select your most-used profile
2. Click "Set as Default"
3. Recommended: **Argo Trading** or **Alpine Full-Stack**

### Step 3: Test Profile Switching (1 minute)

1. Open any file in `argo/` directory
2. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
3. Type "Profile: Switch"
4. Select "Argo Trading"
5. Verify profile indicator shows "Argo Trading"

---

## 🎯 How It Works

### Automatic Detection

The AI assistant automatically:
1. **Detects** your current context (open files, task type)
2. **Recommends** the appropriate profile
3. **Adjusts** responses based on profile

### Manual Switching

You manually switch profiles:
- **Keyboard:** `Cmd+Shift+P` → "Profile: Switch"
- **Status Bar:** Click profile name (bottom-right)
- **Command Palette:** Type "Profile: Switch"

---

## 📋 Profile Quick Reference

| Profile | When to Use | Switch To When... |
|---------|-------------|-------------------|
| **Argo Trading** | Working on `argo/` | Editing trading code, signals, risk management |
| **Alpine Full-Stack** | Working on `alpine-*/` | Editing frontend/backend, APIs, user features |
| **Security-Sensitive** | Trade secret work | Editing proprietary algorithms, IP-protected code |
| **Monorepo Refactoring** | Cross-service work | Refactoring across services, updating rules |
| **Dev Workflow** | Fast iteration | Bug fixes, quick tests, rapid development |

---

## 🔍 Example Workflow

### Scenario: Working on Trading Algorithm

1. **Open file:** `argo/argo/core/signal_generation_service.py`
2. **AI detects:** Trade secret file in `argo/` directory
3. **AI recommends:** "Security-Sensitive Profile"
4. **You switch:** `Cmd+Shift+P` → "Security-Sensitive"
5. **AI responds:** With IP protection focus, appropriate rules

### Scenario: Working on Frontend Feature

1. **Open file:** `alpine-frontend/app/dashboard/page.tsx`
2. **AI detects:** Frontend file in `alpine-frontend/`
3. **AI recommends:** "Alpine Full-Stack Profile"
4. **You switch:** `Cmd+Shift+P` → "Alpine Full-Stack"
5. **AI responds:** With full-stack context, backend-frontend integration

---

## ✅ Verification Checklist

After setup, verify:

- [ ] All 5 profiles created in Cursor
- [ ] Default profile set
- [ ] Can switch profiles via Command Palette
- [ ] Profile indicator shows in status bar
- [ ] AI assistant detects and recommends profiles

---

## 🆘 Troubleshooting

### Profile Not Appearing
- Restart Cursor after creating profiles
- Verify Cursor Pro subscription is active
- Check profile JSON is valid (no syntax errors)

### Wrong Profile Recommended
- Override manually by switching to correct profile
- AI learns from your corrections
- Check file path matches expected patterns

### Performance Issues
- Switch to focused profile (Argo Trading or Alpine Full-Stack)
- Reduce context window size in profile settings
- Check indexing status in Cursor settings

---

## 📚 Next Steps

- **Complete Guide:** See `docs/CURSOR_PROFILES_STRATEGY.md`
- **Detection Rules:** See `.cursor/PROFILE_DETECTION.md`
- **Profile Files:** See `.cursor/profiles/README.md`

---

## 💡 Pro Tips

1. **Set keyboard shortcuts** for frequently used profiles
2. **Watch for AI recommendations** - they're usually correct
3. **Switch profiles** when changing context (different directory)
4. **Use Security-Sensitive** for any trade secret work
5. **Use Dev Workflow** for quick iterations and bug fixes

---

**Ready to go!** Start working and the AI will automatically detect and recommend the right profile.

