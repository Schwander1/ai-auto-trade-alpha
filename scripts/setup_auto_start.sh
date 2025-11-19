#!/bin/bash
# Setup Auto-Start for All Trading Services
# Creates launchd agents for macOS to ensure services always run

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ARGO_DIR="$WORKSPACE_ROOT/argo"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
LOG_DIR="$WORKSPACE_ROOT/logs"
mkdir -p "$LOG_DIR"
mkdir -p "$LAUNCHD_DIR"

echo "🔧 Setting up auto-start for trading services..."
echo ""

# Create Prop Firm Executor LaunchAgent
cat > "$LAUNCHD_DIR/com.argo.prop_firm_executor.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.argo.prop_firm_executor</string>
    <key>ProgramArguments</key>
    <array>
        <string>$ARGO_DIR/venv/bin/python</string>
        <string>-m</string>
        <string>uvicorn</string>
        <string>argo.core.trading_executor:app</string>
        <string>--host</string>
        <string>0.0.0.0</string>
        <string>--port</string>
        <string>8001</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$ARGO_DIR</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>EXECUTOR_ID</key>
        <string>prop_firm</string>
        <key>EXECUTOR_CONFIG_PATH</key>
        <string>$ARGO_DIR/config.json</string>
        <key>PORT</key>
        <string>8001</string>
        <key>PYTHONPATH</key>
        <string>$ARGO_DIR</string>
        <key>ARGO_24_7_MODE</key>
        <string>true</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$LOG_DIR/prop_firm_executor.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/prop_firm_executor.error.log</string>
    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
EOF

echo "✅ Created Prop Firm Executor LaunchAgent"

# Create Health Monitor LaunchAgent
cat > "$LAUNCHD_DIR/com.argo.health_monitor.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.argo.health_monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_DIR/ensure_always_running.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$WORKSPACE_ROOT</string>
    <key>StartInterval</key>
    <integer>300</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$LOG_DIR/health_monitor.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/health_monitor.error.log</string>
</dict>
</plist>
EOF

echo "✅ Created Health Monitor LaunchAgent"

# Load the agents
echo ""
echo "🔄 Loading LaunchAgents..."

launchctl unload "$LAUNCHD_DIR/com.argo.prop_firm_executor.plist" 2>/dev/null || true
launchctl load "$LAUNCHD_DIR/com.argo.prop_firm_executor.plist"
echo "✅ Loaded Prop Firm Executor agent"

launchctl unload "$LAUNCHD_DIR/com.argo.health_monitor.plist" 2>/dev/null || true
launchctl load "$LAUNCHD_DIR/com.argo.health_monitor.plist"
echo "✅ Loaded Health Monitor agent"

echo ""
echo "✅ Auto-start setup complete!"
echo ""
echo "Services will now:"
echo "  - Start automatically on login"
echo "  - Restart automatically if they crash"
echo "  - Be monitored every 5 minutes"
echo ""
echo "To check status:"
echo "  launchctl list | grep argo"
echo ""
echo "To unload (stop auto-start):"
echo "  launchctl unload $LAUNCHD_DIR/com.argo.prop_firm_executor.plist"
echo "  launchctl unload $LAUNCHD_DIR/com.argo.health_monitor.plist"
