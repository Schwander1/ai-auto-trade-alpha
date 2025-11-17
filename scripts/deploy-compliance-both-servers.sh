#!/bin/bash
# Deploy Compliance Features to Both Alpine and Argo Servers
# This script handles deployment to both production servers

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ALPINE_SERVER="91.98.153.49"
ALPINE_USER="root"
ALPINE_PATH="/root/alpine-production"
ARGO_SERVER="178.156.194.174"
ARGO_USER="root"
ARGO_PATH="/root/argo-production"

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
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

# Test SSH connection
test_ssh() {
    local server=$1
    local user=$2
    local name=$3

    print_info "Testing SSH connection to $name ($user@$server)..."
    if ssh -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no ${user}@${server} "echo 'Connected'" 2>/dev/null; then
        print_success "SSH connection to $name successful"
        return 0
    else
        print_warning "SSH connection to $name requires authentication"
        return 1
    fi
}

# Deploy to Alpine Server
deploy_alpine() {
    print_header "DEPLOYING TO ALPINE SERVER ($ALPINE_SERVER)"

    if test_ssh "$ALPINE_SERVER" "$ALPINE_USER" "Alpine Server"; then
        print_info "Pulling latest code..."
        ssh ${ALPINE_USER}@${ALPINE_SERVER} << ENDSSH
set -e
cd ${ALPINE_PATH}
echo "Current directory: \$(pwd)"
echo "Pulling latest changes from git..."
git pull origin main || echo "⚠️  Git pull failed or not a git repo"
echo "✅ Code updated"
ENDSSH

        print_info "Copying deployment script..."
        scp scripts/deploy-compliance-features.sh ${ALPINE_USER}@${ALPINE_SERVER}:${ALPINE_PATH}/scripts/ 2>/dev/null || {
            print_warning "Could not copy script, will use existing or create inline"
        }

        print_info "Running deployment on Alpine server..."
        ssh ${ALPINE_USER}@${ALPINE_SERVER} << ENDSSH
set -e
cd ${ALPINE_PATH}
chmod +x scripts/deploy-compliance-features.sh 2>/dev/null || true

# Run deployment if script exists, otherwise run steps manually
if [ -f "scripts/deploy-compliance-features.sh" ]; then
    echo "Running deployment script..."
    bash scripts/deploy-compliance-features.sh
else
    echo "Deployment script not found, running steps manually..."

    # Step 1: Database migration
    if [ -f "backend/migrations/immutability_and_audit.py" ]; then
        echo "Running database migration..."
        source venv/bin/activate 2>/dev/null || true
        python -m backend.migrations.immutability_and_audit upgrade || echo "⚠️  Migration may already be applied"
    fi

    echo "✅ Alpine deployment steps completed"
fi
ENDSSH

        print_success "Alpine server deployment completed"
    else
        print_warning "Cannot connect to Alpine server automatically"
        print_info "Manual deployment required:"
        echo "  ssh ${ALPINE_USER}@${ALPINE_SERVER}"
        echo "  cd ${ALPINE_PATH}"
        echo "  git pull origin main"
        echo "  ./scripts/deploy-compliance-features.sh"
        return 1
    fi
}

# Deploy to Argo Server
deploy_argo() {
    print_header "DEPLOYING TO ARGO SERVER ($ARGO_SERVER)"

    if test_ssh "$ARGO_SERVER" "$ARGO_USER" "Argo Server"; then
        print_info "Pulling latest code..."
        ssh ${ARGO_USER}@${ARGO_SERVER} << ENDSSH
set -e
cd ${ARGO_PATH}
echo "Current directory: \$(pwd)"
echo "Pulling latest changes from git..."
git pull origin main || echo "⚠️  Git pull failed or not a git repo"
echo "✅ Code updated"
ENDSSH

        print_info "Copying deployment and cron scripts..."
        scp scripts/deploy-compliance-features.sh ${ARGO_USER}@${ARGO_SERVER}:${ARGO_PATH}/scripts/ 2>/dev/null || true
        scp argo/argo/compliance/setup_cron.sh ${ARGO_USER}@${ARGO_SERVER}:${ARGO_PATH}/argo/compliance/ 2>/dev/null || true

        print_info "Running deployment on Argo server..."
        ssh ${ARGO_USER}@${ARGO_SERVER} << ENDSSH
set -e
cd ${ARGO_PATH}

# Setup cron jobs
if [ -f "argo/compliance/setup_cron.sh" ]; then
    echo "Setting up cron jobs..."
    chmod +x argo/compliance/setup_cron.sh
    bash argo/compliance/setup_cron.sh
fi

# Run deployment if script exists
if [ -f "scripts/deploy-compliance-features.sh" ]; then
    echo "Running deployment script..."
    chmod +x scripts/deploy-compliance-features.sh
    bash scripts/deploy-compliance-features.sh
else
    echo "Deployment script not found, running steps manually..."

    # Setup cron jobs manually
    echo "Setting up cron jobs..."
    (crontab -l 2>/dev/null | grep -v "argo-compliance"; cat <<CRON
# Argo Capital Compliance Automation
# Daily backup at 2 AM UTC
0 2 * * * cd ${ARGO_PATH}/argo && /usr/bin/python3 compliance/daily_backup.py >> logs/daily_backup.log 2>&1

# Hourly integrity check (sample 1000 signals)
0 * * * * cd ${ARGO_PATH}/argo && /usr/bin/python3 compliance/integrity_monitor.py 1000 >> logs/integrity_checks.log 2>&1

# Daily full integrity check at 3 AM UTC
0 3 * * * cd ${ARGO_PATH}/argo && /usr/bin/python3 compliance/integrity_monitor.py full >> logs/integrity_checks.log 2>&1

# Weekly report every Sunday at 6 AM UTC
0 6 * * 0 cd ${ARGO_PATH}/argo && /usr/bin/python3 compliance/weekly_report.py >> logs/weekly_report.log 2>&1
CRON
    ) | crontab -

    echo "✅ Cron jobs installed"
    echo "✅ Argo deployment steps completed"
fi
ENDSSH

        print_success "Argo server deployment completed"
    else
        print_warning "Cannot connect to Argo server automatically"
        print_info "Manual deployment required:"
        echo "  ssh ${ARGO_USER}@${ARGO_SERVER}"
        echo "  cd ${ARGO_PATH}"
        echo "  git pull origin main"
        echo "  bash argo/compliance/setup_cron.sh"
        echo "  ./scripts/deploy-compliance-features.sh"
        return 1
    fi
}

# Verify deployments
verify_deployments() {
    print_header "VERIFYING DEPLOYMENTS"

    # Verify Alpine
    if test_ssh "$ALPINE_SERVER" "$ALPINE_USER" "Alpine Server"; then
        print_info "Verifying Alpine deployment..."
        ssh ${ALPINE_USER}@${ALPINE_SERVER} << ENDSSH
cd ${ALPINE_PATH}
if [ -f "scripts/verify-compliance-deployment.sh" ]; then
    bash scripts/verify-compliance-deployment.sh
else
    echo "Verification script not found, checking manually..."
    # Check if migration file exists
    if [ -f "backend/migrations/immutability_and_audit.py" ]; then
        echo "✅ Migration file exists"
    fi
fi
ENDSSH
    fi

    # Verify Argo
    if test_ssh "$ARGO_SERVER" "$ARGO_USER" "Argo Server"; then
        print_info "Verifying Argo deployment..."
        ssh ${ARGO_USER}@${ARGO_SERVER} << ENDSSH
cd ${ARGO_PATH}
echo "Checking cron jobs..."
crontab -l | grep -A 2 "argo-compliance" || echo "⚠️  Cron jobs not found"
echo ""
echo "Checking compliance scripts..."
ls -la argo/compliance/*.py 2>/dev/null | head -5 || echo "⚠️  Compliance scripts not found"
ENDSSH
    fi
}

# Main execution
main() {
    print_header "COMPLIANCE FEATURES DEPLOYMENT - BOTH SERVERS"

    echo "This will deploy compliance features to:"
    echo "  - Alpine Server: ${ALPINE_USER}@${ALPINE_SERVER}"
    echo "  - Argo Server: ${ARGO_USER}@${ARGO_SERVER}"
    echo ""
    read -p "Continue with deployment? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi

    # Deploy to both servers
    deploy_alpine
    deploy_argo

    # Verify
    verify_deployments

    print_header "DEPLOYMENT COMPLETE"
    print_success "Deployment to both servers completed!"
    echo ""
    print_info "Next steps:"
    echo "  1. Check logs on both servers"
    echo "  2. Verify cron jobs are running"
    echo "  3. Monitor Grafana dashboard"
    echo "  4. Test integrity monitoring"
    echo ""
}

main "$@"
