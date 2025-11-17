#!/bin/bash
# Quick Deployment Check
# Fast verification of deployment status

set -e

PRODUCTION_SERVER="${PRODUCTION_SERVER:-178.156.194.174}"
PRODUCTION_USER="${PRODUCTION_USER:-root}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Quick Deployment Check"
echo "=========================="
echo ""

# Check services
echo -n "Services: "
SERVICES=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "systemctl is-active argo-trading.service argo-trading-prop-firm.service 2>&1" || echo "FAILED")
if [[ "$SERVICES" == *"active"* ]]; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
fi

# Check health endpoint
echo -n "Health endpoint: "
HEALTH=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "curl -s -f http://localhost:8000/api/v1/health/simple 2>&1" || echo "FAILED")
if [[ "$HEALTH" == *"ok"* ]] || [[ "$HEALTH" == *"status"* ]]; then
    echo -e "${GREEN}✅ Responding${NC}"
else
    echo -e "${YELLOW}⚠️  Not responding${NC}"
fi

# Check components
echo -n "New components: "
COMPONENTS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "test -f /root/argo-production/argo/core/signal_quality_scorer.py && test -f /root/argo-production/argo/core/performance_monitor.py && echo 'OK'" || echo "MISSING")
if [[ "$COMPONENTS" == "OK" ]]; then
    echo -e "${GREEN}✅ Present${NC}"
else
    echo -e "${RED}❌ Missing${NC}"
fi

# Check scripts
echo -n "Monitoring scripts: "
SCRIPTS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "test -x /root/argo-production/scripts/verify_alpine_sync.py && test -x /root/argo-production/scripts/monitor_signal_quality.py && echo 'OK'" || echo "MISSING")
if [[ "$SCRIPTS" == "OK" ]]; then
    echo -e "${GREEN}✅ Present${NC}"
else
    echo -e "${RED}❌ Missing${NC}"
fi

echo ""
echo "✅ Quick check complete"
