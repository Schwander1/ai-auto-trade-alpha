#!/bin/bash
# Deploy V11 Optimal Configuration to Production
# Complete production deployment with validation and monitoring

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARGO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKSPACE_DIR="$(cd "${ARGO_DIR}/.." && pwd)"

# Configuration
PRODUCTION_SERVER="${PRODUCTION_SERVER:-178.156.194.174}"
PRODUCTION_USER="${PRODUCTION_USER:-root}"
PROP_FIRM_DIR="/root/argo-production-prop-firm"
SERVICE_NAME="argo-trading-prop-firm"

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

print_info "Validating V11 configuration..."
if [ ! -f "${ARGO_DIR}/config.v11.production.json" ]; then
    print_error "V11 configuration file not found!"
    exit 1
fi

# Validate JSON
if ! python3 -m json.tool "${ARGO_DIR}/config.v11.production.json" > /dev/null 2>&1; then
    print_error "V11 configuration is invalid JSON!"
    exit 1
fi

print_success "V11 configuration validated"

# Check deployment script
if [ ! -f "${ARGO_DIR}/scripts/deploy_v11_configuration.py" ]; then
    print_error "Deployment script not found!"
    exit 1
fi

print_success "Deployment script found"

# Step 2: Test local deployment
print_step "STEP 2: TEST LOCAL DEPLOYMENT"

print_info "Testing V11 configuration deployment locally..."
cd "${ARGO_DIR}"

# Backup current config
if [ -f "config.json" ]; then
    BACKUP_FILE="config.backup.$(date +%Y%m%d_%H%M%S).json"
    cp config.json "${BACKUP_FILE}"
    print_success "Backed up current config to ${BACKUP_FILE}"
fi

# Test deployment
if python3 scripts/deploy_v11_configuration.py; then
    print_success "Local deployment test successful"
else
    print_error "Local deployment test failed!"
    if [ -f "${BACKUP_FILE}" ]; then
        cp "${BACKUP_FILE}" config.json
        print_info "Restored backup configuration"
    fi
    exit 1
fi

# Step 3: Connect to production
print_step "STEP 3: CONNECT TO PRODUCTION"

print_info "Connecting to production server: ${PRODUCTION_SERVER}"

# Test connection
if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${PRODUCTION_USER}@${PRODUCTION_SERVER}" "echo 'Connection successful'" > /dev/null 2>&1; then
    print_error "Cannot connect to production server!"
    print_info "Please ensure:"
    print_info "  1. SSH access is configured"
    print_info "  2. Server is reachable"
    print_info "  3. Credentials are correct"
    exit 1
fi

print_success "Connected to production server"

# Step 4: Backup production configuration
print_step "STEP 4: BACKUP PRODUCTION CONFIGURATION"

print_info "Backing up production configuration..."
ssh "${PRODUCTION_USER}@${PRODUCTION_SERVER}" << 'EOF'
    cd /root/argo-production-prop-firm/argo
    if [ -f config.json ]; then
        BACKUP_FILE="config.backup.$(date +%Y%m%d_%H%M%S).json"
        cp config.json "${BACKUP_FILE}"
        echo "✅ Production config backed up to ${BACKUP_FILE}"
    else
        echo "⚠️  No existing config.json found"
    fi
EOF

print_success "Production configuration backed up"

# Step 5: Deploy V11 configuration
print_step "STEP 5: DEPLOY V11 CONFIGURATION"

print_info "Deploying V11 configuration to production..."

# Ensure directories exist on production
ssh "${PRODUCTION_USER}@${PRODUCTION_SERVER}" << EOF
    mkdir -p ${PROP_FIRM_DIR}/argo/scripts
    mkdir -p ${PROP_FIRM_DIR}/argo/reports
EOF

# Copy V11 config to production
scp "${ARGO_DIR}/config.v11.production.json" "${PRODUCTION_USER}@${PRODUCTION_SERVER}:${PROP_FIRM_DIR}/argo/config.v11.production.json"

# Copy deployment script
scp "${ARGO_DIR}/scripts/deploy_v11_configuration.py" "${PRODUCTION_USER}@${PRODUCTION_SERVER}:${PROP_FIRM_DIR}/argo/scripts/deploy_v11_configuration.py"

# Copy monitoring script
scp "${ARGO_DIR}/scripts/monitor_v11_performance.py" "${PRODUCTION_USER}@${PRODUCTION_SERVER}:${PROP_FIRM_DIR}/argo/scripts/monitor_v11_performance.py"

# Execute deployment on production
ssh "${PRODUCTION_USER}@${PRODUCTION_SERVER}" << EOF
    cd ${PROP_FIRM_DIR}/argo
    python3 scripts/deploy_v11_configuration.py
EOF

print_success "V11 configuration deployed to production"

# Step 6: Verify production configuration
print_step "STEP 6: VERIFY PRODUCTION CONFIGURATION"

print_info "Verifying production configuration..."
ssh "${PRODUCTION_USER}@${PRODUCTION_SERVER}" << 'EOF'
    cd /root/argo-production-prop-firm/argo
    
    # Validate JSON
    if python3 -m json.tool config.json > /dev/null 2>&1; then
        echo "✅ Config is valid JSON"
    else
        echo "❌ Config is invalid JSON!"
        exit 1
    fi
    
    # Verify V11 settings
    python3 << 'PYEOF'
import json
with open('config.json') as f:
    config = json.load(f)
    
checks = [
    ('trading.min_confidence', config.get('trading', {}).get('min_confidence'), 60.0),
    ('trading.position_size_pct', config.get('trading', {}).get('position_size_pct'), 9),
    ('trading.max_drawdown_pct', config.get('trading', {}).get('max_drawdown_pct'), 20),
    ('backtest.use_enhanced_cost_model', config.get('backtest', {}).get('use_enhanced_cost_model'), True),
]

all_passed = True
for name, actual, expected in checks:
    if actual == expected:
        print(f"✅ {name}: {actual}")
    else:
        print(f"❌ {name}: {actual} (expected {expected})")
        all_passed = False

if not all_passed:
    exit(1)
PYEOF
EOF

if [ $? -eq 0 ]; then
    print_success "Production configuration verified"
else
    print_error "Production configuration verification failed!"
    exit 1
fi

# Step 7: Restart production service
print_step "STEP 7: RESTART PRODUCTION SERVICE"

print_info "Restarting production trading service..."
ssh "${PRODUCTION_USER}@${PRODUCTION_SERVER}" << EOF
    systemctl restart ${SERVICE_NAME}
    sleep 2
    systemctl status ${SERVICE_NAME} --no-pager -l | head -20
EOF

print_success "Production service restarted"

# Step 8: Verify service status
print_step "STEP 8: VERIFY SERVICE STATUS"

print_info "Checking service status..."
ssh "${PRODUCTION_USER}@${PRODUCTION_SERVER}" << EOF
    if systemctl is-active --quiet ${SERVICE_NAME}; then
        echo "✅ Service is running"
        systemctl status ${SERVICE_NAME} --no-pager -l | head -15
    else
        echo "❌ Service is not running!"
        systemctl status ${SERVICE_NAME} --no-pager -l
        exit 1
    fi
EOF

if [ $? -eq 0 ]; then
    print_success "Service is running correctly"
else
    print_error "Service is not running properly!"
    print_warning "Check logs: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'journalctl -u ${SERVICE_NAME} -n 50'"
    exit 1
fi

# Step 9: Initial monitoring
print_step "STEP 9: INITIAL MONITORING SETUP"

print_info "Setting up monitoring..."
ssh "${PRODUCTION_USER}@${PRODUCTION_SERVER}" << EOF
    cd ${PROP_FIRM_DIR}/argo
    chmod +x scripts/monitor_v11_performance.py
    echo "✅ Monitoring script ready"
EOF

print_success "Monitoring setup complete"

# Step 10: Deployment summary
print_step "STEP 10: DEPLOYMENT SUMMARY"

print_success "V11 Configuration Deployed Successfully!"
echo ""
print_info "Deployment Details:"
echo "  - Server: ${PRODUCTION_SERVER}"
echo "  - Directory: ${PROP_FIRM_DIR}"
echo "  - Service: ${SERVICE_NAME}"
echo "  - Configuration: V11 Optimal"
echo ""
print_info "V11 Settings Applied:"
echo "  - Min Confidence: 60%"
echo "  - Position Size: 9%"
echo "  - Max Drawdown: 20%"
echo "  - Enhanced Cost Model: Enabled"
echo "  - Volume Confirmation: Enabled"
echo "  - Dynamic Stop Loss: Enabled"
echo ""
print_info "Next Steps:"
echo "  1. Monitor service logs: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'journalctl -u ${SERVICE_NAME} -f'"
echo "  2. Run performance monitor: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'cd ${PROP_FIRM_DIR}/argo && python3 scripts/monitor_v11_performance.py'"
echo "  3. Check service status: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'systemctl status ${SERVICE_NAME}'"
echo ""
print_success "Deployment Complete! 🚀"

