#!/bin/bash

# Comprehensive fix for all remaining broken class names

cd "$(dirname "$0")/.." || exit 1

echo "🔧 Fixing all remaining broken class names..."

# Fix alpine-neonpurpl-e → alpine-neon-purple
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/alpine-neonpurpl-e/alpine-neon-purple/g' {} +

# Fix bg-alpine-blackprimaryp-y-24 → bg-alpine-black-primary py-24
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-blackprimaryp-y-24/bg-alpine-black-primary py-24/g' {} +

# Fix border-alpine-blackborder → border-alpine-black-border (with space after)
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-blackborder\([a-z]\)/border-alpine-black-border \1/g' {} +

# Fix bg-alpine-black-secondaryborder → bg-alpine-black-secondary border
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-black-secondaryborder/bg-alpine-black-secondary border/g' {} +

# Fix text-alpine-textsecondarym-t- → text-alpine-text-secondary mt-
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-textsecondarym-t-/text-alpine-text-secondary mt-/g' {} +

# Fix text-alpine-textprimarym-t- → text-alpine-text-primary mt-
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-textprimarym-t-/text-alpine-text-primary mt-/g' {} +

# Fix text-alpine-semanticerrorm-r- → text-alpine-semantic-error mr-
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-semanticerrorm-r-/text-alpine-semantic-error mr-/g' {} +

# Fix text-alpine-neoncyanm-r- → text-alpine-neon-cyan mr-
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-neoncyanm-r-/text-alpine-neon-cyan mr-/g' {} +

# Fix text-alpine-orangem-r- → text-alpine-orange mr-
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-orangem-r-/text-alpine-orange mr-/g' {} +

# Fix border-alpine-blackborderhove-r → border-alpine-black-border hover:
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-blackborderhove-r:/border-alpine-black-border hover:/g' {} +

# Fix bg-alpine-blackborderhove-r → bg-alpine-black-border hover:
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-blackborderhove-r:/bg-alpine-black-border hover:/g' {} +

# Fix hover:bg-alpine-blackborde-r80 → hover:bg-alpine-black-border/80
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/hover:bg-alpine-blackborde-r80/hover:bg-alpine-black-border\/80/g' {} +

# Fix text-alpine-text-primaryrounded-lg → text-alpine-text-primary rounded-lg
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-text-primaryrounded-lg/text-alpine-text-primary rounded-lg/g' {} +

# Fix transition-colorsflex → transition-colors flex
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/transition-colorsflex/transition-colors flex/g' {} +

# Fix border-alpine-blackborderfle-xitems-centerjustify-between → border-alpine-black-border flex items-center justify-between
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-blackborderfle-xitems-centerjustify-between/border-alpine-black-border flex items-center justify-between/g' {} +

# Fix border-alpine-neoncya-n/ → border-alpine-neon-cyan/
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-neoncya-n\//border-alpine-neon-cyan\//g' {} +

# Fix text-alpine-neoncya-n/ → text-alpine-neon-cyan/
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-neoncya-n\//text-alpine-neon-cyan\//g' {} +

# Fix via-alpine-neonpin-k/ → via-alpine-neon-pink/
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/via-alpine-neonpin-k\//via-alpine-neon-pink\//g' {} +

# Fix from-alpine-neoncya-n/ → from-alpine-neon-cyan/
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/from-alpine-neoncya-n\//from-alpine-neon-cyan\//g' {} +

# Fix bg-alpine-black-secondaryroundedlg--p-6 → bg-alpine-black-secondary rounded-lg p-6
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-black-secondaryroundedlg--p-6/bg-alpine-black-secondary rounded-lg p-6/g' {} +

# Fix border-alpine-blackborderm-b-4 → border-alpine-black-border mb-4
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-blackborderm-b-4/border-alpine-black-border mb-4/g' {} +

# Fix border-alpine-blackborderm-t-8 → border-alpine-black-border mt-8
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-blackborderm-t-8/border-alpine-black-border mt-8/g' {} +

# Fix border-alpine-blackborderrounde-d-2xl → border-alpine-black-border rounded-2xl
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-blackborderrounde-d-2xl/border-alpine-black-border rounded-2xl/g' {} +

# Fix text-alpine-blackprimaryp-x-4 → text-alpine-black-primary px-4
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-blackprimaryp-x-4/text-alpine-black-primary px-4/g' {} +

# Fix font-semiboldp-y-3 → font-semibold py-3
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/font-semiboldp-y-3/font-semibold py-3/g' {} +

# Fix text-alpine-orangeflexshri-nk-0 → text-alpine-orange flex-shrink-0
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-orangeflexshri-nk-0/text-alpine-orange flex-shrink-0/g' {} +

# Fix border-alpine-blackborderbg-alpine-blacksecondaryp-x-4 → border-alpine-black-border bg-alpine-black-secondary px-4
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-blackborderbg-alpine-blacksecondaryp-x-4/border-alpine-black-border bg-alpine-black-secondary px-4/g' {} +

# Fix text-alpine-textprimaryplaceholde-r:text-alpine-textsecondaryfocu-s:outline-none → text-alpine-text-primary placeholder:text-alpine-text-secondary focus:outline-none
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-textprimaryplaceholde-r:text-alpine-textsecondaryfocu-s:outline-none/text-alpine-text-primary placeholder:text-alpine-text-secondary focus:outline-none/g' {} +

# Fix focus:ring-alpine-neoncyanfocu-s:ring-offset-2 → focus:ring-alpine-neon-cyan focus:ring-offset-2
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/focus:ring-alpine-neoncyanfocu-s:ring-offset-2/focus:ring-alpine-neon-cyan focus:ring-offset-2/g' {} +

# Fix focus:ring-offset-alpine-blackprimarydisable-d:cursor-not-allowed → focus:ring-offset-alpine-black-primary disabled:cursor-not-allowed
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/focus:ring-offset-alpine-blackprimarydisable-d:cursor-not-allowed/focus:ring-offset-alpine-black-primary disabled:cursor-not-allowed/g' {} +

# Fix disabled:opacity-5alpine-blackprimar-y → disabled:opacity-50
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/disabled:opacity-5alpine-blackprimar-y/disabled:opacity-50/g' {} +

# Fix border-alpine-blackborderhov-er:border-alpine-neoncy-an/50 → border-alpine-black-border hover:border-alpine-neon-cyan/50
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-blackborderhov-er:border-alpine-neoncy-an\/50/border-alpine-black-border hover:border-alpine-neon-cyan\/50/g' {} +

# Fix text-alpine-neon-cyanhover:text-alpine-neonpi-nktransition-colors → text-alpine-neon-cyan hover:text-alpine-neon-pink transition-colors
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-neon-cyanhover:text-alpine-neonpi-nktransition-colors/text-alpine-neon-cyan hover:text-alpine-neon-pink transition-colors/g' {} +

# Fix bg-alpine-neon-cyanrounded-fullanimate-pulse → bg-alpine-neon-cyan rounded-full animate-pulse
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-neon-cyanrounded-fullanimate-pulse/bg-alpine-neon-cyan rounded-full animate-pulse/g' {} +

# Fix border-alpine-blackborderhove-r:bg-alpine-blacksecondar-y50 → border-alpine-black-border hover:bg-alpine-black-secondary/50
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-blackborderhove-r:bg-alpine-blacksecondar-y50/border-alpine-black-border hover:bg-alpine-black-secondary\/50/g' {} +

# Fix border-alpine-neonpurpl-e/30 → border-alpine-neon-purple/30
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-neonpurpl-e\//border-alpine-neon-purple\//g' {} +

# Fix text-alpine-neon-purpleborder-alpine-neonpurpl-e/30 → text-alpine-neon-purple border-alpine-neonpurpl-e/30
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-neon-purpleborder-alpine-neonpurpl-e\//text-alpine-neon-purple border-alpine-neon-purple\//g' {} +

# Fix border-alpine-neonpurpl-e/50 → border-alpine-neon-purple/50
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-neonpurpl-e\/50/border-alpine-neon-purple\/50/g' {} +

# Fix border-alpineoran-ge/30 → border-alpine-orange/30
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpineoran-ge\//border-alpine-orange\//g' {} +

# Fix bg-alpine-orang-e/20 → bg-alpine-orange/20
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-orang-e\//bg-alpine-orange\//g' {} +

# Fix text-alpine-orangeborder-alpineoran-ge/30 → text-alpine-orange border-alpine-orange/30
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-orangeborder-alpineoran-ge\//text-alpine-orange border-alpine-orange\//g' {} +

# Fix bg-alpine-neonpurpl-e/20 → bg-alpine-neon-purple/20
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-neonpurpl-e\//bg-alpine-neon-purple\//g' {} +

# Fix text-alpine-semanticerrorm-b-4 → text-alpine-semantic-error mb-4
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-semanticerrorm-b-4/text-alpine-semantic-error mb-4/g' {} +

# Fix bg-alpine-semanticsuccesshov-er:bg-alpine-greenda-rktext-alpine-blackprimar-yfont-boldrounded-lg → bg-alpine-semantic-success hover:bg-alpine-green-dark text-alpine-black-primary font-bold rounded-lg
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-semanticsuccesshov-er:bg-alpine-greenda-rktext-alpine-blackprimar-yfont-boldrounded-lg/bg-alpine-semantic-success hover:bg-alpine-green-dark text-alpine-black-primary font-bold rounded-lg/g' {} +

# Fix text-alpine-text-primary font-semiboldmb-2 → text-alpine-text-primary font-semibold mb-2
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-text-primary font-semiboldmb-2/text-alpine-text-primary font-semibold mb-2/g' {} +

# Fix bg-alpine-black-primaryborder → bg-alpine-black-primary border
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-black-primaryborder/bg-alpine-black-primary border/g' {} +

# Fix text-alpine-neoncy-an/10 → text-alpine-neon-cyan/10
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/text-alpine-neoncy-an\//text-alpine-neon-cyan\//g' {} +

# Fix bg-alpine-neoncy-an/10 → bg-alpine-neon-cyan/10
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-neoncy-an\//bg-alpine-neon-cyan\//g' {} +

# Fix border-alpine-neoncy-an/30 → border-alpine-neon-cyan/30
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-neoncy-an\//border-alpine-neon-cyan\//g' {} +

# Fix hover:border-alpine-neoncy-an/50 → hover:border-alpine-neon-cyan/50
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/hover:border-alpine-neoncy-an\//hover:border-alpine-neon-cyan\//g' {} +

# Fix border-alpine-blackborderhove-r:border-alpine-neoncya-n/50 → border-alpine-black-border hover:border-alpine-neon-cyan/50
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/border-alpine-blackborderhove-r:border-alpine-neoncya-n\/50/border-alpine-black-border hover:border-alpine-neon-cyan\/50/g' {} +

# Fix bg-alpine-black-secondaryborder border-alpine-blackborderhove-r:border-alpine-neoncya-n/50 → bg-alpine-black-secondary border border-alpine-black-border hover:border-alpine-neon-cyan/50
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-black-secondaryborder border-alpine-blackborderhove-r:border-alpine-neoncya-n\/50/bg-alpine-black-secondary border border-alpine-black-border hover:border-alpine-neon-cyan\/50/g' {} +

# Fix bg-alpine-black-secondaryborder border-alpine-blackborderhove-r:border-alpine-neoncya-n/50 transition-colors → bg-alpine-black-secondary border border-alpine-black-border hover:border-alpine-neon-cyan/50 transition-colors
find alpine-frontend -type f \( -name "*.tsx" -o -name "*.ts" \) -exec sed -i '' 's/bg-alpine-black-secondaryborder border-alpine-blackborderhove-r:border-alpine-neoncya-n\/50 transition-colors/bg-alpine-black-secondary border border-alpine-black-border hover:border-alpine-neon-cyan\/50 transition-colors/g' {} +

echo "✅ All class name fixes applied!"

