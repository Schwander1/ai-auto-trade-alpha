#!/bin/bash
# Enable 24/7 Mode Permanently
# Sets environment variable and updates configuration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ARGO_DIR="$WORKSPACE_ROOT/argo"

echo "🔧 Enabling 24/7 Mode Permanently..."
echo ""

# 1. Add to shell profile
SHELL_PROFILE=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_PROFILE="$HOME/.bash_profile"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_PROFILE="$HOME/.bashrc"
fi

if [ -n "$SHELL_PROFILE" ]; then
    if ! grep -q "ARGO_24_7_MODE" "$SHELL_PROFILE"; then
        echo "" >> "$SHELL_PROFILE"
        echo "# Argo Trading - 24/7 Mode" >> "$SHELL_PROFILE"
        echo "export ARGO_24_7_MODE=true" >> "$SHELL_PROFILE"
        echo "✅ Added ARGO_24_7_MODE=true to $SHELL_PROFILE"
    else
        echo "✅ ARGO_24_7_MODE already in $SHELL_PROFILE"
        # Update if set to false
        sed -i.bak 's/export ARGO_24_7_MODE=.*/export ARGO_24_7_MODE=true/' "$SHELL_PROFILE"
        echo "✅ Updated ARGO_24_7_MODE to true in $SHELL_PROFILE"
    fi
else
    echo "⚠️  Could not find shell profile, creating .argo_env file"
    echo "export ARGO_24_7_MODE=true" > "$HOME/.argo_env"
    echo "   Source it with: source ~/.argo_env"
fi

# 2. Set for current session
export ARGO_24_7_MODE=true
echo "✅ Set ARGO_24_7_MODE=true for current session"

# 3. Create .env file in argo directory
if [ -f "$ARGO_DIR/.env" ]; then
    if ! grep -q "ARGO_24_7_MODE" "$ARGO_DIR/.env"; then
        echo "ARGO_24_7_MODE=true" >> "$ARGO_DIR/.env"
        echo "✅ Added ARGO_24_7_MODE to $ARGO_DIR/.env"
    else
        sed -i.bak 's/ARGO_24_7_MODE=.*/ARGO_24_7_MODE=true/' "$ARGO_DIR/.env"
        echo "✅ Updated ARGO_24_7_MODE in $ARGO_DIR/.env"
    fi
else
    echo "ARGO_24_7_MODE=true" > "$ARGO_DIR/.env"
    echo "✅ Created $ARGO_DIR/.env with ARGO_24_7_MODE=true"
fi

echo ""
echo "✅ 24/7 Mode enabled permanently!"
echo ""
echo "Changes will take effect:"
echo "  - For new terminal sessions: Immediately"
echo "  - For current session: Run 'source $SHELL_PROFILE' or restart terminal"
echo "  - For running services: Restart the services"
echo ""
echo "To verify:"
echo "  echo \$ARGO_24_7_MODE"
