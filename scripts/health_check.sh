#!/bin/bash
# Comprehensive Health Check Script
# Checks all enhancements are properly configured and operational

set -e

echo "🏥 Running Comprehensive Health Check"
echo "======================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# Check 1: Python imports
echo -e "\n${YELLOW}📦 Checking Python imports...${NC}"
python -c "
import sys
sys.path.insert(0, 'argo')

try:
    from argo.core.baseline_metrics import BaselineCollector
    print('✅ BaselineCollector')
except Exception as e:
    print(f'❌ BaselineCollector: {e}')
    sys.exit(1)

try:
    from argo.core.improvement_validator import ImprovementValidator
    print('✅ ImprovementValidator')
except Exception as e:
    print(f'❌ ImprovementValidator: {e}')
    sys.exit(1)

try:
    from argo.core.data_sources.chinese_models_source import ChineseModelsDataSource
    print('✅ ChineseModelsDataSource')
except Exception as e:
    print(f'❌ ChineseModelsDataSource: {e}')
    sys.exit(1)

try:
    from argo.risk.prop_firm_risk_monitor import PropFirmRiskMonitor
    print('✅ PropFirmRiskMonitor')
except Exception as e:
    print(f'❌ PropFirmRiskMonitor: {e}')
    sys.exit(1)

try:
    from argo.validation.data_quality import DataQualityMonitor
    print('✅ DataQualityMonitor')
except Exception as e:
    print(f'❌ DataQualityMonitor: {e}')
    sys.exit(1)

try:
    from argo.backtest.transaction_cost_analyzer import TransactionCostAnalyzer
    print('✅ TransactionCostAnalyzer')
except Exception as e:
    print(f'❌ TransactionCostAnalyzer: {e}')
    sys.exit(1)

try:
    from argo.core.adaptive_weight_manager import AdaptiveWeightManager
    print('✅ AdaptiveWeightManager')
except Exception as e:
    print(f'❌ AdaptiveWeightManager: {e}')
    sys.exit(1)

try:
    from argo.core.performance_budget_monitor import get_performance_monitor
    print('✅ PerformanceMonitor')
except Exception as e:
    print(f'❌ PerformanceMonitor: {e}')
    sys.exit(1)

print('✅ All imports successful')
" || {
    echo -e "${RED}❌ Import check failed${NC}"
    ERRORS=$((ERRORS + 1))
}

# Check 2: Config file
echo -e "\n${YELLOW}⚙️  Checking configuration...${NC}"
if [ -f "argo/config.json" ]; then
    echo "✅ config.json exists"
    
    # Check for Chinese models config
    if grep -q "chinese_models" argo/config.json; then
        echo "✅ Chinese models configuration found"
    else
        echo -e "${YELLOW}⚠️  Chinese models configuration missing${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Check for enhancements config
    if grep -q "enhancements" argo/config.json; then
        echo "✅ Enhancements configuration found"
    else
        echo -e "${YELLOW}⚠️  Enhancements configuration missing${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}❌ config.json not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 3: Test files
echo -e "\n${YELLOW}🧪 Checking test files...${NC}"
TEST_FILES=(
    "argo/tests/unit/test_chinese_models_rate_limiting.py"
    "argo/tests/unit/test_risk_monitoring.py"
    "argo/tests/unit/test_data_quality.py"
    "argo/tests/unit/test_transaction_costs.py"
    "argo/tests/unit/test_adaptive_weights.py"
    "argo/tests/unit/test_performance_budget.py"
)

for test_file in "${TEST_FILES[@]}"; do
    if [ -f "$test_file" ]; then
        echo "✅ $(basename $test_file)"
    else
        echo -e "${RED}❌ Missing: $test_file${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check 4: Integration
echo -e "\n${YELLOW}🔗 Checking integration...${NC}"
if grep -q "ChineseModelsDataSource" argo/argo/core/signal_generation_service.py; then
    echo "✅ Chinese models integrated into signal generation"
else
    echo -e "${RED}❌ Chinese models not integrated${NC}"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "DataQualityMonitor" argo/argo/core/signal_generation_service.py; then
    echo "✅ Data quality monitor integrated"
else
    echo -e "${RED}❌ Data quality monitor not integrated${NC}"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "PropFirmRiskMonitor" argo/argo/core/signal_generation_service.py; then
    echo "✅ Risk monitor integrated"
else
    echo -e "${RED}❌ Risk monitor not integrated${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Summary
echo -e "\n${YELLOW}📊 Health Check Summary${NC}"
echo "================================"
echo -e "Errors: ${RED}${ERRORS}${NC}"
echo -e "Warnings: ${YELLOW}${WARNINGS}${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "\n${GREEN}✅ Health check passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Health check failed with ${ERRORS} error(s)${NC}"
    exit 1
fi

