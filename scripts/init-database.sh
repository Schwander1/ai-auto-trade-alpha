#!/bin/bash
# Initialize database with all models

set -e

ALPINE_SERVER="91.98.153.49"
ALPINE_USER="root"

echo "🗄️  Initializing Alpine Database"
echo "================================="
echo ""

ssh ${ALPINE_USER}@${ALPINE_SERVER} << 'EOF'
cd /root/alpine-production

# Activate virtual environment if exists
if [ -d venv ]; then
    source venv/bin/activate
fi

# Run Python script to create all tables
python3 << 'PYTHON'
from backend.core.database import engine, Base
from backend.models.user import User
from backend.models.signal import Signal
from backend.models.notification import Notification
from backend.models.backtest import Backtest

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")
PYTHON

echo ""
echo "✅ Database initialization complete!"
EOF

