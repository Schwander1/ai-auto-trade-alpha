#!/bin/bash
# Rollback Deployment Script
# Restores system from backup if deployment issues occur

set -e

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

# Step 1: List available backups
print_step "STEP 1: LIST AVAILABLE BACKUPS"

print_info "Finding backups for regular service..."
REGULAR_BACKUPS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "ls -dt ${REGULAR_DIR}.backup.* 2>/dev/null | head -5" || echo "")

if [ -z "$REGULAR_BACKUPS" ]; then
    print_warning "No backups found for regular service"
else
    echo "Available backups:"
    echo "$REGULAR_BACKUPS" | nl
fi

print_info "Finding backups for prop firm service..."
PROP_FIRM_BACKUPS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "ls -dt ${PROP_FIRM_DIR}.backup.* 2>/dev/null | head -5" || echo "")

if [ -z "$PROP_FIRM_BACKUPS" ]; then
    print_warning "No backups found for prop firm service"
else
    echo "Available backups:"
    echo "$PROP_FIRM_BACKUPS" | nl
fi

# Step 2: Select backup
print_step "STEP 2: SELECT BACKUP TO RESTORE"

if [ -z "$REGULAR_BACKUPS" ] && [ -z "$PROP_FIRM_BACKUPS" ]; then
    print_error "No backups available for rollback"
    exit 1
fi

# Use most recent backup by default
LATEST_REGULAR=$(echo "$REGULAR_BACKUPS" | head -1)
LATEST_PROP_FIRM=$(echo "$PROP_FIRM_BACKUPS" | head -1)

print_info "Will restore from:"
if [ -n "$LATEST_REGULAR" ]; then
    echo "  Regular service: $LATEST_REGULAR"
fi
if [ -n "$LATEST_PROP_FIRM" ]; then
    echo "  Prop firm service: $LATEST_PROP_FIRM"
fi

read -p "Continue with rollback? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    print_warning "Rollback cancelled"
    exit 0
fi

# Step 3: Stop services
print_step "STEP 3: STOP SERVICES"

print_info "Stopping services..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

if systemctl is-active --quiet argo-trading.service; then
    systemctl stop argo-trading.service
    echo "✅ Regular service stopped"
else
    echo "⚠️  Regular service was not running"
fi

if systemctl is-active --quiet argo-trading-prop-firm.service; then
    systemctl stop argo-trading-prop-firm.service
    echo "✅ Prop firm service stopped"
else
    echo "⚠️  Prop firm service was not running"
fi
ENDSSH

print_success "Services stopped"

# Step 4: Restore regular service
if [ -n "$LATEST_REGULAR" ]; then
    print_step "STEP 4: RESTORE REGULAR SERVICE"

    print_info "Restoring from: $LATEST_REGULAR"

    ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Remove current directory
if [ -d ${REGULAR_DIR} ]; then
    rm -rf ${REGULAR_DIR}
fi

# Restore from backup
cp -r ${LATEST_REGULAR} ${REGULAR_DIR}
echo "✅ Regular service restored"
ENDSSH

    print_success "Regular service restored"
fi

# Step 5: Restore prop firm service
if [ -n "$LATEST_PROP_FIRM" ]; then
    print_step "STEP 5: RESTORE PROP FIRM SERVICE"

    print_info "Restoring from: $LATEST_PROP_FIRM"

    ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Remove current directory
if [ -d ${PROP_FIRM_DIR} ]; then
    rm -rf ${PROP_FIRM_DIR}
fi

# Restore from backup
cp -r ${LATEST_PROP_FIRM} ${PROP_FIRM_DIR}
echo "✅ Prop firm service restored"
ENDSSH

    print_success "Prop firm service restored"
fi

# Step 6: Restart services
print_step "STEP 6: RESTART SERVICES"

print_info "Restarting services..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Restart regular service
if [ -d ${REGULAR_DIR} ]; then
    systemctl start argo-trading.service
    sleep 3
    if systemctl is-active --quiet argo-trading.service; then
        echo "✅ Regular service restarted"
    else
        echo "❌ Regular service failed to start"
        systemctl status argo-trading.service --no-pager -l | head -20
        exit 1
    fi
fi

# Restart prop firm service
if [ -d ${PROP_FIRM_DIR} ]; then
    systemctl start argo-trading-prop-firm.service
    sleep 3
    if systemctl is-active --quiet argo-trading-prop-firm.service; then
        echo "✅ Prop firm service restarted"
    else
        echo "❌ Prop firm service failed to start"
        systemctl status argo-trading-prop-firm.service --no-pager -l | head -20
        exit 1
    fi
fi
ENDSSH

if [ $? -eq 0 ]; then
    print_success "Services restarted successfully"
else
    print_error "Service restart failed"
    exit 1
fi

# Step 7: Verify rollback
print_step "STEP 7: VERIFY ROLLBACK"

print_info "Verifying services are running..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

if systemctl is-active --quiet argo-trading.service; then
    echo "✅ Regular service is running"
    systemctl status argo-trading.service --no-pager -l | head -5
else
    echo "❌ Regular service is not running"
    exit 1
fi

if systemctl is-active --quiet argo-trading-prop-firm.service; then
    echo "✅ Prop firm service is running"
    systemctl status argo-trading-prop-firm.service --no-pager -l | head -5
else
    echo "❌ Prop firm service is not running"
    exit 1
fi
ENDSSH

if [ $? -eq 0 ]; then
    print_success "Rollback verification successful"
else
    print_error "Rollback verification failed"
    exit 1
fi

# Final summary
print_step "ROLLBACK COMPLETE"

print_success "🎉 Rollback completed successfully!"
echo ""
print_info "Services have been restored from backup and restarted"
echo ""
print_info "Next steps:"
echo "  1. Monitor services: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'systemctl status argo-trading.service'"
echo "  2. Check logs: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'journalctl -u argo-trading.service -f'"
echo "  3. Verify functionality"
echo ""
