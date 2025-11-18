#!/bin/bash
# Setup Cron Monitoring
# Sets up automated health checks via cron

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Create cron job
create_cron_job() {
    print_header "SETTING UP CRON MONITORING"
    
    HEALTH_CHECK_SCRIPT="${SCRIPT_DIR}/automated_health_check.sh"
    
    if [ ! -f "$HEALTH_CHECK_SCRIPT" ]; then
        print_warning "Health check script not found: $HEALTH_CHECK_SCRIPT"
        return 1
    fi
    
    # Make sure script is executable
    chmod +x "$HEALTH_CHECK_SCRIPT"
    
    # Create cron entry (runs every 5 minutes)
    CRON_ENTRY="*/5 * * * * ${HEALTH_CHECK_SCRIPT} >> ${WORKSPACE_DIR}/logs/health_check.log 2>&1"
    
    print_info "Cron entry to add:"
    echo "  $CRON_ENTRY"
    echo ""
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "$HEALTH_CHECK_SCRIPT"; then
        print_warning "Cron job already exists"
        read -p "Do you want to update it? (y/N): " UPDATE
        if [[ "$UPDATE" =~ ^[Yy]$ ]]; then
            # Remove old entry
            crontab -l 2>/dev/null | grep -v "$HEALTH_CHECK_SCRIPT" | crontab -
            # Add new entry
            (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
            print_success "Cron job updated"
        else
            print_info "Cron job update skipped"
        fi
    else
        read -p "Do you want to add this cron job? (y/N): " ADD
        if [[ "$ADD" =~ ^[Yy]$ ]]; then
            # Add cron entry
            (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
            print_success "Cron job added successfully"
            print_info "Health checks will run every 5 minutes"
            print_info "Logs will be written to: ${WORKSPACE_DIR}/logs/health_check.log"
        else
            print_info "Cron job setup skipped"
        fi
    fi
}

# Show current cron jobs
show_cron_jobs() {
    print_header "CURRENT CRON JOBS"
    
    if crontab -l 2>/dev/null | grep -q "health_check\|monitor"; then
        print_info "Monitoring-related cron jobs:"
        crontab -l 2>/dev/null | grep -E "health_check|monitor" || echo "None found"
    else
        print_info "No monitoring cron jobs found"
    fi
}

# Create logs directory
create_logs_directory() {
    if [ ! -d "${WORKSPACE_DIR}/logs" ]; then
        mkdir -p "${WORKSPACE_DIR}/logs"
        print_success "Created logs directory: ${WORKSPACE_DIR}/logs"
    fi
}

# Main execution
main() {
    print_header "CRON MONITORING SETUP"
    
    create_logs_directory
    show_cron_jobs
    create_cron_job
    
    print_header "SETUP COMPLETE"
    print_info "To view cron jobs: crontab -l"
    print_info "To remove cron job: crontab -e (then delete the line)"
    print_info "To view health check logs: tail -f ${WORKSPACE_DIR}/logs/health_check.log"
}

main "$@"

