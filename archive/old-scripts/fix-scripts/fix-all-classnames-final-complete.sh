#!/bin/bash
# Final comprehensive fix for ALL broken class name patterns

echo "🔧 Final comprehensive class name fix..."

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
  
  # Comprehensive fix for all broken patterns
  sed -i '' \
    -e 's/bg-alpine-black-primarytext-/bg-alpine-black-primary text-/g' \
    -e 's/bg-alpine-black-primaryflex-/bg-alpine-black-primary flex-/g' \
    -e 's/bg-alpine-black-primaryborder-/bg-alpine-black-primary border-/g' \
    -e 's/bg-alpine-black-primaryp-/bg-alpine-black-primary p-/g' \
    -e 's/bg-alpine-black-primaryrounded-/bg-alpine-black-primary rounded-/g' \
    -e 's/bg-alpine-black-secondaryborder-/bg-alpine-black-secondary border-/g' \
    -e 's/bg-alpine-black-secondaryborde-r/bg-alpine-black-secondary border/g' \
    -e 's/borderborder-/border border-/g' \
    -e 's/borderborder-alpine-/border border-alpine-/g' \
    -e 's/rounded-lgp-/rounded-lg p-/g' \
    -e 's/rounded-lgtext-/rounded-lg text-/g' \
    -e 's/rounded-lgfont-/rounded-lg font-/g' \
    -e 's/rounded-lghover:/rounded-lg hover:/g' \
    -e 's/rounded-lgoverflow-/rounded-lg overflow-/g' \
    -e 's/text-alpine-text-primarycapitalize/text-alpine-text-primary capitalize/g' \
    -e 's/text-alpine-text-primaryfocus:/text-alpine-text-primary focus:/g' \
    -e 's/text-alpine-text-primaryfont-/text-alpine-text-primary font-/g' \
    -e 's/text-alpine-text-primary /text-alpine-text-primary /g' \
    -e 's/text-alpine-text-primary"/text-alpine-text-primary"/g' \
    -e 's/text-alpine-text-secondarycapitalize/text-alpine-text-secondary capitalize/g' \
    -e 's/text-alpine-text-secondarymb-/text-alpine-text-secondary mb-/g' \
    -e 's/text-alpine-text-secondarytext-/text-alpine-text-secondary text-/g' \
    -e 's/text-alpine-text-secondaryfont-/text-alpine-text-secondary font-/g' \
    -e 's/text-alpine-neoncya-n/text-alpine-neon-cyan/g' \
    -e 's/text-alpine-neon-cyananimate-/text-alpine-neon-cyan animate-/g' \
    -e 's/text-alpine-neon-cyanrounded-/text-alpine-neon-cyan rounded-/g' \
    -e 's/text-alpine-neon-cyanborder-/text-alpine-neon-cyan border-/g' \
    -e 's/text-alpine-neon-cyancapitalize/text-alpine-neon-cyan capitalize/g' \
    -e 's/bg-alpine-neoncya-n/bg-alpine-neon-cyan/g' \
    -e 's/bg-alpine-neon-cyantext-/bg-alpine-neon-cyan text-/g' \
    -e 's/text-alpine-semantic-errormxa-uto/text-alpine-semantic-error mx-auto/g' \
    -e 's/text-alpine-semantic-errormb-/text-alpine-semantic-error mb-/g' \
    -e 's/text-alpine-semantic-errorfont-/text-alpine-semantic-error font-/g' \
    -e 's/text-alpine-semantic-error10/text-alpine-semantic-error\/10/g' \
    -e 's/text-alpine-semantic-error30/text-alpine-semantic-error\/30/g' \
    -e 's/bg-alpine-semanticerr-or10/bg-alpine-semantic-error\/10/g' \
    -e 's/bg-alpine-semanticerr-or/bg-alpine-semantic-error/g' \
    -e 's/text-alpine-semanticerr-or/text-alpine-semantic-error/g' \
    -e 's/text-alpine-semantic-successfontbo-ld/text-alpine-semantic-success font-bold/g' \
    -e 's/text-alpine-semantic-successmb-/text-alpine-semantic-success mb-/g' \
    -e 's/text-alpine-semantic-success>/text-alpine-semantic-success">/g' \
    -e 's/text-alpine-semantic-successhover:/text-alpine-semantic-success hover:/g' \
    -e 's/text-alpine-semantic-successfont-/text-alpine-semantic-success font-/g' \
    -e 's/text-alpine-orangemb-/text-alpine-orange mb-/g' \
    -e 's/text-alpine-orangefont-/text-alpine-orange font-/g' \
    -e 's/text-alpine-neon-purplemb-/text-alpine-neon-purple mb-/g' \
    -e 's/border-alpine-blackborderflex-/border-alpine-black-border flex-/g' \
    -e 's/border-alpine-blackborderhover:/border-alpine-black-border hover:/g' \
    -e 's/border-alpine-blackborderrounded-/border-alpine-black-border rounded-/g' \
    -e 's/border-alpine-blackborderp-/border-alpine-black-border p-/g' \
    -e 's/border-alpine-blackbordertext-/border-alpine-black-border text-/g' \
    -e 's/border-alpine-blackborderfont-/border-alpine-black-border font-/g' \
    -e 's/border-alpine-blackborder80/border-alpine-black-border\/80/g' \
    -e 's/border-alpine-blackborder-/border-alpine-black-border /g' \
    -e 's/border-alpine-neon-cyantext-/border-alpine-neon-cyan text-/g' \
    -e 's/border-alpine-neon-cyanfont-/border-alpine-neon-cyan font-/g' \
    -e 's/border-alpine-neon-cyanrounded-/border-alpine-neon-cyan rounded-/g' \
    -e 's/border-alpine-neon-cyancapitalize/border-alpine-neon-cyan capitalize/g' \
    -e 's/hover:bg-alpine-blackprima-ry50/hover:bg-alpine-black-primary\/50/g' \
    -e 's/hover:bg-alpine-blackprima-ry80/hover:bg-alpine-black-primary\/80/g' \
    -e 's/hover:bg-alpine-blackprima-ry/hover:bg-alpine-black-primary/g' \
    -e 's/hover:border-alpine-neoncya-n/hover:border-alpine-neon-cyan/g' \
    -e 's/hover:border-alpine-neon-cyantext-/hover:border-alpine-neon-cyan text-/g' \
    -e 's/flexitems-centerjustify-center/flex items-center justify-center/g' \
    -e 's/flexitems-center/flex items-center/g' \
    -e 's/justify-centerpx-/justify-center px-/g' \
    -e 's/rounded-lgtext-/rounded-lg text-/g' \
    -e 's/rounded-lgfont-/rounded-lg font-/g' \
    -e 's/rounded-lgp-/rounded-lg p-/g' \
    -e 's/rounded-lgmb-/rounded-lg mb-/g' \
    -e 's/rounded-lgoverflow-/rounded-lg overflow-/g' \
    -e 's/rounded-lghover:/rounded-lg hover:/g' \
    -e 's/rounded-lgtransition-/rounded-lg transition-/g' \
    -e 's/rounded-lgdisabled:/rounded-lg disabled:/g' \
    -e 's/rounded-lgflex-/rounded-lg flex-/g' \
    -e 's/rounded-lgitems-/rounded-lg items-/g' \
    -e 's/rounded-lgjustify-/rounded-lg justify-/g' \
    -e 's/rounded-lg gap-/rounded-lg gap-/g' \
    -e 's/rounded-lgtext-/rounded-lg text-/g' \
    -e 's/rounded-lgfont-/rounded-lg font-/g' \
    -e 's/rounded-lgp-/rounded-lg p-/g' \
    -e 's/rounded-lgmb-/rounded-lg mb-/g' \
    -e 's/rounded-lgoverflow-/rounded-lg overflow-/g' \
    -e 's/rounded-lghover:/rounded-lg hover:/g' \
    -e 's/rounded-lgtransition-/rounded-lg transition-/g' \
    -e 's/rounded-lgdisabled:/rounded-lg disabled:/g' \
    -e 's/rounded-lgflex-/rounded-lg flex-/g' \
    -e 's/rounded-lgitems-/rounded-lg items-/g' \
    -e 's/rounded-lgjustify-/rounded-lg justify-/g' \
    -e 's/rounded-lg gap-/rounded-lg gap-/g' \
    "$file"
  
  echo "  ✅ Fixed: $(basename $file)"
}

find "$COMPONENT_DIR" "$APP_DIR" -name "*.tsx" -type f ! -name "*.bak*" | while read file; do
  if grep -qE "(bg-alpine-black-primarytext|bg-alpine-black-primaryflex|borderborder-|rounded-lgp-|text-alpine-text-primarycapitalize|text-alpine-neoncya-n|flexitems-center|rounded-lgtext|rounded-lgfont|hover:bg-alpine-blackprima-ry)" "$file"; then
    fix_file "$file"
  fi
done

echo ""
echo "✅ Final comprehensive class name fix complete!"

