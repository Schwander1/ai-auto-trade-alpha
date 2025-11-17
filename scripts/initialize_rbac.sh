#!/bin/bash
# Initialize RBAC System
# Requires backend to be running and admin authentication

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

BACKEND_URL="${BACKEND_URL:-http://localhost:8001}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@alpineanalytics.ai}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-}"

print_header "RBAC System Initialization"

# Check if backend is running
print_info "Checking backend health..."
if ! curl -sf "$BACKEND_URL/api/v1/health" > /dev/null 2>&1; then
    print_fail "Backend is not accessible at $BACKEND_URL"
    print_info "Please ensure backend is running"
    exit 1
fi

print_ok "Backend is accessible"

# Initialize RBAC via Python script (direct database access)
print_info "Initializing RBAC roles and permissions..."

cd alpine-backend/backend
python3 << 'EOF'
import sys
from backend.core.database import get_db
from backend.core.rbac import initialize_default_roles

try:
    db = next(get_db())
    print("Initializing default roles and permissions...")
    initialize_default_roles(db)
    print("✅ RBAC initialization complete")
    sys.exit(0)
except Exception as e:
    print(f"❌ RBAC initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

INIT_RESULT=$?

if [ $INIT_RESULT -eq 0 ]; then
    print_ok "RBAC system initialized successfully"
    
    # Verify roles were created
    print_info "Verifying roles..."
    python3 << 'EOF'
from backend.core.database import get_db
from backend.models.role import Role

try:
    db = next(get_db())
    roles = db.query(Role).all()
    print(f"✅ Found {len(roles)} role(s):")
    for role in roles:
        perm_count = len(role.permissions)
        print(f"   - {role.name}: {perm_count} permission(s)")
    sys.exit(0)
except Exception as e:
    print(f"❌ Verification failed: {e}")
    sys.exit(1)
EOF
    
    print_ok "RBAC initialization complete"
else
    print_fail "RBAC initialization failed"
    exit 1
fi

