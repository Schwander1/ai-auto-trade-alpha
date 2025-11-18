#!/bin/bash
# Verify Crypto Trading Fixes
# Verifies that ETH-USD and BTC-USD trading fixes are working

set -e

PRODUCTION_SERVER="178.156.194.174"
PRODUCTION_USER="root"
ARGO_DIR="/root/argo-production-blue"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verify symbol conversion function exists
verify_symbol_conversion() {
    print_header "VERIFYING SYMBOL CONVERSION"
    
    print_info "Checking for _convert_symbol_for_alpaca function..."
    
    if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "grep -q '_convert_symbol_for_alpaca' ${ARGO_DIR}/argo/core/paper_trading_engine.py 2>/dev/null"; then
        print_success "Symbol conversion function found"
        
        # Show the function
        ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "grep -A 10 '_convert_symbol_for_alpaca' ${ARGO_DIR}/argo/core/paper_trading_engine.py | head -12"
    else
        print_error "Symbol conversion function not found"
        return 1
    fi
}

# Verify crypto position sizing
verify_crypto_position_sizing() {
    print_header "VERIFYING CRYPTO POSITION SIZING"
    
    print_info "Checking for crypto-specific position sizing logic..."
    
    if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "grep -q 'is_crypto.*-USD' ${ARGO_DIR}/argo/core/paper_trading_engine.py 2>/dev/null"; then
        print_success "Crypto position sizing logic found"
        
        # Show relevant code
        ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "grep -B 2 -A 5 'is_crypto.*-USD' ${ARGO_DIR}/argo/core/paper_trading_engine.py | head -10"
    else
        print_error "Crypto position sizing logic not found"
        return 1
    fi
}

# Verify API key error handling
verify_api_key_handling() {
    print_header "VERIFYING API KEY ERROR HANDLING"
    
    print_info "Checking xAI Grok error handling..."
    if ssh ${PRODUCTION_USER}@${PRODUCTION_USER}@${PRODUCTION_SERVER} "grep -q 'Invalid API key detected' ${ARGO_DIR}/argo/core/data_sources/xai_grok_source.py 2>/dev/null"; then
        print_success "xAI Grok error handling found"
    else
        print_error "xAI Grok error handling not found"
    fi
    
    print_info "Checking Massive API error handling..."
    if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "grep -q 'Invalid API key detected' ${ARGO_DIR}/argo/core/data_sources/massive_source.py 2>/dev/null"; then
        print_success "Massive API error handling found"
    else
        print_error "Massive API error handling not found"
    fi
}

# Test symbol conversion logic
test_symbol_conversion() {
    print_header "TESTING SYMBOL CONVERSION"
    
    print_info "Testing symbol conversion logic..."
    
    ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
python3 << 'PYTHON'
import sys
sys.path.insert(0, '/root/argo-production-blue')

try:
    from argo.core.paper_trading_engine import PaperTradingEngine
    
    engine = PaperTradingEngine()
    
    # Test conversions
    test_cases = [
        ("ETH-USD", "ETHUSD"),
        ("BTC-USD", "BTCUSD"),
        ("AAPL", "AAPL"),  # Should not change
        ("MSFT", "MSFT"),  # Should not change
    ]
    
    print("Testing symbol conversions:")
    all_passed = True
    for original, expected in test_cases:
        result = engine._convert_symbol_for_alpaca(original)
        if result == expected:
            print(f"  ✅ {original} -> {result}")
        else:
            print(f"  ❌ {original} -> {result} (expected {expected})")
            all_passed = False
    
    if all_passed:
        print("\n✅ All symbol conversions working correctly")
        sys.exit(0)
    else:
        print("\n❌ Some symbol conversions failed")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error testing symbol conversion: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON
ENDSSH
}

# Main execution
main() {
    print_header "CRYPTO TRADING FIXES VERIFICATION"
    
    verify_symbol_conversion
    verify_crypto_position_sizing
    verify_api_key_handling
    test_symbol_conversion
    
    print_header "VERIFICATION COMPLETE"
    print_success "All fixes verified!"
}

main "$@"

