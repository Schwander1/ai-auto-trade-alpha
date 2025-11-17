#!/bin/bash

# Complete First-Time Setup for Argo-Alpine Workspace

# Run this entire script to set everything up at once

# Note: We don't use set -e because we want to handle some errors gracefully

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print error messages
error() {
    echo -e "${RED}❌ Error: $1${NC}" >&2
}

# Function to print success messages
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning messages
warning() {
    echo -e "${YELLOW}⚠️  Warning: $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "═══════════════════════════════════════════════════════════════"

echo "🚀 ARGO-ALPINE WORKSPACE - FIRST-TIME SETUP"

echo "═══════════════════════════════════════════════════════════════"

echo ""

# ============================================================================
# PRE-FLIGHT CHECKS: Verify Required Dependencies
# ============================================================================

echo "🔍 Pre-flight checks: Verifying required dependencies..."

MISSING_DEPS=0

if ! command_exists brew; then
    error "Homebrew is not installed. Please install it from https://brew.sh"
    MISSING_DEPS=1
fi

if ! command_exists pnpm; then
    error "pnpm is not installed. Install with: npm install -g pnpm"
    MISSING_DEPS=1
fi

if ! command_exists python3; then
    error "Python 3 is not installed. Please install Python 3.8 or higher"
    MISSING_DEPS=1
fi

if ! command_exists psql; then
    error "PostgreSQL client (psql) is not installed. Install with: brew install postgresql@14"
    MISSING_DEPS=1
fi

if [ $MISSING_DEPS -eq 1 ]; then
    error "Please install missing dependencies and run the script again."
    exit 1
fi

success "All required dependencies are installed"
echo ""



# ============================================================================

# STEP 1: Navigate to Workspace

# ============================================================================

echo "📍 Step 1: Navigating to workspace..."

cd ~/argo-alpine-workspace || {
    error "Failed to navigate to workspace directory"
    exit 1
}

pwd

success "In workspace"

echo ""



# ============================================================================

# STEP 2: Install Node.js Dependencies

# ============================================================================

echo "📦 Step 2: Installing Node.js dependencies (pnpm)..."

echo "   This installs: monorepo tools, Next.js, React, TypeScript..."

if pnpm install; then
    success "Node dependencies installed"
else
    error "Failed to install Node.js dependencies"
    exit 1
fi

echo ""



# ============================================================================

# STEP 3A: Setup Argo Python Environment

# ============================================================================

echo "🐍 Step 3A: Setting up Argo Python environment..."

cd ~/argo-alpine-workspace/argo || {
    error "Failed to navigate to argo directory"
    exit 1
}

if [ -d "venv" ]; then
    warning "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

echo "   Creating virtual environment..."

if ! python3 -m venv venv; then
    error "Failed to create virtual environment"
    exit 1
fi

echo "   Activating virtual environment..."

source venv/bin/activate

echo "   Upgrading pip..."

pip install --upgrade pip --quiet || {
    error "Failed to upgrade pip"
    deactivate
    exit 1
}

echo "   Installing Python dependencies..."

if pip install -r requirements.txt; then
    success "Python dependencies installed"
else
    error "Failed to install Python dependencies"
    deactivate
    exit 1
fi

echo "   Deactivating..."

deactivate

cd ..

success "Argo Python environment ready"

echo ""



# ============================================================================

# STEP 3B: Setup Alpine Backend Python Environment

# ============================================================================

echo "🐍 Step 3B: Setting up Alpine Backend Python environment..."

cd ~/argo-alpine-workspace/alpine-backend || {
    error "Failed to navigate to alpine-backend directory"
    exit 1
}

if [ -d "venv" ]; then
    warning "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

echo "   Creating virtual environment..."

if ! python3 -m venv venv; then
    error "Failed to create virtual environment"
    exit 1
fi

echo "   Activating virtual environment..."

source venv/bin/activate

echo "   Upgrading pip..."

pip install --upgrade pip --quiet || {
    error "Failed to upgrade pip"
    deactivate
    exit 1
}

echo "   Installing Python dependencies..."

if pip install -r backend/requirements.txt; then
    success "Python dependencies installed"
else
    error "Failed to install Python dependencies"
    deactivate
    exit 1
fi

echo "   Deactivating..."

deactivate

cd ..

success "Alpine Backend Python environment ready"

echo ""



# ============================================================================

# STEP 4: Set Up PostgreSQL Database

# ============================================================================

echo "🗄️  Step 4: Setting up PostgreSQL database..."

echo "   Checking if PostgreSQL is installed..."

if ! brew services list | grep -q postgres; then
    warning "PostgreSQL service not found. Attempting to start..."
fi

echo "   Starting PostgreSQL service..."

# Try to start PostgreSQL, but don't fail if it's already running
brew services start postgresql@14 2>/dev/null || brew services restart postgresql@14 2>/dev/null || true

echo "   Waiting for PostgreSQL to start..."

# Wait up to 10 seconds for PostgreSQL to be ready
MAX_WAIT=10
WAIT_COUNT=0
while ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; do
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        error "PostgreSQL did not start within ${MAX_WAIT} seconds"
        exit 1
    fi
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
done

echo "   Verifying connection..."

if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    success "PostgreSQL is ready"
else
    error "PostgreSQL is not responding"
    exit 1
fi

echo ""

echo "   Creating database and user..."

# Check if user exists, create if not
if psql -U $(whoami) -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='alpine_user'" | grep -q 1; then
    warning "User 'alpine_user' already exists, skipping creation"
else
    echo "   Creating user 'alpine_user'..."
    psql -U $(whoami) -d postgres -c "CREATE USER alpine_user WITH PASSWORD 'alpine_password_dev';" || {
        error "Failed to create database user"
        exit 1
    }
    success "User 'alpine_user' created"
fi

# Check if database exists, create if not
if psql -U $(whoami) -d postgres -lqt | cut -d \| -f 1 | grep -qw alpine_analytics; then
    warning "Database 'alpine_analytics' already exists, skipping creation"
else
    echo "   Creating database 'alpine_analytics'..."
    psql -U $(whoami) -d postgres -c "CREATE DATABASE alpine_analytics OWNER alpine_user;" || {
        error "Failed to create database"
        exit 1
    }
    success "Database 'alpine_analytics' created"
fi

# Grant privileges (idempotent operation)
psql -U $(whoami) -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE alpine_analytics TO alpine_user;" || {
    warning "Failed to grant privileges (may already be granted)"
}

success "PostgreSQL database ready"

echo ""



# ============================================================================

# STEP 5A: Create Argo .env File

# ============================================================================

echo "⚙️  Step 5A: Creating Argo .env file..."

cd ~/argo-alpine-workspace/argo || {
    error "Failed to navigate to argo directory"
    exit 1
}

if [ -f ".env" ]; then
    warning ".env file already exists. Backing up to .env.bak..."
    cp .env .env.bak
fi

cat > .env << 'ENVEOF'

USE_AWS_SECRETS=false

REDIS_HOST=localhost

REDIS_PORT=6379

ENVIRONMENT=development

DEBUG=true

ENVEOF

cat .env

cd ..

success "Argo .env created"

echo ""



# ============================================================================

# STEP 5B: Create Alpine Backend .env File

# ============================================================================

echo "⚙️  Step 5B: Creating Alpine Backend .env file..."

cd ~/argo-alpine-workspace/alpine-backend || {
    error "Failed to navigate to alpine-backend directory"
    exit 1
}

if [ -f ".env" ]; then
    warning ".env file already exists. Backing up to .env.bak..."
    cp .env .env.bak
fi

cat > .env << 'ENVEOF'

USE_AWS_SECRETS=false

DATABASE_URL=postgresql://alpine_user:alpine_password_dev@localhost:5432/alpine_analytics

REDIS_HOST=localhost

REDIS_PORT=6379

JWT_SECRET=local_dev_secret_change_in_production

DOMAIN=localhost

FRONTEND_URL=http://localhost:3000

ENVIRONMENT=development

DEBUG=true

ENVEOF

cat .env

cd ..

success "Alpine Backend .env created"

echo ""



# ============================================================================

# STEP 6: Verify Everything Works

# ============================================================================

echo "✅ Step 6: Verifying setup..."

echo ""

VERIFICATION_FAILED=0

echo "   ✓ Check 1: Argo FastAPI import..."

if cd argo && source venv/bin/activate && python -c "import fastapi; print('     ✓ Argo FastAPI ready')" 2>/dev/null && deactivate && cd ..; then
    success "Argo FastAPI import successful"
else
    error "Argo FastAPI import failed"
    VERIFICATION_FAILED=1
    cd .. 2>/dev/null || true
fi

echo ""

echo "   ✓ Check 2: Alpine Backend FastAPI import..."

if cd alpine-backend && source venv/bin/activate && python -c "import fastapi; print('     ✓ Alpine Backend FastAPI ready')" 2>/dev/null && deactivate && cd ..; then
    success "Alpine Backend FastAPI import successful"
else
    error "Alpine Backend FastAPI import failed"
    VERIFICATION_FAILED=1
    cd .. 2>/dev/null || true
fi

echo ""

echo "   ✓ Check 3: pnpm version..."

if pnpm --version >/dev/null 2>&1; then
    echo "     $(pnpm --version)"
    success "pnpm is working"
else
    error "pnpm is not working"
    VERIFICATION_FAILED=1
fi

echo ""

echo "   ✓ Check 4: PostgreSQL connection..."

if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    pg_isready -h localhost -p 5432 | sed 's/^/     /'
    success "PostgreSQL connection successful"
else
    error "PostgreSQL connection failed"
    VERIFICATION_FAILED=1
fi

echo ""

if [ $VERIFICATION_FAILED -eq 1 ]; then
    warning "Some verification checks failed. Please review the errors above."
fi



echo ""

echo "═══════════════════════════════════════════════════════════════"

if [ $VERIFICATION_FAILED -eq 0 ]; then
    echo "✅ SETUP COMPLETE!"
else
    echo "⚠️  SETUP COMPLETE WITH WARNINGS"
fi

echo "═══════════════════════════════════════════════════════════════"

echo ""

echo "🎉 You're ready to develop! Next steps:"

echo ""

echo "   1. Open 3 new terminal tabs in Cursor (Ctrl+\` or Cmd+\`)"

echo ""

echo "   2. In Terminal 1 (Argo - Port 8000):"

echo "      cd argo && source venv/bin/activate && export USE_AWS_SECRETS=false && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo ""

echo "   3. In Terminal 2 (Alpine Backend - Port 9001):"

echo "      cd alpine-backend && source venv/bin/activate && export USE_AWS_SECRETS=false && export DATABASE_URL=\"postgresql://alpine_user:alpine_password_dev@localhost:5432/alpine_analytics\" && uvicorn backend.main:app --reload --host 0.0.0.0 --port 9001"

echo ""

echo "   4. In Terminal 3 (Frontend - Port 3000):"

echo "      cd alpine-frontend && pnpm dev"

echo ""

echo "   5. Verify health endpoints work:"

echo "      curl http://localhost:8000/health"

echo "      curl http://localhost:9001/health"

echo "      open http://localhost:3000"

echo ""

echo "═══════════════════════════════════════════════════════════════"

