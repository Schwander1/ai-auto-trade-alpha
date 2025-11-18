#!/bin/bash
# Fix systemd service files to use correct Python and paths with dependency management
# This script uses the updated service files from infrastructure/systemd

set -e

echo "🔧 Fixing systemd service files..."
echo ""

# Determine script location and workspace root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if updated service files exist
ARGO_SERVICE_FILE="$WORKSPACE_ROOT/infrastructure/systemd/argo-trading.service"
PROP_SERVICE_FILE="$WORKSPACE_ROOT/infrastructure/systemd/argo-trading-prop-firm.service"

# Check for venv
ARGO_VENV="/root/argo-production-green/venv/bin"
PROP_VENV="/root/argo-production-prop-firm/venv/bin"

# Determine Python path
if [ -f "$ARGO_VENV/python3" ]; then
    ARGO_PYTHON="$ARGO_VENV/python3"
    echo "✅ Found Argo venv: $ARGO_PYTHON"
else
    ARGO_PYTHON="/usr/bin/python3"
    echo "⚠️  Using system Python for Argo"
fi

if [ -f "$PROP_VENV/python3" ]; then
    PROP_PYTHON="$PROP_VENV/python3"
    echo "✅ Found Prop Firm venv: $PROP_PYTHON"
else
    PROP_PYTHON="/usr/bin/python3"
    echo "⚠️  Using system Python for Prop Firm"
fi

# Create logs directories
mkdir -p /root/argo-production-green/logs
mkdir -p /root/argo-production-prop-firm/logs

# Use updated service files if available, otherwise create improved ones
if [ -f "$ARGO_SERVICE_FILE" ] && [ -f "$PROP_SERVICE_FILE" ]; then
    echo "✅ Found updated service files with dependency management"
    echo ""
    
    # Copy service files
    echo "📝 Installing updated Argo service..."
    sudo cp "$ARGO_SERVICE_FILE" /etc/systemd/system/argo-trading.service
    echo "✅ Installed: argo-trading.service"
    
    echo "📝 Installing updated Prop Firm service..."
    sudo cp "$PROP_SERVICE_FILE" /etc/systemd/system/argo-trading-prop-firm.service
    echo "✅ Installed: argo-trading-prop-firm.service"
    
else
    echo "⚠️  Updated service files not found, creating improved service files"
    echo ""
    
    # Fix Argo service with improved settings
    echo "📝 Updating Argo service..."
    sudo tee /etc/systemd/system/argo-trading.service > /dev/null <<EOF
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
ExecStart=$ARGO_PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 30
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
    
    # Fix Prop Firm service with improved settings
    echo "📝 Updating Prop Firm service..."
    sudo tee /etc/systemd/system/argo-trading-prop-firm.service > /dev/null <<EOF
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
ExecStart=$PROP_PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8001 --workers 1 --timeout-keep-alive 30
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
fi

echo "✅ Service files updated"
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
echo "✅ Done!"
echo ""
echo "Now restart services:"
echo "  sudo systemctl restart argo-trading.service"
echo "  sudo systemctl restart argo-trading-prop-firm.service"

