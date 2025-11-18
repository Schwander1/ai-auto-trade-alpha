#!/bin/bash
# Create systemd service files for dual trading

set -e

echo "🔧 Creating systemd service files for dual trading"
echo "=================================================="
echo ""

# Argo Trading Service
ARGO_SERVICE="/etc/systemd/system/argo-trading.service"
echo "Creating: $ARGO_SERVICE"

sudo tee $ARGO_SERVICE > /dev/null <<EOF
[Unit]
Description=Argo Trading Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-green
Environment="ARGO_CONFIG_PATH=/root/argo-production-green/config.json"
Environment="ARGO_24_7_MODE=true"
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=10
StandardOutput=append:/root/argo-production-green/logs/service.log
StandardError=append:/root/argo-production-green/logs/service.error.log

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Created Argo trading service"

# Prop Firm Trading Service
PROP_FIRM_SERVICE="/etc/systemd/system/argo-trading-prop-firm.service"
echo "Creating: $PROP_FIRM_SERVICE"

sudo tee $PROP_FIRM_SERVICE > /dev/null <<EOF
[Unit]
Description=Argo Prop Firm Trading Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-prop-firm
Environment="ARGO_CONFIG_PATH=/root/argo-production-prop-firm/config.json"
Environment="ARGO_24_7_MODE=true"
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --workers 1
Restart=always
RestartSec=10
StandardOutput=append:/root/argo-production-prop-firm/logs/service.log
StandardError=append:/root/argo-production-prop-firm/logs/service.error.log

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Created Prop Firm trading service"

# Reload systemd
echo ""
echo "Reloading systemd..."
sudo systemctl daemon-reload

echo ""
echo "✅ Systemd services created!"
echo ""
echo "To start services:"
echo "  sudo systemctl start argo-trading.service"
echo "  sudo systemctl start argo-trading-prop-firm.service"
echo ""
echo "To enable on boot:"
echo "  sudo systemctl enable argo-trading.service"
echo "  sudo systemctl enable argo-trading-prop-firm.service"
echo ""
echo "To check status:"
echo "  sudo systemctl status argo-trading.service"
echo "  sudo systemctl status argo-trading-prop-firm.service"
echo ""

