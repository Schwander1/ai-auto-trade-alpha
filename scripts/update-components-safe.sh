#!/bin/bash
# Safe component update script - updates color names without breaking numbers

echo "🎨 Safely updating components to Alpine brand system..."

COMPONENT_DIR="../alpine-frontend/components"

# Function to update a file safely
update_file() {
  local file=$1
  if [ ! -f "$file" ]; then
    return
  fi
  
  # Create backup
  cp "$file" "$file.bak-safe"
  
  # Use word boundaries to avoid replacing "0" in numbers
  # Update color names with word boundaries
  sed -i '' \
    -e 's/\belectric-cyan\b/alpine-neon-cyan/g' \
    -e 's/\bneon-pink\b/alpine-neon-pink/g' \
    -e 's/\bneon-purple\b/alpine-neon-purple/g' \
    -e 's/\blaser-green\b/alpine-semantic-success/g' \
    -e 's/\bwarning-red\b/alpine-semantic-error/g' \
    -e 's/\bice-blue\b/alpine-text-primary/g' \
    -e 's/\bspace-gray\b/alpine-black-primary/g' \
    "$file"
  
  # Update text- prefixed colors
  sed -i '' \
    -e 's/\btext-electric-cyan\b/text-alpine-neon-cyan/g' \
    -e 's/\btext-neon-pink\b/text-alpine-neon-pink/g' \
    -e 's/\btext-neon-purple\b/text-alpine-neon-purple/g' \
    -e 's/\btext-laser-green\b/text-alpine-semantic-success/g' \
    -e 's/\btext-warning-red\b/text-alpine-semantic-error/g' \
    -e 's/\btext-ice-blue\b/text-alpine-text-primary/g' \
    "$file"
  
  # Update bg- prefixed colors
  sed -i '' \
    -e 's/\bbg-electric-cyan\b/bg-alpine-neon-cyan/g' \
    -e 's/\bbg-neon-pink\b/bg-alpine-neon-pink/g' \
    -e 's/\bbg-neon-purple\b/bg-alpine-neon-purple/g' \
    -e 's/\bbg-laser-green\b/bg-alpine-semantic-success/g' \
    -e 's/\bbg-warning-red\b/bg-alpine-semantic-error/g' \
    -e 's/\bbg-ice-blue\b/bg-alpine-text-primary/g' \
    -e 's/\bbg-space-gray\b/bg-alpine-black-primary/g' \
    "$file"
  
  # Update border- prefixed colors
  sed -i '' \
    -e 's/\bborder-electric-cyan\b/border-alpine-neon-cyan/g' \
    -e 's/\bborder-neon-pink\b/border-alpine-neon-pink/g' \
    -e 's/\bborder-neon-purple\b/border-alpine-neon-purple/g' \
    -e 's/\bborder-laser-green\b/border-alpine-semantic-success/g' \
    -e 's/\bborder-warning-red\b/border-alpine-semantic-error/g' \
    "$file"
  
  echo "  ✅ Updated: $file"
}

# Find and update all component files
find "$COMPONENT_DIR" -name "*.tsx" -type f | while read file; do
  update_file "$file"
done

echo ""
echo "✅ Safe component update complete!"
echo "📝 Review changes and remove .bak-safe files when satisfied"

