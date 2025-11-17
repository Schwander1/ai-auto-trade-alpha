#!/bin/bash
# Comprehensive fix for ALL broken class name patterns

echo "🔧 Comprehensive class name fix..."

COMPONENT_DIR="../alpine-frontend/components"
APP_DIR="../alpine-frontend/app"

fix_file() {
  local file=$1
  if [ ! -f "$file" ]; then
    return
  fi
  
  if [[ "$file" == *.bak* ]]; then
    return
  fi
  
  # Fix all broken patterns comprehensively
  sed -i '' \
    -e 's/bg-alpine-blackprimar-y/bg-alpine-black-primary/g' \
    -e 's/bg-alpine-blackprimaryfle-x/bg-alpine-black-primary flex/g' \
    -e 's/bg-alpine-blackprimaryrounded--/bg-alpine-black-primary rounded-/g' \
    -e 's/bg-alpine-blacksecondaryborde-r/bg-alpine-black-secondary border/g' \
    -e 's/bg-alpine-blacksecondaryborde-rborder-/bg-alpine-black-secondary border /g' \
    -e 's/bg-alpine-blacksecondaryborde-rborder-alpine-blackborderrounded--/bg-alpine-black-secondary border border-alpine-black-border rounded-/g' \
    -e 's/bg-alpine-blacksecondaryborde-rborder-alpine-blackborderrounded--lgp-/bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-/g' \
    -e 's/text-alpine-textprimar-y/text-alpine-text-primary/g' \
    -e 's/text-alpine-textsecondar-y/text-alpine-text-secondary/g' \
    -e 's/text-alpine-textseconda-ry/text-alpine-text-secondary/g' \
    -e 's/text-alpine-text-secondarymb-/text-alpine-text-secondary mb-/g' \
    -e 's/text-alpine-text-secondarytext-/text-alpine-text-secondary text-/g' \
    -e 's/text-alpine-text-primary  /text-alpine-text-primary /g' \
    -e 's/text-alpine-text-primaryfont-/text-alpine-text-primary font-/g' \
    -e 's/text-alpine-semanticsucces-s/text-alpine-semantic-success/g' \
    -e 's/text-alpine-semanticsucce-ss/text-alpine-semantic-success/g' \
    -e 's/text-alpine-semanticsuccess-mb-/text-alpine-semantic-success mb-/g' \
    -e 's/text-alpine-semanticsuccessfontbo-ld/text-alpine-semantic-success font-bold/g' \
    -e 's/text-alpine-semanticsuccesshov-er:/text-alpine-semantic-success hover:/g' \
    -e 's/text-alpine-semanticerror-mb-/text-alpine-semantic-error mb-/g' \
    -e 's/text-alpine-orangem-b-/text-alpine-orange mb-/g' \
    -e 's/text-alpine-neon-purplemb-/text-alpine-neon-purple mb-/g' \
    -e 's/border-alpine-blackborderrounded--/border-alpine-black-border rounded-/g' \
    -e 's/border-alpine-blackborderrounded--lgp-/border-alpine-black-border rounded-lg p-/g' \
    "$file"
  
  echo "  ✅ Fixed: $(basename $file)"
}

find "$COMPONENT_DIR" "$APP_DIR" -name "*.tsx" -type f ! -name "*.bak*" | while read file; do
  if grep -qE "(bg-alpine-blackprimar|bg-alpine-blacksecondary|text-alpine-textprimar|text-alpine-textsecondar|text-alpine-semanticsucces)" "$file"; then
    fix_file "$file"
  fi
done

echo ""
echo "✅ Comprehensive class name fix complete!"

