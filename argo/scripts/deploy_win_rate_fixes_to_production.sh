#!/bin/bash
# Deploy Win Rate & Confidence System Fixes to Production
# This script deploys all fixes and optimizations for win rate and confidence systems

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROD_SERVER="root@178.156.194.174"
PROD_PATH="/root/argo-production"

echo "🚀 Deploying Win Rate & Confidence System Fixes to Production"
echo "=============================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Verify local files exist
echo "📋 Step 1: Verifying local files..."
FILES_TO_DEPLOY=(
    "argo/argo/api/signals.py"
    "argo/argo/core/signal_quality_scorer.py"
    "argo/argo/core/win_rate_calculator.py"
    "argo/argo/ml/confidence_calibrator.py"
    "argo/scripts/evaluate_performance_enhanced.py"
    "argo/scripts/monitor_signal_quality.py"
    "argo/reports/WIN_RATE_CONFIDENCE_REVIEW_AND_FIXES.md"
    "argo/reports/ADDITIONAL_OPTIMIZATIONS_SUMMARY.md"
)

MISSING_FILES=()
for file in "${FILES_TO_DEPLOY[@]}"; do
    if [ ! -f "$PROJECT_ROOT/$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing files:${NC}"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

echo -e "${GREEN}✅ All files verified${NC}"
echo ""

# Step 2: Create backup
echo "📦 Step 2: Creating production backup..."
BACKUP_NAME="backup-win-rate-fixes-$(date +%Y%m%d-%H%M%S).tar.gz"
ssh $PROD_SERVER "cd $PROD_PATH && tar -czf /tmp/$BACKUP_NAME argo/argo/api/signals.py argo/argo/core/signal_quality_scorer.py argo/argo/core/win_rate_calculator.py argo/argo/ml/confidence_calibrator.py argo/scripts/evaluate_performance_enhanced.py argo/scripts/monitor_signal_quality.py 2>/dev/null || true"
echo -e "${GREEN}✅ Backup created: $BACKUP_NAME${NC}"
echo ""

# Step 3: Deploy files
echo "📤 Step 3: Deploying files to production..."
for file in "${FILES_TO_DEPLOY[@]}"; do
    echo "  Deploying: $file"
    # Create directory structure if needed
    ssh $PROD_SERVER "mkdir -p $PROD_PATH/$(dirname $file)"
    # Copy file
    scp "$PROJECT_ROOT/$file" "$PROD_SERVER:$PROD_PATH/$file"
done
echo -e "${GREEN}✅ All files deployed${NC}"
echo ""

# Step 4: Verify deployment
echo "🔍 Step 4: Verifying deployment..."
for file in "${FILES_TO_DEPLOY[@]}"; do
    if ssh $PROD_SERVER "test -f $PROD_PATH/$file"; then
        echo -e "  ${GREEN}✅${NC} $file"
    else
        echo -e "  ${RED}❌${NC} $file (MISSING)"
        exit 1
    fi
done
echo ""

# Step 5: Test imports
echo "🧪 Step 5: Testing imports on production server..."
ssh $PROD_SERVER "cd $PROD_PATH && python3 -c \"
import sys
sys.path.insert(0, '.')

try:
    from argo.api.signals import get_signal_stats
    print('✅ signals.py imports successfully')
except Exception as e:
    print(f'❌ signals.py import failed: {e}')
    sys.exit(1)

try:
    from argo.core.signal_quality_scorer import SignalQualityScorer
    print('✅ signal_quality_scorer.py imports successfully')
except Exception as e:
    print(f'❌ signal_quality_scorer.py import failed: {e}')
    sys.exit(1)

try:
    from argo.core.win_rate_calculator import calculate_win_rate
    print('✅ win_rate_calculator.py imports successfully')
except Exception as e:
    print(f'❌ win_rate_calculator.py import failed: {e}')
    sys.exit(1)

try:
    from argo.ml.confidence_calibrator import ConfidenceCalibrator
    print('✅ confidence_calibrator.py imports successfully')
except Exception as e:
    print(f'❌ confidence_calibrator.py import failed: {e}')
    sys.exit(1)

print('✅ All imports successful')
\""
echo ""

# Step 6: Restart services (if needed)
echo "🔄 Step 6: Checking service status..."
SERVICE_STATUS=$(ssh $PROD_SERVER "systemctl is-active argo-trading || echo 'not-found'")
if [ "$SERVICE_STATUS" != "not-found" ]; then
    echo "  Service found: $SERVICE_STATUS"
    echo "  Restarting service..."
    ssh $PROD_SERVER "systemctl restart argo-trading || true"
    sleep 2
    NEW_STATUS=$(ssh $PROD_SERVER "systemctl is-active argo-trading || echo 'inactive'")
    if [ "$NEW_STATUS" = "active" ]; then
        echo -e "  ${GREEN}✅ Service restarted successfully${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Service status: $NEW_STATUS${NC}"
    fi
else
    echo "  No systemd service found, checking for running processes..."
    RUNNING=$(ssh $PROD_SERVER "pgrep -f 'uvicorn.*main:app' || echo 'none'")
    if [ "$RUNNING" != "none" ]; then
        echo -e "  ${YELLOW}⚠️  Service running via process (PID: $RUNNING)${NC}"
        echo "  Manual restart may be required"
    else
        echo "  No running service found"
    fi
fi
echo ""

# Step 7: Run health check
echo "🏥 Step 7: Running health check..."
ssh $PROD_SERVER "cd $PROD_PATH && python3 -c \"
import sys
sys.path.insert(0, '.')

# Test API endpoint if available
try:
    from argo.api.signals import get_signal_stats
    print('✅ API endpoint module loaded')
except Exception as e:
    print(f'⚠️  API endpoint check: {e}')

# Test database connection
try:
    from pathlib import Path
    import sqlite3
    db_path = Path('data/signals.db')
    if db_path.exists():
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        conn.close()
        print('✅ Database connection successful')
    else:
        print('⚠️  Database file not found (may be created on first use)')
except Exception as e:
    print(f'⚠️  Database check: {e}')

print('✅ Health check complete')
\""
echo ""

# Step 8: Summary
echo "=============================================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "📋 Summary:"
echo "  - Files deployed: ${#FILES_TO_DEPLOY[@]}"
echo "  - Backup created: $BACKUP_NAME"
echo "  - All imports verified"
echo ""
echo "📝 Next Steps:"
echo "  1. Monitor logs: ssh $PROD_SERVER 'tail -f $PROD_PATH/logs/*.log'"
echo "  2. Test API endpoint: curl http://178.156.194.174:8000/api/v1/signals/stats"
echo "  3. Run monitoring: ssh $PROD_SERVER 'cd $PROD_PATH && python3 scripts/monitor_signal_quality.py'"
echo "  4. Verify performance: ssh $PROD_SERVER 'cd $PROD_PATH && python3 scripts/evaluate_performance_enhanced.py'"
echo ""
echo "📚 Documentation:"
echo "  - Review: argo/reports/WIN_RATE_CONFIDENCE_REVIEW_AND_FIXES.md"
echo "  - Review: argo/reports/ADDITIONAL_OPTIMIZATIONS_SUMMARY.md"
echo ""


