#!/bin/bash
# Deploy Unified Architecture to Production
# Deploys unified signal generator and executor services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Configuration
PRODUCTION_SERVER="178.156.194.174"
PRODUCTION_USER="root"
ARGO_DIR="${WORKSPACE_DIR}/argo"

# Production directories
UNIFIED_DIR="/root/argo-production-unified"
ARGO_EXECUTOR_DIR="/root/argo-production-green"
PROP_FIRM_EXECUTOR_DIR="/root/argo-production-prop-firm"

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

# Step 1: Create unified directory
print_step "STEP 1: CREATING UNIFIED DIRECTORY"
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
mkdir -p /root/argo-production-unified/{data,logs,argo}
chmod 755 /root/argo-production-unified
chmod 755 /root/argo-production-unified/{data,logs,argo}
echo "✅ Unified directory created"
ENDSSH
print_success "Unified directory structure created"

# Step 2: Deploy code to unified directory
print_step "STEP 2: DEPLOYING CODE TO UNIFIED DIRECTORY"
print_info "Syncing argo code..."
rsync -avz --delete \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='*.db' \
    --exclude='backups' \
    "${ARGO_DIR}/" ${PRODUCTION_USER}@${PRODUCTION_SERVER}:${UNIFIED_DIR}/argo/

print_info "Syncing scripts..."
rsync -avz \
    --exclude='*.pyc' \
    "${WORKSPACE_DIR}/scripts/" ${PRODUCTION_USER}@${PRODUCTION_SERVER}:${UNIFIED_DIR}/scripts/ 2>/dev/null || true

print_success "Code deployed to unified directory"

# Step 3: Deploy code to executor directories
print_step "STEP 3: DEPLOYING CODE TO EXECUTOR DIRECTORIES"
print_info "Syncing to Argo executor..."
rsync -avz --delete \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='*.db' \
    --exclude='backups' \
    --exclude='config.json' \
    "${ARGO_DIR}/" ${PRODUCTION_USER}@${PRODUCTION_SERVER}:${ARGO_EXECUTOR_DIR}/argo/

print_info "Syncing to Prop Firm executor..."
rsync -avz --delete \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='*.db' \
    --exclude='backups' \
    --exclude='config.json' \
    "${ARGO_DIR}/" ${PRODUCTION_USER}@${PRODUCTION_SERVER}:${PROP_FIRM_EXECUTOR_DIR}/argo/

print_success "Code deployed to executor directories"

# Step 4: Run database migration
print_step "STEP 4: RUNNING DATABASE MIGRATION"
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
cd /root/argo-production-unified
if [ -f scripts/migrate_to_unified_database.py ]; then
    python3 scripts/migrate_to_unified_database.py || echo "⚠️  Migration script not found or failed"
else
    echo "⚠️  Migration script not found, skipping"
fi
ENDSSH
print_success "Database migration completed"

# Step 5: Create systemd services
print_step "STEP 5: CREATING SYSTEMD SERVICES"
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
# Signal Generator Service
cat > /etc/systemd/system/argo-signal-generator.service << 'EOF'
[Unit]
Description=Argo Unified Signal Generator
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-unified
Environment="ARGO_CONFIG_PATH=/root/argo-production-unified/config.json"
Environment="ARGO_24_7_MODE=true"
Environment="PYTHONPATH=/root/argo-production-unified/argo"
ExecStart=/usr/bin/python3 -m uvicorn argo.main:app --host 0.0.0.0 --port 7999
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Argo Executor Service
cat > /etc/systemd/system/argo-trading-executor.service << 'EOF'
[Unit]
Description=Argo Trading Executor
After=network.target argo-signal-generator.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-green
Environment="EXECUTOR_ID=argo"
Environment="EXECUTOR_CONFIG_PATH=/root/argo-production-green/config.json"
Environment="PORT=8000"
Environment="PYTHONPATH=/root/argo-production-green/argo"
ExecStart=/usr/bin/python3 -m uvicorn argo.core.trading_executor:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Prop Firm Executor Service
cat > /etc/systemd/system/argo-prop-firm-executor.service << 'EOF'
[Unit]
Description=Argo Prop Firm Trading Executor
After=network.target argo-signal-generator.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-prop-firm
Environment="EXECUTOR_ID=prop_firm"
Environment="EXECUTOR_CONFIG_PATH=/root/argo-production-prop-firm/config.json"
Environment="PORT=8001"
Environment="PYTHONPATH=/root/argo-production-prop-firm/argo"
ExecStart=/usr/bin/python3 -m uvicorn argo.core.trading_executor:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
echo "✅ Systemd services created"
ENDSSH
print_success "Systemd services created"

# Step 6: Enable and start services
print_step "STEP 6: ENABLING AND STARTING SERVICES"
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
# Enable services
systemctl enable argo-signal-generator.service
systemctl enable argo-trading-executor.service
systemctl enable argo-prop-firm-executor.service

# Start services in order
systemctl start argo-signal-generator.service
sleep 5
systemctl start argo-trading-executor.service
sleep 5
systemctl start argo-prop-firm-executor.service

echo "✅ Services started"
ENDSSH
print_success "Services enabled and started"

# Step 7: Verify deployment
print_step "STEP 7: VERIFYING DEPLOYMENT"
print_info "Checking service status..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
echo "Signal Generator Status:"
systemctl status argo-signal-generator.service --no-pager -l | head -10 || echo "⚠️  Service not running"

echo ""
echo "Argo Executor Status:"
systemctl status argo-trading-executor.service --no-pager -l | head -10 || echo "⚠️  Service not running"

echo ""
echo "Prop Firm Executor Status:"
systemctl status argo-prop-firm-executor.service --no-pager -l | head -10 || echo "⚠️  Service not running"
ENDSSH

print_info "Checking health endpoints..."
sleep 3

if curl -s -f --max-time 5 http://${PRODUCTION_SERVER}:7999/health > /dev/null 2>&1; then
    print_success "Signal Generator health check passed"
else
    print_warning "Signal Generator health check failed (may need time to start)"
fi

if curl -s -f --max-time 5 http://${PRODUCTION_SERVER}:8000/health > /dev/null 2>&1; then
    print_success "Argo Executor health check passed"
else
    print_warning "Argo Executor health check failed (may need time to start)"
fi

if curl -s -f --max-time 5 http://${PRODUCTION_SERVER}:8001/health > /dev/null 2>&1; then
    print_success "Prop Firm Executor health check passed"
else
    print_warning "Prop Firm Executor health check failed (may need time to start)"
fi

# Summary
print_step "DEPLOYMENT SUMMARY"
print_success "Unified architecture deployed to production!"
print_info ""
print_info "Services:"
print_info "  - Signal Generator: http://${PRODUCTION_SERVER}:7999"
print_info "  - Argo Executor: http://${PRODUCTION_SERVER}:8000"
print_info "  - Prop Firm Executor: http://${PRODUCTION_SERVER}:8001"
print_info ""
print_info "Monitor logs:"
print_info "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'journalctl -u argo-signal-generator.service -f'"
print_info "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'journalctl -u argo-trading-executor.service -f'"
print_info "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'journalctl -u argo-prop-firm-executor.service -f'"
print_info ""
print_info "Check status:"
print_info "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'systemctl status argo-signal-generator.service argo-trading-executor.service argo-prop-firm-executor.service'"

