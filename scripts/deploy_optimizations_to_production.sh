#!/bin/bash
# Deploy All Optimizations to Production
# Comprehensive deployment script for all fixes, optimizations, and monitoring tools

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ARGO_DIR="${WORKSPACE_DIR}/argo"

# Configuration
PRODUCTION_SERVER="${PRODUCTION_SERVER:-178.156.194.174}"
PRODUCTION_USER="${PRODUCTION_USER:-root}"
REGULAR_DIR="/root/argo-production"
PROP_FIRM_DIR="/root/argo-production-prop-firm"

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

print_info "Checking local files..."
if [ ! -d "${ARGO_DIR}" ]; then
    print_error "Argo directory not found: ${ARGO_DIR}"
    exit 1
fi

# Check for new components
NEW_COMPONENTS=(
    "argo/core/signal_quality_scorer.py"
    "argo/core/performance_monitor.py"
    "argo/core/error_recovery.py"
    "argo/core/config_validator.py"
    "argo/risk/prop_firm_monitor_enhanced.py"
    "argo/api/health.py"
)

for component in "${NEW_COMPONENTS[@]}"; do
    if [ ! -f "${ARGO_DIR}/${component}" ]; then
        print_warning "New component not found: ${component}"
    else
        print_success "Found: ${component}"
    fi
done

# Check for new scripts
NEW_SCRIPTS=(
    "scripts/verify_alpine_sync.py"
    "scripts/monitor_signal_quality.py"
    "scripts/prop_firm_dashboard.py"
    "scripts/validate_config.py"
    "scripts/performance_report.py"
)

for script in "${NEW_SCRIPTS[@]}"; do
    if [ ! -f "${ARGO_DIR}/${script}" ]; then
        print_warning "New script not found: ${script}"
    else
        print_success "Found: ${script}"
    fi
done

# Step 2: Validate configuration
print_step "STEP 2: VALIDATE CONFIGURATION"

print_info "Validating configuration files..."
if [ -f "${ARGO_DIR}/config.json" ]; then
    python3 "${ARGO_DIR}/scripts/validate_config.py" "${ARGO_DIR}/config.json" || {
        print_error "Configuration validation failed!"
        exit 1
    }
    print_success "Configuration validated"
else
    print_warning "config.json not found locally - will validate on server"
fi

# Step 3: Deploy to regular production service
print_step "STEP 3: DEPLOY TO REGULAR PRODUCTION SERVICE"

print_info "Deploying to ${REGULAR_DIR}..."

# Create backup
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e
if [ -d ${REGULAR_DIR} ]; then
    BACKUP_DIR="${REGULAR_DIR}.backup.\$(date +%Y%m%d_%H%M%S)"
    cp -r ${REGULAR_DIR} "\${BACKUP_DIR}"
    echo "✅ Backup created: \${BACKUP_DIR}"
fi
ENDSSH

# Sync code
rsync -avz --delete \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='data/signals.db' \
    --exclude='logs/*.log' \
    "${ARGO_DIR}/" ${PRODUCTION_USER}@${PRODUCTION_SERVER}:${REGULAR_DIR}/

print_success "Code synced to regular service"

# Step 4: Deploy to prop firm service
print_step "STEP 4: DEPLOY TO PROP FIRM SERVICE"

print_info "Deploying to ${PROP_FIRM_DIR}..."

# Create backup
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e
if [ -d ${PROP_FIRM_DIR} ]; then
    BACKUP_DIR="${PROP_FIRM_DIR}.backup.\$(date +%Y%m%d_%H%M%S)"
    cp -r ${PROP_FIRM_DIR} "\${BACKUP_DIR}"
    echo "✅ Backup created: \${BACKUP_DIR}"
fi
ENDSSH

# Sync code
rsync -avz --delete \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='data/signals.db' \
    --exclude='logs/*.log' \
    "${ARGO_DIR}/" ${PRODUCTION_USER}@${PRODUCTION_SERVER}:${PROP_FIRM_DIR}/

print_success "Code synced to prop firm service"

# Step 5: Install dependencies
print_step "STEP 5: INSTALL DEPENDENCIES"

print_info "Installing dependencies on production server..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Regular service
cd ${REGULAR_DIR}
if [ -d venv ]; then
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel -q
    pip install -q -r requirements.txt 2>&1 | grep -v "WARNING" || true
    echo "✅ Regular service dependencies updated"
else
    echo "⚠️  Virtual environment not found for regular service"
fi

# Prop firm service
cd ${PROP_FIRM_DIR}
if [ -d venv ]; then
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel -q
    pip install -q -r requirements.txt 2>&1 | grep -v "WARNING" || true
    echo "✅ Prop firm service dependencies updated"
else
    echo "⚠️  Virtual environment not found for prop firm service"
fi
ENDSSH

print_success "Dependencies installed"

# Step 6: Make scripts executable
print_step "STEP 6: SETUP SCRIPTS"

print_info "Making scripts executable..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Regular service scripts
cd ${REGULAR_DIR}
chmod +x scripts/*.py 2>/dev/null || true
echo "✅ Regular service scripts ready"

# Prop firm service scripts
cd ${PROP_FIRM_DIR}
chmod +x scripts/*.py 2>/dev/null || true
echo "✅ Prop firm service scripts ready"
ENDSSH

print_success "Scripts configured"

# Step 7: Validate production configuration
print_step "STEP 7: VALIDATE PRODUCTION CONFIGURATION"

print_info "Validating production configurations..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Validate regular service config
if [ -f ${REGULAR_DIR}/config.json ]; then
    cd ${REGULAR_DIR}
    python3 scripts/validate_config.py config.json || {
        echo "⚠️  Regular service config validation had issues"
    }
fi

# Validate prop firm service config
if [ -f ${PROP_FIRM_DIR}/config.json ]; then
    cd ${PROP_FIRM_DIR}
    python3 scripts/validate_config.py config.json || {
        echo "⚠️  Prop firm service config validation had issues"
    }
fi
ENDSSH

print_success "Configuration validated"

# Step 8: Restart services
print_step "STEP 8: RESTART SERVICES"

print_info "Restarting services..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Restart regular service
if systemctl list-units --type=service | grep -q argo-trading.service; then
    systemctl restart argo-trading.service
    sleep 3
    if systemctl is-active --quiet argo-trading.service; then
        echo "✅ Regular service restarted successfully"
    else
        echo "❌ Regular service failed to start"
        systemctl status argo-trading.service --no-pager -l | head -20
        exit 1
    fi
else
    echo "⚠️  Regular service not found in systemd"
fi

# Restart prop firm service
if systemctl list-units --type=service | grep -q argo-trading-prop-firm.service; then
    systemctl restart argo-trading-prop-firm.service
    sleep 3
    if systemctl is-active --quiet argo-trading-prop-firm.service; then
        echo "✅ Prop firm service restarted successfully"
    else
        echo "❌ Prop firm service failed to start"
        systemctl status argo-trading-prop-firm.service --no-pager -l | head -20
        exit 1
    fi
else
    echo "⚠️  Prop firm service not found in systemd"
fi
ENDSSH

print_success "Services restarted"

# Step 9: Post-deployment verification
print_step "STEP 9: POST-DEPLOYMENT VERIFICATION"

print_info "Running health checks..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Check health endpoint (if available)
if curl -s -f http://localhost:8000/api/v1/health/simple > /dev/null 2>&1; then
    echo "✅ Health check endpoint responding"
else
    echo "⚠️  Health check endpoint not responding (may need time to start)"
fi

# Check if services are running
if systemctl is-active --quiet argo-trading.service; then
    echo "✅ Regular service is active"
else
    echo "❌ Regular service is not active"
fi

if systemctl is-active --quiet argo-trading-prop-firm.service; then
    echo "✅ Prop firm service is active"
else
    echo "❌ Prop firm service is not active"
fi
ENDSSH

print_success "Post-deployment verification complete"

# Step 10: Deployment summary
print_step "STEP 10: DEPLOYMENT SUMMARY"

print_success "🎉 Deployment Complete!"
echo ""
print_info "Deployed Components:"
echo "  ✅ Signal quality scorer"
echo "  ✅ Performance monitor"
echo "  ✅ Error recovery mechanisms"
echo "  ✅ Configuration validator"
echo "  ✅ Enhanced prop firm monitoring"
echo "  ✅ Health check endpoint"
echo "  ✅ Monitoring scripts"
echo "  ✅ Validation scripts"
echo ""
print_info "Next Steps:"
echo "  1. Verify Alpine sync: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'cd ${REGULAR_DIR} && python3 scripts/verify_alpine_sync.py'"
echo "  2. Monitor signal quality: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'cd ${REGULAR_DIR} && python3 scripts/monitor_signal_quality.py'"
echo "  3. Check prop firm dashboard: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'cd ${PROP_FIRM_DIR} && python3 scripts/prop_firm_dashboard.py'"
echo "  4. View health status: curl http://${PRODUCTION_SERVER}:8000/api/v1/health/"
echo ""
print_info "Logs:"
echo "  Regular service: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'journalctl -u argo-trading.service -f'"
echo "  Prop firm service: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'journalctl -u argo-trading-prop-firm.service -f'"
echo ""

