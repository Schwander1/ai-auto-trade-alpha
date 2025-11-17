#!/bin/bash
# Fix display font letter spacing - add tracking-[0.15em] to all font-display without explicit tracking

echo "🔧 Fixing display font letter spacing..."

COMPONENT_DIR="../alpine-frontend/components"

# Find files with font-display that don't have tracking
find "$COMPONENT_DIR" -name "*.tsx" -type f ! -name "*.bak*" | while read file; do
  if [ -f "$file" ]; then
    # Check if file has font-display without tracking
    if grep -q "font-display" "$file" && ! grep -q "font-display.*tracking" "$file"; then
      # Create backup
      cp "$file" "$file.bak-ls"
      
      # Add tracking-[0.15em] to font-display classes that are h1, h2, h3 (main headlines)
      # This is a conservative approach - only add to large display text
      sed -i '' \
        -e 's/className="font-display text-\([4-7]\)xl/className="font-display text-\1xl tracking-[0.15em]/g' \
        -e 's/className="font-display text-\([4-7]\)xl/className="font-display text-\1xl tracking-[0.15em]/g' \
        "$file"
      
      echo "  ✅ Updated: $file"
    fi
  fi
done

echo ""
echo "✅ Letter spacing fixes complete!"
echo "📝 Review changes and remove .bak-ls files when satisfied"

