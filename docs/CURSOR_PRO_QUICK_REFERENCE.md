# Cursor Pro Quick Reference

**Last Updated:** January 15, 2025  
**Version:** 1.0

---

## 🚀 Quick Access

### Composer Mode
- **Shortcut:** `Cmd+I` (Mac) or `Ctrl+I` (Windows/Linux)
- **Use for:** Multi-file refactoring, cross-service changes
- **Best for:** Coordinated changes across monorepo

**Example:**
```
"Refactor signal validation across argo, alpine-backend, and alpine-frontend"
```

### Agent Mode
- **Shortcut:** `Cmd+Shift+A` (Mac) or `Ctrl+Shift+A` (Windows/Linux)
- **Use for:** Complex autonomous tasks
- **Best for:** Following existing patterns, generating boilerplate

**Example:**
```
"Implement new data source following our existing patterns in argo/argo/core/data_sources/"
```

### Codebase Chat
- **Shortcut:** `Cmd+L` (Mac) or `Ctrl+L` (Windows/Linux)
- **Use for:** Understanding architecture, finding patterns
- **Best for:** Learning the codebase, debugging

**Example:**
```
"How does the 7-layer risk management system work in Argo?"
```

---

## 🐛 Bugbot

Automatically reviews PRs for:
- ✅ Security vulnerabilities
- ✅ Code quality issues
- ✅ Naming convention violations (your 25+ rules)
- ✅ Test coverage gaps
- ✅ Performance issues
- ✅ SOLID principles violations
- ✅ Error handling gaps
- ✅ Documentation issues

**Runs automatically on every PR - no action needed!**

### Setup Instructions

Bugbot works through the **Cursor GitHub App**, not a GitHub Action. Here's how to set it up:

#### Step 1: Install Cursor GitHub App
1. Go to: https://github.com/apps/cursor (or find it in Cursor settings)
2. Click "Install" or "Configure"
3. Grant access to your repository (or all repositories)

#### Step 2: Configure Bugbot in Cursor Dashboard
1. Open Cursor
2. Go to Settings → Integrations → GitHub
3. Or go to: https://cursor.com/dashboard (or https://cursor.sh/dashboard)
4. Navigate to Bugbot settings
5. Configure options:
   - ✅ **Automatically review pull requests** (recommended)
   - Or: **Only Run When Mentioned** (if you prefer manual)
6. Point Bugbot to your rules:
   - Rules path: `./Rules`
   - Cursor rules path: `./.cursorrules`

#### Step 3: Verify Setup
1. Create a test PR
2. Bugbot should automatically comment on the PR
3. Check PR comments for Bugbot's review

**Note:** Bugbot uses your `.cursorrules/` and `Rules/` directory to enforce your coding standards automatically.

---

## 📋 Common Tasks

### Refactoring Across Services

**Using Composer:**
1. Press `Cmd+I` (Composer)
2. Type: "Refactor [feature] across argo, alpine-backend, and alpine-frontend"
3. Review changes in preview
4. Apply when satisfied

**Example:**
```
"Extract signal validation logic into a shared utility function and update all three services to use it"
```

### Adding New Features

**Using Agent Mode:**
1. Press `Cmd+Shift+A` (Agent)
2. Type: "Add [feature] following our existing patterns in [service]"
3. Watch it work autonomously
4. Review generated code
5. Commit when ready

**Example:**
```
"Add a new risk management layer following the existing 7-layer pattern, including tests and documentation"
```

### Understanding Codebase

**Using Codebase Chat:**
1. Press `Cmd+L` (Chat)
2. Ask: "How does [feature] work?"
3. Get detailed explanations with file references
4. Follow links to actual code

**Example:**
```
"What are all the data sources we use and their weights?"
"How does environment detection work?"
"Show me all places where we handle position sizing"
```

---

## 🎯 Best Practices

### Use Composer For:
- ✅ Multi-file refactoring
- ✅ Cross-service changes
- ✅ Coordinated updates
- ✅ Pattern application across codebase
- ✅ Renaming across multiple files

### Use Agent For:
- ✅ Complex implementations
- ✅ Following existing patterns
- ✅ Generating boilerplate code
- ✅ Test generation
- ✅ Documentation generation

### Use Chat For:
- ✅ Understanding architecture
- ✅ Finding code patterns
- ✅ Debugging help
- ✅ Learning the codebase
- ✅ Getting code explanations

---

## 🔧 Configuration

### Workspace Settings
Location: `.cursor/settings.json`

**Current Configuration:**
- **Model:** Claude Sonnet 4 (enhanced)
- **Context Window:** Large (better for monorepo)
- **Composer:** Enabled with monorepo mode
- **Codebase Indexing:** Automatic
- **Agent Mode:** Enabled

### Rules Integration
- **Rules Path:** `Rules/` directory (25+ rule files)
- **Cursor Rules:** `.cursorrules/` directory
- **Automatic Enforcement:** Enabled

---

## 📚 Related Documentation

### Development Rules
- **Rules Directory:** `Rules/` - Complete rule system
- **Quick Reference:** `Rules/README.md`
- **Code Quality:** `Rules/02_CODE_QUALITY.md`
- **Development:** `Rules/01_DEVELOPMENT.md`

### Deployment
- **Deployment Rules:** `Rules/04_DEPLOYMENT.md`
- **Environment:** `Rules/05_ENVIRONMENT.md`
- **Dev vs Prod:** `Rules/16_DEV_PROD_DIFFERENCES.md`

### Project-Specific
- **Trading Operations:** `Rules/13_TRADING_OPERATIONS.md`
- **Frontend:** `Rules/11_FRONTEND.md`
- **Backend:** `Rules/12A_ARGO_BACKEND.md`, `Rules/12B_ALPINE_BACKEND.md`

---

## 🧪 Testing Features

### Quick Test Checklist

**Enhanced Models:**
- [ ] Open any Python/TypeScript file
- [ ] Start typing - completions should be context-aware
- [ ] Check model indicator shows "Claude Sonnet" or "GPT-4"

**Composer Mode:**
- [ ] Press `Cmd+I`
- [ ] Panel should open
- [ ] Type a refactoring request
- [ ] Should show files it will modify

**Agent Mode:**
- [ ] Press `Cmd+Shift+A`
- [ ] Panel should open
- [ ] Type a task request
- [ ] Should work autonomously

**Codebase Chat:**
- [ ] Press `Cmd+L`
- [ ] Ask a question about your codebase
- [ ] Should reference actual files

**Bugbot:**
- [ ] Create a test PR with intentional issues
- [ ] Check GitHub Actions tab
- [ ] Bugbot should comment on PR

---

## 🚨 Troubleshooting

### Composer Not Opening
- Check keyboard shortcut: `Cmd+I` (Mac) or `Ctrl+I` (Windows)
- Try: Command Palette → "Composer"
- Verify Pro subscription is active

### Agent Not Working
- Check keyboard shortcut: `Cmd+Shift+A` (Mac) or `Ctrl+Shift+A` (Windows)
- Make sure you're in a code file
- Verify Pro subscription is active

### Bugbot Not Running
- Verify Cursor GitHub App is installed: https://github.com/apps/cursor
- Check app has access to your repository
- Verify Bugbot is enabled in Cursor dashboard
- Check PR comments - Bugbot comments there, not in Actions tab

### Enhanced Models Not Active
- Check Cursor Settings → Account → Should show "Pro"
- Verify model indicator shows "Claude Sonnet" or "GPT-4"
- Restart Cursor if needed

---

## 💡 Tips

1. **Use Composer for Monorepo Refactoring**
   - Perfect for changes across multiple services
   - Shows preview before applying
   - Respects your code structure

2. **Use Agent for Pattern Following**
   - Great for implementing features following existing patterns
   - Automatically follows your naming conventions
   - Creates code that matches your style

3. **Use Chat for Learning**
   - Ask questions about your architecture
   - Understand complex systems
   - Find code patterns quickly

4. **Let Bugbot Do Reviews**
   - Automatically catches issues
   - Enforces your 25+ rules
   - Saves time on manual reviews

---

**For complete rules and guidelines, see:** `Rules/README.md`

