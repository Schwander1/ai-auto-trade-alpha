#!/bin/bash
# Comprehensive local health validation

set -e

echo "🏥 LOCAL HEALTH CHECK"
echo "====================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check 1: Python environment
echo "1️⃣  Python Environment"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION installed"
else
    print_error "Python 3 not found"
fi

# Check 2: Virtual environment
echo ""
echo "2️⃣  Virtual Environment"
if [ -d "argo/venv" ]; then
    print_success "Virtual environment exists"
    if [ -f "argo/venv/bin/activate" ]; then
        print_success "Virtual environment is valid"
    else
        print_error "Virtual environment is corrupted"
    fi
else
    print_error "Virtual environment not found"
fi

# Check 3: Dependencies
echo ""
echo "3️⃣  Dependencies"
cd argo
source venv/bin/activate 2>/dev/null || true

REQUIRED_PACKAGES=("fastapi" "alpaca-py" "yfinance" "pandas" "numpy")
for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import ${package//-/_}" 2>/dev/null; then
        print_success "$package installed"
    else
        print_error "$package not installed"
    fi
done
cd ..

# Check 4: Configuration
echo ""
echo "4️⃣  Configuration"
if [ -f "argo/config.json" ]; then
    print_success "config.json exists"
    
    # Validate JSON
    if python3 -c "import json; json.load(open('argo/config.json'))" 2>/dev/null; then
        print_success "config.json is valid JSON"
    else
        print_error "config.json is invalid JSON"
    fi
    
    # Check required sections
    REQUIRED_SECTIONS=("trading" "strategy" "alpaca")
    for section in "${REQUIRED_SECTIONS[@]}"; do
        if python3 -c "import json; assert '$section' in json.load(open('argo/config.json'))" 2>/dev/null; then
            print_success "config.json has '$section' section"
        else
            print_error "config.json missing '$section' section"
        fi
    done
else
    print_error "config.json not found"
fi

# Check 5: Database
echo ""
echo "5️⃣  Database"
if [ -f "argo/data/signals.db" ]; then
    print_success "Signals database exists"
    
    # Check if database is accessible
    if python3 -c "import sqlite3; conn = sqlite3.connect('argo/data/signals.db'); conn.close()" 2>/dev/null; then
        print_success "Database is accessible"
    else
        print_error "Database is not accessible"
    fi
else
    print_warning "Signals database not found (will be created on first use)"
fi

# Check 6: Alpaca Connection
echo ""
echo "6️⃣  Alpaca Connection"
cd argo
source venv/bin/activate 2>/dev/null || true

python3 << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from argo.core.paper_trading_engine import PaperTradingEngine
    from argo.core.environment import detect_environment
    
    env = detect_environment()
    print(f"Environment: {env}")
    
    engine = PaperTradingEngine()
    if engine.alpaca_enabled:
        account = engine.get_account_details()
        print(f"✅ Connected to: {engine.account_name}")
        print(f"   Portfolio: ${account['portfolio_value']:,.2f}")
        print(f"   Buying Power: ${account['buying_power']:,.2f}")
        sys.exit(0)
    else:
        print("⚠️  Alpaca not connected (simulation mode)")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF

ALPACA_EXIT=$?
if [ $ALPACA_EXIT -eq 0 ]; then
    print_success "Alpaca connection verified"
else
    print_warning "Alpaca connection failed (may be in simulation mode)"
fi
cd ..

# Check 7: Signal Generation Service
echo ""
echo "7️⃣  Signal Generation Service"
cd argo
source venv/bin/activate 2>/dev/null || true

python3 << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from argo.core.signal_generation_service import SignalGenerationService
    
    service = SignalGenerationService()
    print("✅ Signal generation service initialized")
    print(f"   Environment: {service.environment}")
    print(f"   Auto-execute: {service.auto_execute}")
    sys.exit(0)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

SERVICE_EXIT=$?
if [ $SERVICE_EXIT -eq 0 ]; then
    print_success "Signal generation service ready"
else
    print_error "Signal generation service failed to initialize"
fi
cd ..

# Check 8: Data Sources
echo ""
echo "8️⃣  Data Sources"
cd argo
source venv/bin/activate 2>/dev/null || true

python3 << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from argo.core.signal_generation_service import SignalGenerationService
    
    service = SignalGenerationService()
    sources = list(service.data_sources.keys())
    print(f"✅ Data sources initialized: {len(sources)}")
    for source in sources:
        print(f"   - {source}")
    sys.exit(0)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF

SOURCES_EXIT=$?
if [ $SOURCES_EXIT -eq 0 ]; then
    print_success "Data sources ready"
else
    print_error "Data sources failed to initialize"
fi
cd ..

# Check 9: File Permissions
echo ""
echo "9️⃣  File Permissions"
if [ -w "argo/config.json" ]; then
    print_success "config.json is writable"
else
    print_error "config.json is not writable"
fi

if [ -w "argo/data" ]; then
    print_success "Data directory is writable"
else
    print_error "Data directory is not writable"
fi

# Summary
echo ""
echo "====================="
echo "📊 HEALTH CHECK SUMMARY"
echo "====================="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL HEALTH CHECKS PASSED!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  SOME CHECKS FAILED${NC}"
    exit 1
fi

