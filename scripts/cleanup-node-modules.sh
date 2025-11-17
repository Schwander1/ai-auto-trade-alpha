#!/bin/bash

# Node Modules Cleanup Script
# Removes unnecessary files from node_modules to save space

set -e

WORKSPACE_DIR="/Users/dylanneuenschwander/argo-alpine-workspace"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$WORKSPACE_DIR"

echo -e "${BLUE}🧹 Node Modules Cleanup Script${NC}"
echo "================================"
echo ""

TOTAL_SAVED=0

# Find all node_modules directories
find . -type d -name "node_modules" -not -path "*/node_modules/*" | while read nm_dir; do
    echo -e "${BLUE}📦 Processing: $nm_dir${NC}"
    
    SIZE_BEFORE=$(du -sh "$nm_dir" 2>/dev/null | cut -f1)
    
    # Remove .ignored directories (pnpm artifacts)
    find "$nm_dir" -type d -name ".ignored" -exec rm -rf {} + 2>/dev/null || true
    
    # Remove source map files
    find "$nm_dir" -type f -name "*.map" -delete 2>/dev/null || true
    
    # Remove test files
    find "$nm_dir" -type d -name "__tests__" -o -name "test" -o -name "tests" | xargs rm -rf 2>/dev/null || true
    find "$nm_dir" -type f -name "*.test.js" -o -name "*.test.ts" -o -name "*.spec.js" -o -name "*.spec.ts" | xargs rm -f 2>/dev/null || true
    
    # Remove documentation files
    find "$nm_dir" -type f -name "README.md" -o -name "CHANGELOG.md" -o -name "LICENSE*" | xargs rm -f 2>/dev/null || true
    
    SIZE_AFTER=$(du -sh "$nm_dir" 2>/dev/null | cut -f1)
    
    echo -e "  ${GREEN}✅ Cleaned: $SIZE_BEFORE → $SIZE_AFTER${NC}"
done

echo ""
echo -e "${GREEN}✅ Node modules cleanup complete!${NC}"

