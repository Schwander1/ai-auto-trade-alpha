#!/bin/bash
# Production Monitoring Script
# Monitors system health, costs, and performance

set -e

echo "📊 Argo-Alpine Production Monitoring"
echo "===================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$(dirname "$0")/.."

# Check if service is running
echo -e "\n${BLUE}🔍 Service Status:${NC}"
if pgrep -f "signal_generation_service" > /dev/null; then
    echo -e "${GREEN}✅ Signal Generation Service: RUNNING${NC}"
    PID=$(pgrep -f "signal_generation_service" | head -1)
    echo "   PID: $PID"
    echo "   Memory: $(ps -p $PID -o rss= | awk '{printf "%.1f MB", $1/1024}')"
else
    echo -e "${RED}❌ Signal Generation Service: NOT RUNNING${NC}"
fi

# Check API costs
echo -e "\n${BLUE}💰 API Costs:${NC}"
PYTHONPATH=argo python3 -c "
import json
import sys
try:
    from argo.core.data_sources.chinese_models_source import ChineseModelsDataSource
    with open('argo/config.json') as f:
        config = json.load(f)
    chinese = config.get('chinese_models', {})
    ds = ChineseModelsDataSource({
        'glm_api_key': chinese.get('glm', {}).get('api_key', ''),
        'glm_enabled': chinese.get('glm', {}).get('enabled', False),
        'baichuan_api_key': chinese.get('baichuan', {}).get('api_key', ''),
        'baichuan_enabled': chinese.get('baichuan', {}).get('enabled', False),
    })
    report = ds.get_cost_report()
    print(f\"  GLM: \${report['glm']['daily_cost']:.4f} today (\${report['glm']['total_cost']:.4f} total)\")
    print(f\"  DeepSeek: \${report['baichuan']['daily_cost']:.4f} today (\${report['baichuan']['total_cost']:.4f} total)\")
    print(f\"  Total Daily: \${report['total_daily_cost']:.4f}\")
    print(f\"  Monthly Estimate: \${report['total_monthly_estimate']:.2f}\")
except Exception as e:
    print(f\"  ⚠️  Could not fetch costs: {e}\")
" 2>/dev/null || echo -e "${YELLOW}  ⚠️  Cost tracking not available${NC}"

# Check disk usage
echo -e "\n${BLUE}💾 Disk Usage:${NC}"
du -sh argo/baselines argo/reports argo/logs 2>/dev/null | awk '{print "  " $2 ": " $1}' || echo "  No data directories"

# Check latest baseline
echo -e "\n${BLUE}📈 Latest Metrics:${NC}"
LATEST_BASELINE=$(find argo/baselines -name "*.json" -type f 2>/dev/null | sort -r | head -1)
if [ -n "$LATEST_BASELINE" ]; then
    echo "  Latest baseline: $(basename $LATEST_BASELINE)"
    cat "$LATEST_BASELINE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"  Version: {data.get('version', 'unknown')}\")
print(f\"  Timestamp: {data.get('timestamp', 'unknown')}\")
print(f\"  Signal Gen Avg: {data.get('signal_generation_avg_ms', 0):.2f}ms\")
print(f\"  Cache Hit Rate: {data.get('cache_hit_rate', 0):.1f}%\")
print(f\"  Error Rate: {data.get('error_rate', 0):.2f}%\")
" 2>/dev/null || echo "  Could not parse baseline"
else
    echo "  No baseline files found"
fi

# Check logs for errors
echo -e "\n${BLUE}📋 Recent Errors:${NC}"
if [ -d "argo/logs" ]; then
    ERROR_COUNT=$(grep -i "error\|exception\|failed" argo/logs/*.log 2>/dev/null | tail -5 | wc -l | tr -d ' ')
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}  ⚠️  Found $ERROR_COUNT recent errors${NC}"
        grep -i "error\|exception\|failed" argo/logs/*.log 2>/dev/null | tail -3 | sed 's/^/    /'
    else
        echo -e "${GREEN}  ✅ No recent errors${NC}"
    fi
else
    echo "  No logs directory"
fi

# System resources
echo -e "\n${BLUE}🖥️  System Resources:${NC}"
if command -v htop &> /dev/null || command -v top &> /dev/null; then
    echo "  CPU: $(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//' || echo 'N/A')"
    echo "  Memory: $(vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages\s+([^:]+)[^\d]+(\d+)/ and printf("%.1f%%\n", $2 * $size / 1024 / 1024 / 1024 / 16 * 100)')"
else
    echo "  Resource monitoring not available"
fi

echo -e "\n${GREEN}✅ Monitoring complete${NC}"
echo -e "\n💡 Tips:"
echo "  - View logs: tail -f argo/logs/*.log"
echo "  - Check health: ./scripts/health_check.sh"
echo "  - View costs: Check API cost reports above"

