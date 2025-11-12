#!/bin/bash
# Generate professional PDFs from organized documentation sets

set -e

DOCS_DIR="docs"
PDFS_DIR="pdfs"
DATE=$(date +%Y-%m-%d)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📄 PDF Generation Script${NC}"
echo "=========================="
echo ""

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo -e "${YELLOW}⚠️  Pandoc not found. Installing...${NC}"
    echo "Please install pandoc: brew install pandoc (macOS) or apt-get install pandoc (Linux)"
    exit 1
fi

# Check if xelatex is available
if ! command -v xelatex &> /dev/null; then
    echo -e "${YELLOW}⚠️  XeLaTeX not found. Installing...${NC}"
    echo "Please install BasicTeX or MacTeX: brew install --cask basictex (macOS)"
    exit 1
fi

mkdir -p "$PDFS_DIR"

generate_pdf() {
    local doc_set=$1
    local title=$2
    local files_pattern="$DOCS_DIR/$doc_set/v1.0_*.md"
    local output_file="$PDFS_DIR/${doc_set}_v1.0_${DATE}.pdf"
    
    echo -e "${BLUE}Generating ${title}...${NC}"
    
    # Get all files in order
    local files=$(ls -1 $files_pattern | sort)
    
    if [ -z "$files" ]; then
        echo -e "${YELLOW}⚠️  No files found for $doc_set${NC}"
        return 1
    fi
    
    pandoc $files -o "$output_file" \
        --pdf-engine=xelatex \
        --toc \
        --toc-depth=3 \
        --variable=geometry:margin=2cm \
        --variable=fontsize:12pt \
        --variable=linestretch:1.5 \
        --variable=mainfont:Georgia \
        --variable=sansfont:"DejaVu Sans" \
        --variable=monofont:"DejaVu Sans Mono" \
        --variable=linkcolor:#0066CC \
        --variable=urlcolor:#0066CC \
        --highlight-style=tango \
        --variable=colorlinks=true \
        --variable=papersize:a4 \
        2>&1 | grep -v "Warning" || true
    
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
echo -e "${BLUE}📚 Generating PDFs for all document sets...${NC}"
echo ""

generate_pdf "InvestorDocs" "Investor Documentation"
generate_pdf "TechnicalDocs" "Technical Documentation"
generate_pdf "SystemDocs" "System Documentation"

echo ""
echo -e "${GREEN}✅ PDF Generation Complete!${NC}"
echo ""
echo "Generated PDFs:"
ls -lh "$PDFS_DIR"/*.pdf 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}' || echo "  No PDFs found"

