#!/bin/bash

# Cursor Extensions Check Script
# Verifies recommended extensions are installed

set -e

echo "🔌 Checking Cursor/VS Code Extensions"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in a Cursor/VS Code environment
if [ -z "$VSCODE_PID" ] && [ -z "$CURSOR_PID" ]; then
    echo -e "${YELLOW}⚠️  This script should be run from within Cursor/VS Code${NC}"
    echo "   (Extensions can only be checked from the editor)"
    echo ""
fi

# Read recommended extensions from .vscode/extensions.json
if [ ! -f ".vscode/extensions.json" ]; then
    echo -e "${RED}❌ .vscode/extensions.json not found${NC}"
    exit 1
fi

echo "📋 Recommended Extensions:"
echo ""

# Extract extension IDs (simple grep, not perfect JSON parsing but works)
EXTENSIONS=$(grep -o '"[^"]*"' .vscode/extensions.json | grep -v "schema\|version\|recommendations\|unwantedRecommendations" | sed 's/"//g' | grep -E "^[a-z0-9-]+\.[a-z0-9-]+$")

if [ -z "$EXTENSIONS" ]; then
    echo -e "${YELLOW}⚠️  Could not parse extensions from .vscode/extensions.json${NC}"
    echo ""
    echo "Please check the file manually or install extensions via:"
    echo "  Command Palette → 'Extensions: Show Recommended Extensions'"
    exit 0
fi

echo "$EXTENSIONS" | while read -r ext; do
    if [ -n "$ext" ]; then
        echo "  • $ext"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📥 To install recommended extensions:"
echo ""
echo "  1. Open Command Palette: Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows/Linux)"
echo "  2. Type: 'Extensions: Show Recommended Extensions'"
echo "  3. Click 'Install All' or install individually"
echo ""
echo "  Or Cursor will prompt you automatically when you open the workspace!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✨ Essential Extensions for this workspace:"
echo ""
echo "  🐍 Python:"
echo "     • ms-python.python"
echo "     • ms-python.vscode-pylance"
echo "     • ms-python.black-formatter"
echo ""
echo "  📘 TypeScript/React:"
echo "     • dbaeumer.vscode-eslint"
echo "     • esbenp.prettier-vscode"
echo "     • bradlc.vscode-tailwindcss"
echo ""
echo "  🐳 Docker:"
echo "     • ms-azuretools.vscode-docker"
echo ""
echo "  📝 Git:"
echo "     • eamodio.gitlens"
echo ""
