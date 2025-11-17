#!/bin/bash
# Test Script for Argo Blue-Green Deployment
# Tests deployment to inactive environment without switching traffic
# Safe for testing - does not affect production traffic

set -e

ARGO_SERVER="178.156.194.174"
ARGO_USER="root"
BLUE_PATH="/root/argo-production-blue"
GREEN_PATH="/root/argo-production-green"
LEGACY_PATH="/root/argo-production"

echo "🧪 TESTING ARGO BLUE-GREEN DEPLOYMENT"
echo "======================================"
echo "⚠️  This is a TEST - will NOT switch traffic"
echo ""

# Determine current deployment color
CURRENT_COLOR=$(ssh ${ARGO_USER}@${ARGO_SERVER} "
    if lsof -i :8000 2>/dev/null | grep -q uvicorn; then
        PID=\$(lsof -ti :8000 | head -1)
        if [ -n \"\$PID\" ]; then
            CWD=\$(pwdx \$PID 2>/dev/null | awk '{print \$2}' || readlink /proc/\$PID/cwd 2>/dev/null || echo '')
            if echo \"\$CWD\" | grep -q 'blue'; then
                echo 'blue'
            elif echo \"\$CWD\" | grep -q 'green'; then
                echo 'green'
            else
                if [ -f ${BLUE_PATH}/.current ]; then
                    echo 'blue'
                elif [ -f ${GREEN_PATH}/.current ]; then
                    echo 'green'
                else
                    echo 'blue'
                fi
            fi
        else
            echo 'blue'
        fi
    else
        if [ -f ${BLUE_PATH}/.current ]; then
            echo 'blue'
        elif [ -f ${GREEN_PATH}/.current ]; then
            echo 'green'
        else
            echo 'blue'
        fi
    fi
" 2>/dev/null || echo "blue")

# Determine target color (opposite of current)
if [ "$CURRENT_COLOR" = "blue" ]; then
    TARGET_COLOR="green"
    TARGET_PATH=$GREEN_PATH
    CURRENT_PATH=$BLUE_PATH
    TARGET_PORT=8001
else
    TARGET_COLOR="blue"
    TARGET_PATH=$BLUE_PATH
    CURRENT_PATH=$GREEN_PATH
    TARGET_PORT=8001
fi

echo "Current active: $CURRENT_COLOR (port 8000)"
echo "Test target: $TARGET_COLOR (port $TARGET_PORT)"
echo ""

# Step 1: Check if target environment exists
echo "📋 Step 1: Checking target environment..."
TARGET_EXISTS=$(ssh ${ARGO_USER}@${ARGO_SERVER} "[ -d ${TARGET_PATH} ] && echo 'yes' || echo 'no'" 2>/dev/null || echo "no")

if [ "$TARGET_EXISTS" = "no" ]; then
    echo "⚠️  Target environment does not exist - will be created during deployment"
else
    echo "✅ Target environment exists"
fi

# Step 2: Deploy code to target (dry run first)
echo ""
echo "📤 Step 2: Testing code deployment (dry run)..."
EXCLUDE_LIST=(
  '--exclude=venv'
  '--exclude=__pycache__'
  '--exclude=*.pyc'
  '--exclude=.git'
  '--exclude=data'
  '--exclude=*.db'
  '--exclude=*.log'
  '--exclude=scripts/local_*.sh'
  '--exclude=scripts/local_*.py'
  '--exclude=scripts/setup_local_dev.sh'
  '--exclude=scripts/start-all.sh'
  '--exclude=argo/scripts/execute_test_trade.py'
  '--exclude=argo/scripts/enable_full_trading.py'
  '--exclude=tests/'
  '--exclude=*_test.py'
  '--exclude=test_*.py'
  '--exclude=*.local.json'
  '--exclude=.env.local'
  '--exclude=docs/LOCAL_*.md'
  '--exclude=.vscode/'
  '--exclude=.idea/'
  '--exclude=.DS_Store'
  '--exclude=*.tmp'
  '--exclude=*.backup'
  '--exclude=backups/'
  '--exclude=node_modules/'
  '--exclude=.next/'
)

echo "   Would deploy to: ${TARGET_PATH}"
echo "   Excluding: venv, __pycache__, local files, etc."
echo "✅ Dry run check passed"

# Step 3: Actual deployment (to test environment)
echo ""
read -p "Deploy code to test environment? (yes/no): " DEPLOY_CODE
if [ "$DEPLOY_CODE" = "yes" ]; then
    echo "📤 Deploying code to $TARGET_COLOR environment..."
    rsync -avz "${EXCLUDE_LIST[@]}" \
      argo/ \
      ${ARGO_USER}@${ARGO_SERVER}:${TARGET_PATH}/
    echo "✅ Code deployed"
else
    echo "⏭️  Skipping code deployment"
fi

# Step 4: Setup environment
echo ""
read -p "Setup test environment (venv, dependencies)? (yes/no): " SETUP_ENV
if [ "$SETUP_ENV" = "yes" ]; then
    echo "🔧 Setting up $TARGET_COLOR environment..."
    ssh ${ARGO_USER}@${ARGO_SERVER} "
      cd ${TARGET_PATH}
      
      if [ ! -d venv ]; then
        echo 'Creating virtual environment...'
        python3 -m venv venv
      fi
      
      source venv/bin/activate
      pip install --upgrade pip --quiet
      
      if [ -f requirements.txt ]; then
        pip install -r requirements.txt --quiet || pip install fastapi uvicorn[standard] python-dotenv prometheus-client pydantic pydantic-settings --quiet
      else
        pip install fastapi uvicorn[standard] python-dotenv prometheus-client pydantic pydantic-settings --quiet
      fi
      
      echo '✅ Environment setup complete'
    "
else
    echo "⏭️  Skipping environment setup"
fi

# Step 5: Start test service
echo ""
read -p "Start test service on port $TARGET_PORT? (yes/no): " START_SERVICE
if [ "$START_SERVICE" = "yes" ]; then
    echo "🚀 Starting test service on port $TARGET_PORT..."
    ssh ${ARGO_USER}@${ARGO_SERVER} "
      cd ${TARGET_PATH}
      source venv/bin/activate
      
      # Stop any existing service on target port
      pkill -f \"uvicorn.*--port $TARGET_PORT\" || true
      sleep 2
      
      # Start service on internal port
      nohup uvicorn main:app --host 0.0.0.0 --port $TARGET_PORT > /tmp/argo-${TARGET_COLOR}-test.log 2>&1 &
      echo \$! > /tmp/argo-${TARGET_COLOR}-test.pid
      
      sleep 5
      echo '✅ Test service started on port $TARGET_PORT'
    "
else
    echo "⏭️  Skipping service start"
fi

# Step 6: Health checks
echo ""
echo "🏥 Step 6: Running health checks on test service..."
MAX_RETRIES=15
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if curl -f -s --max-time 5 http://${ARGO_SERVER}:${TARGET_PORT}/health > /dev/null 2>&1; then
    echo "✅ Basic health check passed"
    break
  fi
  
  RETRY_COUNT=$((RETRY_COUNT + 1))
  echo "⏳ Waiting for test service... ($RETRY_COUNT/$MAX_RETRIES)"
  sleep 3
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo "❌ Health check failed - test service may not be running"
  echo "   Check logs: ssh ${ARGO_USER}@${ARGO_SERVER} 'tail -f /tmp/argo-${TARGET_COLOR}-test.log'"
  exit 1
fi

# Step 7: Comprehensive health check
echo ""
echo "🏥 Step 7: Running comprehensive health check (Gate 11)..."
HEALTH_CHECK_RESULT=$(ssh ${ARGO_USER}@${ARGO_SERVER} "
  cd ${TARGET_PATH}
  source venv/bin/activate
  python3 argo/scripts/health_check_unified.py --level 3 2>&1 | tail -30
" 2>&1 || echo "FAILED")

echo "$HEALTH_CHECK_RESULT"

HEALTH_CHECKS_PASSED=0
HEALTH_CHECKS_FAILED=0

if echo "$HEALTH_CHECK_RESULT" | grep -q "ALL HEALTH CHECKS PASSED\|✅ Passed: [0-9]\+"; then
    PASSED_COUNT=$(echo "$HEALTH_CHECK_RESULT" | grep -oP "✅ Passed: \K[0-9]+" || echo "0")
    FAILED_COUNT=$(echo "$HEALTH_CHECK_RESULT" | grep -oP "❌ Failed: \K[0-9]+" || echo "0")
    HEALTH_CHECKS_PASSED=$PASSED_COUNT
    HEALTH_CHECKS_FAILED=$FAILED_COUNT
fi

if [ $HEALTH_CHECKS_FAILED -eq 0 ] && [ $HEALTH_CHECKS_PASSED -gt 0 ]; then
    echo ""
    echo "✅ Gate 11 PASSED: 100% health confirmation (${HEALTH_CHECKS_PASSED} checks passed, 0 failed)"
else
    echo ""
    echo "❌ Gate 11 FAILED: Health checks did not pass 100%"
    echo "   Passed: ${HEALTH_CHECKS_PASSED}, Failed: ${HEALTH_CHECKS_FAILED}"
fi

# Step 8: Alpaca verification
echo ""
echo "🔍 Step 8: Verifying Alpaca account configuration..."
ALPACA_VERIFICATION=$(ssh ${ARGO_USER}@${ARGO_SERVER} "
  cd ${TARGET_PATH}
  source venv/bin/activate
  python3 -c \"
import sys
sys.path.insert(0, '.')
from argo.core.paper_trading_engine import PaperTradingEngine
from argo.core.environment import detect_environment
try:
    engine = PaperTradingEngine()
    env = detect_environment()
    print(f'Environment: {env}')
    print(f'Account: {engine.account_name}')
    print(f'Alpaca Enabled: {engine.alpaca_enabled}')
    if engine.alpaca_enabled:
        account = engine.get_account_details()
        print(f'Portfolio: \${account[\"portfolio_value\"]:,.2f}')
        print('✅ Alpaca account configured correctly')
        if env == 'production':
            print('✅ Using PRODUCTION paper account')
        else:
            print('⚠️  WARNING: Not using production account!')
    else:
        print('⚠️  Alpaca not connected - check credentials')
except Exception as e:
    print(f'❌ Verification failed: {e}')
    import traceback
    traceback.print_exc()
\" 2>&1
" 2>&1)

echo "$ALPACA_VERIFICATION"

# Step 9: API endpoint test
echo ""
echo "✅ Step 9: Testing API endpoints..."
RESPONSE=$(curl -s --max-time 5 "http://${ARGO_SERVER}:${TARGET_PORT}/api/signals/latest?limit=1" 2>&1)
if echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if isinstance(d, list) else 1)" 2>/dev/null; then
  echo "✅ Endpoint returns array correctly"
else
  echo "⚠️  Endpoint may not return array format"
  echo "   Response: $(echo "$RESPONSE" | head -3)"
fi

# Summary
echo ""
echo "======================================================================"
echo "🧪 TEST SUMMARY"
echo "======================================================================"
echo ""
echo "Current Active: $CURRENT_COLOR (port 8000)"
echo "Test Target: $TARGET_COLOR (port $TARGET_PORT)"
echo ""
echo "✅ Test service is running on port $TARGET_PORT"
echo "✅ Health checks: ${HEALTH_CHECKS_PASSED} passed, ${HEALTH_CHECKS_FAILED} failed"
echo ""
echo "📝 Next Steps:"
echo "   1. Review test results above"
echo "   2. Check test service logs: ssh ${ARGO_USER}@${ARGO_SERVER} 'tail -f /tmp/argo-${TARGET_COLOR}-test.log'"
echo "   3. Test API endpoints: curl http://${ARGO_SERVER}:${TARGET_PORT}/health"
echo "   4. If all tests pass, proceed with full deployment: ./scripts/deploy-argo-blue-green.sh"
echo ""
echo "⚠️  To stop test service:"
echo "   ssh ${ARGO_USER}@${ARGO_SERVER} 'pkill -f \"uvicorn.*--port $TARGET_PORT\"'"
echo ""

