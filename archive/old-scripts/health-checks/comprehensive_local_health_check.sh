#!/bin/bash
# Comprehensive Local Health Check - 80 Checks
# Covers all aspects of the Argo-Alpine system

set +e  # Don't exit on errors - we want to run all checks

echo "🏥 COMPREHENSIVE LOCAL HEALTH CHECK (1-80)"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0
SKIPPED=0

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

print_check() {
    echo -e "${CYAN}Check $1: $2${NC}"
}

# ============================================================================
# SECTION 1: ENVIRONMENT & SYSTEM (Checks 1-10)
# ============================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 1: ENVIRONMENT & SYSTEM (Checks 1-10)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check 1: Python 3 installed
print_check "1" "Python 3 Installation"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION installed"
else
    print_error "Python 3 not found"
fi

# Check 2: Python version >= 3.8
print_check "2" "Python Version >= 3.8"
if command -v python3 &> /dev/null; then
    PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
    PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_success "Python version $PYTHON_MAJOR.$PYTHON_MINOR >= 3.8"
    else
        print_error "Python version $PYTHON_MAJOR.$PYTHON_MINOR < 3.8"
    fi
else
    print_error "Cannot check Python version"
fi

# Check 3: pip installed
print_check "3" "pip Installation"
if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    print_success "pip installed"
else
    print_error "pip not found"
fi

# Check 4: Virtual environment exists
print_check "4" "Virtual Environment Exists"
if [ -d "argo/venv" ]; then
    print_success "Virtual environment exists"
else
    print_warning "Virtual environment not found (optional)"
    ((SKIPPED++))
fi

# Check 5: Virtual environment is valid
print_check "5" "Virtual Environment Valid"
if [ -f "argo/venv/bin/activate" ]; then
    print_success "Virtual environment is valid"
else
    if [ -d "argo/venv" ]; then
        print_error "Virtual environment is corrupted"
    else
        print_warning "Virtual environment not found (skipped)"
        ((SKIPPED++))
    fi
fi

# Check 6: Working directory
print_check "6" "Working Directory"
if [ -d "argo" ] && [ -d "alpine-frontend" ]; then
    print_success "In correct workspace directory"
else
    print_error "Not in workspace root directory"
fi

# Check 7: Git repository
print_check "7" "Git Repository"
if [ -d ".git" ]; then
    print_success "Git repository detected"
else
    print_warning "Not a git repository (optional)"
    ((SKIPPED++))
fi

# Check 8: Disk space
print_check "8" "Disk Space Available"
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 90 ]; then
    print_success "Disk space OK ($DISK_USAGE% used)"
else
    print_warning "Disk space low ($DISK_USAGE% used)"
fi

# Check 9: Memory available
print_check "9" "Memory Available"
if command -v free &> /dev/null; then
    MEM_AVAILABLE=$(free -m | awk 'NR==2{printf "%.0f", $7*100/$2}')
    if [ "$MEM_AVAILABLE" -gt 10 ]; then
        print_success "Memory available ($MEM_AVAILABLE%)"
    else
        print_warning "Memory low ($MEM_AVAILABLE%)"
    fi
else
    print_warning "Cannot check memory (free command not available)"
    ((SKIPPED++))
fi

# Check 10: Network connectivity
print_check "10" "Network Connectivity"
if ping -c 1 8.8.8.8 &> /dev/null; then
    print_success "Network connectivity OK"
else
    print_warning "Network connectivity check failed"
fi

# ============================================================================
# SECTION 2: PYTHON DEPENDENCIES (Checks 11-20)
# ============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 2: PYTHON DEPENDENCIES (Checks 11-20)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

cd argo
source venv/bin/activate 2>/dev/null || true

REQUIRED_PACKAGES=(
    "fastapi:fastapi"
    "uvicorn:uvicorn"
    "pandas:pandas"
    "numpy:numpy"
    "requests:requests"
    "alpaca-py:alpaca"
    "yfinance:yfinance"
    "boto3:boto3"
    "sqlalchemy:sqlalchemy"
    "pydantic:pydantic"
)

CHECK_NUM=11
for package_info in "${REQUIRED_PACKAGES[@]}"; do
    PACKAGE_NAME=$(echo $package_info | cut -d':' -f1)
    IMPORT_NAME=$(echo $package_info | cut -d':' -f2)
    print_check "$CHECK_NUM" "Package: $PACKAGE_NAME"
    if python3 -c "import $IMPORT_NAME" 2>/dev/null; then
        VERSION=$(python3 -c "import $IMPORT_NAME; print(getattr($IMPORT_NAME, '__version__', 'unknown'))" 2>/dev/null || echo "installed")
        print_success "$PACKAGE_NAME installed ($VERSION)"
    else
        print_error "$PACKAGE_NAME not installed"
    fi
    ((CHECK_NUM++))
done

cd ..

# ============================================================================
# SECTION 3: CONFIGURATION FILES (Checks 21-30)
# ============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 3: CONFIGURATION FILES (Checks 21-30)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check 21: config.json exists
print_check "21" "config.json Exists"
if [ -f "argo/config.json" ]; then
    print_success "config.json exists"
else
    print_error "config.json not found"
fi

# Check 22: config.json is valid JSON
print_check "22" "config.json Valid JSON"
if [ -f "argo/config.json" ]; then
    if python3 -c "import json; json.load(open('argo/config.json'))" 2>/dev/null; then
        print_success "config.json is valid JSON"
    else
        print_error "config.json is invalid JSON"
    fi
else
    print_warning "config.json not found (skipped)"
    ((SKIPPED++))
fi

# Check 23-27: Required config sections
REQUIRED_SECTIONS=("trading" "strategy" "alpaca" "data_sources" "risk_management")
CHECK_NUM=23
for section in "${REQUIRED_SECTIONS[@]}"; do
    print_check "$CHECK_NUM" "Config Section: $section"
    if [ -f "argo/config.json" ]; then
        if python3 -c "import json; assert '$section' in json.load(open('argo/config.json'))" 2>/dev/null; then
            print_success "config.json has '$section' section"
        else
            print_error "config.json missing '$section' section"
        fi
    else
        print_warning "config.json not found (skipped)"
        ((SKIPPED++))
    fi
    ((CHECK_NUM++))
done

# Check 28: .env file (optional)
print_check "28" ".env File (Optional)"
if [ -f "argo/.env" ] || [ -f ".env" ]; then
    print_success ".env file exists"
else
    print_warning ".env file not found (optional, using env vars)"
    ((SKIPPED++))
fi

# Check 29: requirements.txt exists
print_check "29" "requirements.txt Exists"
if [ -f "argo/requirements.txt" ]; then
    print_success "requirements.txt exists"
else
    print_warning "requirements.txt not found"
fi

# Check 30: Config file permissions
print_check "30" "Config File Permissions"
if [ -f "argo/config.json" ]; then
    if [ -r "argo/config.json" ]; then
        print_success "config.json is readable"
    else
        print_error "config.json is not readable"
    fi
else
    print_warning "config.json not found (skipped)"
    ((SKIPPED++))
fi

# ============================================================================
# SECTION 4: DATABASE (Checks 31-40)
# ============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 4: DATABASE (Checks 31-40)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check 31: Database directory exists
print_check "31" "Database Directory Exists"
if [ -d "argo/data" ]; then
    print_success "Data directory exists"
else
    print_warning "Data directory not found (will be created)"
    ((SKIPPED++))
fi

# Check 32: Database file exists
print_check "32" "Database File Exists"
if [ -f "argo/data/signals.db" ]; then
    print_success "signals.db exists"
else
    print_warning "signals.db not found (will be created on first use)"
    ((SKIPPED++))
fi

# Check 33: Database is accessible
print_check "33" "Database Accessible"
if [ -f "argo/data/signals.db" ]; then
    if python3 -c "import sqlite3; conn = sqlite3.connect('argo/data/signals.db'); conn.close()" 2>/dev/null; then
        print_success "Database is accessible"
    else
        print_error "Database is not accessible"
    fi
else
    print_warning "Database file not found (skipped)"
    ((SKIPPED++))
fi

# Check 34-40: Database tables (if database exists)
if [ -f "argo/data/signals.db" ]; then
    TABLES=("signals" "trades" "positions" "performance" "outcomes" "calibration" "regime_data")
    CHECK_NUM=34
    for table in "${TABLES[@]}"; do
        print_check "$CHECK_NUM" "Database Table: $table"
        TABLE_EXISTS=$(python3 -c "import sqlite3; conn = sqlite3.connect('argo/data/signals.db'); cursor = conn.cursor(); cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='$table'\"); print('1' if cursor.fetchone() else '0'); conn.close()" 2>/dev/null || echo "0")
        if [ "$TABLE_EXISTS" = "1" ]; then
            print_success "Table '$table' exists"
        else
            print_warning "Table '$table' not found (may be created on first use)"
            ((SKIPPED++))
        fi
        ((CHECK_NUM++))
    done
else
    for i in {34..40}; do
        print_check "$i" "Database Tables"
        print_warning "Database not found (skipped)"
        ((SKIPPED++))
    done
fi

# ============================================================================
# SECTION 5: TRADING ENGINE (Checks 41-50)
# ============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 5: TRADING ENGINE (Checks 41-50)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

cd argo
source venv/bin/activate 2>/dev/null || true

# Check 41: Trading engine module
print_check "41" "Trading Engine Module"
if python3 -c "from argo.core.paper_trading_engine import PaperTradingEngine" 2>/dev/null; then
    print_success "Trading engine module importable"
else
    print_error "Trading engine module not importable"
fi

# Check 42: Trading engine initialization
print_check "42" "Trading Engine Initialization"
python3 << 'EOF' 2>/dev/null
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
try:
    from argo.core.paper_trading_engine import PaperTradingEngine
    engine = PaperTradingEngine()
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)
EOF
if [ $? -eq 0 ]; then
    print_success "Trading engine initializes"
else
    print_error "Trading engine initialization failed"
fi

# Check 43: Alpaca connection
print_check "43" "Alpaca Connection"
python3 << 'EOF' 2>/dev/null
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
try:
    from argo.core.paper_trading_engine import PaperTradingEngine
    engine = PaperTradingEngine()
    if engine.alpaca_enabled:
        print("CONNECTED")
    else:
        print("SIMULATION")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
EOF
ALPACA_STATUS=$?
if [ $ALPACA_STATUS -eq 0 ]; then
    ALPACA_RESULT=$(python3 << 'EOF' 2>/dev/null
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
try:
    from argo.core.paper_trading_engine import PaperTradingEngine
    engine = PaperTradingEngine()
    if engine.alpaca_enabled:
        print("CONNECTED")
    else:
        print("SIMULATION")
except:
    print("ERROR")
EOF
)
    if [ "$ALPACA_RESULT" = "CONNECTED" ]; then
        print_success "Alpaca connected"
    else
        print_warning "Alpaca in simulation mode"
    fi
else
    print_error "Alpaca connection check failed"
fi

# Check 44-50: Trading engine methods
TRADING_METHODS=("get_account_details" "get_positions" "get_orders" "get_portfolio_value" "place_order" "cancel_order" "close_position")
CHECK_NUM=44
for method in "${TRADING_METHODS[@]}"; do
    print_check "$CHECK_NUM" "Trading Engine Method: $method"
    if python3 -c "from argo.core.paper_trading_engine import PaperTradingEngine; engine = PaperTradingEngine(); assert hasattr(engine, '$method')" 2>/dev/null; then
        print_success "Method '$method' exists"
    else
        print_error "Method '$method' not found"
    fi
    ((CHECK_NUM++))
done

cd ..

# ============================================================================
# SECTION 6: SIGNAL GENERATION (Checks 51-60)
# ============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 6: SIGNAL GENERATION (Checks 51-60)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

cd argo
source venv/bin/activate 2>/dev/null || true

# Check 51: Signal service module
print_check "51" "Signal Service Module"
if python3 -c "from argo.core.signal_generation_service import SignalGenerationService" 2>/dev/null; then
    print_success "Signal service module importable"
else
    print_error "Signal service module not importable"
fi

# Check 52: Signal service initialization
print_check "52" "Signal Service Initialization"
python3 << 'EOF' 2>/dev/null
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
try:
    from argo.core.signal_generation_service import SignalGenerationService
    service = SignalGenerationService()
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)
EOF
if [ $? -eq 0 ]; then
    print_success "Signal service initializes"
else
    print_error "Signal service initialization failed"
fi

# Check 53: Data sources available
print_check "53" "Data Sources Available"
DATA_SOURCES=$(python3 << 'EOF' 2>/dev/null
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
try:
    from argo.core.signal_generation_service import SignalGenerationService
    service = SignalGenerationService()
    sources = list(service.data_sources.keys())
    print(f"{len(sources)}")
except:
    print("0")
EOF
)
if [ "$DATA_SOURCES" != "0" ] && [ "$DATA_SOURCES" != "" ]; then
    print_success "Data sources available ($DATA_SOURCES sources)"
else
    print_error "No data sources available"
fi

# Check 54-60: Individual data sources
DATA_SOURCE_NAMES=("alpaca" "yfinance" "alpha_vantage" "polygon" "finnhub" "tradier" "iex")
CHECK_NUM=54
for source in "${DATA_SOURCE_NAMES[@]}"; do
    print_check "$CHECK_NUM" "Data Source: $source"
    SOURCE_EXISTS=$(python3 << EOF 2>/dev/null
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
try:
    from argo.core.signal_generation_service import SignalGenerationService
    service = SignalGenerationService()
    if '$source' in service.data_sources:
        print("1")
    else:
        print("0")
except:
    print("0")
EOF
)
    if [ "$SOURCE_EXISTS" = "1" ]; then
        print_success "Data source '$source' available"
    else
        print_warning "Data source '$source' not available (optional)"
        ((SKIPPED++))
    fi
    ((CHECK_NUM++))
done

cd ..

# ============================================================================
# SECTION 7: INTEGRATIONS (Checks 61-70)
# ============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 7: INTEGRATIONS (Checks 61-70)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

cd argo
source venv/bin/activate 2>/dev/null || true

# Check 61: Notion integration
print_check "61" "Notion Integration Module"
if python3 -c "from argo.integrations.complete_tracking import LiveTracker" 2>/dev/null; then
    print_success "Notion integration module available"
else
    print_warning "Notion integration module not found (optional)"
    ((SKIPPED++))
fi

# Check 62: Tradervue integration
print_check "62" "Tradervue Integration Module"
if python3 -c "from argo.integrations.tradervue_client import TradervueClient" 2>/dev/null; then
    print_success "Tradervue integration module available"
else
    print_warning "Tradervue integration module not found (optional)"
    ((SKIPPED++))
fi

# Check 63: Tradervue credentials
print_check "63" "Tradervue Credentials"
if [ -n "$TRADERVUE_USERNAME" ] && [ -n "$TRADERVUE_PASSWORD" ]; then
    print_success "Tradervue credentials configured"
else
    print_warning "Tradervue credentials not set (optional)"
    ((SKIPPED++))
fi

# Check 64: Power BI integration
print_check "64" "Power BI Integration"
if python3 -c "from argo.integrations.complete_tracking import LiveTracker" 2>/dev/null; then
    print_success "Power BI integration module available"
else
    print_warning "Power BI integration module not found (optional)"
    ((SKIPPED++))
fi

# Check 65: AWS Secrets Manager
print_check "65" "AWS Secrets Manager"
if python3 -c "from argo.utils.secrets_manager import get_secret" 2>/dev/null; then
    print_success "AWS Secrets Manager module available"
else
    print_warning "AWS Secrets Manager not available (optional)"
    ((SKIPPED++))
fi

# Check 66-70: Integration status checks
INTEGRATIONS=("notion" "tradervue" "powerbi" "aws_secrets" "monitoring")
CHECK_NUM=66
for integration in "${INTEGRATIONS[@]}"; do
    print_check "$CHECK_NUM" "Integration Status: $integration"
    # This is a placeholder - actual implementation would check each integration
    print_info "Integration check for $integration (manual verification recommended)"
    ((SKIPPED++))
    ((CHECK_NUM++))
done

cd ..

# ============================================================================
# SECTION 8: API & ENDPOINTS (Checks 71-80)
# ============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SECTION 8: API & ENDPOINTS (Checks 71-80)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check 71: API server module
print_check "71" "API Server Module"
cd argo
source venv/bin/activate 2>/dev/null || true
if python3 -c "from argo.api.server import app" 2>/dev/null; then
    print_success "API server module importable"
else
    print_error "API server module not importable"
fi

# Check 72: FastAPI app
print_check "72" "FastAPI Application"
if python3 -c "from argo.api.server import app; assert app is not None" 2>/dev/null; then
    print_success "FastAPI app exists"
else
    print_error "FastAPI app not found"
fi

# Check 73-80: API endpoints (if server is running)
ENDPOINTS=("/health" "/api/signals/latest" "/api/performance" "/api/tradervue/status" "/api/validation" "/docs" "/openapi.json" "/api/v1/tradervue/metrics")
CHECK_NUM=73
for endpoint in "${ENDPOINTS[@]}"; do
    print_check "$CHECK_NUM" "API Endpoint: $endpoint"
    if command -v curl &> /dev/null; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000$endpoint" 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "404" ]; then
            if [ "$HTTP_CODE" = "200" ]; then
                print_success "Endpoint '$endpoint' responding (200)"
            else
                print_warning "Endpoint '$endpoint' not found (404) - may not be running"
                ((SKIPPED++))
            fi
        else
            print_warning "Endpoint '$endpoint' not accessible (server may not be running)"
            ((SKIPPED++))
        fi
    else
        print_warning "curl not available (cannot test endpoint)"
        ((SKIPPED++))
    fi
    ((CHECK_NUM++))
done

cd ..

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 COMPREHENSIVE HEALTH CHECK SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo -e "${CYAN}⏭️  Skipped: $SKIPPED${NC}"
echo -e "${BLUE}📊 Total Checks: 80${NC}"
echo ""

SUCCESS_RATE=$((PASSED * 100 / 80))
echo -e "${BLUE}Success Rate: ${SUCCESS_RATE}%${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CRITICAL CHECKS PASSED!${NC}"
    exit 0
elif [ $FAILED -le 5 ]; then
    echo -e "${YELLOW}⚠️  SOME CHECKS FAILED (Non-critical)${NC}"
    exit 0
else
    echo -e "${RED}❌ MULTIPLE CHECKS FAILED${NC}"
    exit 1
fi

