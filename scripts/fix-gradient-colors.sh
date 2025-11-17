#!/bin/bash
# Fix hardcoded gradient colors to use brand CSS variables

echo "🎨 Fixing hardcoded gradient colors..."

COMPONENT_DIR="../alpine-frontend/components"

# Function to update gradient colors
update_gradients() {
  local file=$1
  if [ ! -f "$file" ]; then
    return
  fi
  
  # Create backup
  cp "$file" "$file.bak-grad"
  
  # Replace hardcoded rgba colors with brand-aligned values
  # Cyan: rgba(0,240,255,0.05) -> rgba(24,224,255,0.05) (alpine-neon-cyan)
  # Pink: rgba(255,0,110,0.05) -> rgba(254,28,128,0.05) (alpine-neon-pink)
  # Purple: rgba(176,38,255,0.05) -> rgba(150,0,255,0.05) (alpine-neon-purple)
  # Red: rgba(255,45,85,0.05) -> rgba(255,45,85,0.05) (alpine-semantic-error - already correct)
  
  sed -i '' \
    -e 's/rgba(0,240,255,0\.05)/rgba(24,224,255,0.05)/g' \
    -e 's/rgba(255,0,110,0\.05)/rgba(254,28,128,0.05)/g' \
    -e 's/rgba(176,38,255,0\.05)/rgba(150,0,255,0.05)/g' \
    "$file"
  
  echo "  ✅ Updated: $file"
}

# Find and update files with hardcoded gradients
find "$COMPONENT_DIR" -name "*.tsx" -type f ! -name "*.bak*" | while read file; do
  if grep -q "bg-\[radial-gradient.*rgba" "$file"; then
    update_gradients "$file"
  fi
done

echo ""
echo "✅ Gradient color fixes complete!"
echo "📝 Review changes and remove .bak-grad files when satisfied"

