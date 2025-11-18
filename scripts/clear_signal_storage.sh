#!/bin/bash
# Clear Signal Storage and Start Fresh
# Stops signal generator, backs up database, clears it, and restarts

set -e

PRODUCTION_SERVER="178.156.194.174"
PRODUCTION_USER="root"

echo "🔄 Clearing Signal Storage and Starting Fresh"
echo "=============================================="
echo ""

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
set -e

echo '⏸️  Stopping signal generator...'
systemctl stop argo-signal-generator.service
sleep 2

# Create backup
BACKUP_DIR="/root/argo-production-unified/backups/clear_restart_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f /root/argo-production-unified/data/signals_unified.db ]; then
    echo '💾 Creating backup...'
    cp /root/argo-production-unified/data/signals_unified.db "$BACKUP_DIR/signals_unified_backup.db"
    
    # Get signal count before clearing
    COUNT=$(sqlite3 /root/argo-production-unified/data/signals_unified.db "SELECT COUNT(*) FROM signals;" 2>/dev/null || echo "0")
    echo "  📊 Backed up $COUNT signals"
    echo "  📁 Backup: $BACKUP_DIR"
fi

# Remove old database
echo '🗑️  Removing old database...'
rm -f /root/argo-production-unified/data/signals_unified.db*

# Initialize fresh database
echo '🆕 Initializing fresh database...'
python3 << 'PYTHON'
import sqlite3
from pathlib import Path

db_path = Path("/root/argo-production-unified/data/signals_unified.db")
db_path.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Enable WAL mode
cursor.execute('PRAGMA journal_mode=WAL')

# Create table with unified schema
cursor.execute('''
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        signal_id TEXT UNIQUE NOT NULL,
        symbol TEXT NOT NULL,
        action TEXT NOT NULL,
        entry_price REAL NOT NULL,
        target_price REAL NOT NULL,
        stop_price REAL NOT NULL,
        confidence REAL NOT NULL,
        strategy TEXT NOT NULL,
        asset_type TEXT NOT NULL,
        data_source TEXT DEFAULT 'weighted_consensus',
        timestamp TEXT NOT NULL,
        outcome TEXT DEFAULT NULL,
        exit_price REAL DEFAULT NULL,
        profit_loss_pct REAL DEFAULT NULL,
        sha256 TEXT NOT NULL,
        order_id TEXT DEFAULT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        service_type TEXT DEFAULT 'both',
        executor_id TEXT DEFAULT NULL,
        generated_by TEXT DEFAULT 'signal_generator',
        regime TEXT DEFAULT NULL,
        reasoning TEXT DEFAULT NULL
    )
''')

# Add indexes
cursor.execute('CREATE INDEX IF NOT EXISTS idx_service_type ON signals(service_type)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_executor_id ON signals(executor_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_generated_by ON signals(generated_by)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_symbol_created ON signals(symbol, created_at)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_confidence ON signals(confidence)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON signals(created_at)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_id ON signals(order_id)')

conn.commit()
conn.close()

print('✅ Fresh database initialized')
PYTHON

# Start signal generator
echo '🚀 Starting signal generator...'
systemctl start argo-signal-generator.service
sleep 3

# Verify
echo ''
echo '✅ Verification:'
if systemctl is-active argo-signal-generator.service > /dev/null; then
    echo '  ✅ Signal generator: ACTIVE'
else
    echo '  ❌ Signal generator: INACTIVE'
    exit 1
fi

# Check database
python3 << 'PYTHON'
import sqlite3
conn = sqlite3.connect('/root/argo-production-unified/data/signals_unified.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM signals')
count = cursor.fetchone()[0]
print(f'  ✅ Database signals: {count}')
conn.close()
PYTHON

echo ''
echo '✅ Signal storage cleared and restarted!'
echo "📁 Backup location: $BACKUP_DIR"
ENDSSH

echo ""
echo "✅ Signal storage cleared and fresh start initiated!"
echo ""
echo "Monitor signal generation:"
echo "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'journalctl -u argo-signal-generator.service -f'"
echo ""
echo "Check database:"
echo "  ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'sqlite3 /root/argo-production-unified/data/signals_unified.db \"SELECT COUNT(*) FROM signals;\"'"

