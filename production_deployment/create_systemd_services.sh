#!/bin/bash
# Create systemd service files for dual trading with dependency management
# This script uses the updated service files from infrastructure/systemd

set -e

echo "🔧 Creating systemd service files for dual trading"
echo "=================================================="
echo ""

# Determine script location and workspace root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if updated service files exist
ARGO_SERVICE_FILE="$WORKSPACE_ROOT/infrastructure/systemd/argo-trading.service"
PROP_SERVICE_FILE="$WORKSPACE_ROOT/infrastructure/systemd/argo-trading-prop-firm.service"
WAIT_SCRIPT="$WORKSPACE_ROOT/infrastructure/systemd/wait-for-dependencies.sh"
HEALTH_SCRIPT="$WORKSPACE_ROOT/infrastructure/systemd/verify-service-health.sh"

# Use updated service files if available, otherwise create basic ones
if [ -f "$ARGO_SERVICE_FILE" ] && [ -f "$PROP_SERVICE_FILE" ]; then
    echo "✅ Found updated service files with dependency management"
    echo ""
    
    # Copy service files
    echo "📝 Installing Argo trading service..."
    sudo cp "$ARGO_SERVICE_FILE" /etc/systemd/system/argo-trading.service
    echo "✅ Installed: argo-trading.service"
    
    echo "📝 Installing Prop Firm trading service..."
    sudo cp "$PROP_SERVICE_FILE" /etc/systemd/system/argo-trading-prop-firm.service
    echo "✅ Installed: argo-trading-prop-firm.service"
    
    # Ensure helper scripts are executable and accessible
    if [ -f "$WAIT_SCRIPT" ]; then
        chmod +x "$WAIT_SCRIPT" 2>/dev/null || sudo chmod +x "$WAIT_SCRIPT"
        echo "✅ Helper script: wait-for-dependencies.sh"
    fi
    
    if [ -f "$HEALTH_SCRIPT" ]; then
        chmod +x "$HEALTH_SCRIPT" 2>/dev/null || sudo chmod +x "$HEALTH_SCRIPT"
        echo "✅ Helper script: verify-service-health.sh"
    fi
    
else
    echo "⚠️  Updated service files not found, creating basic service files"
    echo "   (For full dependency management, ensure infrastructure/systemd/ files are available)"
    echo ""
    
    # Fallback to basic service files
    ARGO_SERVICE="/etc/systemd/system/argo-trading.service"
    echo "Creating: $ARGO_SERVICE"
    
    sudo tee $ARGO_SERVICE > /dev/null <<EOF
[Unit]
Description=Argo Trading Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-green
Environment="PATH=/root/argo-production-green/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/root/argo-production-green"
Environment="ARGO_ENVIRONMENT=production"
Environment="ARGO_24_7_MODE=true"
Environment="ARGO_API_SECRET=988807abc6a05772fd1900bcbfd35b6037f4f3ba4656e99e78f67b1242041736"
Environment="REDIS_HOST=localhost"
Environment="REDIS_PORT=6379"
Environment="REDIS_PASSWORD="
ExecStart=/root/argo-production-green/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 30
Restart=always
RestartSec=30
StartLimitInterval=300
StartLimitBurst=5
StandardOutput=append:/tmp/argo-green.log
StandardError=append:/tmp/argo-green.log
SyslogIdentifier=argo-trading
NoNewPrivileges=true
PrivateTmp=true
LimitNOFILE=65536
MemoryMax=4G
MemoryHigh=3G
MemoryLimit=4G
CPUQuota=200%
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=60
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF
    
    echo "✅ Created Argo trading service"
    
    PROP_FIRM_SERVICE="/etc/systemd/system/argo-trading-prop-firm.service"
    echo "Creating: $PROP_FIRM_SERVICE"
    
    sudo tee $PROP_FIRM_SERVICE > /dev/null <<EOF
[Unit]
Description=Argo Prop Firm Trading Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-prop-firm
Environment="PATH=/root/argo-production-prop-firm/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/root/argo-production-prop-firm"
Environment="ARGO_ENVIRONMENT=production"
Environment="ARGO_24_7_MODE=true"
Environment="ARGO_API_SECRET=988807abc6a05772fd1900bcbfd35b6037f4f3ba4656e99e78f67b1242041736"
Environment="USE_AWS_SECRETS=true"
Environment="REDIS_HOST=localhost"
Environment="REDIS_PORT=6379"
Environment="REDIS_PASSWORD="
ExecStart=/root/argo-production-prop-firm/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001 --workers 1 --timeout-keep-alive 30
Restart=always
RestartSec=30
StartLimitInterval=300
StartLimitBurst=5
StandardOutput=append:/tmp/argo-prop-firm.log
StandardError=append:/tmp/argo-prop-firm.log
SyslogIdentifier=argo-trading-prop-firm
NoNewPrivileges=true
PrivateTmp=true
LimitNOFILE=65536
MemoryMax=4G
MemoryHigh=3G
MemoryLimit=4G
CPUQuota=200%
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=60
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF
    
    echo "✅ Created Prop Firm trading service"
fi

# Reload systemd
echo ""
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

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
echo "✅ Systemd services created!"
echo ""
echo "📋 Next steps:"
echo ""
echo "To start services:"
echo "  sudo systemctl start argo-trading.service"
echo "  sudo systemctl start argo-trading-prop-firm.service"
echo ""
echo "To enable on boot:"
echo "  sudo systemctl enable argo-trading.service"
echo "  sudo systemctl enable argo-trading-prop-firm.service"
echo ""
echo "To check status:"
echo "  sudo systemctl status argo-trading.service"
echo "  sudo systemctl status argo-trading-prop-firm.service"
echo ""

