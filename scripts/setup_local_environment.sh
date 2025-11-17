#!/bin/bash
# Setup Local Development Environment
# Sets up virtual environments and installs dependencies for Argo and Alpine Backend

set -e

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORKSPACE_ROOT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
    echo "=========================================="
    echo "$1"
    echo "=========================================="
}

# Check Python version
print_header "CHECKING PYTHON VERSION"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
else
    print_warning "Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Setup Argo virtual environment
print_header "SETTING UP ARGO VIRTUAL ENVIRONMENT"
if [ ! -d "argo/venv" ]; then
    print_info "Creating virtual environment for Argo..."
    cd argo
    python3 -m venv venv
    print_success "Virtual environment created"
    cd ..
else
    print_success "Virtual environment already exists"
fi

print_info "Installing Argo dependencies..."
cd argo
source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Argo dependencies installed"
else
    print_warning "requirements.txt not found, installing core dependencies..."
    pip install fastapi uvicorn sqlalchemy pydantic python-dotenv requests redis prometheus-client
    print_success "Core dependencies installed"
fi
deactivate
cd ..

# Setup Alpine Backend virtual environment
print_header "SETTING UP ALPINE BACKEND VIRTUAL ENVIRONMENT"
if [ ! -d "alpine-backend/venv" ]; then
    print_info "Creating virtual environment for Alpine Backend..."
    cd alpine-backend
    python3 -m venv venv
    print_success "Virtual environment created"
    cd ..
else
    print_success "Virtual environment already exists"
fi

print_info "Installing Alpine Backend dependencies..."
cd alpine-backend
source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt
    print_success "Alpine Backend dependencies installed"
else
    print_warning "requirements.txt not found, installing core dependencies..."
    pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic pydantic-settings redis prometheus_client
    print_success "Core dependencies installed"
fi
deactivate
cd ..

# Install optional dependencies for health checks
print_header "INSTALLING OPTIONAL DEPENDENCIES"
print_info "Installing psutil for system resource monitoring..."
python3 -m pip install --user psutil requests > /dev/null 2>&1 || print_warning "Could not install optional dependencies (this is OK)"

# Verify installations
print_header "VERIFICATION"
print_info "Verifying Argo environment..."
cd argo
source venv/bin/activate
python3 -c "import fastapi, sqlalchemy, pydantic; print('✅ Argo dependencies OK')" 2>/dev/null || print_warning "Some Argo dependencies may be missing"
deactivate
cd ..

print_info "Verifying Alpine Backend environment..."
cd alpine-backend
source venv/bin/activate
python3 -c "import fastapi, sqlalchemy, pydantic; print('✅ Alpine Backend dependencies OK')" 2>/dev/null || print_warning "Some Alpine Backend dependencies may be missing"
deactivate
cd ..

print_header "SETUP COMPLETE"
print_success "Local development environment is ready!"
echo ""
echo "To activate Argo environment:"
echo "  cd argo && source venv/bin/activate"
echo ""
echo "To activate Alpine Backend environment:"
echo "  cd alpine-backend && source venv/bin/activate"
echo ""

