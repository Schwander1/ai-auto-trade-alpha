#!/bin/bash
set -e

echo "🚀 COMPLETE ARGO DEPLOYMENT - ALL FEATURES"
echo "==========================================="

cd ~/argo-production

# Stop containers
docker compose down

# Rebuild with all new code
echo "🔨 Building Docker image..."
docker compose build --no-cache

# Start containers
docker compose up -d

# Wait for startup
echo "⏳ Waiting for API to start (30 seconds)..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health &>/dev/null; then
        echo "✅ API started after $i seconds!"
        break
    fi
    sleep 1
done

sleep 5

# Test all endpoints
echo ""
echo "📊 TESTING ALL ENDPOINTS:"
echo "========================="

echo ""
echo "1️⃣  Health:"
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "2️⃣  Crypto Signals:"
curl -s http://localhost:8000/api/v1/signals/crypto | python3 -m json.tool | head -30

echo ""
echo "3️⃣  Stock Signals:"
curl -s http://localhost:8000/api/v1/signals/stocks | python3 -m json.tool | head -30

echo ""
echo "4️⃣  Premium Tier:"
curl -s http://localhost:8000/api/v1/signals/tier/premium | python3 -m json.tool | head -25

echo ""
echo "5️⃣  Stats:"
curl -s http://localhost:8000/api/v1/stats | python3 -m json.tool

echo ""
echo "6️⃣  Metrics (Prometheus):"
curl -s http://localhost:8000/metrics | grep "argo_" | head -10

echo ""
echo "7️⃣  Live Signal (if endpoint exists):"
curl -s http://localhost:8000/api/v1/signals/live/AAPL 2>/dev/null | python3 -m json.tool || echo "Live endpoint not yet added"

echo ""
echo "==========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "==========================================="
