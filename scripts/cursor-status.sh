#!/bin/bash

# Cursor Status Check Script
# Quick status check of Cursor setup and configuration

set -e

echo "📊 Cursor Workspace Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check configuration files
echo -e "${BLUE}📁 Configuration Files:${NC}"
echo ""

CONFIG_FILES=(
  ".cursor/settings.json"
  ".cursorignore"
  ".vscode/settings.json"
  ".vscode/extensions.json"
  ".vscode/tasks.json"
  ".vscode/launch.json"
  ".prettierrc.json"
  ".editorconfig"
)

for file in "${CONFIG_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo -e "  ${GREEN}✅${NC} $file"
  else
    echo -e "  ${RED}❌${NC} $file (missing)"
  fi
done

echo ""

# Check snippets
echo -e "${BLUE}📝 Code Snippets:${NC}"
echo ""

if [ -f ".vscode/snippets/python.json" ]; then
  PYTHON_SNIPPETS=$(grep -c '"prefix"' .vscode/snippets/python.json 2>/dev/null || echo "0")
  echo -e "  ${GREEN}✅${NC} Python snippets ($PYTHON_SNIPPETS snippets)"
else
  echo -e "  ${RED}❌${NC} Python snippets (missing)"
fi

if [ -f ".vscode/snippets/typescript.json" ]; then
  TS_SNIPPETS=$(grep -c '"prefix"' .vscode/snippets/typescript.json 2>/dev/null || echo "0")
  echo -e "  ${GREEN}✅${NC} TypeScript snippets ($TS_SNIPPETS snippets)"
else
  echo -e "  ${RED}❌${NC} TypeScript snippets (missing)"
fi

echo ""

# Check helper scripts
echo -e "${BLUE}🛠️  Helper Scripts:${NC}"
echo ""

SCRIPTS=(
  "scripts/verify-cursor-setup.sh"
  "scripts/cursor-rebuild-index.sh"
  "scripts/cursor-check-extensions.sh"
  "scripts/cursor-status.sh"
)

for script in "${SCRIPTS[@]}"; do
  if [ -f "$script" ] && [ -x "$script" ]; then
    echo -e "  ${GREEN}✅${NC} $script (executable)"
  elif [ -f "$script" ]; then
    echo -e "  ${YELLOW}⚠️${NC}  $script (not executable)"
  else
    echo -e "  ${RED}❌${NC} $script (missing)"
  fi
done

echo ""

# Check documentation
echo -e "${BLUE}📚 Documentation:${NC}"
echo ""

DOCS=(
  "docs/CURSOR_QUICK_START.md"
  "docs/CURSOR_OPTIMIZATION_COMPLETE.md"
  "docs/CURSOR_FINAL_SETUP.md"
  "docs/CURSOR_ONBOARDING_CHECKLIST.md"
  "CURSOR_SETUP_SUMMARY.md"
)

for doc in "${DOCS[@]}"; do
  if [ -f "$doc" ]; then
    echo -e "  ${GREEN}✅${NC} $doc"
  else
    echo -e "  ${RED}❌${NC} $doc (missing)"
  fi
done

echo ""

# File counts
echo -e "${BLUE}📊 Workspace Statistics:${NC}"
echo ""

PYTHON_FILES=$(find . -name "*.py" -not -path "*/node_modules/*" -not -path "*/venv/*" -not -path "*/__pycache__/*" -not -path "*/archive/*" -not -path "*/backups/*" 2>/dev/null | wc -l | tr -d ' ')
TS_FILES=$(find . -name "*.ts" -o -name "*.tsx" -not -path "*/node_modules/*" -not -path "*/dist/*" -not -path "*/archive/*" -not -path "*/backups/*" 2>/dev/null | wc -l | tr -d ' ')
MD_FILES=$(find . -name "*.md" -not -path "*/node_modules/*" -not -path "*/archive/*" -not -path "*/backups/*" 2>/dev/null | wc -l | tr -d ' ')

echo "  Python files: $PYTHON_FILES"
echo "  TypeScript files: $TS_FILES"
echo "  Markdown files: $MD_FILES"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Quick actions
echo -e "${BLUE}⚡ Quick Actions:${NC}"
echo ""
echo "  • Verify setup:     ./scripts/verify-cursor-setup.sh"
echo "  • Check extensions: ./scripts/cursor-check-extensions.sh"
echo "  • Index info:       ./scripts/cursor-rebuild-index.sh"
echo "  • This status:      ./scripts/cursor-status.sh"
echo ""

echo -e "${GREEN}✨ Status check complete!${NC}"
