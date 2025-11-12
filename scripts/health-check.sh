#!/bin/bash

# Health check script for all services
# Verifies all production services are running and healthy

echo "🏥 Health Check - All Services"
echo "=============================="
echo ""

EXIT_CODE=0

# Check Argo
echo "🔍 Checking Argo (178.156.194.174:8000)..."
if curl -f -s --max-time 5 http://178.156.194.174:8000/health > /dev/null; then
  HEALTH=$(curl -s --max-time 5 http://178.156.194.174:8000/health)
  STATUS=$(echo $HEALTH | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('status', 'unknown'))" 2>/dev/null || echo "unknown")
  echo "   ✅ Status: $STATUS"
  
  # Check /api/signals/latest
  SIGNALS=$(curl -s --max-time 5 "http://178.156.194.174:8000/api/signals/latest?limit=1")
  if echo "$SIGNALS" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if isinstance(d, list) else 1)" 2>/dev/null; then
    echo "   ✅ /api/signals/latest: Returns array"
  else
    echo "   ⚠️  /api/signals/latest: May not return array"
    EXIT_CODE=1
  fi
else
  echo "   ❌ Not responding"
  EXIT_CODE=1
fi

echo ""

# Check Alpine Backend
echo "🔍 Checking Alpine Backend (91.98.153.49:8001)..."
if curl -f -s --max-time 5 http://91.98.153.49:8001/health > /dev/null; then
  HEALTH=$(curl -s --max-time 5 http://91.98.153.49:8001/health)
  STATUS=$(echo $HEALTH | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('status', 'unknown'))" 2>/dev/null || echo "unknown")
  echo "   ✅ Status: $STATUS"
else
  echo "   ❌ Not responding"
  EXIT_CODE=1
fi

echo ""

# Check Alpine Frontend
echo "🔍 Checking Alpine Frontend (91.98.153.49:3000)..."
if curl -f -s --max-time 5 http://91.98.153.49:3000 > /dev/null; then
  echo "   ✅ Responding"
else
  echo "   ❌ Not responding"
  EXIT_CODE=1
fi

echo ""

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ All services healthy!"
else
  echo "❌ Some services are unhealthy"
fi

exit $EXIT_CODE

