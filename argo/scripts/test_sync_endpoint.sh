#!/bin/bash
# Test Alpine Backend Sync Endpoint
# This script tests the signal sync endpoint directly

ALPINE_URL="${ALPINE_API_URL:-http://91.98.153.49:8001}"
API_KEY="${ARGO_API_KEY:-test-key}"

echo "=========================================="
echo "Testing Alpine Backend Sync Endpoint"
echo "=========================================="
echo "Alpine URL: $ALPINE_URL"
echo "API Key: ${API_KEY:0:8}..."
echo ""

# Test 1: Health check
echo "1. Testing Alpine backend health..."
HEALTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$ALPINE_URL/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$HEALTH_RESPONSE" | sed '/HTTP_CODE/d')
echo "   Status: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Alpine backend is healthy"
    echo "$BODY" | python3 -m json.tool 2>/dev/null | head -5
else
    echo "   ❌ Alpine backend health check failed"
fi
echo ""

# Test 2: Check if sync endpoint exists
echo "2. Testing sync health endpoint..."
SYNC_HEALTH=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$ALPINE_URL/api/v1/external-signals/sync/health")
SYNC_HTTP_CODE=$(echo "$SYNC_HEALTH" | grep "HTTP_CODE" | cut -d: -f2)
SYNC_BODY=$(echo "$SYNC_HEALTH" | sed '/HTTP_CODE/d')
echo "   Status: $SYNC_HTTP_CODE"
if [ "$SYNC_HTTP_CODE" = "200" ]; then
    echo "   ✅ Sync health endpoint is accessible"
    echo "$SYNC_BODY" | python3 -m json.tool 2>/dev/null
else
    echo "   ❌ Sync health endpoint returned $SYNC_HTTP_CODE"
    echo "   Response: $SYNC_BODY"
fi
echo ""

# Test 3: Test sync endpoint with test signal
echo "3. Testing sync signal endpoint..."
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TEST_SIGNAL=$(cat <<EOF
{
  "signal_id": "test-$(date +%s)",
  "symbol": "AAPL",
  "action": "BUY",
  "entry_price": 175.50,
  "target_price": 184.25,
  "stop_price": 171.00,
  "confidence": 95.5,
  "strategy": "test",
  "timestamp": "$TIMESTAMP",
  "sha256": "test-hash-1234567890abcdef"
}
EOF
)

SYNC_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -X POST "$ALPINE_URL/api/v1/external-signals/sync/signal" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d "$TEST_SIGNAL")

SYNC_RESPONSE_CODE=$(echo "$SYNC_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
SYNC_RESPONSE_BODY=$(echo "$SYNC_RESPONSE" | sed '/HTTP_CODE/d')

echo "   Status: $SYNC_RESPONSE_CODE"
if [ "$SYNC_RESPONSE_CODE" = "201" ]; then
    echo "   ✅ Signal synced successfully!"
    echo "$SYNC_RESPONSE_BODY" | python3 -m json.tool 2>/dev/null
elif [ "$SYNC_RESPONSE_CODE" = "401" ]; then
    echo "   ⚠️  Authentication failed - check API key"
    echo "   Response: $SYNC_RESPONSE_BODY"
elif [ "$SYNC_RESPONSE_CODE" = "404" ]; then
    echo "   ❌ Endpoint not found - router may not be registered"
    echo "   Response: $SYNC_RESPONSE_BODY"
    echo ""
    echo "   Possible causes:"
    echo "   - Backend needs to be restarted"
    echo "   - Router import is failing silently"
    echo "   - Route path is incorrect"
else
    echo "   ❌ Sync failed with status $SYNC_RESPONSE_CODE"
    echo "   Response: $SYNC_RESPONSE_BODY"
fi
echo ""

# Test 4: Check OpenAPI spec
echo "4. Checking OpenAPI spec for sync routes..."
OPENAPI_PATHS=$(curl -s "$ALPINE_URL/api/v1/openapi.json" | \
    python3 -c "import sys, json; data=json.load(sys.stdin); paths=[p for p in data.get('paths', {}).keys() if 'external' in p.lower() or 'sync' in p.lower()]; print('\n'.join(paths) if paths else 'No matching paths found')" 2>/dev/null)

if [ -n "$OPENAPI_PATHS" ] && [ "$OPENAPI_PATHS" != "No matching paths found" ]; then
    echo "   ✅ Found sync routes in OpenAPI spec:"
    echo "$OPENAPI_PATHS" | sed 's/^/      /'
else
    echo "   ⚠️  No sync routes found in OpenAPI spec"
    echo "   This suggests the router is not being registered"
fi
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Alpine Backend: $([ "$HTTP_CODE" = "200" ] && echo "✅ Healthy" || echo "❌ Unhealthy")"
echo "Sync Endpoint: $([ "$SYNC_HTTP_CODE" = "200" ] && echo "✅ Accessible" || echo "❌ Not accessible ($SYNC_HTTP_CODE)")"
echo "Signal Sync: $([ "$SYNC_RESPONSE_CODE" = "201" ] && echo "✅ Working" || echo "❌ Failed ($SYNC_RESPONSE_CODE)")"
echo ""

if [ "$SYNC_RESPONSE_CODE" = "404" ]; then
    echo "⚠️  RECOMMENDATION: Backend may need to be restarted to load the sync router"
fi

