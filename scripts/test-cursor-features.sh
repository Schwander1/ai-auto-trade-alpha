#!/bin/bash

# Test Cursor Features Script
# Verifies that Cursor features are working correctly

set -e

echo "🧪 Testing Cursor Features"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Test 1: Check extensions are installed
echo -e "${BLUE}📦 Test 1: Checking Extensions${NC}"
echo ""

REQUIRED_EXTENSIONS=(
    "ms-python.python"
    "ms-python.vscode-pylance"
    "ms-python.black-formatter"
    "dbaeumer.vscode-eslint"
    "esbenp.prettier-vscode"
)

for ext in "${REQUIRED_EXTENSIONS[@]}"; do
    if code --list-extensions 2>/dev/null | grep -q "^${ext}$"; then
        echo -e "  ${GREEN}✅${NC} $ext"
        ((PASSED++))
    else
        echo -e "  ${RED}❌${NC} $ext (not installed)"
        ((FAILED++))
    fi
done

echo ""

# Test 2: Check configuration files
echo -e "${BLUE}⚙️  Test 2: Checking Configuration Files${NC}"
echo ""

CONFIG_FILES=(
    ".cursor/settings.json"
    ".vscode/settings.json"
    ".vscode/extensions.json"
    ".prettierrc.json"
    ".editorconfig"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✅${NC} $file"
        ((PASSED++))
    else
        echo -e "  ${RED}❌${NC} $file (missing)"
        ((FAILED++))
    fi
done

echo ""

# Test 3: Check test files exist
echo -e "${BLUE}📝 Test 3: Checking Test Files${NC}"
echo ""

TEST_FILES=(
    ".cursor-test/test-formatting.py"
    ".cursor-test/test-formatting.tsx"
    ".cursor-test/test-snippets.py"
    ".cursor-test/test-snippets.tsx"
)

for file in "${TEST_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✅${NC} $file"
        ((PASSED++))
    else
        echo -e "  ${YELLOW}⚠️${NC}  $file (not found, will create)"
    fi
done

echo ""

# Test 4: Check Python formatter (Black)
echo -e "${BLUE}🐍 Test 4: Checking Python Formatter${NC}"
echo ""

if command -v black &> /dev/null; then
    echo -e "  ${GREEN}✅${NC} Black formatter installed"
    ((PASSED++))
else
    echo -e "  ${YELLOW}⚠️${NC}  Black formatter not in PATH (may be in venv)"
fi

echo ""

# Test 5: Check Prettier
echo -e "${BLUE}💅 Test 5: Checking Prettier${NC}"
echo ""

if command -v prettier &> /dev/null || [ -f "node_modules/.bin/prettier" ]; then
    echo -e "  ${GREEN}✅${NC} Prettier available"
    ((PASSED++))
else
    echo -e "  ${YELLOW}⚠️${NC}  Prettier not in PATH (may be in node_modules)"
fi

echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Test Results:"
echo -e "  ${GREEN}✅ Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "  ${RED}❌ Failed: $FAILED${NC}"
fi
echo ""

# Manual testing instructions
echo -e "${BLUE}📋 Manual Testing Instructions:${NC}"
echo ""
echo "1. ${GREEN}Test Format-on-Save:${NC}"
echo "   • Open .cursor-test/test-formatting.py"
echo "   • Make a small change"
echo "   • Save the file (Cmd+S / Ctrl+S)"
echo "   • Code should auto-format"
echo ""
echo "2. ${GREEN}Test Code Snippets:${NC}"
echo "   • Open .cursor-test/test-snippets.py"
echo "   • Type 'fastapi-route' and press Tab"
echo "   • Should expand to FastAPI route template"
echo ""
echo "3. ${GREEN}Test AI Assistance:${NC}"
echo "   • Press Cmd+I (Mac) or Ctrl+I (Windows/Linux)"
echo "   • Ask: 'What does this function do?'"
echo "   • Should get helpful response"
echo ""
echo "4. ${GREEN}Test Auto-Imports:${NC}"
echo "   • Type a function name like 'json.loads'"
echo "   • Should suggest importing json module"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✨ All automated tests passed!${NC}"
    echo "Follow the manual testing instructions above to verify features."
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed.${NC}"
    echo "Please check the failed items above."
    exit 1
fi
