#!/bin/bash
# Verify Tradervue Enhanced Integration Setup

echo "=========================================="
echo "Tradervue Enhanced Integration Setup Check"
echo "=========================================="
echo ""

# Check Python environment
echo "1. Checking Python environment..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ Python found: $PYTHON_VERSION"
else
    echo "   ❌ Python3 not found"
    exit 1
fi

# Check if we're in the right directory
echo ""
echo "2. Checking directory structure..."
if [ -f "argo/argo/integrations/tradervue_client.py" ]; then
    echo "   ✅ tradervue_client.py found"
elif [ -f "argo/integrations/tradervue_client.py" ]; then
    echo "   ✅ tradervue_client.py found (legacy path)"
else
    echo "   ❌ tradervue_client.py not found"
    exit 1
fi

if [ -f "argo/argo/integrations/tradervue_integration.py" ]; then
    echo "   ✅ tradervue_integration.py found"
elif [ -f "argo/integrations/tradervue_integration.py" ]; then
    echo "   ✅ tradervue_integration.py found (legacy path)"
else
    echo "   ❌ tradervue_integration.py not found"
    exit 1
fi

if [ -f "argo/argo/api/tradervue.py" ]; then
    echo "   ✅ tradervue.py API endpoint found"
elif [ -f "argo/api/tradervue.py" ]; then
    echo "   ✅ tradervue.py API endpoint found (legacy path)"
else
    echo "   ❌ tradervue.py API endpoint not found"
    exit 1
fi

# Check environment variables
echo ""
echo "3. Checking environment variables..."
if [ -n "$TRADERVUE_USERNAME" ]; then
    echo "   ✅ TRADERVUE_USERNAME is set"
else
    echo "   ⚠️  TRADERVUE_USERNAME not set"
fi

if [ -n "$TRADERVUE_PASSWORD" ]; then
    echo "   ✅ TRADERVUE_PASSWORD is set"
else
    echo "   ⚠️  TRADERVUE_PASSWORD not set"
fi

# Check AWS credentials (optional)
echo ""
echo "4. Checking AWS credentials (optional)..."
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "   ✅ AWS credentials found (for Secrets Manager)"
else
    echo "   ⚠️  AWS credentials not found (will use env vars if set)"
fi

# Check Python dependencies
echo ""
echo "5. Checking Python dependencies..."
cd argo 2>/dev/null || cd . 2>/dev/null

if python3 -c "import requests" 2>/dev/null; then
    echo "   ✅ requests module available"
else
    echo "   ⚠️  requests module not found (install with: pip install requests)"
fi

if python3 -c "import boto3" 2>/dev/null; then
    echo "   ✅ boto3 module available (for AWS Secrets Manager)"
else
    echo "   ⚠️  boto3 module not found (optional, for AWS Secrets Manager)"
fi

# Summary
echo ""
echo "=========================================="
echo "Setup Check Complete"
echo "=========================================="
echo ""
echo "To configure Tradervue:"
echo "1. Set environment variables:"
echo "   export TRADERVUE_USERNAME=your_username"
echo "   export TRADERVUE_PASSWORD=your_password"
echo ""
echo "2. Or configure in AWS Secrets Manager:"
echo "   - argo-capital/argo/tradervue-username"
echo "   - argo-capital/argo/tradervue-password"
echo ""
echo "Note: Tradervue uses your account username and password (not an API token)"
echo ""
echo "3. Run test script:"
echo "   python3 scripts/test_tradervue_integration.py"
echo ""

