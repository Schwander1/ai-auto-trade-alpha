#!/bin/bash
# Complete local environment setup for testing

set -e

echo "🔧 LOCAL ENVIRONMENT SETUP"
echo "=========================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Step 1: Verify Python environment
echo "1️⃣  Verifying Python environment..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Step 2: Check virtual environment
echo ""
echo "2️⃣  Checking virtual environment..."
if [ -d "argo/venv" ]; then
    print_success "Virtual environment found"
    print_info "Activate with: source argo/venv/bin/activate"
else
    print_warning "Virtual environment not found"
    print_info "Creating virtual environment..."
    cd argo
    python3 -m venv venv
    cd ..
    print_success "Virtual environment created"
fi

# Step 3: Install dependencies
echo ""
echo "3️⃣  Installing dependencies..."
if [ -f "argo/requirements.txt" ]; then
    cd argo
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    print_info "Installing core dependencies..."
    pip install pandas numpy yfinance alpaca-py fastapi uvicorn sqlalchemy python-dotenv requests pydantic > /dev/null 2>&1
    print_info "Installing remaining dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1 || {
        print_warning "Some dependencies failed, installing core packages..."
        pip install pandas numpy yfinance alpaca-py fastapi uvicorn sqlalchemy python-dotenv requests pydantic prometheus-client redis alpha-vantage tweepy boto3 botocore PyYAML > /dev/null 2>&1
    }
    cd ..
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Step 4: Setup local databases
echo ""
echo "4️⃣  Setting up local databases..."
if [ ! -d "argo/data" ]; then
    mkdir -p argo/data
    print_success "Data directory created"
fi

if [ ! -f "argo/data/signals.db" ]; then
    print_info "Initializing SQLite database..."
    python3 -c "
import sqlite3
from pathlib import Path
db_path = Path('argo/data/signals.db')
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        signal_id TEXT UNIQUE,
        symbol TEXT NOT NULL,
        action TEXT NOT NULL,
        entry_price REAL NOT NULL,
        stop_price REAL,
        target_price REAL,
        confidence REAL NOT NULL,
        timestamp TEXT NOT NULL,
        strategy TEXT,
        sha256 TEXT,
        reasoning TEXT
    )
''')
conn.commit()
conn.close()
print('Database initialized')
" 2>/dev/null || print_warning "Database initialization skipped"
    print_success "SQLite database ready"
fi

# Step 5: Verify config.json
echo ""
echo "5️⃣  Verifying configuration..."
if [ -f "argo/config.json" ]; then
    print_success "config.json found"
    
    # Check if auto_execute is set
    AUTO_EXECUTE=$(python3 -c "import json; print(json.load(open('argo/config.json')).get('trading', {}).get('auto_execute', False))" 2>/dev/null || echo "false")
    if [ "$AUTO_EXECUTE" = "True" ]; then
        print_warning "auto_execute is enabled (trading will execute automatically)"
    else
        print_info "auto_execute is disabled (safe for testing)"
    fi
else
    print_error "config.json not found"
    exit 1
fi

# Step 6: Verify Alpaca connection (dev account)
echo ""
echo "6️⃣  Verifying Alpaca connection..."
cd argo
source venv/bin/activate
python3 -c "
from argo.core.paper_trading_engine import PaperTradingEngine
from argo.core.environment import detect_environment

env = detect_environment()
print(f'Environment: {env}')

engine = PaperTradingEngine()
if engine.alpaca_enabled:
    account = engine.get_account_details()
    print(f'✅ Connected to: {engine.account_name}')
    print(f'   Portfolio: \${account[\"portfolio_value\"]:,.2f}')
    print(f'   Buying Power: \${account[\"buying_power\"]:,.2f}')
else:
    print('⚠️  Alpaca not connected (simulation mode)')
" 2>&1 | while IFS= read -r line; do
    if [[ $line == *"✅"* ]] || [[ $line == *"Connected"* ]]; then
        print_success "$line"
    elif [[ $line == *"⚠️"* ]] || [[ $line == *"not connected"* ]]; then
        print_warning "$line"
    else
        print_info "$line"
    fi
done
cd ..

# Step 7: Initialize data directories
echo ""
echo "7️⃣  Initializing data directories..."
mkdir -p argo/data/historical
mkdir -p argo/data/backtest_results
mkdir -p argo/logs
print_success "Data directories ready"

# Step 8: Summary
echo ""
echo "=========================="
echo "✅ LOCAL SETUP COMPLETE"
echo "=========================="
echo ""
echo "📝 Next Steps:"
echo "   1. Run health check: ./scripts/local_health_check.sh"
echo "   2. Run security audit: ./scripts/local_security_audit.sh"
echo "   3. Execute test trade: python argo/scripts/execute_test_trade.py"
echo ""

