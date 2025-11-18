#!/bin/bash
# Deploy Production Fixes
# Deploys trading execution fixes and optimizations to production

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ARGO_DIR="${WORKSPACE_DIR}/argo"

# Configuration
PRODUCTION_SERVER="178.156.194.174"
PRODUCTION_USER="root"
# Deploy to both blue and green (blue-green deployment)
BLUE_DIR="/root/argo-production-blue"
GREEN_DIR="/root/argo-production-green"

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

# Step 1: Pre-deployment checks
print_step "STEP 1: PRE-DEPLOYMENT CHECKS"

print_info "Checking modified files..."
MODIFIED_FILES=(
    "argo/argo/core/paper_trading_engine.py"
    "argo/argo/core/data_sources/xai_grok_source.py"
    "argo/argo/core/data_sources/massive_source.py"
    "argo/argo/api/health.py"
)

for file in "${MODIFIED_FILES[@]}"; do
    if [ -f "${WORKSPACE_DIR}/${file}" ]; then
        print_success "Found: ${file}"
    else
        print_error "Missing: ${file}"
        exit 1
    fi
done

# Step 2: Create backups
print_step "STEP 2: CREATE BACKUPS"

print_info "Creating backups of production code..."
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e
# Backup blue
if [ -d ${BLUE_DIR} ]; then
    BACKUP_DIR="${BLUE_DIR}.backup.\$(date +%Y%m%d_%H%M%S)"
    cp -r ${BLUE_DIR} "\${BACKUP_DIR}"
    echo "✅ Blue backup created: \${BACKUP_DIR}"
fi
# Backup green
if [ -d ${GREEN_DIR} ]; then
    BACKUP_DIR="${GREEN_DIR}.backup.\$(date +%Y%m%d_%H%M%S)"
    cp -r ${GREEN_DIR} "\${BACKUP_DIR}"
    echo "✅ Green backup created: \${BACKUP_DIR}"
fi
ENDSSH

# Step 3: Deploy code to both environments
print_step "STEP 3: DEPLOY CODE"

print_info "Syncing code to ${BLUE_DIR}..."
rsync -avz --delete \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='data/signals.db' \
    --exclude='logs/*.log' \
    --exclude='config.json' \
    "${ARGO_DIR}/" ${PRODUCTION_USER}@${PRODUCTION_SERVER}:${BLUE_DIR}/

print_success "Code synced to blue"

print_info "Syncing code to ${GREEN_DIR}..."
rsync -avz --delete \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='data/signals.db' \
    --exclude='logs/*.log' \
    --exclude='config.json' \
    "${ARGO_DIR}/" ${PRODUCTION_USER}@${PRODUCTION_SERVER}:${GREEN_DIR}/

print_success "Code synced to green"

# Step 4: Restart service
print_step "STEP 4: RESTART SERVICE"

print_info "Restarting Argo service..."
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

if systemctl list-units --type=service | grep -q argo-trading.service; then
    systemctl restart argo-trading.service
    sleep 3
    if systemctl is-active --quiet argo-trading.service; then
        echo "✅ Service restarted successfully"
    else
        echo "❌ Service failed to start"
        systemctl status argo-trading.service --no-pager -l | head -20
        exit 1
    fi
else
    echo "⚠️  Service not found in systemd"
    exit 1
fi
ENDSSH

# Step 5: Verify deployment
print_step "STEP 5: VERIFY DEPLOYMENT"

print_info "Running health checks..."
sleep 5

# Check health endpoint
if curl -s -f http://${PRODUCTION_SERVER}:8000/health > /dev/null 2>&1; then
    print_success "Health endpoint responding"
else
    print_warning "Health endpoint not responding (may need more time)"
fi

# Check service status
if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl is-active --quiet argo-trading.service"; then
    print_success "Service is active"
else
    print_error "Service is not active"
    exit 1
fi

# Check logs for errors
print_info "Checking logs for errors..."
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
tail -n 50 /tmp/argo-blue.log 2>/dev/null | grep -E "ERROR|Exception|Traceback" | tail -5 || echo "No recent errors found"
ENDSSH

print_step "DEPLOYMENT COMPLETE"
print_success "All fixes have been deployed to production!"
print_info "Next steps:"
print_info "  1. Update API keys: ./scripts/update_production_api_keys.sh"
print_info "  2. Monitor logs: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'tail -f /tmp/argo-blue.log'"
print_info "  3. Test trading: Check for successful ETH-USD and BTC-USD order execution"

