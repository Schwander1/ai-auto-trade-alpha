#!/bin/bash

# Final comprehensive fix for all remaining broken class names

cd "$(dirname "$0")/.." || exit 1

echo "🔧 Fixing final remaining broken class names..."

# Fix bg-alpine-blackprimaryborde-rborder-alpine-black-border → bg-alpine-black-primary border border-alpine-black-border
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-blackprimaryborde-rborder-alpine-black-border/bg-alpine-black-primary border border-alpine-black-border/g' {} +

# Fix focus:border-alpine-neoncy-an → focus:border-alpine-neon-cyan
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/focus:border-alpine-neoncy-an/focus:border-alpine-neon-cyan/g' {} +

# Fix text-alpine-textsecondaryhove-r:text-alpine-neon-cyantransitioncolo-rs → text-alpine-text-secondary hover:text-alpine-neon-cyan transition-colors
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-textsecondaryhove-r:text-alpine-neon-cyantransitioncolo-rs/text-alpine-text-secondary hover:text-alpine-neon-cyan transition-colors/g' {} +

# Fix text-alpine-textsecondaryhove-r:text-alpine-neon-cyantransition-colors-text-sm → text-alpine-text-secondary hover:text-alpine-neon-cyan transition-colors text-sm
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-textsecondaryhove-r:text-alpine-neon-cyantransition-colors-text-sm/text-alpine-text-secondary hover:text-alpine-neon-cyan transition-colors text-sm/g' {} +

# Fix text-alpine-textsecondaryhove-r:text-alpine-semantic-successtransition-colors-texts-m → text-alpine-text-secondary hover:text-alpine-semantic-success transition-colors text-sm
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-textsecondaryhove-r:text-alpine-semantic-successtransition-colors-texts-m/text-alpine-text-secondary hover:text-alpine-semantic-success transition-colors text-sm/g' {} +

# Fix bg-alpine-blackprimaryborde-r-bborder-alpine-blackbord-er → bg-alpine-black-primary border border-alpine-black-border
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-blackprimaryborde-r-bborder-alpine-blackbord-er/bg-alpine-black-primary border border-alpine-black-border/g' {} +

# Fix hove-r:bg-alpine-blacksecondar-y50 → hover:bg-alpine-black-secondary/50
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/hove-r:bg-alpine-blacksecondar-y50/hover:bg-alpine-black-secondary\/50/g' {} +

# Fix bg-alpine-black-secondarytext-alpine-textsecondaryhove-r:text-alpine-text-primary → bg-alpine-black-secondary text-alpine-text-secondary hover:text-alpine-text-primary
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-black-secondarytext-alpine-textsecondaryhove-r:text-alpine-text-primary/bg-alpine-black-secondary text-alpine-text-secondary hover:text-alpine-text-primary/g' {} +

# Fix text-alpine-textsecondaryhove-r:text-alpine-text-primarytransitioncolor-s → text-alpine-text-secondary hover:text-alpine-text-primary transition-colors
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-textsecondaryhove-r:text-alpine-text-primarytransitioncolor-s/text-alpine-text-secondary hover:text-alpine-text-primary transition-colors/g' {} +

# Fix text-alpine-textsecondaryhove-r:text-alpine-text-primary hover:bg-alpine-black-primary → text-alpine-text-secondary hover:text-alpine-text-primary hover:bg-alpine-black-primary
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-textsecondaryhove-r:text-alpine-text-primary hover:bg-alpine-black-primary/text-alpine-text-secondary hover:text-alpine-text-primary hover:bg-alpine-black-primary/g' {} +

# Fix text-alpine-textsecondaryuppercas-e → text-alpine-text-secondary uppercase
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-textsecondaryuppercas-e/text-alpine-text-secondary uppercase/g' {} +

# Fix text-alpine-textsecondarycapitaliz-e → text-alpine-text-secondary capitalize
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-textsecondarycapitaliz-e/text-alpine-text-secondary capitalize/g' {} +

# Fix hover:bg-alpine-blacksecondar-y/50 → hover:bg-alpine-black-secondary/50
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/hover:bg-alpine-blacksecondar-y\/50/hover:bg-alpine-black-secondary\/50/g' {} +

# Fix bg-alpine-blacksecondar-y${ → bg-alpine-black-secondary ${
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-blacksecondar-y\${/bg-alpine-black-secondary ${/g' {} +

# Fix bg-alpine-black-secondarytext-alpine-text-primary hover:bg-alpine-blacksecondar-y/80 → bg-alpine-black-secondary text-alpine-text-primary hover:bg-alpine-black-secondary/80
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-black-secondarytext-alpine-text-primary hover:bg-alpine-blacksecondar-y\/80/bg-alpine-black-secondary text-alpine-text-primary hover:bg-alpine-black-secondary\/80/g' {} +

# Fix inline-flex h-1alpine-blackprimar-yitems-centerjustify-centerrounded-lg → inline-flex h-10 items-center justify-center rounded-lg
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/inline-flex h-1alpine-blackprimar-yitems-centerjustify-centerrounded-lg/inline-flex h-10 items-center justify-center rounded-lg/g' {} +

# Fix bg-alpine-blacksecondar-yrounded-lg → bg-alpine-black-secondary rounded-lg
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-blacksecondar-yrounded-lg/bg-alpine-black-secondary rounded-lg/g' {} +

# Fix bg-alpine-blacksecondar-yborder border-alpine-blackborde-rrounded-lg → bg-alpine-black-secondary border border-alpine-black-border rounded-lg
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-blacksecondar-yborder border-alpine-blackborde-rrounded-lg/bg-alpine-black-secondary border border-alpine-black-border rounded-lg/g' {} +

# Fix bg-alpine-blacksecondar-yborder border-alpine-neon-cyan/20 → bg-alpine-black-secondary border border-alpine-neon-cyan/20
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-blacksecondar-yborder border-alpine-neon-cyan\/20/bg-alpine-black-secondary border border-alpine-neon-cyan\/20/g' {} +

# Fix placeholder-alpine-textsecondar-yfocus:outline-none → placeholder:text-alpine-text-secondary focus:outline-none
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/placeholder-alpine-textsecondar-yfocus:outline-none/placeholder:text-alpine-text-secondary focus:outline-none/g' {} +

# Fix bg-alpine-blacksecondar-yhover:bg-alpine-blackseconda-ry/80 → bg-alpine-black-secondary hover:bg-alpine-black-secondary/80
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-blacksecondar-yhover:bg-alpine-blackseconda-ry\/80/bg-alpine-black-secondary hover:bg-alpine-black-secondary\/80/g' {} +

# Fix bg-alpine-blacksecondar-yborder border-alpine-black-border rounded-xlp-8 → bg-alpine-black-secondary border border-alpine-black-border rounded-xl p-8
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-blacksecondar-yborder border-alpine-black-border rounded-xlp-8/bg-alpine-black-secondary border border-alpine-black-border rounded-xl p-8/g' {} +

# Fix border-alpine-semanticerr-or30 → border-alpine-semantic-error/30
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-semanticerr-or30/border-alpine-semantic-error\/30/g' {} +

# Fix text-alpine-semanticerrorfle-xitems-centergap-2 → text-alpine-semantic-error flex items-center gap-2
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-semanticerrorfle-xitems-centergap-2/text-alpine-semantic-error flex items-center gap-2/g' {} +

# Fix text-alpine-neon-cyanflex items-centergap-2 → text-alpine-neon-cyan flex items-center gap-2
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-neon-cyanflex items-centergap-2/text-alpine-neon-cyan flex items-center gap-2/g' {} +

# Fix from-alpine-neoncya-nto-alpine-neonpi-nkhover:from-alpine-neonpi-nkhover:to-alpine-neoncya-ntext-whitefont-bold → from-alpine-neon-cyan to-alpine-neon-pink hover:from-alpine-neon-pink hover:to-alpine-neon-cyan text-white font-bold
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/from-alpine-neoncya-nto-alpine-neonpi-nkhover:from-alpine-neonpi-nkhover:to-alpine-neoncya-ntext-whitefont-bold/from-alpine-neon-cyan to-alpine-neon-pink hover:from-alpine-neon-pink hover:to-alpine-neon-cyan text-white font-bold/g' {} +

# Fix bg-alpine-blacksecondary-p-1 → bg-alpine-black-secondary p-1
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-blacksecondary-p-1/bg-alpine-black-secondary p-1/g' {} +

# Fix text-alpine-text-secondaryborder-border-alpine-black-border → text-alpine-text-secondary border border-alpine-black-border
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-text-secondaryborder-border-alpine-black-border/text-alpine-text-secondary border border-alpine-black-border/g' {} +

echo "✅ All final class name fixes applied!"

