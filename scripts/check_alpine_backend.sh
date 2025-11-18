#!/bin/bash
# Check and Fix Alpine Backend Service
# Script to check Alpine backend status and provide restart instructions

set -e

ALPINE_SERVER="91.98.153.49"
ALPINE_USER="root"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
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

# Check Alpine backend health
check_health() {
    print_header "CHECKING ALPINE BACKEND HEALTH"
    
    print_info "Checking health endpoint: http://${ALPINE_SERVER}:8001/api/v1/health"
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${ALPINE_SERVER}:8001/api/v1/health 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "Alpine backend is healthy (HTTP 200)"
        
        # Get health response
        HEALTH_RESPONSE=$(curl -s http://${ALPINE_SERVER}:8001/api/v1/health 2>/dev/null || echo "")
        if [ -n "$HEALTH_RESPONSE" ]; then
            echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null | head -20 || echo "$HEALTH_RESPONSE"
        fi
        return 0
    else
        print_error "Alpine backend is unhealthy (HTTP $HTTP_CODE)"
        return 1
    fi
}

# Check containers
check_containers() {
    print_header "CHECKING ALPINE CONTAINERS"
    
    print_info "Checking Docker containers on ${ALPINE_SERVER}..."
    
    CONTAINERS=$(ssh ${ALPINE_USER}@${ALPINE_SERVER} "docker ps -a --filter 'name=alpine' --format '{{.Names}}\t{{.Status}}' 2>/dev/null || echo ''" 2>/dev/null || echo "")
    
    if [ -z "$CONTAINERS" ]; then
        print_error "No Alpine containers found"
        return 1
    fi
    
    echo "$CONTAINERS" | while IFS=$'\t' read -r name status; do
        if echo "$status" | grep -q "Up"; then
            print_success "$name: $status"
        else
            print_error "$name: $status"
        fi
    done
    
    return 0
}

# Find docker-compose file
find_compose_file() {
    print_info "Finding docker-compose file..."
    
    COMPOSE_FILE=$(ssh ${ALPINE_USER}@${ALPINE_SERVER} "
        find /root -name 'docker-compose.production.yml' -type f 2>/dev/null | head -1
    " 2>/dev/null || echo "")
    
    if [ -z "$COMPOSE_FILE" ]; then
        print_error "Could not find docker-compose.production.yml"
        print_info "Searching for any docker-compose files..."
        ssh ${ALPINE_USER}@${ALPINE_SERVER} "find /root -name 'docker-compose*.yml' -type f 2>/dev/null | head -5" 2>/dev/null || echo "No docker-compose files found"
        return 1
    fi
    
    print_success "Found: $COMPOSE_FILE"
    echo "$COMPOSE_FILE"
    return 0
}

# Restart Alpine backend
restart_backend() {
    print_header "RESTARTING ALPINE BACKEND"
    
    COMPOSE_FILE=$(find_compose_file)
    if [ $? -ne 0 ]; then
        print_error "Cannot restart without docker-compose file"
        return 1
    fi
    
    COMPOSE_DIR=$(dirname "$COMPOSE_FILE")
    
    print_info "Restarting services in: $COMPOSE_DIR"
    
    # Try new docker compose syntax first
    print_info "Attempting restart with 'docker compose'..."
    RESTART_OUTPUT=$(ssh ${ALPINE_USER}@${ALPINE_SERVER} "
        cd ${COMPOSE_DIR}
        docker compose -f docker-compose.production.yml restart 2>&1
    " 2>&1)
    
    if [ $? -eq 0 ]; then
        print_success "Restart command executed successfully"
        echo "$RESTART_OUTPUT"
    else
        # Try old docker-compose syntax
        print_info "Trying 'docker-compose' syntax..."
        RESTART_OUTPUT=$(ssh ${ALPINE_USER}@${ALPINE_SERVER} "
            cd ${COMPOSE_DIR}
            docker-compose -f docker-compose.production.yml restart 2>&1
        " 2>&1)
        
        if [ $? -eq 0 ]; then
            print_success "Restart command executed successfully"
            echo "$RESTART_OUTPUT"
        else
            print_error "Failed to restart services"
            echo "$RESTART_OUTPUT"
            return 1
        fi
    fi
    
    print_info "Waiting 15 seconds for services to start..."
    sleep 15
    
    # Verify
    check_health
}

# Check sync endpoint
check_sync_endpoint() {
    print_header "CHECKING SYNC ENDPOINT"
    
    print_info "Checking sync health endpoint: http://${ALPINE_SERVER}:8001/api/v1/external-signals/sync/health"
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${ALPINE_SERVER}:8001/api/v1/external-signals/sync/health 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "Sync endpoint is accessible (HTTP 200)"
        return 0
    elif [ "$HTTP_CODE" = "404" ]; then
        print_error "Sync endpoint not found (HTTP 404)"
        print_warning "Router may not be loaded - backend restart required"
        return 1
    else
        print_warning "Sync endpoint returned HTTP $HTTP_CODE"
        return 1
    fi
}

# Main execution
main() {
    print_header "ALPINE BACKEND STATUS CHECK"
    
    # Check health
    HEALTH_OK=false
    if check_health; then
        HEALTH_OK=true
    fi
    
    # Check containers
    check_containers
    
    # Check sync endpoint
    SYNC_OK=false
    if check_sync_endpoint; then
        SYNC_OK=true
    fi
    
    # Summary
    print_header "SUMMARY"
    
    if [ "$HEALTH_OK" = true ] && [ "$SYNC_OK" = true ]; then
        print_success "Alpine backend is fully operational"
        return 0
    else
        print_warning "Alpine backend has issues"
        
        if [ "$HEALTH_OK" = false ]; then
            print_error "Health endpoint is not responding"
        fi
        
        if [ "$SYNC_OK" = false ]; then
            print_error "Sync endpoint is not accessible"
        fi
        
        echo ""
        print_info "Would you like to restart the Alpine backend?"
        read -p "Restart now? (y/N): " RESTART
        
        if [[ "$RESTART" =~ ^[Yy]$ ]]; then
            restart_backend
            check_sync_endpoint
        else
            print_info "To restart manually:"
            print_info "  ssh ${ALPINE_USER}@${ALPINE_SERVER}"
            COMPOSE_FILE=$(find_compose_file 2>/dev/null || echo "/path/to/docker-compose.production.yml")
            if [ -n "$COMPOSE_FILE" ]; then
                COMPOSE_DIR=$(dirname "$COMPOSE_FILE")
                print_info "  cd ${COMPOSE_DIR}"
                print_info "  docker compose -f docker-compose.production.yml restart"
            fi
        fi
    fi
}

main "$@"

