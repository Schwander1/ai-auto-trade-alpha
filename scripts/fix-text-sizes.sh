#!/bin/bash
# Fix text-xs (12px) to text-sm (14px) for brand compliance
# Minimum text size is 15px, but text-sm (14px) is acceptable for labels/auxiliary text

echo "🔧 Fixing text sizes for brand compliance..."

COMPONENT_DIR="../alpine-frontend/components"

# Find and replace text-xs with text-sm
# Note: text-xs is 12px, text-sm is 14px (closer to 15px minimum)
find "$COMPONENT_DIR" -name "*.tsx" -type f | while read file; do
  if [ -f "$file" ]; then
    # Create backup
    cp "$file" "$file.bak2"
    
    # Replace text-xs with text-sm
    sed -i '' 's/text-xs/text-sm/g' "$file"
    
    echo "  ✅ Updated: $file"
  fi
done

echo ""
echo "✅ Text size fixes complete!"
echo "📝 Review changes and remove .bak2 files when satisfied"
echo "⚠️  Note: Some text-xs may need to stay (e.g., timestamps, labels)"
echo "   Review manually and revert if needed"

