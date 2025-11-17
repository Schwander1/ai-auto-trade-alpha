#!/bin/bash
# Final fix for broken class names - restore correct spacing

echo "🔧 Final fix for broken class names..."

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
  
  # Fix broken patterns - restore correct class names
  sed -i '' \
    -e 's/text-alpine-textprimar-y/text-alpine-text-primary/g' \
    -e 's/text-alpine-textsecondar-y/text-alpine-text-secondary/g' \
    -e 's/text-alpine-neoncya-n/text-alpine-neon-cyan/g' \
    -e 's/text-alpine-neonpin-k/text-alpine-neon-pink/g' \
    -e 's/text-alpine-neonpurpl-e/text-alpine-neon-purple/g' \
    -e 's/text-alpine-semanticerro-r/text-alpine-semantic-error/g' \
    -e 's/text-alpine-orang-e/text-alpine-orange/g' \
    -e 's/bg-alpine-black-primaryp-y-/bg-alpine-black-primary py-/g' \
    -e 's/bg-alpine-black-primaryborde-r-/bg-alpine-black-primary border-/g' \
    -e 's/bg-alpine-black-primaryborder-y-/bg-alpine-black-primary border-y /g' \
    -e 's/bg-alpine-black-primaryp-/bg-alpine-black-primary p-/g' \
    -e 's/border-alpine-blackborde-r/border-alpine-black-border/g' \
    -e 's/border-alpine-blackborder-/border-alpine-black-border /g' \
    -e 's/border-alpine-black-borderrounded-/border-alpine-black-border rounded-/g' \
    -e 's/border-alpine-black-borderroundedl-g-/border-alpine-black-border rounded-lg /g' \
    -e 's/border-alpine-black-borderp-/border-alpine-black-border p-/g' \
    -e 's/border-alpine-black-bordertext-/border-alpine-black-border text-/g' \
    -e 's/border-alpine-black-borderfont-/border-alpine-black-border font-/g' \
    -e 's/from-alpine-neon-cyanto-/from-alpine-neon-cyan to-/g' \
    -e 's/from-alpine-neon-cyanto-alpine-neon-pink-/from-alpine-neon-cyan to-alpine-neon-pink /g' \
    -e 's/from-alpine-neon-cyanto-alpine-neon-pink-bg-/from-alpine-neon-cyan to-alpine-neon-pink bg-/g' \
    -e 's/hover:from-alpine-neon-pinkhover:/hover:from-alpine-neon-pink hover:/g' \
    -e 's/hover:to-alpine-neon-cyanhover:/hover:to-alpine-neon-cyan hover:/g' \
    -e 's/hover:to-alpine-neon-cyantext-/hover:to-alpine-neon-cyan text-/g' \
    -e 's/hover:to-alpine-neon-cyantransition-/hover:to-alpine-neon-cyan transition-/g' \
    -e 's/text-alpine-text-secondarym-b-/text-alpine-text-secondary mb-/g' \
    -e 's/text-alpine-text-secondaryleading-/text-alpine-text-secondary leading-/g' \
    -e 's/text-alpine-text-secondarytext-/text-alpine-text-secondary text-/g' \
    -e 's/text-alpine-text-secondarymax-/text-alpine-text-secondary max-/g' \
    -e 's/text-alpine-text-secondarytext-sm-/text-alpine-text-secondary text-sm /g' \
    -e 's/text-alpine-text-secondarytext-smma-x-/text-alpine-text-secondary text-sm max-/g' \
    -e 's/text-alpine-text-primarym-b-/text-alpine-text-primary mb-/g' \
    -e 's/text-alpine-text-primary-/text-alpine-text-primary /g' \
    -e 's/text-alpine-neon-cyanm-b-/text-alpine-neon-cyan mb-/g' \
    -e 's/text-alpine-neon-cyanfont-/text-alpine-neon-cyan font-/g' \
    -e 's/text-alpine-neon-cyantext-/text-alpine-neon-cyan text-/g' \
    -e 's/bg-alpine-neon-cyantext-/bg-alpine-neon-cyan text-/g' \
    -e 's/text-alpine-semantic-errorfont-/text-alpine-semantic-error font-/g' \
    -e 's/text-alpine-semantic-errormr-/text-alpine-semantic-error mr-/g' \
    -e 's/text-alpine-orangeflex-/text-alpine-orange flex-/g' \
    -e 's/text-alpine-orangemr-/text-alpine-orange mr-/g' \
    -e 's/text-alpine-orangeflexshri-n k-/text-alpine-orange flex-shrink-/g' \
    -e 's/bg-alpine-black-secondaryborder-/bg-alpine-black-secondary border-/g' \
    -e 's/bg-alpine-black-secondaryrounded-/bg-alpine-black-secondary rounded-/g' \
    -e 's/bg-alpine-black-secondaryp-/bg-alpine-black-secondary p-/g' \
    -e 's/bg-alpine-semantic-successhover:/bg-alpine-semantic-success hover:/g' \
    -e 's/card-neon border border-alpine-black-borderrounded-/card-neon border border-alpine-black-border rounded-/g' \
    -e 's/card-neon border border-alpine-black-borderp-/card-neon border border-alpine-black-border p-/g' \
    -e 's/card-neon border-2 border-alpine-black-bordertext-/card-neon border-2 border-alpine-black-border text-/g' \
    -e 's/card-neon border-2 border-alpine-black-borderfont-/card-neon border-2 border-alpine-black-border font-/g' \
    -e 's/card-neon hover:bg-alpine-black-primaryborder-/card-neon hover:bg-alpine-black-primary border-/g' \
    -e 's/card-neon rounded-lg border border-alpine-blackborder-/card-neon rounded-lg border border-alpine-black-border /g' \
    -e 's/card-neon rounded-lg border border-alpine-blackborder-p-/card-neon rounded-lg border border-alpine-black-border p-/g' \
    -e 's/bg-alpine-blackprimary-/bg-alpine-black-primary /g' \
    -e 's/bg-alpine-blackprimary-p-/bg-alpine-black-primary p-/g' \
    -e 's/text-alpine-neon-cyanfont-mono-/text-alpine-neon-cyan font-mono /g' \
    -e 's/text-alpine-neon-cyanfont-mono-overflow-/text-alpine-neon-cyan font-mono overflow-/g' \
    -e 's/text-alpine-neon-cyanfont-mono-text-/text-alpine-neon-cyan font-mono text-/g' \
    -e 's/bg-alpine-neon-cyantextblac-k-/bg-alpine-neon-cyan text-black /g' \
    -e 's/bg-alpine-neon-cyantextblac-k-w-/bg-alpine-neon-cyan text-black w-/g' \
    -e 's/text-alpine-neoncyanm-b-/text-alpine-neon-cyan mb-/g' \
    -e 's/text-alpine-textsecondarym-b-/text-alpine-text-secondary mb-/g' \
    -e 's/text-alpine-textsecondarymax--/text-alpine-text-secondary max-/g' \
    -e 's/text-alpine-textprimar-y-/text-alpine-text-primary /g' \
    -e 's/text-alpine-textprimar-y-mb-/text-alpine-text-primary mb-/g' \
    -e 's/text-alpine-textprimar-y-font-/text-alpine-text-primary font-/g' \
    -e 's/text-alpine-textsecondar-y/text-alpine-text-secondary/g' \
    -e 's/text-alpine-textsecondar-yhover:/text-alpine-text-secondary hover:/g' \
    -e 's/text-alpine-textsecondar-y>/text-alpine-text-secondary>/g' \
    -e 's/text-alpine-neon-cyanfont-bold-/text-alpine-neon-cyan font-bold /g' \
    -e 's/text-alpine-neon-cyanfont-bold-text-/text-alpine-neon-cyan font-bold text-/g' \
    -e 's/text-alpine-semantic-errorfont-bold-/text-alpine-semantic-error font-bold /g' \
    -e 's/text-alpine-semantic-errorfont-bold-text-/text-alpine-semantic-error font-bold text-/g' \
    -e 's/text-alpine-text-secondarytext-sm-/text-alpine-text-secondary text-sm /g' \
    -e 's/text-alpine-text-secondarytext-sm-mb-/text-alpine-text-secondary text-sm mb-/g' \
    -e 's/text-alpine-text-secondarytext-sm-ma-/text-alpine-text-secondary text-sm ma-/g' \
    -e 's/text-alpine-text-secondarytext-sm-mt-/text-alpine-text-secondary text-sm mt-/g' \
    -e 's/border-yborder-/border-y border-/g' \
    -e 's/border-yborder-alpine-/border-y border-alpine-/g' \
    -e 's/alpine-verif-y/alpine-verify/g' \
    "$file"
  
  echo "  ✅ Fixed: $(basename $file)"
}

# Find and fix all TSX files
find "$COMPONENT_DIR" "$APP_DIR" -name "*.tsx" -type f ! -name "*.bak*" | while read file; do
  if grep -qE "(text-alpine-textprimar|text-alpine-textsecondar|text-alpine-neoncya|text-alpine-neonpin|bg-alpine-black-primaryp|border-alpine-blackborde|from-alpine-neon-cyanto)" "$file"; then
    fix_file "$file"
  fi
done

echo ""
echo "✅ Final class name fix complete!"

