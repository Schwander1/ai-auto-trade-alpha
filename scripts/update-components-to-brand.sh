#!/bin/bash
# Script to update all components to use Alpine brand system colors

echo "🎨 Updating components to use Alpine brand system..."

# Color mappings
declare -A color_map=(
  ["electric-cyan"]="alpine-neon-cyan"
  ["neon-pink"]="alpine-neon-pink"
  ["neon-purple"]="alpine-neon-purple"
  ["laser-green"]="alpine-semantic-success"
  ["warning-red"]="alpine-semantic-error"
  ["ice-blue"]="alpine-text-primary"
  ["space-gray"]="alpine-black-primary"
  ["black"]="alpine-black-primary"
)

# Find all component files
COMPONENT_DIR="../alpine-frontend/components"

for file in $(find "$COMPONENT_DIR" -name "*.tsx" -o -name "*.ts"); do
  if [ -f "$file" ]; then
    echo "Processing: $file"
    
    # Create backup
    cp "$file" "$file.bak"
    
    # Replace colors
    for old_color in "${!color_map[@]}"; do
      new_color="${color_map[$old_color]}"
      sed -i '' "s/$old_color/$new_color/g" "$file"
    done
    
    # Replace text-ice-blue with text-alpine-text-primary
    sed -i '' "s/text-ice-blue/text-alpine-text-primary/g" "$file"
    sed -i '' "s/text-electric-cyan/text-alpine-neon-cyan/g" "$file"
    sed -i '' "s/text-neon-pink/text-alpine-neon-pink/g" "$file"
    sed -i '' "s/text-neon-purple/text-alpine-neon-purple/g" "$file"
    sed -i '' "s/text-laser-green/text-alpine-semantic-success/g" "$file"
    sed -i '' "s/text-warning-red/text-alpine-semantic-error/g" "$file"
    
    # Replace bg- colors
    sed -i '' "s/bg-electric-cyan/bg-alpine-neon-cyan/g" "$file"
    sed -i '' "s/bg-neon-pink/bg-alpine-neon-pink/g" "$file"
    sed -i '' "s/bg-neon-purple/bg-alpine-neon-purple/g" "$file"
    sed -i '' "s/bg-laser-green/bg-alpine-semantic-success/g" "$file"
    sed -i '' "s/bg-warning-red/bg-alpine-semantic-error/g" "$file"
    sed -i '' "s/bg-space-gray/bg-alpine-black-primary/g" "$file"
    
    # Replace border- colors
    sed -i '' "s/border-electric-cyan/border-alpine-neon-cyan/g" "$file"
    sed -i '' "s/border-neon-pink/border-alpine-neon-pink/g" "$file"
    sed -i '' "s/border-neon-purple/border-alpine-neon-purple/g" "$file"
    
    echo "  ✅ Updated: $file"
  fi
done

echo ""
echo "✅ Component update complete!"
echo "📝 Review changes and remove .bak files when satisfied"

