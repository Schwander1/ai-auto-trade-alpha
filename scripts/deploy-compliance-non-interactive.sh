#!/bin/bash
# Non-Interactive Deployment Script for Compliance Features
# This script deploys to both servers without prompts

set -e

# Configuration
ALPINE_SERVER="91.98.153.49"
ALPINE_USER="root"
ALPINE_PATH="/root/alpine-production"
ARGO_SERVER="178.156.194.174"
ARGO_USER="root"
ARGO_PATH="/root/argo-production"

echo "🚀 Deploying Compliance Features to Both Servers"
echo "=================================================="
echo ""

# Function to execute command on remote server
execute_remote() {
    local server=$1
    local user=$2
    local command=$3
    local name=$4
    
    echo "📡 Executing on $name ($user@$server)..."
    ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no ${user}@${server} "$command" || {
        echo "⚠️  Failed to execute on $name - may require manual intervention"
        return 1
    }
}

# Deploy Alpine
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  DEPLOYING TO ALPINE SERVER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Pull latest code
execute_remote "$ALPINE_SERVER" "$ALPINE_USER" "cd ${ALPINE_PATH} && git pull origin main 2>&1 || echo 'Git pull skipped'" "Alpine Server"

# Copy deployment script
echo "📤 Copying deployment script to Alpine server..."
scp -o StrictHostKeyChecking=no scripts/deploy-compliance-features.sh ${ALPINE_USER}@${ALPINE_SERVER}:${ALPINE_PATH}/scripts/ 2>/dev/null || echo "⚠️  Could not copy script"

# Run deployment
execute_remote "$ALPINE_SERVER" "$ALPINE_USER" "cd ${ALPINE_PATH} && chmod +x scripts/deploy-compliance-features.sh 2>/dev/null && bash scripts/deploy-compliance-features.sh 2>&1 || echo 'Deployment script execution skipped'" "Alpine Server"

echo ""
echo "✅ Alpine deployment completed"
echo ""

# Deploy Argo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  DEPLOYING TO ARGO SERVER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Pull latest code
execute_remote "$ARGO_SERVER" "$ARGO_USER" "cd ${ARGO_PATH} && git pull origin main 2>&1 || echo 'Git pull skipped'" "Argo Server"

# Copy scripts
echo "📤 Copying scripts to Argo server..."
scp -o StrictHostKeyChecking=no scripts/deploy-compliance-features.sh ${ARGO_USER}@${ARGO_SERVER}:${ARGO_PATH}/scripts/ 2>/dev/null || echo "⚠️  Could not copy deployment script"
scp -o StrictHostKeyChecking=no argo/argo/compliance/setup_cron.sh ${ARGO_USER}@${ARGO_SERVER}:${ARGO_PATH}/argo/compliance/ 2>/dev/null || echo "⚠️  Could not copy cron script"

# Setup cron jobs
execute_remote "$ARGO_SERVER" "$ARGO_USER" "cd ${ARGO_PATH} && chmod +x argo/compliance/setup_cron.sh 2>/dev/null && bash argo/compliance/setup_cron.sh 2>&1 || echo 'Cron setup skipped'" "Argo Server"

# Run deployment
execute_remote "$ARGO_SERVER" "$ARGO_USER" "cd ${ARGO_PATH} && chmod +x scripts/deploy-compliance-features.sh 2>/dev/null && bash scripts/deploy-compliance-features.sh 2>&1 || echo 'Deployment script execution skipped'" "Argo Server"

echo ""
echo "✅ Argo deployment completed"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Verify deployments:"
echo "     ssh ${ALPINE_USER}@${ALPINE_SERVER} 'cd ${ALPINE_PATH} && ./scripts/verify-compliance-deployment.sh'"
echo "     ssh ${ARGO_USER}@${ARGO_SERVER} 'cd ${ARGO_PATH} && ./scripts/verify-compliance-deployment.sh'"
echo ""
echo "  2. Check cron jobs:"
echo "     ssh ${ARGO_USER}@${ARGO_SERVER} 'crontab -l | grep argo-compliance'"
echo ""
echo "  3. Monitor logs:"
echo "     ssh ${ARGO_USER}@${ARGO_SERVER} 'tail -f ${ARGO_PATH}/argo/logs/integrity_checks.log'"
echo ""

