#!/bin/bash

echo "🔍 VERIFYING SYSTEM"
echo "==================="
echo ""

echo "Files:"
[ -f argo/tracking/__init__.py ] && echo "✅ tracking/__init__.py" || echo "❌ MISSING"
[ -f argo/tracking/unified_tracker.py ] && echo "✅ unified_tracker.py" || echo "❌ MISSING"
[ -f argo/api/performance.py ] && echo "✅ performance.py" || echo "❌ MISSING"
[ -f test_performance_tracking.py ] && echo "✅ test script" || echo "❌ MISSING"

echo ""
echo "API Server:"
if docker compose ps | grep -q "argo-api.*Up"; then
    echo "✅ Running"
else
    echo "⚠️ Not running"
fi

echo ""
echo "Endpoints:"
curl -s http://localhost:8000/health >/dev/null 2>&1 && echo "✅ /health" || echo "❌ /health"
curl -s http://localhost:8000/api/performance/stats >/dev/null 2>&1 && echo "✅ /api/performance/stats" || echo "⚠️ /api/performance/stats"

echo ""
echo "==================="
echo "✅ Done"
