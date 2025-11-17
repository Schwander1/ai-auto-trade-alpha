# Cursor Onboarding Checklist

**Date:** January 17, 2025
**For:** New developers joining the workspace

---

## ✅ Pre-Setup Checklist

- [ ] Cursor Pro subscription active
- [ ] Git configured (`git config user.name` and `git config user.email`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] pnpm 8+ installed (`pnpm --version`)

---

## 🚀 Setup Steps

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd argo-alpine-workspace
```

### Step 2: Install Dependencies
```bash
# Install root dependencies
pnpm install

# Install Python dependencies (if needed)
cd alpine-backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../argo && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### Step 3: Open in Cursor
```bash
cursor .
```

### Step 4: Install Recommended Extensions
- Cursor will prompt automatically, or:
- Command Palette: `Cmd+Shift+P` → "Extensions: Show Recommended Extensions"
- Click "Install All"

**Essential Extensions:**
- ✅ Python (`ms-python.python`)
- ✅ Pylance (`ms-python.vscode-pylance`)
- ✅ Black Formatter (`ms-python.black-formatter`)
- ✅ ESLint (`dbaeumer.vscode-eslint`)
- ✅ Prettier (`esbenp.prettier-vscode`)
- ✅ Tailwind CSS (`bradlc.vscode-tailwindcss`)

### Step 5: Verify Setup
```bash
./scripts/verify-cursor-setup.sh
```

Expected output: ✨ **All checks passed!**

### Step 6: Rebuild Codebase Index (Recommended)
- Command Palette: `Cmd+Shift+P` → "Cursor: Rebuild Codebase Index"
- Wait 2-5 minutes for completion

### Step 7: Configure Environment Variables
```bash
# Copy example env files (if they exist)
cp .env.example .env.local
# Edit .env.local with your values
```

---

## 🎯 Verify Everything Works

### Test Format-on-Save
1. Open any Python file
2. Make a formatting change (add extra spaces)
3. Save the file (`Cmd+S`)
4. ✅ Code should auto-format

### Test AI Assistance
1. Open any file
2. Press `Cmd+I` (Mac) or `Ctrl+I` (Windows/Linux)
3. ✅ Composer should open
4. Ask: "What does this function do?"
5. ✅ Should get helpful response

### Test Code Navigation
1. Click on any function name
2. Press `F12` (Go to Definition)
3. ✅ Should jump to definition

### Test Search
1. Press `Cmd+Shift+F` (Mac) or `Ctrl+Shift+F` (Windows/Linux)
2. Search for a function name
3. ✅ Should find all occurrences

---

## 📚 Read Documentation

- [ ] **Quick Start**: Read `docs/CURSOR_QUICK_START.md`
- [ ] **Rules System**: Skim `Rules/README.md`
- [ ] **Entity Separation**: Read `Rules/10_MONOREPO.md`
- [ ] **Development Practices**: Read `Rules/01_DEVELOPMENT.md`

---

## 🎓 Learn Keyboard Shortcuts

### Essential Shortcuts
- [ ] **AI Composer**: `Cmd+I` (Mac) / `Ctrl+I` (Windows/Linux)
- [ ] **AI Chat**: `Cmd+L` (Mac) / `Ctrl+L` (Windows/Linux)
- [ ] **Format Document**: `Shift+Option+F` (Mac) / `Shift+Alt+F` (Windows/Linux)
- [ ] **Go to Definition**: `F12`
- [ ] **Find References**: `Shift+F12`
- [ ] **Search in Files**: `Cmd+Shift+F` (Mac) / `Ctrl+Shift+F` (Windows/Linux)
- [ ] **Command Palette**: `Cmd+Shift+P` (Mac) / `Ctrl+Shift+P` (Windows/Linux)

---

## 🔧 Test Common Tasks

### Run Format All
- Command Palette: `Cmd+Shift+P` → "Tasks: Run Task" → "Format All Files"
- ✅ Should format all files

### Run Lint
- Command Palette: `Cmd+Shift+P` → "Tasks: Run Task" → "Lint All"
- ✅ Should run linters

### Run Type Check
- Command Palette: `Cmd+Shift+P` → "Tasks: Run Task" → "Type Check"
- ✅ Should check TypeScript types

---

## 🐛 Troubleshooting

### If Format-on-Save Doesn't Work
1. Check file is saved (not just auto-saved)
2. Verify formatter extension is installed
3. Check language-specific settings

### If AI Assistance Doesn't Work
1. Check Cursor Pro subscription is active
2. Verify internet connection
3. Restart Cursor

### If Extensions Don't Install
1. Check internet connection
2. Try installing manually from Extensions panel
3. Restart Cursor

---

## ✅ Final Checklist

- [ ] All extensions installed
- [ ] Setup verification passed
- [ ] Codebase index rebuilt
- [ ] Format-on-save working
- [ ] AI assistance working
- [ ] Code navigation working
- [ ] Documentation read
- [ ] Keyboard shortcuts learned
- [ ] Tasks tested

---

## 🎉 You're Ready!

Once all items are checked, you're ready to start developing!

**Next Steps:**
1. Pick a task from your backlog
2. Use AI assistance (`Cmd+I`) to help with implementation
3. Format code on save (automatic)
4. Run tests before committing

**Need Help?**
- Check `docs/CURSOR_QUICK_START.md` for quick reference
- Check `docs/CURSOR_FINAL_SETUP.md` for complete guide
- Ask team members for assistance

---

**Welcome to the team! Happy coding! 🚀**
