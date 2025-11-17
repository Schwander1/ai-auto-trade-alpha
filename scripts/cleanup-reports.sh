#!/bin/bash

# Automated Report Cleanup Script
# Archives and compresses old report files to save disk space

set -e

WORKSPACE_DIR="/Users/dylanneuenschwander/argo-alpine-workspace"
ARCHIVE_DIR="$WORKSPACE_DIR/archive/reports"
REPORTS_DIRS=("$WORKSPACE_DIR/argo/reports" "$WORKSPACE_DIR/argo/argo/reports")

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$WORKSPACE_DIR"

echo -e "${BLUE}🧹 Report Cleanup Script${NC}"
echo "=========================="
echo ""

# Create archive directory if it doesn't exist
mkdir -p "$ARCHIVE_DIR"

# Days to keep reports uncompressed
KEEP_DAYS=7
ARCHIVE_DAYS=30

TOTAL_SAVED=0

for REPORTS_DIR in "${REPORTS_DIRS[@]}"; do
    if [ ! -d "$REPORTS_DIR" ]; then
        continue
    fi
    
    echo -e "${BLUE}📁 Processing: $REPORTS_DIR${NC}"
    
    # Compress large JSONL files older than KEEP_DAYS
    find "$REPORTS_DIR" -type f -name "*.jsonl" -mtime +$KEEP_DAYS | while read file; do
        if [ -f "$file" ]; then
            SIZE_BEFORE=$(du -h "$file" | cut -f1)
            gzip -c "$file" > "$ARCHIVE_DIR/$(basename "$file")_$(date +%Y%m%d).gz"
            SIZE_AFTER=$(du -h "$ARCHIVE_DIR/$(basename "$file")_$(date +%Y%m%d).gz" | cut -f1)
            rm -f "$file"
            echo -e "  ${GREEN}✅ Compressed: $(basename "$file") ($SIZE_BEFORE → $SIZE_AFTER)${NC}"
        fi
    done
    
    # Compress JSON files older than ARCHIVE_DAYS
    find "$REPORTS_DIR" -type f -name "*.json" -mtime +$ARCHIVE_DAYS ! -name "*.gz" | while read file; do
        if [ -f "$file" ]; then
            SIZE_BEFORE=$(du -h "$file" | cut -f1)
            gzip "$file"
            SIZE_AFTER=$(du -h "${file}.gz" | cut -f1)
            echo -e "  ${GREEN}✅ Compressed: $(basename "$file") ($SIZE_BEFORE → $SIZE_AFTER)${NC}"
        fi
    done
    
    # Remove very old compressed files (older than 90 days)
    find "$REPORTS_DIR" -type f -name "*.gz" -mtime +90 | while read file; do
        if [ -f "$file" ]; then
            SIZE=$(du -h "$file" | cut -f1)
            mv "$file" "$ARCHIVE_DIR/" 2>/dev/null || rm -f "$file"
            echo -e "  ${YELLOW}📦 Archived: $(basename "$file") ($SIZE)${NC}"
        fi
    done
done

# Clean up archive directory (keep last 180 days)
echo ""
echo -e "${BLUE}🗑️  Cleaning old archives (older than 180 days)...${NC}"
find "$ARCHIVE_DIR" -type f -mtime +180 -delete 2>/dev/null || true

# Show summary
echo ""
echo -e "${GREEN}✅ Report cleanup complete!${NC}"
echo ""
echo "Archive location: $ARCHIVE_DIR"
du -sh "$ARCHIVE_DIR" 2>/dev/null || echo "Archive directory is empty"

