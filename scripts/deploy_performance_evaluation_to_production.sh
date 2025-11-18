#!/bin/bash
# Deploy Performance Evaluation System to Production
# Deploys all performance evaluation scripts and sets up automation

set -e

# Configuration
PRODUCTION_SERVER="${PRODUCTION_SERVER:-178.156.194.174}"
PRODUCTION_USER="${PRODUCTION_USER:-root}"
REGULAR_DIR="/root/argo-production"
PROP_FIRM_DIR="/root/argo-production-prop-firm"
ARGO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../argo" && pwd)"

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Step 1: Verify local files
print_step "STEP 1: VERIFY LOCAL FILES"

REQUIRED_SCRIPTS=(
    "scripts/evaluate_performance.py"
    "scripts/evaluate_performance_enhanced.py"
    "scripts/performance_optimizer.py"
    "scripts/performance_trend_analyzer.py"
    "scripts/performance_comparator.py"
    "scripts/performance_alert.py"
    "scripts/auto_optimize.py"
    "scripts/performance_summary.py"
    "scripts/performance_exporter.py"
    "scripts/setup_performance_monitoring.sh"
)

MISSING_FILES=()
for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ ! -f "${ARGO_DIR}/${script}" ]; then
        MISSING_FILES+=("${script}")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    print_warning "Missing files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - ${file}"
    done
    exit 1
fi

print_success "All required scripts found"

# Step 2: Deploy to regular production service
print_step "STEP 2: DEPLOY TO REGULAR PRODUCTION SERVICE"

print_info "Deploying performance evaluation scripts to ${REGULAR_DIR}..."

# Create backup
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e
if [ -d ${REGULAR_DIR}/scripts ]; then
    BACKUP_DIR="${REGULAR_DIR}/scripts.backup.\$(date +%Y%m%d_%H%M%S)"
    mkdir -p "\${BACKUP_DIR}"
    cp -r ${REGULAR_DIR}/scripts/*.py "\${BACKUP_DIR}/" 2>/dev/null || true
    echo "✅ Backup created: \${BACKUP_DIR}"
fi
ENDSSH

# Deploy scripts
rsync -avz \
    --include='evaluate_performance*.py' \
    --include='performance_*.py' \
    --include='auto_optimize.py' \
    --include='setup_performance_monitoring.sh' \
    --exclude='*' \
    "${ARGO_DIR}/scripts/" ${PRODUCTION_USER}@${PRODUCTION_SERVER}:${REGULAR_DIR}/scripts/

# Make scripts executable
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
cd ${REGULAR_DIR}/scripts
chmod +x evaluate_performance*.py performance_*.py auto_optimize.py setup_performance_monitoring.sh 2>/dev/null || true
echo "✅ Scripts made executable"
ENDSSH

print_success "Scripts deployed to regular service"

# Step 3: Deploy to prop firm service
print_step "STEP 3: DEPLOY TO PROP FIRM SERVICE"

print_info "Deploying performance evaluation scripts to ${PROP_FIRM_DIR}..."

# Create backup
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e
if [ -d ${PROP_FIRM_DIR}/scripts ]; then
    BACKUP_DIR="${PROP_FIRM_DIR}/scripts.backup.\$(date +%Y%m%d_%H%M%S)"
    mkdir -p "\${BACKUP_DIR}"
    cp -r ${PROP_FIRM_DIR}/scripts/*.py "\${BACKUP_DIR}/" 2>/dev/null || true
    echo "✅ Backup created: \${BACKUP_DIR}"
fi
ENDSSH

# Deploy scripts
rsync -avz \
    --include='evaluate_performance*.py' \
    --include='performance_*.py' \
    --include='auto_optimize.py' \
    --include='setup_performance_monitoring.sh' \
    --exclude='*' \
    "${ARGO_DIR}/scripts/" ${PRODUCTION_USER}@${PRODUCTION_SERVER}:${PROP_FIRM_DIR}/scripts/

# Make scripts executable
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
cd ${PROP_FIRM_DIR}/scripts
chmod +x evaluate_performance*.py performance_*.py auto_optimize.py setup_performance_monitoring.sh 2>/dev/null || true
echo "✅ Scripts made executable"
ENDSSH

print_success "Scripts deployed to prop firm service"

# Step 4: Setup automation on production
print_step "STEP 4: SETUP AUTOMATION ON PRODUCTION"

print_info "Setting up performance monitoring automation..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Create directories
mkdir -p ${REGULAR_DIR}/reports
mkdir -p ${REGULAR_DIR}/logs/monitoring
mkdir -p ${PROP_FIRM_DIR}/reports
mkdir -p ${PROP_FIRM_DIR}/logs/monitoring

# Setup cron jobs for regular service
cd ${REGULAR_DIR}

# Remove old performance evaluation cron jobs
(crontab -l 2>/dev/null | grep -v "performance_evaluation" | grep -v "performance_trend" | grep -v "performance_optimizer" | grep -v "performance_alert") | crontab - || true

# Add new cron jobs with absolute paths to ensure reports go to specific folders
(crontab -l 2>/dev/null; cat << CRON_JOBS
# Performance Evaluation - Daily at 9 AM
# Reports saved to: /root/argo-production/reports/
0 9 * * * cd ${REGULAR_DIR} && python3 scripts/evaluate_performance_enhanced.py --days 1 --json --reports-dir ${REGULAR_DIR}/reports > ${REGULAR_DIR}/reports/daily_evaluation_\$(date +\%Y\%m\%d).json 2>&1

# Performance Trend Analysis - Weekly on Sundays at 10 AM
# Reports saved to: /root/argo-production/reports/
0 10 * * 0 cd ${REGULAR_DIR} && python3 scripts/performance_trend_analyzer.py --days 7 --output ${REGULAR_DIR}/reports/weekly_trends_\$(date +\%Y\%m\%d).txt 2>&1

# Performance Optimization Check - Daily at 11 AM
# Reports saved to: /root/argo-production/reports/
0 11 * * * cd ${REGULAR_DIR} && python3 scripts/performance_optimizer.py ${REGULAR_DIR}/reports/daily_evaluation_\$(date +\%Y\%m\%d).json --output ${REGULAR_DIR}/reports/daily_optimizations_\$(date +\%Y\%m\%d).txt 2>&1

# Performance Alert Check - Every 6 hours
# Logs saved to: /root/argo-production/logs/monitoring/
0 */6 * * * cd ${REGULAR_DIR} && python3 scripts/performance_alert.py --check --reports-dir ${REGULAR_DIR}/reports 2>&1 | tee -a ${REGULAR_DIR}/logs/monitoring/alerts.log
CRON_JOBS
) | crontab -

echo "✅ Cron jobs configured for regular service"

# Setup cron jobs for prop firm service
cd ${PROP_FIRM_DIR}

# Note: Prop firm uses same scripts but different directory
# Cron jobs can be added separately if needed

echo "✅ Automation setup complete"
ENDSSH

print_success "Automation configured"

# Step 5: Verify deployment
print_step "STEP 5: VERIFY DEPLOYMENT"

print_info "Verifying scripts are deployed..."

VERIFICATION=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
cd ${REGULAR_DIR}/scripts
echo "Checking scripts..."
for script in evaluate_performance.py evaluate_performance_enhanced.py performance_optimizer.py performance_alert.py; do
    if [ -f "\$script" ] && [ -x "\$script" ]; then
        echo "✅ \$script"
    else
        echo "❌ \$script"
    fi
done
ENDSSH
)

echo "$VERIFICATION"

# Step 6: Test deployment
print_step "STEP 6: TEST DEPLOYMENT"

print_info "Testing performance summary script..."

TEST_RESULT=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
cd ${REGULAR_DIR}
python3 scripts/performance_summary.py 2>&1 | head -20
ENDSSH
)

echo "$TEST_RESULT"

# Final summary
print_step "DEPLOYMENT COMPLETE"

print_success "Performance evaluation system deployed to production!"
print_info ""
print_info "Deployed to:"
print_info "  • Regular service: ${REGULAR_DIR}"
print_info "  • Prop firm service: ${PROP_FIRM_DIR}"
print_info ""
print_info "Automation configured:"
print_info "  • Daily evaluation at 9 AM"
print_info "  • Weekly trend analysis on Sundays at 10 AM"
print_info "  • Daily optimization check at 11 AM"
print_info "  • Alert checks every 6 hours"
print_info ""
print_info "To verify:"
print_info "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'cd ${REGULAR_DIR} && python3 scripts/performance_summary.py'"
print_info ""
print_info "To check cron jobs:"
print_info "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'crontab -l | grep performance'"
print_info ""
print_info "To view reports:"
print_info "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'ls -lh ${REGULAR_DIR}/reports/daily_*'"
print_info ""
print_success "Deployment complete!"
