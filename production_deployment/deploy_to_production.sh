#!/bin/bash
# Complete production deployment script
# Run this on the production server after copying files

set -e

echo "🚀 ARGO PRODUCTION DEPLOYMENT"
echo "=============================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
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

# Step 1: Verify we're on production server
print_step "Step 1: Verifying production environment"
if [ ! -d "/root/argo-production-green" ] && [ ! -d "/root/argo-production-prop-firm" ]; then
    print_warning "Production directories not found. Creating them..."
    mkdir -p /root/argo-production-green
    mkdir -p /root/argo-production-prop-firm
    print_success "Created production directories"
else
    print_success "Production directories found"
fi

# Step 2: Run configuration setup
print_step "Step 2: Configuring dual trading"
if [ -f "enable_dual_trading_production.sh" ]; then
    chmod +x enable_dual_trading_production.sh
    ./enable_dual_trading_production.sh
    print_success "Configuration complete"
else
    print_error "enable_dual_trading_production.sh not found"
    exit 1
fi

# Step 3: Verify Alpaca credentials
print_step "Step 3: Verifying Alpaca credentials"
if [ -f "/root/argo-production-green/config.json" ]; then
    ARGO_KEY=$(python3 -c "import json; d=json.load(open('/root/argo-production-green/config.json')); print(d.get('alpaca', {}).get('api_key', ''))" 2>/dev/null || echo "")
    if [ -z "$ARGO_KEY" ] || [ "$ARGO_KEY" = "YOUR_ALPACA_API_KEY" ]; then
        print_warning "Argo Alpaca credentials not configured"
        print_warning "Please add credentials to /root/argo-production-green/config.json"
    else
        print_success "Argo Alpaca credentials found"
    fi
fi

if [ -f "/root/argo-production-prop-firm/config.json" ]; then
    PROP_KEY=$(python3 -c "import json; d=json.load(open('/root/argo-production-prop-firm/config.json')); pf=d.get('alpaca', {}).get('prop_firm_test', {}); print(pf.get('api_key', ''))" 2>/dev/null || echo "")
    if [ -z "$PROP_KEY" ] || [ "$PROP_KEY" = "YOUR_ALPACA_API_KEY" ]; then
        print_warning "Prop Firm Alpaca credentials not configured"
        print_warning "Please add credentials to /root/argo-production-prop-firm/config.json"
    else
        print_success "Prop Firm Alpaca credentials found"
    fi
fi

# Step 4: Setup production dependencies
print_step "Step 4: Setting up production dependencies"
if [ -f "setup_production_dependencies.sh" ]; then
    chmod +x setup_production_dependencies.sh
    sudo ./setup_production_dependencies.sh
    print_success "Production dependencies setup complete"
else
    print_warning "setup_production_dependencies.sh not found, skipping"
fi

# Step 5: Create systemd services
print_step "Step 5: Creating systemd services"
if [ -f "create_systemd_services.sh" ]; then
    chmod +x create_systemd_services.sh
    sudo ./create_systemd_services.sh
    print_success "Systemd services created"
else
    print_error "create_systemd_services.sh not found"
    exit 1
fi

# Step 6: Stop existing services
print_step "Step 6: Stopping existing services"
sudo systemctl stop argo-trading.service 2>/dev/null || true
sudo systemctl stop argo-trading-prop-firm.service 2>/dev/null || true
pkill -f "uvicorn.*main:app" 2>/dev/null || true
sleep 2
print_success "Existing services stopped"

# Step 7: Start services
print_step "Step 7: Starting services"
sudo systemctl daemon-reload
sudo systemctl start argo-trading.service
sudo systemctl start argo-trading-prop-firm.service
print_success "Services started"

# Step 8: Enable on boot
print_step "Step 8: Enabling services on boot"
sudo systemctl enable argo-trading.service
sudo systemctl enable argo-trading-prop-firm.service
print_success "Services enabled on boot"

# Step 9: Wait for services to start
print_step "Step 9: Waiting for services to initialize"

# Source dependency checking utilities if available
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
if [ -f "$WORKSPACE_DIR/scripts/lib/wait-for-dependencies.sh" ]; then
    source "$WORKSPACE_DIR/scripts/lib/wait-for-dependencies.sh"
fi

# Wait for services with retry logic
MAX_RETRIES=30
RETRY_COUNT=0

# Wait for Argo service
print_info "Waiting for Argo service to be ready..."
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf --max-time 5 http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Argo service (port 8000) is healthy"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        echo "  Retry $RETRY_COUNT/$MAX_RETRIES..."
        sleep 2
    fi
done

if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    print_error "Argo service (port 8000) did not become ready after $MAX_RETRIES attempts"
    echo "Check logs: sudo journalctl -u argo-trading.service -n 50"
fi

# Wait for Prop Firm service
RETRY_COUNT=0
print_info "Waiting for Prop Firm service to be ready..."
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf --max-time 5 http://localhost:8001/health > /dev/null 2>&1; then
        print_success "Prop Firm service (port 8001) is healthy"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        echo "  Retry $RETRY_COUNT/$MAX_RETRIES..."
        sleep 2
    fi
done

if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    print_error "Prop Firm service (port 8001) did not become ready after $MAX_RETRIES attempts"
    echo "Check logs: sudo journalctl -u argo-trading-prop-firm.service -n 50"
fi

# Step 11: Run verification script
print_step "Step 11: Running verification"
if [ -f "verify_dual_trading_setup.py" ]; then
    python3 verify_dual_trading_setup.py
else
    print_warning "Verification script not found"
fi

# Summary
echo ""
echo "=============================="
echo "📊 DEPLOYMENT SUMMARY"
echo "=============================="
echo ""
echo "Service Status:"
sudo systemctl status argo-trading.service --no-pager -l | head -5
echo ""
sudo systemctl status argo-trading-prop-firm.service --no-pager -l | head -5
echo ""
echo "Health Checks:"
echo "  Argo:      http://localhost:8000/health"
echo "  Prop Firm: http://localhost:8001/health"
echo ""
echo "Logs:"
echo "  Argo:      sudo journalctl -u argo-trading.service -f"
echo "  Prop Firm: sudo journalctl -u argo-trading-prop-firm.service -f"
echo ""
echo "=============================="
print_success "DEPLOYMENT COMPLETE!"
echo "=============================="

