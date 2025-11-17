#!/bin/bash
# Aggressive fix for ALL old color references - replaces ALL instances

echo "🎨 Aggressive color fix - replacing ALL instances..."

COMPONENT_DIR="../alpine-frontend/components"
APP_DIR="../alpine-frontend/app"

# Function to update a file aggressively
update_file() {
  local file=$1
  if [ ! -f "$file" ]; then
    return
  fi
  
  # Skip backup files
  if [[ "$file" == *.bak* ]]; then
    return
  fi
  
  # Aggressive replacement - replace ALL instances regardless of context
  sed -i '' \
    -e 's/alpine-accent/alpine-neon-cyan/g' \
    -e 's/alpine-pink/alpine-neon-pink/g' \
    -e 's/alpine-blue/alpine-neon-purple/g' \
    -e 's/alpine-dark[^e]/alpine-black-primary/g' \
    -e 's/alpine-darker/alpine-black-primary/g' \
    -e 's/alpine-card[^-]/alpine-black-secondary/g' \
    -e 's/alpine-border[^-]/alpine-black-border/g' \
    -e 's/alpine-text-dim/alpine-text-secondary/g' \
    -e 's/alpine-text[^-]/alpine-text-primary/g' \
    -e 's/alpine-red[^-]/alpine-semantic-error/g' \
    -e 's/alpine-green[^-]/alpine-semantic-success/g' \
    -e 's/alpine-bg[^-]/alpine-black-primary/g' \
    "$file"
  
  # Fix any double replacements
  sed -i '' \
    -e 's/alpine-text-primary-primary/alpine-text-primary/g' \
    -e 's/alpine-text-primary-secondary/alpine-text-secondary/g' \
    -e 's/alpine-text-primary-tertiary/alpine-text-tertiary/g' \
    -e 's/alpine-black-primary-primary/alpine-black-primary/g' \
    -e 's/alpine-black-primary-secondary/alpine-black-secondary/g' \
    "$file"
  
  echo "  ✅ Updated: $(basename $file)"
}

# Find and update all TSX files
find "$COMPONENT_DIR" "$APP_DIR" -name "*.tsx" -type f ! -name "*.bak*" | while read file; do
  if grep -qE "(alpine-accent|alpine-pink|alpine-blue|alpine-dark|alpine-darker|alpine-card|alpine-border|alpine-text-dim|alpine-text[^-]|alpine-red|alpine-green|alpine-bg)" "$file"; then
    update_file "$file"
  fi
done

echo ""
echo "✅ Aggressive color fix complete!"

