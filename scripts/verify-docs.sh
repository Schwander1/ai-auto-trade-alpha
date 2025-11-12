#!/bin/bash
# Verify documentation standards are applied correctly

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Verifying Documentation Standards"
echo "===================================="
echo ""

ERRORS=0
WARNINGS=0

check_file() {
    local file=$1
    local is_first=$2
    local errors=0
    
    # Check frontmatter in first file
    if [ "$is_first" = "true" ]; then
        if ! grep -q "^---$" "$file" || ! grep -q "^title:" "$file"; then
            echo -e "${RED}❌ Missing frontmatter: $file${NC}"
            ((errors++))
        fi
    fi
    
    # Check versioning in filename
    if [[ ! "$file" =~ v[0-9]+\.[0-9]+_[0-9]+_ ]]; then
        echo -e "${RED}❌ Invalid versioning: $file${NC}"
        ((errors++))
    fi
    
    # Check for code blocks without language
    if grep -q '^```$' "$file"; then
        echo -e "${YELLOW}⚠️  Code block without language: $file${NC}"
        ((WARNINGS++))
    fi
    
    # Check heading hierarchy
    if [ "$is_first" != "true" ]; then
        if grep -q "^# [^#]" "$file"; then
            echo -e "${YELLOW}⚠️  H1 heading in non-first file: $file${NC}"
            ((WARNINGS++))
        fi
    fi
    
    return $errors
}

# Check InvestorDocs
echo "📚 Checking InvestorDocs..."
for file in docs/InvestorDocs/v1.0_*.md; do
    if [ -f "$file" ]; then
        is_first="false"
        if [[ "$file" == *"01_"* ]]; then
            is_first="true"
        fi
        check_file "$file" "$is_first" || ((ERRORS++))
    fi
done

# Check TechnicalDocs
echo ""
echo "📚 Checking TechnicalDocs..."
for file in docs/TechnicalDocs/v1.0_*.md; do
    if [ -f "$file" ]; then
        is_first="false"
        if [[ "$file" == *"01_"* ]]; then
            is_first="true"
        fi
        check_file "$file" "$is_first" || ((ERRORS++))
    fi
done

# Check SystemDocs
echo ""
echo "📚 Checking SystemDocs..."
for file in docs/SystemDocs/v1.0_*.md; do
    if [ -f "$file" ]; then
        is_first="false"
        if [[ "$file" == *"01_"* ]]; then
            is_first="true"
        fi
        check_file "$file" "$is_first" || ((ERRORS++))
    fi
done

echo ""
echo "===================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS warnings found${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS errors, $WARNINGS warnings found${NC}"
    exit 1
fi

