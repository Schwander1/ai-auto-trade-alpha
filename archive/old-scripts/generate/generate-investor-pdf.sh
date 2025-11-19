#!/bin/bash
# Generate InvestorDocs PDF with emoji removal and proper formatting

set -e

DOCS_DIR="docs/InvestorDocs"
PDFS_DIR="pdfs"
DATE=$(date +%Y-%m-%d)
TEMP_DIR=$(mktemp -d)
OUTPUT_PDF="pdfs/InvestorDocs_v1.0_${DATE}.pdf"

echo "📄 Generating InvestorDocs PDF..."
echo "=================================="
echo ""

# Create temp directory for cleaned files
mkdir -p "$TEMP_DIR" "$PDFS_DIR"

# Python script to clean markdown
cat > "$TEMP_DIR/clean_md.py" << 'PYTHON_SCRIPT'
import re
import sys

file_path = sys.argv[1]
output_path = sys.argv[2]

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all emoji and symbol ranges comprehensively
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"  # enclosed characters
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U00002600-\U000026FF"  # miscellaneous symbols
    "\U00002700-\U000027BF"  # dingbats
    "\U0000200D"  # zero width joiner
    "\U0000FE00-\U0000FE0F"  # variation selectors
    "]+", 
    flags=re.UNICODE
)
content = emoji_pattern.sub('', content)

# Remove variation selectors and zero-width characters
content = re.sub(r'[\uFE00-\uFE0F]', '', content)  # Variation selectors
content = re.sub(r'[\u200B-\u200D]', '', content)  # Zero-width spaces
content = re.sub(r'[\u2060-\u206F]', '', content)  # Word joiner

# Replace specific problematic characters with ASCII equivalents
replacements = {
    '→': '->',
    '←': '<-',
    '↑': '^',
    '↓': 'v',
    '…': '...',
    '⚖': '~',
    '✅': '[OK]',
    '❌': '[X]',
    '⚠️': '[!]',
    '—': '--',
    '–': '-',
    '"': '"',
    '"': '"',
    ''': "'",
    ''': "'",
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Remove any remaining problematic Unicode
content = re.sub(r'[^\x00-\x7F\u00A0-\u00FF]', '', content)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)
PYTHON_SCRIPT

# Remove emojis and clean files
echo "Cleaning markdown files (removing emojis)..."
for file in "$DOCS_DIR"/v1.0_*.md; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        python3 "$TEMP_DIR/clean_md.py" "$file" "$TEMP_DIR/$filename"
        echo "  Cleaned: $filename"
    fi
done

echo ""
echo "Generating PDF with xelatex..."

# Generate PDF using pdflatex (no font issues)
pandoc "$TEMP_DIR"/v1.0_*.md -o "$OUTPUT_PDF" \
  --pdf-engine=pdflatex \
  --toc \
  --toc-depth=3 \
  -V geometry:margin=2cm \
  -V fontsize=12pt \
  -V linestretch=1.5 \
  -V papersize=a4paper \
  -V colorlinks=true \
  -V linkcolor=blue \
  -V urlcolor=blue \
  -V documentclass=article \
  --syntax-highlighting=tango \
  -V lang=en \
  2>&1 | grep -v "Overfull\|Underfull\|LaTeX Warning" | tail -20

# Cleanup
rm -rf "$TEMP_DIR"

if [ -f "$OUTPUT_PDF" ]; then
    echo ""
    echo "✅ PDF Generated Successfully!"
    ls -lh "$OUTPUT_PDF"
    echo ""
    echo "📍 Location: $(pwd)/$OUTPUT_PDF"
    exit 0
else
    echo ""
    echo "❌ PDF generation failed"
    exit 1
fi
