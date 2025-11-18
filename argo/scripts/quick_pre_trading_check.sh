#!/bin/bash
# Quick Pre-Trading Check Script
# Runs essential checks before trading starts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARGO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🚀 QUICK PRE-TRADING CHECK"
echo "=========================="
echo ""

cd "${ARGO_DIR}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Check 1: Python available
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅${NC} Python: ${PYTHON_VERSION}"
else
    echo -e "${RED}❌${NC} Python3 not found"
    ((ERRORS++))
fi
echo ""

# Check 2: Config file exists
echo "2. Checking configuration..."
if [ -f "config.json" ]; then
    if python3 -c "import json; json.load(open('config.json'))" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} config.json exists and is valid"
    else
        echo -e "${RED}❌${NC} config.json is invalid JSON"
        ((ERRORS++))
    fi
else
    echo -e "${YELLOW}⚠️${NC}  config.json not found (may be in different location)"
    ((WARNINGS++))
fi
echo ""

# Check 3: Required directories
echo "3. Checking directories..."
for dir in "data" "logs"; do
    if [ -d "${dir}" ]; then
        if [ -w "${dir}" ]; then
            echo -e "${GREEN}✅${NC} ${dir}/ directory exists and is writable"
        else
            echo -e "${YELLOW}⚠️${NC}  ${dir}/ directory exists but is not writable"
            ((WARNINGS++))
        fi
    else
        echo -e "${YELLOW}⚠️${NC}  ${dir}/ directory does not exist (will be created)"
        ((WARNINGS++))
    fi
done
echo ""

# Check 4: Disk space
echo "4. Checking disk space..."
if command -v df &> /dev/null; then
    DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "${DISK_USAGE}" -gt 90 ]; then
        echo -e "${RED}❌${NC} Disk usage critical: ${DISK_USAGE}%"
        ((ERRORS++))
    elif [ "${DISK_USAGE}" -gt 80 ]; then
        echo -e "${YELLOW}⚠️${NC}  Disk usage high: ${DISK_USAGE}%"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✅${NC} Disk usage: ${DISK_USAGE}%"
    fi
else
    echo -e "${YELLOW}⚠️${NC}  Cannot check disk space"
    ((WARNINGS++))
fi
echo ""

# Check 5: Run comprehensive check
echo "5. Running comprehensive preparation check..."
echo ""
if [ -f "scripts/pre_trading_preparation.py" ]; then
    python3 scripts/pre_trading_preparation.py
    PREP_EXIT=$?
    if [ $PREP_EXIT -ne 0 ]; then
        ((ERRORS++))
    fi
else
    echo -e "${YELLOW}⚠️${NC}  Comprehensive check script not found"
    ((WARNINGS++))
fi
echo ""

# Summary
echo "=========================="
echo "QUICK CHECK SUMMARY"
echo "=========================="
echo -e "${GREEN}✅ Passed:${NC} Basic checks"
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Warnings:${NC} ${WARNINGS}"
fi
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ Errors:${NC} ${ERRORS}"
    echo ""
    echo "Please fix errors before trading!"
    exit 1
fi

echo ""
echo "✅ Quick check complete!"
echo "Run full check: python3 scripts/pre_trading_preparation.py"

