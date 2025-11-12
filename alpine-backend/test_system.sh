#!/bin/bash

echo "==================================="
echo "🚀 COMPLETE SYSTEM VERIFICATION"
echo "==================================="
echo ""

echo "1️⃣ ARGO SERVER CHECK"
echo "-----------------------------------"
echo "Testing: http://178.156.194.174:8000"
ARGO_HEALTH=$(curl -s http://178.156.194.174:8000/health)
if echo "$ARGO_HEALTH" | grep -q "healthy"; then
  echo "✅ Argo API: HEALTHY"
  echo "   $ARGO_HEALTH" | python3 -m json.tool | grep -E '(status|ai_enabled)'
else
  echo "❌ Argo API: DOWN"
fi
echo ""

echo "Testing: Argo signal generation"
ARGO_SIGNAL=$(curl -s "http://178.156.194.174:8000/api/signals/latest?limit=1")
if echo "$ARGO_SIGNAL" | grep -q "symbol"; then
  echo "✅ Argo Signals: WORKING"
  echo "   Sample signal:"
  echo "$ARGO_SIGNAL" | python3 -m json.tool | head -10
else
  echo "❌ Argo Signals: FAILED"
fi
echo ""

echo "2️⃣ ALPINE BACKEND INSTANCES"
echo "-----------------------------------"
for port in 8001 8002 8003; do
  STATUS=$(curl -s http://localhost:$port/api/health 2>/dev/null)
  if echo "$STATUS" | grep -q "healthy"; then
    echo "✅ Backend-$((port-8000)): HEALTHY (port $port)"
  else
    echo "❌ Backend-$((port-8000)): DOWN (port $port)"
  fi
done
echo ""

echo "3️⃣ ALPINE FRONTEND INSTANCES"
echo "-----------------------------------"
if curl -s http://localhost:3000 2>/dev/null | grep -q "Alpine"; then
  echo "✅ Frontend-1: HEALTHY (port 3000)"
else
  echo "❌ Frontend-1: DOWN (port 3000)"
fi

if curl -s http://localhost:3002 2>/dev/null | grep -q "Alpine"; then
  echo "✅ Frontend-2: HEALTHY (port 3002)"
else
  echo "❌ Frontend-2: DOWN (port 3002)"
fi
echo ""

echo "4️⃣ NGINX LOAD BALANCER"
echo "-----------------------------------"
NGINX_HEALTH=$(curl -s http://91.98.153.49/health 2>/dev/null)
if echo "$NGINX_HEALTH" | grep -q "healthy"; then
  echo "✅ Nginx → Backend: CONNECTED"
else
  echo "⚠️  Nginx → Backend: CHECK NEEDED"
  echo "   Response: $NGINX_HEALTH"
fi
echo ""

echo "5️⃣ END-TO-END SIGNAL FLOW"
echo "-----------------------------------"
echo "Testing: Argo → Alpine → Nginx → Public"
SIGNALS=$(curl -s "http://91.98.153.49/api/signals?limit=1" 2>/dev/null)
if echo "$SIGNALS" | grep -q "symbol"; then
  echo "✅ Complete Flow: WORKING"
  echo "   Signal received with explanation:"
  echo "$SIGNALS" | python3 -m json.tool | head -15
else
  echo "❌ Complete Flow: BROKEN"
  echo "   Response: $SIGNALS"
fi
echo ""

echo "6️⃣ MONITORING STACK"
echo "-----------------------------------"
if curl -s http://91.98.153.49:9090/-/healthy 2>/dev/null | grep -q "Healthy"; then
  echo "✅ Prometheus: HEALTHY"
else
  echo "⚠️  Prometheus: CHECK NEEDED"
fi

if curl -s http://91.98.153.49:3001/api/health 2>/dev/null | grep -q "database"; then
  echo "✅ Grafana: HEALTHY"
else
  echo "⚠️  Grafana: CHECK NEEDED"
fi
echo ""

echo "7️⃣ DATABASE & CACHE"
echo "-----------------------------------"
if docker compose -f docker-compose.production.yml ps | grep -q "postgres.*Up"; then
  echo "✅ PostgreSQL: RUNNING (port 5433)"
else
  echo "❌ PostgreSQL: DOWN"
fi

if docker compose -f docker-compose.production.yml ps | grep -q "redis.*Up"; then
  echo "✅ Redis: RUNNING (port 6380)"
else
  echo "❌ Redis: DOWN"
fi
echo ""

echo "==================================="
echo "📊 SUMMARY"
echo "==================================="
TOTAL=$(docker compose -f docker-compose.production.yml ps | grep -c "Up")
echo "Containers Running: $TOTAL / 13"
echo ""
echo "🌐 PUBLIC ACCESS URLS:"
echo "   Homepage:    http://91.98.153.49"
echo "   Dashboard:   http://91.98.153.49/dashboard"
echo "   Grafana:     http://91.98.153.49/grafana"
echo "   Prometheus:  http://91.98.153.49:9090"
echo ""
if [ $TOTAL -eq 13 ]; then
  echo "✅ System Status: FULLY OPERATIONAL"
  echo "🎉 YOUR PLATFORM IS READY FOR CUSTOMERS!"
else
  echo "⚠️  System Status: $TOTAL/13 containers running"
  echo "   Run: docker compose -f docker-compose.production.yml ps"
fi
echo "==================================="
