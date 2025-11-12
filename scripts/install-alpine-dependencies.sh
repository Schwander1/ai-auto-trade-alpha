#!/bin/bash
# Install Alpine backend dependencies

set -e

ALPINE_SERVER="91.98.153.49"
ALPINE_USER="root"

echo "📦 Installing Alpine Backend Dependencies"
echo "=========================================="
echo ""

ssh ${ALPINE_USER}@${ALPINE_SERVER} << 'EOF'
cd /root/alpine-production

# Create venv if it doesn't exist
if [ ! -d venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install fastapi uvicorn[standard] python-dotenv \
    sqlalchemy psycopg2-binary \
    pydantic pydantic-settings \
    python-jose[cryptography] argon2-cffi \
    stripe \
    httpx \
    prometheus-client

echo ""
echo "✅ Dependencies installed successfully!"
EOF

echo ""
echo "✅ Alpine dependencies installation complete!"

