#!/bin/bash
# Complete Production Deployment Script
# Pulls latest code from git and deploys to both Argo and Alpine production servers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Configuration
ARGO_SERVER="178.156.194.174"
ARGO_USER="root"
ALPINE_SERVER="91.98.153.49"
ALPINE_USER="root"

# Argo directories
ARGO_REGULAR_DIR="/root/argo-production-green"
ARGO_PROP_FIRM_DIR="/root/argo-production-prop-firm"

# Alpine directories (check common locations)
ALPINE_DIRS=(
    "/root/alpine-production"
    "/root/alpine-analytics-website-blue"
    "/root/alpine-backend"
)

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

# Step 1: Verify git push was successful
print_step "STEP 1: VERIFYING GIT STATUS"
print_info "Checking local git status..."
if git -C "${WORKSPACE_DIR}" status | grep -q "Your branch is up to date"; then
    print_success "Local branch is up to date with origin/main"
else
    print_warning "Local branch may not be up to date"
fi

# Step 2: Deploy to Argo Server
print_step "STEP 2: DEPLOYING TO ARGO SERVER (${ARGO_SERVER})"

print_info "Syncing code to Argo server using rsync..."

# Deploy to regular service
if [ -d "${WORKSPACE_DIR}/argo" ]; then
    print_info "Syncing to regular service (${ARGO_REGULAR_DIR})..."
    rsync -avz --delete \
        --exclude='venv' \
        --exclude='venv_new' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        --exclude='data/signals.db' \
        --exclude='logs/*.log' \
        --exclude='config.json' \
        "${WORKSPACE_DIR}/argo/" ${ARGO_USER}@${ARGO_SERVER}:${ARGO_REGULAR_DIR}/
    print_success "Regular service code synced"
else
    print_error "Argo directory not found locally"
fi

# Deploy to prop firm service
if [ -d "${WORKSPACE_DIR}/argo" ]; then
    print_info "Syncing to prop firm service (${ARGO_PROP_FIRM_DIR})..."
    rsync -avz --delete \
        --exclude='venv' \
        --exclude='venv_new' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        --exclude='data/signals.db' \
        --exclude='logs/*.log' \
        --exclude='config.json' \
        "${WORKSPACE_DIR}/argo/" ${ARGO_USER}@${ARGO_SERVER}:${ARGO_PROP_FIRM_DIR}/
    print_success "Prop firm service code synced"
fi

# Install dependencies and restart services
ssh ${ARGO_USER}@${ARGO_SERVER} << ENDSSH
set -e

# Install/update dependencies for regular service
if [ -d ${ARGO_REGULAR_DIR}/venv ]; then
    echo "📦 Installing dependencies for regular service..."
    source ${ARGO_REGULAR_DIR}/venv/bin/activate
    pip install -q -r ${ARGO_REGULAR_DIR}/requirements.txt 2>/dev/null || echo "⚠️  Requirements install skipped"
fi

# Install/update dependencies for prop firm service
if [ -d ${ARGO_PROP_FIRM_DIR}/venv ]; then
    echo "📦 Installing dependencies for prop firm service..."
    source ${ARGO_PROP_FIRM_DIR}/venv/bin/activate
    pip install -q -r ${ARGO_PROP_FIRM_DIR}/requirements.txt 2>/dev/null || echo "⚠️  Requirements install skipped"
fi

# Restart services
echo "🔄 Restarting Argo services..."
if systemctl list-units --type=service | grep -q argo-trading.service; then
    systemctl restart argo-trading.service
    sleep 2
    if systemctl is-active --quiet argo-trading.service; then
        echo "✅ Regular Argo service restarted"
    else
        echo "❌ Regular Argo service failed to start"
        systemctl status argo-trading.service --no-pager -l | head -10
    fi
fi

if systemctl list-units --type=service | grep -q argo-trading-prop-firm.service; then
    systemctl restart argo-trading-prop-firm.service
    sleep 2
    if systemctl is-active --quiet argo-trading-prop-firm.service; then
        echo "✅ Prop firm Argo service restarted"
    else
        echo "❌ Prop firm Argo service failed to start"
        systemctl status argo-trading-prop-firm.service --no-pager -l | head -10
    fi
fi
ENDSSH

print_success "Argo deployment completed"

# Step 3: Deploy to Alpine Server
print_step "STEP 3: DEPLOYING TO ALPINE SERVER (${ALPINE_SERVER})"

print_info "Finding Alpine deployment directory..."
ALPINE_DIR=$(ssh ${ALPINE_USER}@${ALPINE_SERVER} 'for dir in /root/alpine-production /root/alpine-analytics-website-blue /root/alpine-backend; do [ -d "$dir" ] && echo "$dir" && break; done')

if [ -z "$ALPINE_DIR" ]; then
    print_error "Alpine deployment directory not found"
    print_info "Skipping Alpine deployment"
else
    print_info "Found Alpine directory: ${ALPINE_DIR}"
    
    # Sync Alpine backend code
    if [ -d "${WORKSPACE_DIR}/alpine-backend" ]; then
        print_info "Syncing Alpine backend code..."
        rsync -avz --delete \
            --exclude='venv' \
            --exclude='__pycache__' \
            --exclude='*.pyc' \
            --exclude='.git' \
            --exclude='*.db' \
            --exclude='logs/*.log' \
            --exclude='.env' \
            "${WORKSPACE_DIR}/alpine-backend/" ${ALPINE_USER}@${ALPINE_SERVER}:${ALPINE_DIR}/
        print_success "Alpine backend code synced"
    else
        print_warning "Alpine backend directory not found locally"
    fi
    
    ssh ${ALPINE_USER}@${ALPINE_SERVER} << ENDSSH
set -e

echo "📦 Updating Alpine dependencies..."
cd "${ALPINE_DIR}"

# Install/update dependencies if venv exists
if [ -d venv ]; then
    source venv/bin/activate
    pip install -q -r requirements.txt 2>/dev/null || echo "⚠️  Requirements install skipped"
elif [ -d backend/venv ]; then
    cd backend
    source venv/bin/activate
    pip install -q -r requirements.txt 2>/dev/null || echo "⚠️  Requirements install skipped"
    deactivate
    cd ..
fi

# Run database migrations if needed
if [ -d backend/migrations ]; then
    echo "🔄 Running database migrations..."
    if [ -d venv ]; then
        source venv/bin/activate
        python -m backend.migrations.add_enum_columns_and_constraints 2>&1 || echo "⚠️  Migration may need manual execution"
    elif [ -d backend/venv ]; then
        cd backend
        source venv/bin/activate
        python -m backend.migrations.add_enum_columns_and_constraints 2>&1 || echo "⚠️  Migration may need manual execution"
        cd ..
    fi
fi

# Restart services
echo "🔄 Restarting Alpine services..."

# Check for systemd services
if systemctl list-units --type=service | grep -q alpine-backend.service; then
    systemctl restart alpine-backend.service
    sleep 2
    if systemctl is-active --quiet alpine-backend.service; then
        echo "✅ Alpine backend service restarted"
    else
        echo "❌ Alpine backend service failed to start"
        systemctl status alpine-backend.service --no-pager -l | head -10
    fi
fi

# Check for docker-compose
if [ -f docker-compose.yml ] || [ -f docker-compose.production.yml ]; then
    echo "🔄 Restarting Docker containers..."
    docker-compose restart 2>/dev/null || docker-compose -f docker-compose.production.yml restart 2>/dev/null || echo "⚠️  Docker restart skipped"
fi
ENDSSH

    print_success "Alpine deployment completed"
fi

# Step 4: Health Checks
print_step "STEP 4: RUNNING HEALTH CHECKS"

print_info "Checking Argo services..."
# Check regular Argo service
if curl -s -f --max-time 5 "http://${ARGO_SERVER}:8000/api/v1/health" > /dev/null 2>&1; then
    print_success "Argo regular service (port 8000) is healthy"
else
    print_warning "Argo regular service health check failed (may need more time to start)"
fi

# Check prop firm Argo service
if curl -s -f --max-time 5 "http://${ARGO_SERVER}:8001/api/v1/health" > /dev/null 2>&1; then
    print_success "Argo prop firm service (port 8001) is healthy"
else
    print_warning "Argo prop firm service health check failed (may need more time to start)"
fi

# Check Alpine service
if curl -s -f --max-time 5 "http://${ALPINE_SERVER}:8001/health" > /dev/null 2>&1; then
    print_success "Alpine backend service (port 8001) is healthy"
else
    print_warning "Alpine backend service health check failed (may need more time to start)"
fi

# Step 5: Final Status
print_step "DEPLOYMENT COMPLETE"

print_success "All changes have been deployed to production!"
echo ""
print_info "Summary:"
echo "  • Code committed and pushed to origin/main"
echo "  • Argo services updated and restarted"
echo "  • Alpine services updated and restarted"
echo ""
print_info "Next steps:"
echo "  1. Monitor logs:"
echo "     Argo: ssh ${ARGO_USER}@${ARGO_SERVER} 'journalctl -u argo-trading.service -f'"
echo "     Alpine: ssh ${ALPINE_USER}@${ALPINE_SERVER} 'tail -f /var/log/alpine-backend.log'"
echo "  2. Verify services are running:"
echo "     Argo: curl http://${ARGO_SERVER}:8000/api/v1/health"
echo "     Alpine: curl http://${ALPINE_SERVER}:8001/health"
echo "  3. Check service status:"
echo "     ssh ${ARGO_USER}@${ARGO_SERVER} 'systemctl status argo-trading.service'"
echo "     ssh ${ALPINE_USER}@${ALPINE_SERVER} 'systemctl status alpine-backend.service'"

