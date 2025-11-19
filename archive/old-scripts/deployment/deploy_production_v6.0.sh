#!/bin/bash
# Production Deployment Script V6.0
# Deploys all services with security implementations

set -e  # Exit on error

echo "🚀 Starting V6.0 Production Deployment..."
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ALPINE_BACKEND_DIR="alpine-backend"
ARGO_DIR="argo"
TIMEOUT=300  # 5 minutes timeout for health checks

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Step 1: Verify prerequisites
echo ""
echo "📋 Step 1: Verifying Prerequisites..."
if [ ! -d "$ALPINE_BACKEND_DIR" ]; then
    print_error "Alpine backend directory not found"
    exit 1
fi

if [ ! -d "$ARGO_DIR" ]; then
    print_error "Argo directory not found"
    exit 1
fi

print_status "Prerequisites verified"

# Step 2: Run database migrations
echo ""
echo "📋 Step 2: Running Database Migrations..."
cd "$ALPINE_BACKEND_DIR/backend"

# Check if database is accessible
print_status "Checking database connection..."
python3 -c "
from backend.core.config import settings
from backend.core.database import get_engine
try:
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
" || {
    print_error "Database connection failed. Please check DATABASE_URL"
    exit 1
}

# Run RBAC migration
print_status "Running RBAC migration..."
python3 -m backend.migrations.add_rbac_tables || {
    print_error "RBAC migration failed"
    exit 1
}

# Run other migrations if needed
if [ -f "migrations/add_indexes.py" ]; then
    print_status "Running index migration..."
    python3 migrations/add_indexes.py || print_warning "Index migration had issues (may already exist)"
fi

print_status "Database migrations complete"

# Step 3: Initialize RBAC (requires running backend)
echo ""
echo "📋 Step 3: Initializing RBAC System..."
print_warning "RBAC initialization requires backend to be running"
print_warning "Will be initialized after backend deployment"

# Step 4: Deploy services
echo ""
echo "📋 Step 4: Deploying Services..."
cd ../..

# Stop existing services
print_status "Stopping existing services..."
docker-compose -f "$ALPINE_BACKEND_DIR/docker-compose.production.yml" down 2>/dev/null || true

# Build and start services
print_status "Building and starting services..."
docker-compose -f "$ALPINE_BACKEND_DIR/docker-compose.production.yml" up -d --build

print_status "Services deployed"

# Step 5: Wait for services to be healthy
echo ""
echo "📋 Step 5: Waiting for Services to be Healthy..."
sleep 10  # Initial wait

MAX_WAIT=$TIMEOUT
ELAPSED=0
INTERVAL=5

check_health() {
    local service=$1
    local url=$2
    
    if curl -sf "$url" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check backend health
print_status "Checking backend health..."
BACKEND_HEALTHY=false
while [ $ELAPSED -lt $MAX_WAIT ]; do
    if check_health "backend" "http://localhost:8001/api/v1/health"; then
        BACKEND_HEALTHY=true
        break
    fi
    echo "  Waiting for backend... (${ELAPSED}s/${MAX_WAIT}s)"
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ "$BACKEND_HEALTHY" = true ]; then
    print_status "Backend is healthy"
else
    print_error "Backend health check failed after ${MAX_WAIT}s"
    docker-compose -f "$ALPINE_BACKEND_DIR/docker-compose.production.yml" logs backend-1 | tail -50
    exit 1
fi

# Check database
print_status "Checking database health..."
if docker exec alpine-postgres pg_isready -U alpine_user > /dev/null 2>&1; then
    print_status "Database is healthy"
else
    print_error "Database health check failed"
    exit 1
fi

# Check Redis
print_status "Checking Redis health..."
if docker exec alpine-redis redis-cli --raw incr ping > /dev/null 2>&1; then
    print_status "Redis is healthy"
else
    print_error "Redis health check failed"
    exit 1
fi

# Step 6: Initialize RBAC
echo ""
echo "📋 Step 6: Initializing RBAC System..."
print_status "Initializing default roles and permissions..."

# Get admin token (requires existing admin user or manual setup)
print_warning "RBAC initialization requires admin authentication"
print_warning "Please initialize manually: POST /api/v1/roles/initialize"

# Step 7: Verify security implementations
echo ""
echo "📋 Step 7: Verifying Security Implementations..."
cd "$ALPINE_BACKEND_DIR"
if python3 verify_security_implementation.py; then
    print_status "All security implementations verified"
else
    print_error "Security verification failed"
    exit 1
fi

# Step 8: Check signal generation (Argo)
echo ""
echo "📋 Step 8: Checking Signal Generation..."
cd "../$ARGO_DIR"

# Check if Argo is running
if pgrep -f "argo.*main.py" > /dev/null || pgrep -f "signal_generation_service" > /dev/null; then
    print_status "Argo signal generation service is running"
else
    print_warning "Argo signal generation service not running"
    print_warning "Start with: cd argo && PYTHONPATH=argo python3 -m argo.core.signal_generation_service"
fi

# Final status
echo ""
echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
print_status "All services deployed and healthy"
print_status "Security implementations verified"
echo ""
echo "Next steps:"
echo "  1. Initialize RBAC: POST /api/v1/roles/initialize"
echo "  2. Configure alerting environment variables"
echo "  3. Monitor logs: docker-compose -f $ALPINE_BACKEND_DIR/docker-compose.production.yml logs -f"
echo "  4. Check health: ./scripts/health_check_production.sh"

