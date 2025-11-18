#!/bin/bash
# Archive old documentation files
set -e

ARCHIVE_DIR="docs/archived/$(date +%Y%m%d)"
mkdir -p "$ARCHIVE_DIR"

echo "📦 Archiving old documentation..."

# Archive dual trading docs
if [ -f "production_deployment/DUAL_TRADING_PRODUCTION_SETUP.md" ]; then
    mv "production_deployment/DUAL_TRADING_PRODUCTION_SETUP.md" "$ARCHIVE_DIR/"
    echo "  ✅ Archived: DUAL_TRADING_PRODUCTION_SETUP.md"
fi

if [ -f "docs/production_setup/DUAL_TRADING_PRODUCTION_SETUP.md" ]; then
    mv "docs/production_setup/DUAL_TRADING_PRODUCTION_SETUP.md" "$ARCHIVE_DIR/"
    echo "  ✅ Archived: docs/production_setup/DUAL_TRADING_PRODUCTION_SETUP.md"
fi

# Archive old signal generation docs (keep main one, archive duplicates)
if [ -f "SIGNAL_GENERATION_SUCCESS.md" ]; then
    mv "SIGNAL_GENERATION_SUCCESS.md" "$ARCHIVE_DIR/"
    echo "  ✅ Archived: SIGNAL_GENERATION_SUCCESS.md"
fi

if [ -f "SIGNAL_GENERATION_FIX_COMPLETE.md" ]; then
    mv "SIGNAL_GENERATION_FIX_COMPLETE.md" "$ARCHIVE_DIR/"
    echo "  ✅ Archived: SIGNAL_GENERATION_FIX_COMPLETE.md"
fi

if [ -f "SIGNAL_GENERATION_STATUS_UPDATE.md" ]; then
    mv "SIGNAL_GENERATION_STATUS_UPDATE.md" "$ARCHIVE_DIR/"
    echo "  ✅ Archived: SIGNAL_GENERATION_STATUS_UPDATE.md"
fi

if [ -f "SIGNAL_GENERATION_ISSUE_FOUND.md" ]; then
    mv "SIGNAL_GENERATION_ISSUE_FOUND.md" "$ARCHIVE_DIR/"
    echo "  ✅ Archived: SIGNAL_GENERATION_ISSUE_FOUND.md"
fi

# Archive signal storage docs
if [ -f "SIGNAL_STORAGE_RECOMMENDATIONS_COMPLETE.md" ]; then
    mv "SIGNAL_STORAGE_RECOMMENDATIONS_COMPLETE.md" "$ARCHIVE_DIR/"
    echo "  ✅ Archived: SIGNAL_STORAGE_RECOMMENDATIONS_COMPLETE.md"
fi

if [ -f "SIGNAL_STORAGE_FIXES.md" ]; then
    mv "SIGNAL_STORAGE_FIXES.md" "$ARCHIVE_DIR/"
    echo "  ✅ Archived: SIGNAL_STORAGE_FIXES.md"
fi

# Create archive index
cat > "$ARCHIVE_DIR/README.md" << EOF
# Archived Documentation

**Archive Date:** $(date +%Y-%m-%d)

This directory contains documentation archived during the migration to unified architecture (v3.0).

## Contents

- DUAL_TRADING_PRODUCTION_SETUP.md - Old dual trading setup (replaced by unified architecture)
- SIGNAL_GENERATION_*.md - Old signal generation status docs
- SIGNAL_STORAGE_*.md - Old signal storage docs

## New Documentation

See:
- docs/UNIFIED_ARCHITECTURE_COMPLETE_GUIDE.md - Complete unified architecture guide
- Rules/13_TRADING_OPERATIONS.md - Updated trading operations rules (v3.0)
- production_deployment/UNIFIED_ARCHITECTURE_DEPLOYMENT.md - Deployment guide
EOF

echo ""
echo "✅ Archiving complete! Files archived to: $ARCHIVE_DIR"
echo "📝 Archive index created: $ARCHIVE_DIR/README.md"

