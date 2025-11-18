#!/bin/bash
# Setup production dependencies and helper scripts
# This ensures all dependency checking utilities are available on production server

set -e

echo "🔧 Setting up production dependencies and helper scripts"
echo "========================================================"
echo ""

# Determine script location and workspace root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Create production scripts directory
PROD_SCRIPTS_DIR="/root/argo-alpine-workspace/infrastructure/systemd"
sudo mkdir -p "$PROD_SCRIPTS_DIR"

# Copy helper scripts to production location
echo "📝 Installing helper scripts..."

# Copy wait-for-dependencies.sh
if [ -f "$WORKSPACE_ROOT/infrastructure/systemd/wait-for-dependencies.sh" ]; then
    sudo cp "$WORKSPACE_ROOT/infrastructure/systemd/wait-for-dependencies.sh" "$PROD_SCRIPTS_DIR/"
    sudo chmod +x "$PROD_SCRIPTS_DIR/wait-for-dependencies.sh"
    echo "✅ Installed: wait-for-dependencies.sh"
else
    echo "⚠️  wait-for-dependencies.sh not found in workspace"
fi

# Copy verify-service-health.sh
if [ -f "$WORKSPACE_ROOT/infrastructure/systemd/verify-service-health.sh" ]; then
    sudo cp "$WORKSPACE_ROOT/infrastructure/systemd/verify-service-health.sh" "$PROD_SCRIPTS_DIR/"
    sudo chmod +x "$PROD_SCRIPTS_DIR/verify-service-health.sh"
    echo "✅ Installed: verify-service-health.sh"
else
    echo "⚠️  verify-service-health.sh not found in workspace"
fi

# Also copy to alternative location for scripts/lib
PROD_LIB_DIR="/root/argo-alpine-workspace/scripts/lib"
sudo mkdir -p "$PROD_LIB_DIR"

if [ -f "$WORKSPACE_ROOT/scripts/lib/wait-for-dependencies.sh" ]; then
    sudo cp "$WORKSPACE_ROOT/scripts/lib/wait-for-dependencies.sh" "$PROD_LIB_DIR/"
    sudo chmod +x "$PROD_LIB_DIR/wait-for-dependencies.sh"
    echo "✅ Installed: scripts/lib/wait-for-dependencies.sh"
fi

echo ""
echo "✅ Production dependencies setup complete!"
echo ""
echo "Helper scripts are now available at:"
echo "  - $PROD_SCRIPTS_DIR/wait-for-dependencies.sh"
echo "  - $PROD_SCRIPTS_DIR/verify-service-health.sh"
if [ -f "$PROD_LIB_DIR/wait-for-dependencies.sh" ]; then
    echo "  - $PROD_LIB_DIR/wait-for-dependencies.sh"
fi
echo ""

