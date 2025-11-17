#!/bin/bash

# Install Cursor Recommended Extensions Script
# Installs all recommended extensions from .vscode/extensions.json

set -e

echo "🔌 Installing Cursor Recommended Extensions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if 'cursor' command is available
if ! command -v cursor &> /dev/null; then
    echo -e "${YELLOW}⚠️  'cursor' command not found. Trying 'code' command instead...${NC}"
    if ! command -v code &> /dev/null; then
        echo -e "${RED}❌ Neither 'cursor' nor 'code' command found.${NC}"
        echo "Please install Cursor CLI or VS Code CLI first."
        echo ""
        echo "For Cursor:"
        echo "  1. Open Cursor"
        echo "  2. Command Palette: Cmd+Shift+P → 'Shell Command: Install cursor command in PATH'"
        exit 1
    fi
    CMD="code"
else
    CMD="cursor"
fi

echo -e "${GREEN}✅ Using command: $CMD${NC}"
echo ""

# List of recommended extensions
EXTENSIONS=(
    # Python
    "ms-python.python"
    "ms-python.vscode-pylance"
    "ms-python.black-formatter"
    "ms-python.isort"
    "ms-python.debugpy"

    # TypeScript/JavaScript
    "dbaeumer.vscode-eslint"
    "esbenp.prettier-vscode"
    "bradlc.vscode-tailwindcss"

    # React/Next.js
    "dsznajder.es7-react-js-snippets"
    "formulahendry.auto-rename-tag"

    # Docker
    "ms-azuretools.vscode-docker"

    # Git
    "eamodio.gitlens"
    "mhutchie.git-graph"

    # Markdown
    "yzhang.markdown-all-in-one"
    "davidanson.vscode-markdownlint"

    # YAML
    "redhat.vscode-yaml"

    # Database
    "cweijan.vscode-postgresql-client2"

    # Testing
    "ms-python.pytest"
    "orta.vscode-jest"

    # Utilities
    "editorconfig.editorconfig"
    "ms-vscode.vscode-json"
    "usernamehw.errorlens"
    "streetsidesoftware.code-spell-checker"

    # Cursor (if available)
    "cursor.cursor-ai"
)

INSTALLED=0
FAILED=0
SKIPPED=0

echo "📦 Installing extensions..."
echo ""

for ext in "${EXTENSIONS[@]}"; do
    echo -n "  Installing $ext... "

    # Check if extension is already installed
    if $CMD --list-extensions | grep -q "^${ext}$"; then
        echo -e "${YELLOW}⏭️  Already installed${NC}"
        ((SKIPPED++))
    else
        # Install extension
        if $CMD --install-extension "$ext" --force > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Installed${NC}"
            ((INSTALLED++))
        else
            echo -e "${RED}❌ Failed${NC}"
            ((FAILED++))
        fi
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Installation Summary:"
echo -e "  ${GREEN}✅ Installed: $INSTALLED${NC}"
echo -e "  ${YELLOW}⏭️  Skipped (already installed): $SKIPPED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "  ${RED}❌ Failed: $FAILED${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✨ All extensions installed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Reload Cursor window (Cmd+R / Ctrl+R)"
    echo "  2. Verify extensions are working"
    echo "  3. Run: ./scripts/cursor-check-extensions.sh"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some extensions failed to install.${NC}"
    echo "You may need to install them manually or check your internet connection."
    exit 1
fi
