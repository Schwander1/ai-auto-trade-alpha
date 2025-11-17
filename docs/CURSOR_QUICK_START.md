# Cursor Quick Start Guide

**Date:** January 17, 2025
**Status:** ✅ Ready to Use

---

## 🚀 Quick Setup (2 minutes)

### 1. Install Recommended Extensions

Cursor will automatically prompt you to install recommended extensions. Click "Install All" when prompted.

**Or install manually:**
- Open Command Palette: `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
- Type: "Extensions: Show Recommended Extensions"
- Click "Install All"

### 2. Verify Setup

Run the verification script:

```bash
./scripts/verify-cursor-setup.sh
```

You should see: ✨ **All checks passed!**

### 3. Rebuild Codebase Index (Optional but Recommended)

- Open Command Palette: `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
- Type: "Cursor: Rebuild Codebase Index"
- Wait for completion (may take 2-5 minutes)

---

## 🎯 Key Features Now Active

### ✅ Format-on-Save
- Code automatically formats when you save
- Python: Black formatter (100 char line length)
- TypeScript/JavaScript: Prettier (100 char line length)

### ✅ Auto-Imports
- Automatic import suggestions
- Import organization on save

### ✅ AI Assistance
- **Composer**: `Cmd+I` (Mac) or `Ctrl+I` (Windows/Linux)
- **Chat**: `Cmd+L` (Mac) or `Ctrl+L` (Windows/Linux)
- **Agent**: Available in Composer

### ✅ Code Navigation
- Go to Definition: `Cmd+Click` or `F12`
- Find References: `Shift+F12`
- Search Codebase: `Cmd+Shift+F`

---

## 📋 Common Tasks

### Format Code Manually
- **Mac**: `Shift+Option+F`
- **Windows/Linux**: `Shift+Alt+F`

### Organize Imports
- **Mac**: `Shift+Option+O`
- **Windows/Linux**: `Shift+Alt+O`

### Run Linter
- **Mac**: `Cmd+Shift+P` → "ESLint: Fix all auto-fixable Problems"
- **Windows/Linux**: `Ctrl+Shift+P` → "ESLint: Fix all auto-fixable Problems"

### Switch Cursor Profiles
- **Mac**: `Cmd+Shift+P` → "Profile: Switch"
- **Windows/Linux**: `Ctrl+Shift+P` → "Profile: Switch"
- Or click profile name in status bar (bottom-right)

---

## 🔧 Configuration Files

All settings are in:
- **Cursor Settings**: `.cursor/settings.json`
- **Editor Settings**: `.vscode/settings.json`
- **Extensions**: `.vscode/extensions.json`
- **Prettier**: `.prettierrc.json`
- **EditorConfig**: `.editorconfig`

**Don't edit these unless you know what you're doing!**

---

## 🐛 Troubleshooting

### Code Not Formatting on Save

1. Check file is saved (not just auto-saved)
2. Verify formatter extension is installed
3. Check language-specific settings in `.vscode/settings.json`

### AI Assistance Not Working

1. Check Cursor Pro subscription is active
2. Verify internet connection
3. Try restarting Cursor

### Slow Performance

1. Rebuild codebase index (see step 3 above)
2. Check `.cursorignore` includes large directories
3. Close unused files/tabs
4. Restart Cursor

### Import Suggestions Not Working

1. Verify TypeScript/JavaScript language server is running
2. Check `node_modules` is installed: `pnpm install`
3. Restart TypeScript server: `Cmd+Shift+P` → "TypeScript: Restart TS Server"

---

## 📚 More Information

- **Complete Guide**: `docs/CURSOR_OPTIMIZATION_COMPLETE.md`
- **Configuration Docs**: `.cursor/README.md`
- **Quick Summary**: `CURSOR_SETUP_SUMMARY.md`
- **Rules System**: `Rules/README.md`

---

## ✨ You're All Set!

Everything is configured and optimized. Start coding and enjoy the enhanced AI assistance! 🎉
