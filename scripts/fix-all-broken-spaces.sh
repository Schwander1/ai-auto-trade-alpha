#!/bin/bash
# Fix ALL broken class names by adding spaces back

echo "🔧 Fixing ALL broken class name spaces..."

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
  # Pattern: alpine-xxx[letter] -> alpine-xxx [letter]
  sed -i '' \
    -e 's/\(alpine-[a-z-]*\)\([a-z]\)/\1 \2/g' \
    -e 's/\(alpine-[a-z-]*\)-\([a-z]\)/\1 \2/g' \
    -e 's/\(alpine-[a-z-]*\)\([0-9]\)/\1 \2/g' \
    -e 's/\(alpine-[a-z-]*\)-\([0-9]\)/\1 \2/g' \
    -e 's/\(alpine-[a-z-]*\)>/\1">/g' \
    -e 's/\(alpine-[a-z-]*\)-\([a-z-]*\)/\1-\2/g' \
    "$file"
  
  # Fix specific patterns
  sed -i '' \
    -e 's/text-alpine-text-primary- /text-alpine-text-primary /g' \
    -e 's/text-alpine-text-secondary\([a-z]\)/text-alpine-text-secondary \1/g' \
    -e 's/bg-alpine-black-primary\([a-z]\)/bg-alpine-black-primary \1/g' \
    -e 's/from-alpine-neon-cyan\([a-z]\)/from-alpine-neon-cyan \1/g' \
    -e 's/to-alpine-neon-pink\([a-z]\)/to-alpine-neon-pink \1/g' \
    -e 's/border-alpine-black-border\([a-z]\)/border-alpine-black-border \1/g' \
    -e 's/text-alpine-neon-cyan\([a-z]\)/text-alpine-neon-cyan \1/g' \
    -e 's/bg-alpine-neon-cyan\([a-z]\)/bg-alpine-neon-cyan \1/g' \
    -e 's/text-alpine-semantic-error\([a-z]\)/text-alpine-semantic-error \1/g' \
    -e 's/text-alpine-orange\([a-z]\)/text-alpine-orange \1/g' \
    -e 's/text-alpine-neon-cyantext-/text-alpine-neon-cyan text-/g' \
    -e 's/from-alpine-neon-cyanto-/from-alpine-neon-cyan to-/g' \
    -e 's/hover:from-alpine-neon-pink-hover:/hover:from-alpine-neon-pink hover:/g' \
    -e 's/hover:to-alpine-neon-cyantransition-/hover:to-alpine-neon-cyan transition-/g' \
    -e 's/bg-alpine-black-primaryborder-/bg-alpine-black-primary border-/g' \
    -e 's/bg-alpine-black-primarypy-/bg-alpine-black-primary py-/g' \
    -e 's/bg-alpine-black-primaryp-/bg-alpine-black-primary p-/g' \
    -e 's/border-alpine-black-borderrounded-/border-alpine-black-border rounded-/g' \
    -e 's/border-alpine-black-borderp-/border-alpine-black-border p-/g' \
    -e 's/text-alpine-text-secondaryleading-/text-alpine-text-secondary leading-/g' \
    -e 's/text-alpine-text-secondarytext-/text-alpine-text-secondary text-/g' \
    -e 's/text-alpine-text-secondarymb-/text-alpine-text-secondary mb-/g' \
    -e 's/text-alpine-text-secondarymax-/text-alpine-text-secondary max-/g' \
    -e 's/text-alpine-text-secondarytext-sm-/text-alpine-text-secondary text-sm /g' \
    -e 's/text-alpine-text-secondarytext-sm/text-alpine-text-secondary text-sm/g' \
    -e 's/text-alpine-text-secondarymb-4/text-alpine-text-secondary mb-4/g' \
    -e 's/text-alpine-text-primary- /text-alpine-text-primary /g' \
    -e 's/text-alpine-text-primary-"/text-alpine-text-primary "/g' \
    -e 's/text-alpine-text-primary-\([a-z]\)/text-alpine-text-primary \1/g' \
    -e 's/text-alpine-neon-cyanfont-/text-alpine-neon-cyan font-/g' \
    -e 's/text-alpine-neon-cyanmb-/text-alpine-neon-cyan mb-/g' \
    -e 's/bg-alpine-neon-cyantext-/bg-alpine-neon-cyan text-/g' \
    -e 's/text-alpine-semantic-errorfont-/text-alpine-semantic-error font-/g' \
    -e 's/text-alpine-semantic-errormr-/text-alpine-semantic-error mr-/g' \
    -e 's/text-alpine-orangeflex-/text-alpine-orange flex-/g' \
    -e 's/text-alpine-orangemr-/text-alpine-orange mr-/g' \
    -e 's/text-alpine-neon-cyantext-center-/text-alpine-neon-cyan text-center /g' \
    -e 's/border-alpine-black-bordertext-/border-alpine-black-border text-/g' \
    -e 's/border-alpine-black-borderfont-/border-alpine-black-border font-/g' \
    -e 's/border-alpine-black-borderrounded-lg-/border-alpine-black-border rounded-lg /g' \
    -e 's/border-alpine-black-borderp-6/border-alpine-black-border p-6/g' \
    -e 's/bg-alpine-black-secondaryborder-/bg-alpine-black-secondary border-/g' \
    -e 's/bg-alpine-black-secondaryrounded-/bg-alpine-black-secondary rounded-/g' \
    -e 's/bg-alpine-black-secondaryp-/bg-alpine-black-secondary p-/g' \
    -e 's/bg-alpine-semantic-successhover:/bg-alpine-semantic-success hover:/g' \
    -e 's/from-alpine-neon-cyanto-alpine-neon-pink-/from-alpine-neon-cyan to-alpine-neon-pink /g' \
    -e 's/from-alpine-neon-cyanto-alpine-neon-pink-bg-/from-alpine-neon-cyan to-alpine-neon-pink bg-/g' \
    -e 's/bg-alpine-black-primaryborder-y-/bg-alpine-black-primary border-y /g' \
    -e 's/border-y-border-alpine-black-border/border-y border-alpine-black-border/g' \
    -e 's/card-neon border border-alpine-black-borderrounded-/card-neon border border-alpine-black-border rounded-/g' \
    -e 's/card-neon border border-alpine-black-borderp-/card-neon border border-alpine-black-border p-/g' \
    -e 's/card-neon rounded-lg border border-alpine-black-borderp-/card-neon rounded-lg border border-alpine-black-border p-/g' \
    -e 's/card-neon hover:bg-alpine-black-primaryborder-/card-neon hover:bg-alpine-black-primary border-/g' \
    -e 's/card-neon border-2 border-alpine-black-bordertext-/card-neon border-2 border-alpine-black-border text-/g' \
    -e 's/card-neon border-2 border-alpine-black-borderfont-/card-neon border-2 border-alpine-black-border font-/g' \
    "$file"
  
  echo "  ✅ Fixed: $(basename $file)"
}

# Find and fix all TSX files
find "$COMPONENT_DIR" "$APP_DIR" -name "*.tsx" -type f ! -name "*.bak*" | while read file; do
  if grep -qE "(alpine-[a-z-]*[a-z0-9]|alpine-[a-z-]*-[a-z]|alpine-[a-z-]*>)" "$file"; then
    fix_file "$file"
  fi
done

echo ""
echo "✅ All broken class name spaces fixed!"

