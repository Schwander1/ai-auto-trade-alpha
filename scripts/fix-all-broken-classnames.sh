#!/bin/bash
# Fix ALL broken class names from sed replacements

echo "🔧 Fixing ALL broken class names..."

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
  
  # Fix broken class names - remove spaces in middle of class names
  sed -i '' \
    -e 's/\([a-z-]*\)-alpine-\([a-z-]*\) \([a-z]\)/\1-alpine-\2\3/g' \
    -e 's/\([a-z-]*\)-alpine-\([a-z-]*\) \([0-9]\)/\1-alpine-\2\/\3/g' \
    -e 's/\([a-z-]*\)-alpine-\([a-z-]*\)>/\1-alpine-\2">/g' \
    -e 's/\([a-z-]*\)-alpine-\([a-z-]*\) \([a-z-]*\)/\1-alpine-\2-\3/g' \
    -e 's/ r /r/g' \
    -e 's/ y /y/g' \
    -e 's/ n /n/g' \
    -e 's/ x /x/g' \
    -e 's/ l /l/g' \
    -e 's/ e /e/g' \
    -e 's/ s>/s">/g' \
    -e 's/ k>/k">/g' \
    -e 's/ g>/g">/g' \
    "$file"
  
  echo "  ✅ Fixed: $(basename $file)"
}

# Find and fix all TSX files
find "$COMPONENT_DIR" "$APP_DIR" -name "*.tsx" -type f ! -name "*.bak*" | while read file; do
  if grep -qE "([a-z-]*)-alpine-([a-z-]*) [a-z0-9>]| r | y | n | x | l | e | s>| k>| g>" "$file"; then
    fix_file "$file"
  fi
done

echo ""
echo "✅ All broken class names fixed!"

