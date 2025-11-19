#!/bin/bash

# Verify Extensions Are Running and Configured
# This script checks that all recommended extensions are installed and properly configured

set -e

echo "🔌 Verifying VS Code/Cursor Extensions Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Determine if we're in Cursor or VS Code
if command -v cursor &> /dev/null; then
    CMD="cursor"
    EDITOR_NAME="Cursor"
elif command -v code &> /dev/null; then
    CMD="code"
    EDITOR_NAME="VS Code"
else
    echo -e "${YELLOW}⚠️  Neither 'cursor' nor 'code' command found in PATH${NC}"
    echo "   This script requires Cursor or VS Code CLI to be installed"
    echo ""
    echo "   Install Cursor CLI:"
    echo "     Cursor → Command Palette → 'Shell Command: Install cursor command'"
    echo ""
    echo "   Or install VS Code CLI:"
    echo "     VS Code → Command Palette → 'Shell Command: Install code command'"
    exit 1
fi

echo -e "${BLUE}Using: $EDITOR_NAME${NC}"
echo ""

# Check if extensions.json exists
if [ ! -f ".vscode/extensions.json" ]; then
    echo -e "${RED}❌ .vscode/extensions.json not found${NC}"
    exit 1
fi

# Extract extension IDs from extensions.json
echo "📋 Checking Recommended Extensions:"
echo ""

# Read extensions from JSON (simple extraction)
EXTENSIONS=$(grep -o '"[^"]*"' .vscode/extensions.json | grep -v "schema\|version\|recommendations\|unwantedRecommendations" | sed 's/"//g' | grep -E "^[a-z0-9-]+\.[a-z0-9-]+$" | sort -u)

if [ -z "$EXTENSIONS" ]; then
    echo -e "${YELLOW}⚠️  Could not parse extensions from .vscode/extensions.json${NC}"
    exit 1
fi

INSTALLED=0
MISSING=0
TOTAL=0

# Check each extension
while IFS= read -r ext; do
    if [ -n "$ext" ]; then
        TOTAL=$((TOTAL + 1))
        if $CMD --list-extensions 2>/dev/null | grep -q "^${ext}$"; then
            echo -e "  ${GREEN}✅${NC} $ext"
            INSTALLED=$((INSTALLED + 1))
        else
            echo -e "  ${RED}❌${NC} $ext ${YELLOW}(not installed)${NC}"
            MISSING=$((MISSING + 1))
        fi
    fi
done <<< "$EXTENSIONS"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Summary:"
echo -e "  ${GREEN}✅ Installed: $INSTALLED/$TOTAL${NC}"
if [ $MISSING -gt 0 ]; then
    echo -e "  ${RED}❌ Missing: $MISSING/$TOTAL${NC}"
fi
echo ""

# Check settings.json or workspace file
echo "⚙️  Checking Extension Settings:"
echo ""

SETTINGS_FILE=".vscode/settings.json"
WORKSPACE_FILE="argo-alpine.code-workspace"
CHECKS=0
PASSED=0

# Check workspace file first (primary), then settings.json (fallback)
if [ -f "$WORKSPACE_FILE" ]; then
    SETTINGS_SOURCE="$WORKSPACE_FILE"
    echo -e "  ${BLUE}Checking workspace file: $WORKSPACE_FILE${NC}"
elif [ -f "$SETTINGS_FILE" ]; then
    SETTINGS_SOURCE="$SETTINGS_FILE"
    echo -e "  ${BLUE}Checking settings file: $SETTINGS_FILE${NC}"
else
    echo -e "  ${YELLOW}⚠️${NC}  Neither .vscode/settings.json nor argo-alpine.code-workspace found"
    SETTINGS_SOURCE=""
fi

if [ -n "$SETTINGS_SOURCE" ]; then
    # Python
    if grep -q '"python.linting.enabled": true' "$SETTINGS_SOURCE" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} Python linting enabled"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠️${NC}  Python linting not explicitly enabled"
    fi
    CHECKS=$((CHECKS + 1))

    # ESLint
    if grep -q '"eslint.enable": true' "$SETTINGS_SOURCE" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} ESLint enabled"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠️${NC}  ESLint not explicitly enabled"
    fi
    CHECKS=$((CHECKS + 1))

    # Prettier
    if grep -q '"prettier.enable": true\|"editor.formatOnSave": true' "$SETTINGS_SOURCE" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} Prettier/Formatting enabled"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠️${NC}  Prettier/Formatting not explicitly enabled"
    fi
    CHECKS=$((CHECKS + 1))

    # Error Lens
    if grep -q '"errorLens.enabled": true' "$SETTINGS_SOURCE" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} Error Lens enabled"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠️${NC}  Error Lens not explicitly enabled"
    fi
    CHECKS=$((CHECKS + 1))

    # GitLens
    if grep -q '"gitlens.enabled": true' "$SETTINGS_SOURCE" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} GitLens enabled"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠️${NC}  GitLens not explicitly enabled"
    fi
    CHECKS=$((CHECKS + 1))

    # Tailwind CSS
    if grep -q '"tailwindCSS' "$SETTINGS_SOURCE" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} Tailwind CSS configured"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠️${NC}  Tailwind CSS not configured"
    fi
    CHECKS=$((CHECKS + 1))

    # Jest
    if grep -q '"jest\.' "$SETTINGS_SOURCE" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} Jest configured"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠️${NC}  Jest not configured"
    fi
    CHECKS=$((CHECKS + 1))

    # Playwright
    if grep -q '"playwright\.' "$SETTINGS_SOURCE" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} Playwright configured"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${YELLOW}⚠️${NC}  Playwright not configured"
    fi
    CHECKS=$((CHECKS + 1))

    echo ""
    echo -e "  Settings configured: ${GREEN}$PASSED/$CHECKS${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $MISSING -gt 0 ]; then
    echo -e "${YELLOW}📥 To install missing extensions:${NC}"
    echo ""
    echo "  1. Open Command Palette: Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows/Linux)"
    echo "  2. Type: 'Extensions: Show Recommended Extensions'"
    echo "  3. Click 'Install All' or install individually"
    echo ""
    echo "  Or run: $CMD --install-extension <extension-id>"
    echo ""
    exit 1
else
    echo -e "${GREEN}✨ All recommended extensions are installed!${NC}"
    echo ""
    echo "💡 Tips to ensure extensions are running:"
    echo "  • Reload window: Cmd+Shift+P → 'Developer: Reload Window'"
    echo "  • Check extension status in Extensions view (Cmd+Shift+X)"
    echo "  • Verify language servers are running in Output panel"
    echo ""
    exit 0
fi
