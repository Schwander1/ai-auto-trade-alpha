#!/bin/bash
# Install systemd services with proper dependency management
# This script copies service files and ensures helper scripts are in place

set -e

# Determine script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

echo "🔧 Installing Argo systemd services with dependency management"
echo "=============================================================="
echo ""

# Ensure helper scripts are executable
echo "📝 Setting up helper scripts..."
chmod +x "$SCRIPT_DIR/wait-for-dependencies.sh"
chmod +x "$SCRIPT_DIR/verify-service-health.sh"
echo "✅ Helper scripts are executable"

# Copy service files
echo ""
echo "📝 Installing service files..."

# Argo Trading Service
ARGO_SERVICE="$SCRIPT_DIR/argo-trading.service"
ARGO_SYSTEMD="/etc/systemd/system/argo-trading.service"
if [ -f "$ARGO_SERVICE" ]; then
    cp "$ARGO_SERVICE" "$ARGO_SYSTEMD"
    echo "✅ Installed: argo-trading.service"
else
    echo "⚠️  Service file not found: $ARGO_SERVICE"
fi

# Argo Prop Firm Service
PROP_SERVICE="$SCRIPT_DIR/argo-trading-prop-firm.service"
PROP_SYSTEMD="/etc/systemd/system/argo-trading-prop-firm.service"
if [ -f "$PROP_SERVICE" ]; then
    cp "$PROP_SERVICE" "$PROP_SYSTEMD"
    echo "✅ Installed: argo-trading-prop-firm.service"
else
    echo "⚠️  Service file not found: $PROP_SERVICE"
fi

# Reload systemd
echo ""
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload
echo "✅ Systemd daemon reloaded"

# Validate service files
echo ""
echo "🔍 Validating service files..."
systemd-analyze verify argo-trading.service 2>&1 || {
    echo "⚠️  argo-trading.service validation warnings (may be non-critical)"
}
systemd-analyze verify argo-trading-prop-firm.service 2>&1 || {
    echo "⚠️  argo-trading-prop-firm.service validation warnings (may be non-critical)"
}

echo ""
echo "✅ Service installation complete!"
echo ""
echo "📋 Next steps:"
echo "   To enable services on boot:"
echo "     sudo systemctl enable argo-trading.service"
echo "     sudo systemctl enable argo-trading-prop-firm.service"
echo ""
echo "   To start services:"
echo "     sudo systemctl start argo-trading.service"
echo "     sudo systemctl start argo-trading-prop-firm.service"
echo ""
echo "   To check status:"
echo "     sudo systemctl status argo-trading.service"
echo "     sudo systemctl status argo-trading-prop-firm.service"
echo ""

