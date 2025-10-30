#!/bin/bash
# ARGO Capital Master System Startup

echo "🚀 ARGO Capital Complete System Startup"
echo "========================================"

# Start databases
echo "1. Starting database systems..."
cd 70database/redis && ./setup_redis.sh &
cd ../clickhouse && ./setup_clickhouse.sh &
cd ../..

# Wait for databases to start
sleep 10

# Start communication hub
echo "2. Starting communication hub..."
python3 80communication/argo_system_hub.py &
HUB_PID=$!

# Start main scheduler
echo "3. Starting main scheduler..."
python3 autoscheduler.py &
SCHEDULER_PID=$!

# Start dashboards
echo "4. Starting dashboard suite..."
cd 50monitoring
streamlit run argodarkultimate.py --server.port 8501 &
DASHBOARD_PID=$!
cd ..

# Wait a moment
sleep 5

# Run system check
echo "5. Running system validation..."
./complete_system_check.sh

echo "✅ ARGO Capital System Startup Complete!"
echo "📊 Access points:"
echo "   • Command Center: http://localhost:8501"
echo "   • ClickHouse: http://localhost:8123"
echo "   • Redis: localhost:6379"
echo "   • PowerBI: Your workspace online"

# Save PIDs for later management
echo "$HUB_PID" > system_hub.pid
echo "$SCHEDULER_PID" > scheduler.pid
echo "$DASHBOARD_PID" > dashboard.pid

