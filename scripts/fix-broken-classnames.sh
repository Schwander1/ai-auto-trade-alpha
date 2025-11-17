#!/bin/bash
# Fix broken class names from aggressive replacement

echo "🔧 Fixing broken class names..."

COMPONENT_DIR="../alpine-frontend/components"
APP_DIR="../alpine-frontend/app"

# Function to fix a file
fix_file() {
  local file=$1
  if [ ! -f "$file" ]; then
    return
  fi
  
  # Skip backup files
  if [[ "$file" == *.bak* ]]; then
    return
  fi
  
  # Fix broken class names - add spaces where needed
  sed -i '' \
    -e 's/text-alpine-text-primarymb-/text-alpine-text-primary mb-/g' \
    -e 's/text-alpine-text-primarytext-/text-alpine-text-primary text-/g' \
    -e 's/text-alpine-text-primaryhover:/text-alpine-text-primary hover:/g' \
    -e 's/text-alpine-text-primary>/text-alpine-text-primary">/g' \
    -e 's/text-alpine-text-primary"/text-alpine-text-primary "/g' \
    -e 's/border-alpine-black-bordertext-/border-alpine-black-border text-/g' \
    -e 's/bg-alpine-black-secondarybg-/bg-alpine-black-secondary bg-/g' \
    -e 's/text-alpine-semantic-errormr-/text-alpine-semantic-error mr-/g' \
    "$file"
  
  echo "  ✅ Fixed: $(basename $file)"
}

# Find and fix all TSX files
find "$COMPONENT_DIR" "$APP_DIR" -name "*.tsx" -type f ! -name "*.bak*" | while read file; do
  if grep -qE "(text-alpine-text-primary[^-\s\"']|border-alpine-black-bordertext-|bg-alpine-black-secondarybg-|text-alpine-semantic-errormr-)" "$file"; then
    fix_file "$file"
  fi
done

echo ""
echo "✅ Broken class names fixed!"

