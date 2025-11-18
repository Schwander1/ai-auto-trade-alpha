#!/bin/bash
# Complete Prop Firm Deployment Script
# Deploys code and configures both regular and prop firm services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ARGO_DIR="${WORKSPACE_DIR}/argo"

# Configuration
PRODUCTION_SERVER="178.156.194.174"
PRODUCTION_USER="root"
REGULAR_DIR="/root/argo-production-green"
PROP_FIRM_DIR="/root/argo-production-prop-firm"
REGULAR_PORT=8000
PROP_FIRM_PORT=8001

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Step 1: Pre-deployment validation
print_step "STEP 1: PRE-DEPLOYMENT VALIDATION"
if ! "${SCRIPT_DIR}/pre_deployment_validation.sh"; then
    print_error "Pre-deployment validation failed. Aborting."
    exit 1
fi

# Step 2: Deploy code to regular service
print_step "STEP 2: DEPLOYING CODE TO REGULAR SERVICE"
print_info "Syncing code to ${REGULAR_DIR}..."

rsync -avz --delete \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='*.db' \
    --exclude='backups' \
    --exclude='config.json' \
    "${ARGO_DIR}/" ${PRODUCTION_USER}@${PRODUCTION_SERVER}:${REGULAR_DIR}/

print_success "Code synced to regular service directory"

# Step 3: Configure regular service
print_step "STEP 3: CONFIGURING REGULAR SERVICE"
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

cd ${REGULAR_DIR}

# Ensure config has prop_firm.enabled = false
if [ -f config.json ]; then
    python3 << PYTHON
import json
with open('config.json', 'r') as f:
    config = json.load(f)
if 'prop_firm' not in config:
    config['prop_firm'] = {}
config['prop_firm']['enabled'] = False
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)
PYTHON
    echo "✅ Regular service config updated (prop_firm.enabled = false)"
else
    echo "⚠️  config.json not found - will need to be created manually"
fi

# Install/update dependencies
if [ -d venv ]; then
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel -q
    pip install -q -r requirements.txt 2>&1 | grep -v "WARNING" || echo "⚠️  Some dependencies may have issues"
else
    echo "⚠️  Virtual environment not found - creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel -q
    pip install -q -r requirements.txt 2>&1 | grep -v "WARNING" || echo "⚠️  Some dependencies may have issues"
fi

# Install systemd service
if [ -f ../infrastructure/systemd/argo-trading.service ]; then
    cp ../infrastructure/systemd/argo-trading.service /etc/systemd/system/
    systemctl daemon-reload
    echo "✅ Regular service file installed"
elif [ -f infrastructure/systemd/argo-trading.service ]; then
    cp infrastructure/systemd/argo-trading.service /etc/systemd/system/
    systemctl daemon-reload
    echo "✅ Regular service file installed"
else
    echo "⚠️  Service file not found - will need manual installation"
fi
ENDSSH

# Step 4: Deploy code to prop firm service
print_step "STEP 4: DEPLOYING CODE TO PROP FIRM SERVICE"
print_info "Syncing code to ${PROP_FIRM_DIR}..."

# Ensure directory exists
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "mkdir -p ${PROP_FIRM_DIR}"

rsync -avz --delete \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='*.db' \
    --exclude='backups' \
    --exclude='config.json' \
    "${ARGO_DIR}/" ${PRODUCTION_USER}@${PRODUCTION_SERVER}:${PROP_FIRM_DIR}/

print_success "Code synced to prop firm service directory"

# Step 5: Configure prop firm service
print_step "STEP 5: CONFIGURING PROP FIRM SERVICE"
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

cd ${PROP_FIRM_DIR}

# Copy config.json from regular service if it doesn't exist
if [ ! -f config.json ] && [ -f ${REGULAR_DIR}/config.json ]; then
    cp ${REGULAR_DIR}/config.json config.json
    echo "✅ Copied config.json from regular service"
fi

# Ensure config has prop_firm.enabled = true
if [ -f config.json ]; then
    python3 << PYTHON
import json
with open('config.json', 'r') as f:
    config = json.load(f)
if 'prop_firm' not in config:
    config['prop_firm'] = {}
config['prop_firm']['enabled'] = True
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)
PYTHON
    echo "✅ Prop firm service config updated (prop_firm.enabled = true)"
else
    echo "⚠️  config.json not found - will need to be created manually"
fi

# Install/update dependencies
if [ -d venv ]; then
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel -q
    pip install -q -r requirements.txt 2>&1 | grep -v "WARNING" || echo "⚠️  Some dependencies may have issues"
else
    echo "⚠️  Virtual environment not found - creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel -q
    pip install -q -r requirements.txt 2>&1 | grep -v "WARNING" || echo "⚠️  Some dependencies may have issues"
fi

# Install systemd service
if [ -f ${WORKSPACE_DIR}/infrastructure/systemd/argo-trading-prop-firm.service ]; then
    cp ${WORKSPACE_DIR}/infrastructure/systemd/argo-trading-prop-firm.service /etc/systemd/system/
    systemctl daemon-reload
    echo "✅ Prop firm service file installed"
elif [ -f ../infrastructure/systemd/argo-trading-prop-firm.service ]; then
    cp ../infrastructure/systemd/argo-trading-prop-firm.service /etc/systemd/system/
    systemctl daemon-reload
    echo "✅ Prop firm service file installed"
elif [ -f infrastructure/systemd/argo-trading-prop-firm.service ]; then
    cp infrastructure/systemd/argo-trading-prop-firm.service /etc/systemd/system/
    systemctl daemon-reload
    echo "✅ Prop firm service file installed"
else
    echo "⚠️  Service file not found - will need manual installation"
    echo "   Looking for: ${WORKSPACE_DIR}/infrastructure/systemd/argo-trading-prop-firm.service"
fi
ENDSSH

# Step 6: Start/Restart services
print_step "STEP 6: STARTING SERVICES"

# Start regular service
print_info "Starting regular service..."
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Restart regular service
systemctl restart argo-trading.service 2>/dev/null || systemctl start argo-trading.service
echo "⏳ Waiting for regular service to start..."

# Wait for service to be active with retry logic
MAX_RETRIES=30
RETRY_COUNT=0
while [ \$RETRY_COUNT -lt \$MAX_RETRIES ]; do
    if systemctl is-active --quiet argo-trading.service; then
        echo "✅ Regular service is running"
        break
    fi
    RETRY_COUNT=\$((RETRY_COUNT + 1))
    if [ \$RETRY_COUNT -lt \$MAX_RETRIES ]; then
        echo "  Waiting... (\$RETRY_COUNT/\$MAX_RETRIES)"
        sleep 2
    fi
done

if [ \$RETRY_COUNT -eq \$MAX_RETRIES ]; then
    echo "❌ Regular service failed to start after \$MAX_RETRIES attempts"
    systemctl status argo-trading.service --no-pager -l | head -20
    exit 1
fi
ENDSSH

# Start prop firm service
print_info "Starting prop firm service..."
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Restart prop firm service
systemctl restart argo-trading-prop-firm.service 2>/dev/null || systemctl start argo-trading-prop-firm.service
echo "⏳ Waiting for prop firm service to start..."

# Wait for service to be active with retry logic
MAX_RETRIES=30
RETRY_COUNT=0
while [ \$RETRY_COUNT -lt \$MAX_RETRIES ]; do
    if systemctl is-active --quiet argo-trading-prop-firm.service; then
        echo "✅ Prop firm service is running"
        break
    fi
    RETRY_COUNT=\$((RETRY_COUNT + 1))
    if [ \$RETRY_COUNT -lt \$MAX_RETRIES ]; then
        echo "  Waiting... (\$RETRY_COUNT/\$MAX_RETRIES)"
        sleep 2
    fi
done

if [ \$RETRY_COUNT -eq \$MAX_RETRIES ]; then
    echo "❌ Prop firm service failed to start after \$MAX_RETRIES attempts"
    systemctl status argo-trading-prop-firm.service --no-pager -l | head -20
    exit 1
fi
ENDSSH

# Step 7: Verify deployment
print_step "STEP 7: VERIFYING DEPLOYMENT"

print_info "Checking service status..."
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
echo "Regular Service Status:"
systemctl status argo-trading.service --no-pager -l | head -5
echo ""
echo "Prop Firm Service Status:"
systemctl status argo-trading-prop-firm.service --no-pager -l | head -5
ENDSSH

print_info "Checking health endpoints..."
sleep 2

# Check regular service health
if curl -s -f http://${PRODUCTION_SERVER}:${REGULAR_PORT}/api/v1/health > /dev/null 2>&1; then
    print_success "Regular service health check passed"
else
    print_warning "Regular service health check failed (may need a moment to start)"
fi

# Check prop firm service health
if curl -s -f http://${PRODUCTION_SERVER}:${PROP_FIRM_PORT}/api/v1/health > /dev/null 2>&1; then
    print_success "Prop firm service health check passed"
else
    print_warning "Prop firm service health check failed (may need a moment to start)"
fi

# Step 8: Verify account selection
print_step "STEP 8: VERIFYING ACCOUNT SELECTION"
print_info "Checking logs for account selection..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
echo "Regular Service Logs (account selection):"
tail -20 /tmp/argo-green.log 2>/dev/null | grep -E "(Using|PROP FIRM|Account)" || echo "No account selection logs found yet"
echo ""
echo "Prop Firm Service Logs (account selection):"
tail -20 /tmp/argo-prop-firm.log 2>/dev/null | grep -E "(Using|PROP FIRM|Account)" || echo "No account selection logs found yet"
ENDSSH

# Final summary
print_step "DEPLOYMENT COMPLETE"
print_success "Both services deployed!"
echo ""
echo "Service URLs:"
echo "  Regular: http://${PRODUCTION_SERVER}:${REGULAR_PORT}"
echo "  Prop Firm: http://${PRODUCTION_SERVER}:${PROP_FIRM_PORT}"
echo ""
echo "To check logs:"
echo "  Regular: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'tail -f /tmp/argo-green.log'"
echo "  Prop Firm: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'tail -f /tmp/argo-prop-firm.log'"
echo ""
echo "To check status:"
echo "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'systemctl status argo-trading.service argo-trading-prop-firm.service'"
echo ""

