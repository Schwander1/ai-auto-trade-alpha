#!/bin/bash
# Generate combined PDF of all SystemDocs v4.0

set -e

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directories
DOCS_DIR="docs/SystemDocs/v4.0"
PDFS_DIR="pdfs"
DATE=$(date +%Y-%m-%d)

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo -e "${YELLOW}⚠️  pandoc not found. Install with: brew install pandoc${NC}"
    exit 1
fi

# Check if xelatex is installed
if ! command -v xelatex &> /dev/null; then
    echo -e "${YELLOW}⚠️  xelatex not found. Install with: brew install --cask mactex${NC}"
    exit 1
fi

mkdir -p "$PDFS_DIR"

echo -e "${BLUE}📚 Generating combined SystemDocs v4.0 PDF...${NC}"
echo ""

# Get all files in order
FILES=(
    "$DOCS_DIR/00_VERSION_HISTORY.md"
    "$DOCS_DIR/README.md"
    "$DOCS_DIR/01_COMPLETE_SYSTEM_ARCHITECTURE.md"
    "$DOCS_DIR/02_SIGNAL_GENERATION_COMPLETE_GUIDE.md"
    "$DOCS_DIR/03_PERFORMANCE_OPTIMIZATIONS.md"
    "$DOCS_DIR/04_SYSTEM_MONITORING_COMPLETE_GUIDE.md"
    "$DOCS_DIR/05_DEPLOYMENT_GUIDE.md"
    "$DOCS_DIR/06_ALERTING_SYSTEM.md"
    "$DOCS_DIR/07_BRAND_SYSTEM.md"
    "$DOCS_DIR/08_VERIFICATION_SYSTEM.md"
    "$DOCS_DIR/09_PERFORMANCE_REPORTING.md"
)

# Check files exist
MISSING_FILES=()
for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Missing files:${NC}"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

OUTPUT_FILE="$PDFS_DIR/SystemDocs_v4.0_Complete_${DATE}.pdf"

echo -e "${BLUE}Combining ${#FILES[@]} documents...${NC}"

# Generate PDF
pandoc "${FILES[@]}" \
    -o "$OUTPUT_FILE" \
    --pdf-engine=xelatex \
    --toc \
    --toc-depth=3 \
    -V geometry:margin=2cm \
    -V fontsize=11pt \
    -V linestretch=1.4 \
    -V mainfont="Georgia" \
    -V sansfont="Helvetica Neue" \
    -V monofont="Menlo" \
    -V title="Argo Capital / Alpine Analytics LLC - Complete System Documentation" \
    -V subtitle="Version 4.0 - January 2025" \
    -V author="Argo Capital and Alpine Analytics LLC" \
    -V date="$(date +'%B %d, %Y')" \
    -V linkcolor=blue \
    -V urlcolor=blue \
    -V colorlinks=true \
    -V documentclass=report \
    -V classoption=oneside \
    -V classoption=openany \
    --wrap=none \
    2>&1 | grep -v "Warning" || true

if [ -f "$OUTPUT_FILE" ]; then
    SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo ""
    echo -e "${GREEN}✅ Generated: $OUTPUT_FILE (${SIZE})${NC}"
    echo ""
    echo "PDF includes:"
    for file in "${FILES[@]}"; do
        echo "  - $(basename "$file")"
    done
    exit 0
else
    echo -e "${YELLOW}⚠️  Failed to generate PDF${NC}"
    exit 1
fi

