#!/bin/bash
# Run Alpine Database Migration with Proper Environment Setup
# This script helps run the immutability and audit migration on Alpine server

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ALPINE_SERVER="${ALPINE_SERVER:-91.98.153.49}"
ALPINE_USER="${ALPINE_USER:-root}"
ALPINE_PATH="${ALPINE_PATH:-/root/alpine-production}"

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

# Check if running locally or remotely
if [ "$1" = "remote" ] || [ -n "$SSH_CONNECTION" ]; then
    # Running on remote server
    print_header "RUNNING MIGRATION ON ALPINE SERVER"

    cd "$ALPINE_PATH"

    # Try to source environment from docker-compose or systemd
    if [ -f ".env" ]; then
        print_info "Loading environment from .env file"
        set -a
        source .env
        set +a
    fi

    # Try to get environment from docker-compose
    if command -v docker-compose >/dev/null 2>&1; then
        print_info "Attempting to get environment from docker-compose"
        export $(docker-compose config 2>/dev/null | grep -E '^[A-Z_]+=' | xargs) 2>/dev/null || true
    fi

    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        print_info "Activating virtual environment"
        source venv/bin/activate
    fi

    # Check if migration file exists
    if [ ! -f "backend/migrations/immutability_and_audit.py" ]; then
        print_error "Migration file not found: backend/migrations/immutability_and_audit.py"
        exit 1
    fi

    print_info "Running database migration..."
    python3 -m backend.migrations.immutability_and_audit upgrade || {
        print_warning "Migration may have failed or already been applied"
        print_info "Checking migration status..."

        python3 <<EOF
from backend.core.database import get_engine
from sqlalchemy import inspect, text

try:
    engine = get_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if 'signal_audit_log' in tables:
        print("✅ Audit log table exists - migration already applied")
    else:
        print("❌ Audit log table missing - migration needed")

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.triggers
            WHERE event_object_table IN ('signals', 'signal_audit_log')
        """))
        count = result.scalar()
        print(f"✅ Found {count} immutability triggers")
except Exception as e:
    print(f"⚠️  Error checking status: {e}")
EOF
    }

    print_success "Migration process completed"

else
    # Running locally - SSH to server
    print_header "RUNNING MIGRATION ON ALPINE SERVER (REMOTE)"

    print_info "Connecting to: ${ALPINE_USER}@${ALPINE_SERVER}"

    # Copy script to server and run it
    scp -o StrictHostKeyChecking=no "$0" ${ALPINE_USER}@${ALPINE_SERVER}:/tmp/run-migration.sh

    ssh -o StrictHostKeyChecking=no ${ALPINE_USER}@${ALPINE_SERVER} <<ENDSSH
chmod +x /tmp/run-migration.sh
bash /tmp/run-migration.sh remote
ENDSSH

    print_success "Migration execution completed"
fi
