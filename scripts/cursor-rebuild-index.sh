#!/bin/bash

# Cursor Rebuild Codebase Index Script
# Helps rebuild the Cursor codebase index for better AI assistance

set -e

echo "🔄 Cursor Codebase Index Rebuild Helper"
echo ""
echo "This script helps you rebuild the Cursor codebase index."
echo "A rebuilt index improves AI assistance accuracy and speed."
echo ""
echo "To rebuild the index manually:"
echo "  1. Open Command Palette: Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows/Linux)"
echo "  2. Type: 'Cursor: Rebuild Codebase Index'"
echo "  3. Press Enter and wait for completion"
echo ""
echo "Alternatively, you can:"
echo "  - Click on the Cursor icon in the status bar"
echo "  - Select 'Rebuild Codebase Index'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Current Index Status:"
echo ""

# Check if .cursor directory exists
if [ -d ".cursor" ]; then
    echo "✅ Cursor configuration directory found"
else
    echo "❌ Cursor configuration directory not found"
    exit 1
fi

# Check if .cursorignore exists
if [ -f ".cursorignore" ]; then
    EXCLUDED_COUNT=$(wc -l < .cursorignore | tr -d ' ')
    echo "✅ .cursorignore found ($EXCLUDED_COUNT exclusion patterns)"
else
    echo "⚠️  .cursorignore not found (indexing may be slower)"
fi

# Count files that would be indexed
echo ""
echo "📁 Files to be indexed (approximate):"
echo ""

PYTHON_FILES=$(find . -name "*.py" -not -path "*/node_modules/*" -not -path "*/venv/*" -not -path "*/__pycache__/*" -not -path "*/.pytest_cache/*" -not -path "*/archive/*" -not -path "*/backups/*" 2>/dev/null | wc -l | tr -d ' ')
TS_FILES=$(find . -name "*.ts" -o -name "*.tsx" -not -path "*/node_modules/*" -not -path "*/dist/*" -not -path "*/.next/*" -not -path "*/archive/*" -not -path "*/backups/*" 2>/dev/null | wc -l | tr -d ' ')
JS_FILES=$(find . -name "*.js" -o -name "*.jsx" -not -path "*/node_modules/*" -not -path "*/dist/*" -not -path "*/.next/*" -not -path "*/archive/*" -not -path "*/backups/*" 2>/dev/null | wc -l | tr -d ' ')
MD_FILES=$(find . -name "*.md" -not -path "*/node_modules/*" -not -path "*/archive/*" -not -path "*/backups/*" -not -path "*/pdfs/*" 2>/dev/null | wc -l | tr -d ' ')

echo "  Python files: $PYTHON_FILES"
echo "  TypeScript files: $TS_FILES"
echo "  JavaScript files: $JS_FILES"
echo "  Markdown files: $MD_FILES"
echo ""
TOTAL=$((PYTHON_FILES + TS_FILES + JS_FILES + MD_FILES))
echo "  Total: ~$TOTAL files"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Tips for better indexing:"
echo ""
echo "  • Rebuild after major code changes"
echo "  • Rebuild after adding new dependencies"
echo "  • Rebuild if AI suggestions seem inaccurate"
echo "  • Rebuild takes 2-5 minutes depending on codebase size"
echo ""
echo "✨ Ready to rebuild? Follow the instructions above!"
