#!/bin/bash
# Production Deployment Script
# Deploys Argo-Alpine trading system with all enhancements

set -e

echo "🚀 Argo-Alpine Production Deployment"
echo "====================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check prerequisites
echo -e "\n${BLUE}📋 Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3 found${NC}"

# Check dependencies
echo -e "\n${BLUE}📦 Checking dependencies...${NC}"
cd "$(dirname "$0")/.."
PYTHONPATH=argo python3 -c "
import sys
required = ['numpy', 'pandas', 'dashscope', 'zhipuai', 'openai']
missing = []
for pkg in required:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        missing.append(pkg)
        print(f'❌ {pkg} - MISSING')
if missing:
    print(f'\n⚠️  Missing packages: {missing}')
    print('Install with: pip install ' + ' '.join(missing))
    sys.exit(1)
" || {
    echo -e "${YELLOW}⚠️  Some dependencies missing. Installing...${NC}"
    python3 -m pip install numpy pandas dashscope zhipuai openai --break-system-packages --quiet
}

# Check configuration
echo -e "\n${BLUE}⚙️  Checking configuration...${NC}"
if [ ! -f "argo/config.json" ]; then
    echo -e "${RED}❌ config.json not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ config.json found${NC}"

# Verify API keys
PYTHONPATH=argo python3 -c "
import json
with open('argo/config.json') as f:
    config = json.load(f)
chinese = config.get('chinese_models', {})
glm_key = chinese.get('glm', {}).get('api_key', '')
deepseek_key = chinese.get('baichuan', {}).get('api_key', '')
print('✅ GLM API Key:', 'Present' if glm_key else 'Missing')
print('✅ DeepSeek API Key:', 'Present' if deepseek_key else 'Missing')
" || echo -e "${YELLOW}⚠️  Could not verify API keys${NC}"

# Create necessary directories
echo -e "\n${BLUE}📁 Creating directories...${NC}"
mkdir -p argo/baselines
mkdir -p argo/reports
mkdir -p argo/logs
mkdir -p argo/data
echo -e "${GREEN}✅ Directories created${NC}"

# Health check
echo -e "\n${BLUE}🏥 Running health check...${NC}"
if [ -f "scripts/health_check.sh" ]; then
    bash scripts/health_check.sh || echo -e "${YELLOW}⚠️  Health check had warnings${NC}"
else
    echo -e "${YELLOW}⚠️  Health check script not found${NC}"
fi

# Deployment options
echo -e "\n${BLUE}🚀 Deployment Options:${NC}"
echo "1. Start Signal Generation Service (Direct)"
echo "2. Docker Deployment"
echo "3. Systemd Service"
echo "4. Exit"

read -p "Select option (1-4): " choice

case $choice in
    1)
        echo -e "\n${GREEN}🚀 Starting Signal Generation Service...${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"
        PYTHONPATH=argo python3 -m argo.core.signal_generation_service
        ;;
    2)
        echo -e "\n${GREEN}🐳 Docker Deployment...${NC}"
        if [ -f "docker-compose.yml" ]; then
            docker-compose up -d
            echo -e "${GREEN}✅ Docker containers started${NC}"
        else
            echo -e "${RED}❌ docker-compose.yml not found${NC}"
        fi
        ;;
    3)
        echo -e "\n${GREEN}⚙️  Systemd Service...${NC}"
        echo -e "${YELLOW}Create systemd service file manually${NC}"
        echo "See deployment documentation for systemd setup"
        ;;
    4)
        echo -e "\n${GREEN}✅ Deployment preparation complete${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Invalid option${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}🎉 Deployment complete!${NC}"
echo -e "\n📊 Monitor logs: tail -f argo/logs/*.log"
echo -e "📈 Check status: ./scripts/health_check.sh"

