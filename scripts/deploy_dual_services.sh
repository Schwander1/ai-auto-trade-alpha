#!/bin/bash
# Deploy Dual Services Script
# Deploys both regular Argo service and prop firm service to production

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Configuration
PRODUCTION_SERVER="178.156.194.174"
PRODUCTION_USER="root"
REGULAR_DIR="/root/argo-production-green"
PROP_FIRM_DIR="/root/argo-production-prop-firm"
REGULAR_PORT=8000
PROP_FIRM_PORT=8001

echo "🚀 Deploying Dual Services to Production"
echo "========================================="
echo ""
echo "Regular Service: Port ${REGULAR_PORT}"
echo "Prop Firm Service: Port ${PROP_FIRM_PORT}"
echo ""

# Run pre-deployment validation
echo "Step 1: Running pre-deployment validation..."
if ! "${SCRIPT_DIR}/pre_deployment_validation.sh"; then
    echo "❌ Pre-deployment validation failed. Aborting."
    exit 1
fi
echo ""

# Check if we're deploying from local
if [ ! -d "/root/argo-production" ]; then
    echo "📦 Preparing deployment package..."
    # This would typically involve creating a tarball or using git
    echo "   (Local deployment - ensure code is committed and pushed)"
fi

# Deploy regular service
echo "Step 2: Deploying Regular Service..."
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Create directory if it doesn't exist
mkdir -p ${REGULAR_DIR}

# Clone or update code (adjust based on your deployment method)
# For now, assuming code is already there or will be deployed via git

# Ensure config has prop_firm.enabled = false
if [ -f ${REGULAR_DIR}/config.json ]; then
    python3 << PYTHON
import json
with open('${REGULAR_DIR}/config.json', 'r') as f:
    config = json.load(f)
if 'prop_firm' not in config:
    config['prop_firm'] = {}
config['prop_firm']['enabled'] = False
with open('${REGULAR_DIR}/config.json', 'w') as f:
    json.dump(config, f, indent=2)
PYTHON
    echo "✅ Regular service config updated (prop_firm.enabled = false)"
fi

# Install/update dependencies
if [ -d ${REGULAR_DIR}/venv ]; then
    source ${REGULAR_DIR}/venv/bin/activate
    pip install -q -r ${REGULAR_DIR}/requirements.txt 2>/dev/null || echo "⚠️  Requirements install skipped"
fi

# Install systemd service
if [ -f ${REGULAR_DIR}/../infrastructure/systemd/argo-trading.service ]; then
    cp ${REGULAR_DIR}/../infrastructure/systemd/argo-trading.service /etc/systemd/system/
    systemctl daemon-reload
    echo "✅ Regular service file installed"
fi

# Restart service
systemctl restart argo-trading.service || systemctl start argo-trading.service
echo "✅ Regular service started/restarted"

# Check status
sleep 2
if systemctl is-active --quiet argo-trading.service; then
    echo "✅ Regular service is running"
else
    echo "❌ Regular service failed to start"
    systemctl status argo-trading.service --no-pager -l
    exit 1
fi
ENDSSH

echo ""

# Deploy prop firm service
echo "Step 3: Deploying Prop Firm Service..."
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Create directory if it doesn't exist
mkdir -p ${PROP_FIRM_DIR}

# Clone or update code (adjust based on your deployment method)
# For now, assuming code is already there or will be deployed via git

# Ensure config has prop_firm.enabled = true
if [ -f ${PROP_FIRM_DIR}/config.json ]; then
    python3 << PYTHON
import json
with open('${PROP_FIRM_DIR}/config.json', 'r') as f:
    config = json.load(f)
if 'prop_firm' not in config:
    config['prop_firm'] = {}
config['prop_firm']['enabled'] = True
with open('${PROP_FIRM_DIR}/config.json', 'w') as f:
    json.dump(config, f, indent=2)
PYTHON
    echo "✅ Prop firm service config updated (prop_firm.enabled = true)"
fi

# Install/update dependencies
if [ -d ${PROP_FIRM_DIR}/venv ]; then
    source ${PROP_FIRM_DIR}/venv/bin/activate
    pip install -q -r ${PROP_FIRM_DIR}/requirements.txt 2>/dev/null || echo "⚠️  Requirements install skipped"
fi

# Install systemd service
if [ -f ${PROP_FIRM_DIR}/../infrastructure/systemd/argo-trading-prop-firm.service ]; then
    cp ${PROP_FIRM_DIR}/../infrastructure/systemd/argo-trading-prop-firm.service /etc/systemd/system/
    systemctl daemon-reload
    echo "✅ Prop firm service file installed"
fi

# Restart service
systemctl restart argo-trading-prop-firm.service || systemctl start argo-trading-prop-firm.service
echo "✅ Prop firm service started/restarted"

# Check status
sleep 2
if systemctl is-active --quiet argo-trading-prop-firm.service; then
    echo "✅ Prop firm service is running"
else
    echo "❌ Prop firm service failed to start"
    systemctl status argo-trading-prop-firm.service --no-pager -l
    exit 1
fi
ENDSSH

echo ""

# Verify both services
echo "Step 4: Verifying Services..."
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
echo "Checking Regular Service (Port ${REGULAR_PORT})..."
if curl -s http://localhost:${REGULAR_PORT}/api/v1/health > /dev/null 2>&1; then
    echo "✅ Regular service health check passed"
else
    echo "❌ Regular service health check failed"
    exit 1
fi

echo "Checking Prop Firm Service (Port ${PROP_FIRM_PORT})..."
if curl -s http://localhost:${PROP_FIRM_PORT}/api/v1/health > /dev/null 2>&1; then
    echo "✅ Prop firm service health check passed"
else
    echo "❌ Prop firm service health check failed"
    exit 1
fi

echo ""
echo "Service Status:"
systemctl status argo-trading.service --no-pager -l | head -5
echo ""
systemctl status argo-trading-prop-firm.service --no-pager -l | head -5
ENDSSH

echo ""
echo "============================"
echo "✅ Deployment Complete!"
echo "============================"
echo ""
echo "Regular Service: http://${PRODUCTION_SERVER}:${REGULAR_PORT}"
echo "Prop Firm Service: http://${PRODUCTION_SERVER}:${PROP_FIRM_PORT}"
echo ""
echo "To check logs:"
echo "  Regular: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'tail -f /tmp/argo-green.log'"
echo "  Prop Firm: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'tail -f /tmp/argo-prop-firm.log'"
echo ""

