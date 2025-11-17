#!/bin/bash
# Final comprehensive fix for ALL old color references

echo "🎨 Final comprehensive color fix..."

COMPONENT_DIR="../alpine-frontend/components"
APP_DIR="../alpine-frontend/app"

# Function to update a file
update_file() {
  local file=$1
  if [ ! -f "$file" ]; then
    return
  fi
  
  # Skip backup files
  if [[ "$file" == *.bak* ]]; then
    return
  fi
  
  # Update old color names to brand colors - comprehensive with all variations
  sed -i '' \
    -e 's/\balpine-accent\b/alpine-neon-cyan/g' \
    -e 's/\balpine-pink\b/alpine-neon-pink/g' \
    -e 's/\balpine-blue\b/alpine-neon-purple/g' \
    -e 's/\balpine-dark\b/alpine-black-primary/g' \
    -e 's/\balpine-darker\b/alpine-black-primary/g' \
    -e 's/\balpine-card\b/alpine-black-secondary/g' \
    -e 's/\balpine-border\b/alpine-black-border/g' \
    -e 's/\balpine-text-dim\b/alpine-text-secondary/g' \
    -e 's/\balpine-text\b/alpine-text-primary/g' \
    -e 's/\balpine-red\b/alpine-semantic-error/g' \
    -e 's/\balpine-green\b/alpine-semantic-success/g' \
    -e 's/\balpine-bg\b/alpine-black-primary/g' \
    "$file"
  
  echo "  ✅ Updated: $(basename $file)"
}

# Find and update all TSX files
find "$COMPONENT_DIR" "$APP_DIR" -name "*.tsx" -type f ! -name "*.bak*" | while read file; do
  if grep -qE "\b(alpine-accent|alpine-pink|alpine-blue|alpine-dark|alpine-darker|alpine-card|alpine-border|alpine-text-dim|alpine-text[^-]|alpine-red|alpine-green|alpine-bg)\b" "$file"; then
    update_file "$file"
  fi
done

echo ""
echo "✅ Final color fix complete!"

