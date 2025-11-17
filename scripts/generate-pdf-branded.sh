#!/bin/bash
# Generate branded PDFs using Alpine brand template

set -e

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directories
DOCS_DIR="docs"
PDFS_DIR="pdfs"
BRAND_TEMPLATE="scripts/pdf-template-alpine.tex"
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

generate_branded_pdf() {
    local doc_set=$1
    local title=$2
    local files_pattern="$DOCS_DIR/$doc_set/v2.0_*.md"
    local output_file="$PDFS_DIR/${doc_set}_v2.0_${DATE}.pdf"
    
    if [ ! -f "$BRAND_TEMPLATE" ]; then
        echo -e "${YELLOW}⚠️  Brand template not found: $BRAND_TEMPLATE${NC}"
        echo "   Using default template instead"
        BRAND_TEMPLATE=""
    fi
    
    echo -e "${BLUE}Generating ${title} with Alpine branding...${NC}"
    
    # Get all files in order
    local files=$(ls -1 $files_pattern 2>/dev/null | sort)
    
    if [ -z "$files" ]; then
        echo -e "${YELLOW}⚠️  No files found for $doc_set${NC}"
        return 1
    fi
    
    # Build pandoc command
    local pandoc_cmd="pandoc $files -o \"$output_file\""
    
    if [ -n "$BRAND_TEMPLATE" ]; then
        pandoc_cmd="$pandoc_cmd --template=\"$BRAND_TEMPLATE\""
    fi
    
    pandoc_cmd="$pandoc_cmd --pdf-engine=xelatex"
    pandoc_cmd="$pandoc_cmd --toc --toc-depth=3"
    pandoc_cmd="$pandoc_cmd --variable=geometry:margin=2cm"
    pandoc_cmd="$pandoc_cmd --variable=fontsize:12pt"
    pandoc_cmd="$pandoc_cmd --variable=linestretch:1.5"
    pandoc_cmd="$pandoc_cmd --variable=title:\"$title\""
    pandoc_cmd="$pandoc_cmd --variable=subtitle:\"Alpine Analytics LLC\""
    pandoc_cmd="$pandoc_cmd --variable=author:\"Alpine Analytics LLC\""
    pandoc_cmd="$pandoc_cmd --variable=date:\"$(date +'%B %Y')\""
    pandoc_cmd="$pandoc_cmd 2>&1 | grep -v \"Warning\" || true"
    
    eval $pandoc_cmd
    
    if [ -f "$output_file" ]; then
        local size=$(du -h "$output_file" | cut -f1)
        echo -e "${GREEN}✅ Generated: $output_file (${size})${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Failed to generate PDF${NC}"
        return 1
    fi
}

# Generate all PDFs
echo -e "${BLUE}📚 Generating branded PDFs for all document sets...${NC}"
echo ""

generate_branded_pdf "InvestorDocs" "Investor Documentation"
generate_branded_pdf "TechnicalDocs" "Technical Documentation"
generate_branded_pdf "SystemDocs" "System Documentation"

echo ""
echo -e "${GREEN}✅ Branded PDF Generation Complete!${NC}"
echo ""
echo "Generated PDFs:"
ls -lh "$PDFS_DIR"/*.pdf 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}' || echo "  No PDFs found"

