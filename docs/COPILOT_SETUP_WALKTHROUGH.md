# GitHub Copilot CLI Setup Walkthrough

**Date:** January 15, 2025  
**Status:** Step-by-Step Setup Guide

---

## Step 1: Sign Up for GitHub Copilot Pro

### 1.1 Go to GitHub Copilot

1. Open your browser
2. Go to: **https://github.com/features/copilot**
3. Click **"Get Copilot Pro"** or **"Start free trial"**

### 1.2 Choose Plan

- Select **Copilot Pro** ($10/month or $100/year)
- This includes:
  - Unlimited code completions
  - 300 premium requests/month
  - Access to advanced AI models
  - **Copilot CLI access** (included)

### 1.3 Complete Payment

- Enter payment information
- Confirm subscription
- You'll be redirected to your GitHub account

---

## Step 2: Install Copilot CLI

### 2.1 Install via npm

Open your terminal and run:

```bash
npm install -g @githubnext/github-copilot-cli
```

**Expected output:**
```
+ @githubnext/github-copilot-cli@x.x.x
added 1 package in 5s
```

### 2.2 Verify Installation

```bash
copilot --version
```

**Expected output:**
```
@githubnext/github-copilot-cli/x.x.x
```

If you see an error, try:
```bash
# Check if npm global bin is in PATH
npm config get prefix

# Add to PATH if needed (add to ~/.zshrc or ~/.bashrc)
export PATH="$(npm config get prefix)/bin:$PATH"
```

---

## Step 3: Authenticate Copilot CLI

### 3.1 Start Authentication

```bash
copilot auth
```

### 3.2 Follow the Prompts

1. **Browser will open automatically** (or you'll get a URL)
2. **Sign in to GitHub** if not already signed in
3. **Authorize Copilot CLI** - Click "Authorize" button
4. **Copy the token** shown in browser
5. **Paste token in terminal** when prompted
6. **Press Enter**

**Expected output:**
```
✅ Successfully authenticated!
```

### 3.3 Verify Authentication

```bash
copilot "Hello, can you help me?"
```

**Expected output:**
```
[Helpful response from Copilot]
```

---

## Step 4: Test with Your Workspace

### 4.1 Test Basic Command

```bash
cd /Users/dylanneuenschwander/argo-alpine-workspace
copilot "What files are in the current directory?"
```

### 4.2 Test with Rules Wrapper

```bash
./scripts/agentic/copilot-with-rules.sh "Explain the deployment workflow"
```

**Expected output:**
```
🤖 Executing agentic command with automatic rule enforcement...
[Response with rules context included]
✅ Agentic operation completed successfully
```

---

## Troubleshooting

### Issue: "copilot: command not found"

**Solution:**
```bash
# Reinstall
npm install -g @githubnext/github-copilot-cli

# Check PATH
which copilot

# If not found, add npm global bin to PATH
echo 'export PATH="$(npm config get prefix)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Issue: Authentication Fails

**Solution:**
```bash
# Reset authentication
copilot auth --reset

# Try again
copilot auth
```

### Issue: "Not authorized" or "Subscription required"

**Solution:**
1. Verify you have Copilot Pro subscription:
   - Go to: https://github.com/settings/copilot
   - Check subscription status
2. If not subscribed:
   - Go to: https://github.com/features/copilot
   - Sign up for Copilot Pro
3. Re-authenticate:
   ```bash
   copilot auth --reset
   copilot auth
   ```

### Issue: Browser doesn't open

**Solution:**
1. Copy the URL shown in terminal
2. Open it manually in your browser
3. Complete authorization
4. Copy token back to terminal

---

## Verification Checklist

- [ ] Copilot Pro subscription active
- [ ] Copilot CLI installed (`copilot --version` works)
- [ ] Authentication successful (`copilot auth` completed)
- [ ] Basic command works (`copilot "test"` returns response)
- [ ] Rules wrapper works (`./scripts/agentic/copilot-with-rules.sh "test"`)

---

## Next Steps

Once Copilot CLI is set up:

1. **Test deployment automation:**
   ```bash
   ./scripts/agentic/copilot-with-rules.sh "Deploy Argo to production"
   ```

2. **Test refactoring:**
   ```bash
   ./scripts/agentic/copilot-with-rules.sh "Refactor functions over 50 lines"
   ```

3. **Monitor usage:**
   ```bash
   pnpm agentic:usage
   ```

---

## Quick Reference

```bash
# Install
npm install -g @githubnext/github-copilot-cli

# Authenticate
copilot auth

# Test
copilot "test command"

# Use with rules
./scripts/agentic/copilot-with-rules.sh "your command"
```

---

**Need Help?** See `docs/AGENTIC_SETUP_GUIDE.md` for complete setup guide.

