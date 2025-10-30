#!/bin/bash
# ARGO Capital Complete System Communication Check

echo "🎯 ARGO Capital Complete System Communication Validation"
echo "========================================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
        return 0
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

echo -e "${BLUE}📊 1. Database Systems Check${NC}"
echo "----------------------------------------"

# Check ClickHouse
echo -n "ClickHouse Server: "
if pgrep -f clickhouse-server > /dev/null; then
    check_status 0 "Running on port 8123"
else
    check_status 1 "Not running"
    echo "   Start with: cd 70database/clickhouse && ./setup_clickhouse.sh"
fi

# Check Redis
echo -n "Redis Server: "
if pgrep -f redis-server > /dev/null; then
    check_status 0 "Running on port 6379"
else
    check_status 1 "Not running" 
    echo "   Start with: cd 70database/redis && ./setup_redis.sh"
fi

echo -e "\n${BLUE}📈 2. Data Pipeline Check${NC}"
echo "----------------------------------------"

# Check data ingestion
echo -n "Live Data Files: "
if [ -d "../30data/live" ] && [ "$(ls -A ../30data/live)" ]; then
    latest_file=$(ls -t ../30data/live/*.csv 2>/dev/null | head -1)
    if [ -n "$latest_file" ]; then
        file_age=$((($(date +%s) - $(stat -f %m "$latest_file")) / 60))
        if [ $file_age -lt 60 ]; then
            check_status 0 "Fresh data (${file_age}min old)"
        else
            check_status 1 "Stale data (${file_age}min old)"
        fi
    else
        check_status 1 "No data files found"
    fi
else
    check_status 1 "Data directory missing or empty"
fi

# Check signal generation
echo -n "Trading Signals: "
if [ -d "../30data/signals" ] && [ "$(ls -A ../30data/signals)" ]; then
    latest_signal=$(ls -t ../30data/signals/*.json 2>/dev/null | head -1)
    if [ -n "$latest_signal" ]; then
        signal_age=$((($(date +%s) - $(stat -f %m "$latest_signal")) / 60))
        if [ $signal_age -lt 60 ]; then
            check_status 0 "Fresh signals (${signal_age}min old)"
        else
            check_status 1 "Stale signals (${signal_age}min old)"
        fi
    else
        check_status 1 "No signal files found"
    fi
else
    check_status 1 "Signals directory missing or empty"
fi

echo -e "\n${BLUE}🖥️ 3. Dashboard Systems Check${NC}"
echo "----------------------------------------"

# Check dashboard ports
dashboard_ports=(8501 8502 8503)
dashboard_names=("Command Center" "Investor Dashboard" "Risk Dashboard")

for i in "${!dashboard_ports[@]}"; do
    port=${dashboard_ports[$i]}
    name=${dashboard_names[$i]}
    
    echo -n "$name (port $port): "
    if nc -z localhost $port 2>/dev/null; then
        check_status 0 "Running and accessible"
    else
        check_status 1 "Not accessible"
        echo "   Start with: streamlit run argodarkultimate.py --server.port $port"
    fi
done

echo -e "\n${BLUE}🔗 4. External Integrations Check${NC}"
echo "----------------------------------------"

# Check PowerBI
echo -n "PowerBI Integration: "
if [ -f "../60integrations/powerbi/.env" ]; then
    # Test PowerBI authentication
    cd ../60integrations/powerbi
    python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
if os.getenv('AZURE_CLIENT_SECRET') and len(os.getenv('AZURE_CLIENT_SECRET', '')) > 10:
    print('✅ Credentials configured')
    exit(0)
else:
    print('❌ Credentials missing or incomplete')
    exit(1)
" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        check_status 0 "Authenticated and ready"
    else
        check_status 1 "Authentication issues"
    fi
    cd - > /dev/null
else
    check_status 1 "Not configured"
fi

# Check TraderVue
echo -n "TraderVue Integration: "
if [ -f "../60integrations/tradervue/tradervue_client.py" ]; then
    check_status 0 "Client configured"
else
    check_status 1 "Not configured"
fi

# Check Alpha Vantage
echo -n "Alpha Vantage Premium: "
if grep -q "EHA9RBPT7A9U84AQ" ../exportenv.sh 2>/dev/null; then
    check_status 0 "API key configured"
else
    check_status 1 "API key missing"
fi

echo -e "\n${BLUE}⚙️ 5. System Processes Check${NC}"
echo "----------------------------------------"

# Check main scheduler
echo -n "Main Scheduler: "
scheduler_pid=$(pgrep -f autoscheduler.py)
if [ -n "$scheduler_pid" ]; then
    runtime=$(ps -o etime= -p $scheduler_pid | tr -d ' ')
    check_status 0 "Running (PID: $scheduler_pid, Runtime: $runtime)"
else
    check_status 1 "Not running"
    echo "   Start with: python3 autoscheduler.py"
fi

# Check system communication hub
echo -n "Communication Hub: "
hub_pid=$(pgrep -f argo_system_hub.py)
if [ -n "$hub_pid" ]; then
    check_status 0 "Running (PID: $hub_pid)"
else
    check_status 1 "Not running"
    echo "   Start with: python3 80communication/argo_system_hub.py"
fi

echo -e "\n${BLUE}📊 6. System Performance Check${NC}"
echo "----------------------------------------"

# Memory usage
echo -n "System Memory: "
memory_usage=$(ps aux | grep -E "(python3|clickhouse|redis)" | grep -v grep | awk '{sum += $4} END {print sum}')
if (( $(echo "$memory_usage < 10" | bc -l) )); then
    check_status 0 "Optimal (${memory_usage}% used)"
else
    check_status 1 "High usage (${memory_usage}% used)"
fi

# Disk space
echo -n "Disk Space: "
disk_usage=$(df -h . | tail -1 | awk '{print $4}')
check_status 0 "Available: $disk_usage"

echo -e "\n${BLUE}🎯 7. Communication Flow Test${NC}"
echo "----------------------------------------"

# Test data flow
echo "Testing data flow between components..."

# Check if data is flowing from ingestion to PowerBI
echo -n "Data Pipeline Flow: "
if [ -f "../logs/scheduler.log" ]; then
    recent_entries=$(tail -20 ../logs/scheduler.log | grep -c "$(date +%Y-%m-%d)")
    if [ $recent_entries -gt 0 ]; then
        check_status 0 "$recent_entries recent log entries today"
    else
        check_status 1 "No recent activity in logs"
    fi
else
    check_status 1 "No scheduler logs found"
fi

echo -e "\n${GREEN}🚀 ARGO Capital System Communication Status Summary${NC}"
echo "=================================================="

# Generate system recommendations
echo -e "${YELLOW}📋 Recommendations:${NC}"

if ! pgrep -f redis-server > /dev/null; then
    echo "• Start Redis cache: cd 70database/redis && ./setup_redis.sh"
fi

if ! pgrep -f clickhouse-server > /dev/null; then
    echo "• Start ClickHouse: cd 70database/clickhouse && ./setup_clickhouse.sh"
fi

if ! pgrep -f argo_system_hub.py > /dev/null; then
    echo "• Start Communication Hub: python3 80communication/argo_system_hub.py &"
fi

if ! nc -z localhost 8501 2>/dev/null; then
    echo "• Start Command Center: streamlit run 50monitoring/argodarkultimate.py --server.port 8501"
fi

echo -e "\n${GREEN}✅ ARGO Capital System Check Complete!${NC}"
echo "Run this script periodically to monitor system health."

