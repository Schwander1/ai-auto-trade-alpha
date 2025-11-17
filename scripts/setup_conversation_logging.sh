#!/bin/bash
# Setup Conversation Logging System
# One-time setup script for automatic conversation logging

set -e

echo "🚀 Setting up Conversation Logging System"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_step() {
    echo ""
    echo -e "${BLUE}$1${NC}"
    echo "----------------------------------------"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_warning "This script is designed for macOS. Some features may not work on other systems."
fi

# Step 1: Verify environment
print_step "1️⃣  Verifying Environment"

# Check if we're in development
if [ -f "argo/argo/core/environment.py" ]; then
    ENV_CHECK=$(python3 -c "import sys; sys.path.insert(0, 'argo'); from argo.core.environment import detect_environment; print(detect_environment())" 2>/dev/null || echo "development")
    
    if [ "$ENV_CHECK" = "production" ]; then
        print_error "Production environment detected - conversation logging is LOCAL ONLY"
        echo "This script should only be run in development environment."
        exit 1
    fi
    
    print_success "Development environment confirmed"
else
    print_warning "Environment detection not available, assuming development"
fi

# Step 2: Ensure directories exist
print_step "2️⃣  Creating Directory Structure"

mkdir -p conversation_logs/sessions
mkdir -p conversation_logs/decisions
print_success "Directories created"

# Step 3: Make scripts executable
print_step "3️⃣  Making Scripts Executable"

chmod +x scripts/conversation_logger_service.py
chmod +x scripts/cleanup_conversation_logs.py
print_success "Scripts made executable"

# Step 4: Test scripts
print_step "4️⃣  Testing Scripts"

# Test cleanup script (should work even with no logs)
if python3 scripts/cleanup_conversation_logs.py > /dev/null 2>&1; then
    print_success "Cleanup script test passed"
else
    print_warning "Cleanup script test had issues (may be normal if no logs exist)"
fi

# Step 5: Setup launchd service (macOS)
print_step "5️⃣  Setting up Background Service (macOS)"

if [[ "$OSTYPE" == "darwin"* ]]; then
    WORKSPACE_ROOT=$(pwd)
    SERVICE_NAME="com.argo.conversation-logger"
    PLIST_FILE="$HOME/Library/LaunchAgents/${SERVICE_NAME}.plist"
    
    # Create plist file with wake handling
    cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${SERVICE_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>${WORKSPACE_ROOT}/scripts/conversation_logger_service.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${WORKSPACE_ROOT}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${WORKSPACE_ROOT}/conversation_logs/service.log</string>
    <key>StandardErrorPath</key>
    <string>${WORKSPACE_ROOT}/conversation_logs/service.error.log</string>
    <key>StartOnMount</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>30</integer>
    <key>ExitTimeOut</key>
    <integer>10</integer>
</dict>
</plist>
EOF
    
    # Load service
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    launchctl load "$PLIST_FILE"
    
    print_success "Background service installed and started"
    echo "   Service name: ${SERVICE_NAME}"
    echo "   Plist file: ${PLIST_FILE}"
    echo ""
    echo "   To stop: launchctl unload ${PLIST_FILE}"
    echo "   To start: launchctl load ${PLIST_FILE}"
    echo "   To check status: launchctl list | grep ${SERVICE_NAME}"
else
    print_warning "Non-macOS system - manual service setup required"
    echo "   Run: python3 scripts/conversation_logger_service.py &"
fi

# Step 6: Setup cron job for cleanup
print_step "6️⃣  Setting up Daily Cleanup (Cron)"

CRON_CMD="0 2 * * * cd $(pwd) && /usr/bin/python3 scripts/cleanup_conversation_logs.py >> conversation_logs/cleanup.log 2>&1"
CRON_JOB="conversation-logs-cleanup"

# Remove existing cron job if present
(crontab -l 2>/dev/null | grep -v "$CRON_JOB" || true) | crontab -

# Add new cron job
(crontab -l 2>/dev/null; echo "# ${CRON_JOB} - Daily cleanup of conversation logs"; echo "$CRON_CMD") | crontab -

print_success "Daily cleanup cron job installed (runs at 2 AM daily)"
echo "   To view: crontab -l | grep conversation-logs"
echo "   To remove: crontab -l | grep -v conversation-logs | crontab -"

# Step 7: Verify setup
print_step "7️⃣  Verifying Setup"

# Check directories
if [ -d "conversation_logs/sessions" ] && [ -d "conversation_logs/decisions" ]; then
    print_success "Directories exist"
else
    print_error "Directories missing"
fi

# Check scripts
if [ -x "scripts/conversation_logger_service.py" ] && [ -x "scripts/cleanup_conversation_logs.py" ]; then
    print_success "Scripts are executable"
else
    print_error "Scripts not executable"
fi

# Check service (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if launchctl list | grep -q "${SERVICE_NAME}"; then
        print_success "Background service is running"
    else
        print_warning "Background service may not be running (check manually)"
    fi
fi

# Check cron
if crontab -l 2>/dev/null | grep -q "conversation-logs-cleanup"; then
    print_success "Cron job installed"
else
    print_warning "Cron job may not be installed (check manually)"
fi

# Final summary
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📋 Summary:"
echo "   - Directories created: conversation_logs/"
echo "   - Background service: ${SERVICE_NAME} (macOS)"
echo "   - Daily cleanup: 2 AM (cron)"
echo "   - Retention: 3 days (sessions), 30 days (decisions)"
echo ""
echo "📖 Documentation:"
echo "   - conversation_logs/README.md"
echo "   - Rules/23_CONVERSATION_LOGGING.md"
echo ""
echo "🔍 Verify:"
echo "   - Check service: launchctl list | grep ${SERVICE_NAME}"
echo "   - Check logs: tail -f conversation_logs/service.log"
echo "   - Manual cleanup: python3 scripts/cleanup_conversation_logs.py"
echo ""
