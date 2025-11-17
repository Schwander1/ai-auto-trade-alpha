#!/bin/bash

# Verify Extensions Optimization Script
# Checks that all extension-specific settings are properly configured

set -e

echo "🔍 Verifying Extensions Optimization..."
echo ""

ERRORS=0
WARNINGS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check setting exists
check_setting() {
    local file=$1
    local setting=$2
    local description=$3

    if grep -q "$setting" "$file" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $description"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC}  $description (not found)"
        ((WARNINGS++))
        return 1
    fi
}

echo -e "${BLUE}📦 Checking Extension Settings...${NC}"
echo ""

# Check Python extension settings
echo "Python Extensions:"
check_setting ".vscode/settings.json" "python.formatting.blackArgs" "Black formatter args"
check_setting ".vscode/settings.json" "isort.args" "isort configuration"
check_setting ".vscode/settings.json" "pythonIndent" "Python indent settings"
check_setting ".vscode/settings.json" "python.analysis.completeFunctionParens" "Python function completion"
echo ""

# Check TypeScript/JavaScript extension settings
echo "TypeScript/JavaScript Extensions:"
check_setting ".vscode/settings.json" "eslint.workingDirectories" "ESLint working directories"
check_setting ".vscode/settings.json" "eslint.codeActionsOnSave" "ESLint code actions"
check_setting ".vscode/settings.json" "typescript.inlayHints" "TypeScript inlay hints"
check_setting ".vscode/settings.json" "tailwindCSS.experimental" "Tailwind CSS experimental"
echo ""

# Check utility extension settings
echo "Utility Extensions:"
check_setting ".vscode/settings.json" "errorLens.enabled" "Error Lens enabled"
check_setting ".vscode/settings.json" "gitlens.codeLens" "GitLens code lens"
check_setting ".vscode/settings.json" "cSpell.ignoreWords" "Spell checker ignore words"
check_setting ".vscode/settings.json" "jest.runMode" "Jest run mode"
echo ""

# Check editor enhancements
echo "Editor Enhancements:"
check_setting ".vscode/settings.json" "files.autoSave" "Auto-save enabled"
check_setting ".vscode/settings.json" "editor.tabCompletion" "Tab completion"
check_setting ".vscode/settings.json" "workbench.editor.highlightModifiedTabs" "Modified tab highlighting"
echo ""

# Check ESLint config
echo -e "${BLUE}📝 Checking ESLint Configuration...${NC}"
echo ""

if [ -f ".eslintrc.json" ]; then
    echo -e "${GREEN}✅${NC} .eslintrc.json exists"
    if python3 -m json.tool .eslintrc.json > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} .eslintrc.json is valid JSON"
    else
        echo -e "${RED}❌${NC} .eslintrc.json is invalid JSON"
        ((ERRORS++))
    fi
else
    echo -e "${RED}❌${NC} .eslintrc.json missing"
    ((ERRORS++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✨ All extension optimizations verified!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Verification complete with $WARNINGS warning(s)${NC}"
    echo "Review warnings above, but optimizations should work."
    exit 0
else
    echo -e "${RED}❌ Verification incomplete: $ERRORS error(s), $WARNINGS warning(s)${NC}"
    exit 1
fi
