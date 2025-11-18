#!/bin/bash
# Install systemd service for Argo Trading Engine
# This provides process management and auto-recovery

set -e

echo "🔧 Installing Argo Trading Engine systemd service"
echo "=================================================="

# Determine script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SERVICE_FILE="$WORKSPACE_ROOT/infrastructure/systemd/argo-trading.service"
SYSTEMD_PATH="/etc/systemd/system/argo-trading.service"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Copy service file
if [ -f "$SERVICE_FILE" ]; then
    cp "$SERVICE_FILE" "$SYSTEMD_PATH"
    echo "✅ Service file copied to $SYSTEMD_PATH"
else
    echo "❌ Service file not found: $SERVICE_FILE"
    echo "   Looking in: $WORKSPACE_ROOT"
    exit 1
fi

# Copy helper scripts
HELPER_SCRIPTS_DIR="$WORKSPACE_ROOT/infrastructure/systemd"
if [ -d "$HELPER_SCRIPTS_DIR" ]; then
    # Ensure helper scripts are executable
    chmod +x "$HELPER_SCRIPTS_DIR/wait-for-dependencies.sh" 2>/dev/null || true
    chmod +x "$HELPER_SCRIPTS_DIR/verify-service-health.sh" 2>/dev/null || true
    echo "✅ Helper scripts verified"
else
    echo "⚠️  Helper scripts directory not found: $HELPER_SCRIPTS_DIR"
    echo "   Service may fail if scripts are not accessible"
fi

# Reload systemd
systemctl daemon-reload
echo "✅ Systemd daemon reloaded"

# Enable service (start on boot)
systemctl enable argo-trading.service
echo "✅ Service enabled (will start on boot)"

# Validate service file syntax
echo ""
echo "🔍 Validating service file syntax..."
systemd-analyze verify argo-trading.service 2>&1 || {
    echo "⚠️  Service file validation warnings (may be non-critical)"
}

# Check if service is already running
if systemctl is-active --quiet argo-trading.service; then
    echo "⚠️  Service is already running. Restarting..."
    systemctl restart argo-trading.service
else
    echo "🚀 Starting service..."
    systemctl start argo-trading.service
fi

# Wait a moment and check status
sleep 3
if systemctl is-active --quiet argo-trading.service; then
    echo "✅ Service is running"
    systemctl status argo-trading.service --no-pager -l
    
    # Additional verification: check if port is listening
    echo ""
    echo "🔍 Verifying service is listening on port 8000..."
    sleep 2
    if lsof -ti :8000 >/dev/null 2>&1; then
        echo "✅ Service is listening on port 8000"
    else
        echo "⚠️  Service is running but not listening on port 8000 yet"
    fi
else
    echo "❌ Service failed to start"
    systemctl status argo-trading.service --no-pager -l
    echo ""
    echo "📋 Checking logs for errors..."
    journalctl -u argo-trading.service -n 20 --no-pager
    exit 1
fi

echo ""
echo "📋 Useful commands:"
echo "   sudo systemctl status argo-trading"
echo "   sudo systemctl restart argo-trading"
echo "   sudo systemctl stop argo-trading"
echo "   sudo systemctl start argo-trading"
echo "   sudo journalctl -u argo-trading -f"

