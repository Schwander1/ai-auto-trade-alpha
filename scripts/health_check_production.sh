#!/bin/bash
# Production Health Check Script V6.0
# Comprehensive health check for all services

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ALPINE_BACKEND_DIR="alpine-backend"
ARGO_DIR="argo"

print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_ok() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_fail() {
    echo -e "${RED}❌ $1${NC}"
}

print_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Health check results
HEALTHY=true
ISSUES=()

check_service() {
    local name=$1
    local check_cmd=$2
    
    if eval "$check_cmd" > /dev/null 2>&1; then
        print_ok "$name is healthy"
        return 0
    else
        print_fail "$name is unhealthy"
        ISSUES+=("$name")
        HEALTHY=false
        return 1
    fi
}

# Alpine Backend Health Checks
print_header "Alpine Backend Health Checks"

# Backend 1
check_service "Backend-1" "curl -sf http://localhost:8001/api/v1/health" || {
    print_info "Backend-1 logs:"
    docker logs alpine-backend-1 --tail 20 2>&1 | head -10
}

# Backend 2
check_service "Backend-2" "curl -sf http://localhost:8002/api/v1/health" || {
    print_info "Backend-2 logs:"
    docker logs alpine-backend-2 --tail 20 2>&1 | head -10
}

# Backend 3
check_service "Backend-3" "curl -sf http://localhost:8003/api/v1/health" || {
    print_info "Backend-3 logs:"
    docker logs alpine-backend-3 --tail 20 2>&1 | head -10
}

# Frontend 1
check_service "Frontend-1" "curl -sf http://localhost:3000" || {
    print_info "Frontend-1 logs:"
    docker logs alpine-frontend-1 --tail 20 2>&1 | head -10
}

# Frontend 2
check_service "Frontend-2" "curl -sf http://localhost:3002" || {
    print_info "Frontend-2 logs:"
    docker logs alpine-frontend-2 --tail 20 2>&1 | head -10
}

# Database
check_service "PostgreSQL" "docker exec alpine-postgres pg_isready -U alpine_user"

# Redis
check_service "Redis" "docker exec alpine-redis redis-cli --raw incr ping"

# Prometheus
check_service "Prometheus" "curl -sf http://localhost:9090/-/healthy"

# Grafana
check_service "Grafana" "curl -sf http://localhost:3001/api/health"

# Argo Signal Generation
print_header "Argo Signal Generation Health"

if pgrep -f "argo.*main.py" > /dev/null || pgrep -f "signal_generation_service" > /dev/null; then
    print_ok "Argo signal generation service is running"
    
    # Check if signals are being generated
    if [ -f "$ARGO_DIR/logs/signal_generation.log" ]; then
        RECENT_SIGNALS=$(tail -100 "$ARGO_DIR/logs/signal_generation.log" | grep -c "Signal generated" || echo "0")
        if [ "$RECENT_SIGNALS" -gt 0 ]; then
            print_ok "Signals are being generated (found $RECENT_SIGNALS recent entries)"
        else
            print_warn "No recent signal generation found in logs"
        fi
    fi
    
    # Check Argo API
    if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        print_ok "Argo API is healthy"
    else
        print_warn "Argo API health check failed (may not be exposed)"
    fi
else
    print_warn "Argo signal generation service is not running"
    print_info "Start with: cd argo && PYTHONPATH=argo python3 -m argo.core.signal_generation_service"
fi

# Security Checks
print_header "Security Implementation Checks"

cd "$ALPINE_BACKEND_DIR"
if python3 verify_security_implementation.py > /dev/null 2>&1; then
    print_ok "All security implementations verified"
else
    print_fail "Security verification failed"
    HEALTHY=false
    ISSUES+=("Security verification")
fi

# Database Schema Checks
print_header "Database Schema Checks"

cd backend
python3 << 'EOF'
from backend.core.database import get_engine
from sqlalchemy import inspect, text

try:
    engine = get_engine()
    inspector = inspect(engine)
    
    required_tables = ['users', 'signals', 'roles', 'permissions', 'user_roles', 'role_permissions']
    missing_tables = []
    
    for table in required_tables:
        if inspector.has_table(table):
            print(f"✅ Table '{table}' exists")
        else:
            print(f"❌ Table '{table}' is missing")
            missing_tables.append(table)
    
    if missing_tables:
        print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
        exit(1)
    else:
        print("\n✅ All required tables exist")
        exit(0)
except Exception as e:
    print(f"❌ Database schema check failed: {e}")
    exit(1)
EOF

SCHEMA_OK=$?
if [ $SCHEMA_OK -ne 0 ]; then
    HEALTHY=false
    ISSUES+=("Database schema")
fi

# Summary
print_header "Health Check Summary"

if [ "$HEALTHY" = true ]; then
    print_ok "All systems are healthy!"
    echo ""
    echo "Services Status:"
    echo "  ✅ Alpine Backend: Running"
    echo "  ✅ Frontend: Running"
    echo "  ✅ Database: Healthy"
    echo "  ✅ Redis: Healthy"
    echo "  ✅ Monitoring: Running"
    echo "  ✅ Security: Verified"
    echo ""
    exit 0
else
    print_fail "Health check found issues:"
    for issue in "${ISSUES[@]}"; do
        echo "  - $issue"
    done
    echo ""
    exit 1
fi

