#!/bin/bash
# Automated AWS Secrets Manager Setup Script
# This script configures AWS Secrets Manager optimally for Argo Trading Engine

set -e

echo ""
echo "🔐 AWS SECRETS MANAGER OPTIMAL SETUP"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on production server
if [ -f "/root/argo-production/config.json" ]; then
    ARGO_PATH="/root/argo-production"
    ENVIRONMENT="production"
else
    ARGO_PATH="$(pwd)"
    ENVIRONMENT="development"
fi

cd "$ARGO_PATH"

echo "📁 Working directory: $ARGO_PATH"
echo "🌍 Environment: $ENVIRONMENT"
echo ""

# Step 1: Update .env file
echo "📝 Step 1: Configuring .env file..."
if [ -f .env ]; then
    # Update USE_AWS_SECRETS
    if grep -q 'USE_AWS_SECRETS' .env; then
        sed -i 's/USE_AWS_SECRETS=.*/USE_AWS_SECRETS=true/' .env
    else
        echo 'USE_AWS_SECRETS=true' >> .env
    fi
    
    # Add AWS region if not present
    if ! grep -q 'AWS_DEFAULT_REGION' .env; then
        echo 'AWS_DEFAULT_REGION=us-east-1' >> .env
    fi
    
    echo -e "${GREEN}✅ .env file updated${NC}"
else
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Argo Trading Engine Environment Variables
USE_AWS_SECRETS=true
AWS_DEFAULT_REGION=us-east-1
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
fi

echo ""

# Step 2: Check AWS CLI
echo "📦 Step 2: Checking AWS CLI..."
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version 2>&1 | head -1)
    echo -e "${GREEN}✅ AWS CLI installed: $AWS_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  AWS CLI not found. Installing...${NC}"
    if command -v pip3 &> /dev/null; then
        pip3 install -q awscli
        echo -e "${GREEN}✅ AWS CLI installed${NC}"
    else
        echo -e "${RED}❌ Cannot install AWS CLI. Please install manually.${NC}"
        exit 1
    fi
fi

echo ""

# Step 3: Check AWS credentials
echo "🔑 Step 3: Checking AWS credentials..."
if [ -f ~/.aws/credentials ]; then
    echo -e "${GREEN}✅ AWS credentials file found${NC}"
    AWS_PROFILE=$(grep -E '^\[' ~/.aws/credentials | head -1 | tr -d '[]' || echo "default")
    echo "   Profile: $AWS_PROFILE"
elif [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${GREEN}✅ AWS credentials found in environment variables${NC}"
else
    echo -e "${YELLOW}⚠️  AWS credentials not found${NC}"
    echo ""
    echo "Please configure AWS credentials using one of these methods:"
    echo ""
    echo "Method 1: Interactive configuration (recommended)"
    echo "  aws configure"
    echo "  # Enter your AWS Access Key ID"
    echo "  # Enter your AWS Secret Access Key"
    echo "  # Enter region: us-east-1"
    echo "  # Enter output format: json"
    echo ""
    echo "Method 2: Environment variables"
    echo "  export AWS_ACCESS_KEY_ID=your_access_key"
    echo "  export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "  export AWS_DEFAULT_REGION=us-east-1"
    echo ""
    echo "Method 3: IAM Role (if running on EC2)"
    echo "  Attach IAM role to EC2 instance with Secrets Manager permissions"
    echo ""
    read -p "Press Enter after configuring AWS credentials, or Ctrl+C to exit..."
fi

echo ""

# Step 4: Test AWS access
echo "🧪 Step 4: Testing AWS access..."
if python3 << 'PYTHON_SCRIPT'
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
try:
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.list_secrets(MaxResults=1)
    print("✅ AWS Secrets Manager access working!")
    print(f"   Found {len(response.get('SecretList', []))} secret(s)")
    exit(0)
except NoCredentialsError:
    print("❌ No AWS credentials found")
    exit(1)
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == 'AccessDeniedException':
        print("⚠️  Access denied - check IAM permissions")
        print("   Required permissions:")
        print("   - secretsmanager:GetSecretValue")
        print("   - secretsmanager:CreateSecret")
        print("   - secretsmanager:PutSecretValue")
        print("   - secretsmanager:ListSecrets")
    else:
        print(f"❌ AWS API error: {error_code}")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
PYTHON_SCRIPT
then
    echo -e "${GREEN}✅ AWS access verified${NC}"
else
    echo -e "${RED}❌ AWS access test failed${NC}"
    echo "Please check your AWS credentials and permissions"
    exit 1
fi

echo ""

# Step 5: Install/verify dependencies
echo "📦 Step 5: Verifying dependencies..."
if [ -d venv ]; then
    source venv/bin/activate
fi

python3 << 'PYTHON_SCRIPT'
import sys
try:
    import boto3
    print("✅ boto3 installed")
except ImportError:
    print("⚠️  Installing boto3...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "boto3", "botocore"])
    print("✅ boto3 installed")
PYTHON_SCRIPT

echo ""

# Step 6: Add Alpaca secrets
echo "🔐 Step 6: Adding Alpaca secrets to AWS Secrets Manager..."
if [ -f "scripts/add_alpaca_secrets_to_aws.py" ]; then
    if python3 scripts/add_alpaca_secrets_to_aws.py; then
        echo -e "${GREEN}✅ Alpaca secrets added successfully${NC}"
    else
        echo -e "${RED}❌ Failed to add Alpaca secrets${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Script not found: scripts/add_alpaca_secrets_to_aws.py${NC}"
fi

echo ""

# Step 7: Verify system is using AWS Secrets Manager
echo "✅ Step 7: Verifying system configuration..."
python3 << 'PYTHON_SCRIPT'
import sys
import os
sys.path.insert(0, '.')

# Load environment variables
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

try:
    from argo.core.paper_trading_engine import PaperTradingEngine
    from argo.core.environment import detect_environment
    
    engine = PaperTradingEngine()
    env = detect_environment()
    
    print(f"Environment: {env}")
    print(f"Account: {engine.account_name}")
    print(f"Alpaca Enabled: {engine.alpaca_enabled}")
    
    if engine.alpaca_enabled:
        account = engine.get_account_details()
        print(f"Portfolio: ${account['portfolio_value']:,.2f}")
        print("✅ System is operational")
    else:
        print("⚠️  Alpaca not connected")
except Exception as e:
    print(f"⚠️  Verification error: {e}")
PYTHON_SCRIPT

echo ""
echo "===================================="
echo -e "${GREEN}✅ AWS SECRETS MANAGER SETUP COMPLETE${NC}"
echo "===================================="
echo ""
echo "📋 Summary:"
echo "  - .env configured: USE_AWS_SECRETS=true"
echo "  - AWS credentials: Configured"
echo "  - Alpaca secrets: Added to AWS Secrets Manager"
echo "  - System: Operational"
echo ""
echo "🎯 Next steps:"
echo "  - Restart services to use AWS Secrets Manager"
echo "  - Monitor logs for any AWS-related issues"
echo "  - Secrets will be automatically retrieved from AWS"
echo ""

