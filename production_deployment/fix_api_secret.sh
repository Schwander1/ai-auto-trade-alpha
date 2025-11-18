#!/bin/bash
# Fix ARGO_API_SECRET in systemd services

set -e

echo "🔧 Fixing ARGO_API_SECRET in systemd services..."
echo ""

# Generate or use existing secret
if [ -f "/root/argo-production-green/.env" ]; then
    SECRET=$(grep ARGO_API_SECRET /root/argo-production-green/.env | cut -d'=' -f2 | tr -d '"' | tr -d "'" || echo "")
fi

if [ -z "$SECRET" ]; then
    # Generate new secret
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "Generated new ARGO_API_SECRET"
fi

echo "Using ARGO_API_SECRET: ${SECRET:0:20}..."

# Update Argo service
echo ""
echo "📝 Updating Argo service..."
sudo sed -i "s|Environment=\"ARGO_CONFIG_PATH=|Environment=\"ARGO_API_SECRET=$SECRET\"\nEnvironment=\"ARGO_CONFIG_PATH=|g" /etc/systemd/system/argo-trading.service

# Update Prop Firm service
echo "📝 Updating Prop Firm service..."
sudo sed -i "s|Environment=\"ARGO_CONFIG_PATH=|Environment=\"ARGO_API_SECRET=$SECRET\"\nEnvironment=\"ARGO_CONFIG_PATH=|g" /etc/systemd/system/argo-trading-prop-firm.service

# Alternative: Use tee to properly add the environment variable
sudo tee /etc/systemd/system/argo-trading.service > /dev/null <<EOF
[Unit]
Description=Argo Trading Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-green
Environment="ARGO_API_SECRET=$SECRET"
Environment="ARGO_CONFIG_PATH=/root/argo-production-green/config.json"
Environment="ARGO_24_7_MODE=true"
Environment="PATH=/root/argo-production-green/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/root/argo-production-green/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=10
StandardOutput=append:/root/argo-production-green/logs/service.log
StandardError=append:/root/argo-production-green/logs/service.error.log

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/argo-trading-prop-firm.service > /dev/null <<EOF
[Unit]
Description=Argo Prop Firm Trading Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-prop-firm
Environment="ARGO_API_SECRET=$SECRET"
Environment="ARGO_CONFIG_PATH=/root/argo-production-prop-firm/config.json"
Environment="ARGO_24_7_MODE=true"
Environment="PATH=/root/argo-production-prop-firm/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/root/argo-production-prop-firm/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --workers 1
Restart=always
RestartSec=10
StandardOutput=append:/root/argo-production-prop-firm/logs/service.log
StandardError=append:/root/argo-production-prop-firm/logs/service.error.log

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service files updated with ARGO_API_SECRET"
echo ""
echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "✅ Done!"
echo ""
echo "Restart services:"
echo "  sudo systemctl restart argo-trading.service"
echo "  sudo systemctl restart argo-trading-prop-firm.service"

