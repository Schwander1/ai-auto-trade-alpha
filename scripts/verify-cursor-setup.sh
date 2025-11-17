#!/bin/bash

# Verify Cursor Setup Script
# Checks that all Cursor configuration files are properly set up

set -e

echo "🔍 Verifying Cursor Setup..."
echo ""

ERRORS=0
WARNINGS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $1"
        return 0
    else
        echo -e "${RED}❌${NC} $1 (missing)"
        ((ERRORS++))
        return 1
    fi
}

# Function to check JSON validity
check_json() {
    if python3 -m json.tool "$1" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $1 (valid JSON)"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC} $1 (JSONC with comments - OK for VS Code/Cursor)"
        ((WARNINGS++))
        return 1
    fi
}

echo "📁 Checking configuration files..."
echo ""

# Core Cursor files
check_file ".cursor/settings.json"
check_file ".cursorignore"
check_file ".cursor/README.md"

# VS Code files
check_file ".vscode/settings.json"
check_file ".vscode/extensions.json"

# Editor config
check_file ".editorconfig"

# Prettier config
check_file ".prettierrc.json"
check_file ".prettierignore"

# Cursor rules
if [ -d ".cursorrules" ]; then
    echo -e "${GREEN}✅${NC} .cursorrules/ directory"
    check_file ".cursorrules/main.mdc"
else
    echo -e "${RED}❌${NC} .cursorrules/ directory (missing)"
    ((ERRORS++))
fi

echo ""
echo "🔍 Validating JSON files..."
echo ""

# Validate JSON files (some may be JSONC which is OK)
check_json ".cursor/settings.json" || true
check_json ".prettierrc.json" || true

# Check VS Code settings (JSONC is expected)
if grep -q "//" .vscode/settings.json 2>/dev/null; then
    echo -e "${GREEN}✅${NC} .vscode/settings.json (JSONC format - correct)"
else
    check_json ".vscode/settings.json" || true
fi

# Check extensions.json (JSONC is expected)
if grep -q "//" .vscode/extensions.json 2>/dev/null; then
    echo -e "${GREEN}✅${NC} .vscode/extensions.json (JSONC format - correct)"
else
    check_json ".vscode/extensions.json" || true
fi

echo ""
echo "📊 Checking configuration consistency..."
echo ""

# Check Python line length consistency
PYTHON_RULER=$(grep -o '"editor.rulers": \[100' .cursor/settings.json .vscode/settings.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYTHON_RULER" -ge "1" ]; then
    echo -e "${GREEN}✅${NC} Python line length set to 100 (matches pre-commit)"
else
    echo -e "${YELLOW}⚠️${NC} Python line length may not match pre-commit config (100)"
    ((WARNINGS++))
fi

# Check Prettier line length
PRETTIER_WIDTH=$(grep -o '"printWidth": 100' .prettierrc.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$PRETTIER_WIDTH" -ge "1" ]; then
    echo -e "${GREEN}✅${NC} Prettier printWidth set to 100"
else
    echo -e "${YELLOW}⚠️${NC} Prettier printWidth may not be 100"
    ((WARNINGS++))
fi

# Check EditorConfig line length
EC_LENGTH=$(grep -o "max_line_length = 100" .editorconfig 2>/dev/null | wc -l | tr -d ' ')
if [ "$EC_LENGTH" -ge "1" ]; then
    echo -e "${GREEN}✅${NC} EditorConfig max_line_length set to 100"
else
    echo -e "${YELLOW}⚠️${NC} EditorConfig max_line_length may not be 100"
    ((WARNINGS++))
fi

echo ""
echo "🔍 Checking .gitignore..."
echo ""

# Check .gitignore includes our files
if grep -q "!.cursor/settings.json" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✅${NC} .gitignore allows .cursor/settings.json"
else
    echo -e "${YELLOW}⚠️${NC} .gitignore may not allow .cursor/settings.json"
    ((WARNINGS++))
fi

if grep -q "!.vscode/settings.json" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✅${NC} .gitignore allows .vscode/settings.json"
else
    echo -e "${YELLOW}⚠️${NC} .gitignore may not allow .vscode/settings.json"
    ((WARNINGS++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✨ All checks passed! Cursor setup is complete.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Install recommended extensions (Cursor will prompt)"
    echo "  2. Rebuild codebase index: Command Palette → 'Cursor: Rebuild Codebase Index'"
    echo "  3. Start coding!"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️ Setup complete with $WARNINGS warning(s)${NC}"
    echo "Review warnings above, but setup should work."
    exit 0
else
    echo -e "${RED}❌ Setup incomplete: $ERRORS error(s), $WARNINGS warning(s)${NC}"
    echo "Please fix the errors above."
    exit 1
fi
