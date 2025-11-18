#!/bin/bash
# Verify Unified Architecture Deployment
# Checks all services, health endpoints, and database

set -e

PRODUCTION_SERVER="178.156.194.174"
PRODUCTION_USER="root"

echo "🔍 Verifying Unified Architecture Deployment"
echo "=============================================="
echo ""

# Check service status
echo "📊 Service Status:"
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
echo "Signal Generator:"
systemctl is-active argo-signal-generator.service && echo "  ✅ ACTIVE" || echo "  ❌ INACTIVE"

echo "Argo Executor:"
systemctl is-active argo-trading-executor.service && echo "  ✅ ACTIVE" || echo "  ❌ INACTIVE"

echo "Prop Firm Executor:"
systemctl is-active argo-prop-firm-executor.service && echo "  ✅ ACTIVE" || echo "  ❌ INACTIVE"
ENDSSH

echo ""
echo "🏥 Health Checks:"
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
echo "Signal Generator (7999):"
curl -s -f http://localhost:7999/health && echo "  ✅ HEALTHY" || echo "  ❌ UNHEALTHY"

echo "Argo Executor (8000):"
curl -s -f http://localhost:8000/health && echo "  ✅ HEALTHY" || echo "  ❌ UNHEALTHY"

echo "Prop Firm Executor (8001):"
curl -s -f http://localhost:8001/health && echo "  ✅ HEALTHY" || echo "  ❌ UNHEALTHY"
ENDSSH

echo ""
echo "💾 Database Status:"
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
sqlite3 /root/argo-production-unified/data/signals_unified.db << 'SQL'
SELECT 
    COUNT(*) as total_signals,
    COUNT(DISTINCT service_type) as service_types,
    COUNT(*) FILTER (WHERE created_at >= datetime('now', '-1 hour')) as signals_last_hour,
    COUNT(*) FILTER (WHERE created_at >= datetime('now', '-5 minutes')) as signals_last_5min
FROM signals;
SQL
ENDSSH

echo ""
echo "📈 Recent Activity:"
ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
echo "Signal Generator logs (last 5 lines):"
journalctl -u argo-signal-generator.service -n 5 --no-pager | tail -3

echo ""
echo "Argo Executor logs (last 3 lines):"
journalctl -u argo-trading-executor.service -n 3 --no-pager | tail -2

echo ""
echo "Prop Firm Executor logs (last 3 lines):"
journalctl -u argo-prop-firm-executor.service -n 3 --no-pager | tail -2
ENDSSH

echo ""
echo "✅ Verification complete!"

