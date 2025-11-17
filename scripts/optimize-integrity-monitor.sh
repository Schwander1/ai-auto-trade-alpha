#!/bin/bash
# Optimize Integrity Monitor Performance
# Adds database indexes and optimizations for faster integrity checks

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

ARGO_SERVER="${ARGO_SERVER:-178.156.194.174}"
ARGO_USER="${ARGO_USER:-root}"
ARGO_PATH="${ARGO_PATH:-/root/argo-production}"

echo -e "${BLUE}🔧 Optimizing Integrity Monitor Performance${NC}"
echo ""

# Create optimization SQL script
cat > /tmp/optimize_integrity.sql <<'SQL'
-- Add indexes for faster integrity checks
CREATE INDEX IF NOT EXISTS idx_signals_sha256 ON signals(sha256);
CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_signals_signal_id ON signals(signal_id);

-- Analyze tables for query optimization
ANALYZE signals;

-- Show index information
SELECT
    name,
    tbl_name,
    sql
FROM sqlite_master
WHERE type='index' AND tbl_name='signals';
SQL

echo "📤 Copying optimization script to server..."
scp -o StrictHostKeyChecking=no /tmp/optimize_integrity.sql ${ARGO_USER}@${ARGO_SERVER}:/tmp/ 2>/dev/null || echo "⚠️  Could not copy script"

echo "🔧 Running optimizations on Argo server..."
ssh -o StrictHostKeyChecking=no ${ARGO_USER}@${ARGO_SERVER} <<ENDSSH
cd ${ARGO_PATH}
DB_FILE="data/signals.db"

if [ -f "\$DB_FILE" ]; then
    echo "Optimizing database indexes..."
    sqlite3 "\$DB_FILE" < /tmp/optimize_integrity.sql

    echo ""
    echo "✅ Database optimization complete"
    echo ""
    echo "Index information:"
    sqlite3 "\$DB_FILE" "SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND tbl_name='signals';"
else
    echo "⚠️  Database file not found: \$DB_FILE"
fi
ENDSSH

echo ""
echo -e "${GREEN}✅ Optimization complete${NC}"
