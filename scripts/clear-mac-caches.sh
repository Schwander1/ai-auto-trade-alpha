#!/bin/bash

# Mac Cache Clearing Script
# Safely clears various Mac system and application caches

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

WORKSPACE_DIR="/Users/dylanneuenschwander/argo-alpine-workspace"
REPORT_FILE="$WORKSPACE_DIR/MAC_CACHE_CLEAR_REPORT_$(date +%Y%m%d_%H%M%S).md"

# Parse command line arguments
AGGRESSIVE=false
SKIP_CONFIRM=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --aggressive)
            AGGRESSIVE=true
            shift
            ;;
        --yes)
            SKIP_CONFIRM=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--aggressive] [--yes]"
            exit 1
            ;;
    esac
done

cd "$WORKSPACE_DIR"

echo -e "${BLUE}🧹 Mac Cache Clearing Utility${NC}"
echo "=================================="
echo ""

# Initialize report
cat > "$REPORT_FILE" << EOF
# Mac Cache Clearing Report

**Generated:** $(date)
**User:** $(whoami)
**Workspace:** $WORKSPACE_DIR
**Mode:** $([ "$AGGRESSIVE" = true ] && echo "Aggressive" || echo "Standard")

---

## Summary

This report documents the cache clearing actions performed on your Mac system.

---

EOF

TOTAL_FREED=0

# Function to calculate directory size
get_size() {
    if [ -d "$1" ]; then
        local size=$(du -sk "$1" 2>/dev/null | awk '{print $1}' || echo "0")
        # Ensure we return a number, default to 0 if empty or non-numeric
        if [ -z "$size" ] || ! [[ "$size" =~ ^[0-9]+$ ]]; then
            echo "0"
        else
            echo "$size"
        fi
    else
        echo "0"
    fi
}

# Function to format size
format_size() {
    local size_kb=$1
    if [ "$size_kb" -gt 1048576 ]; then
        echo "$(echo "scale=2; $size_kb/1048576" | bc)GB"
    elif [ "$size_kb" -gt 1024 ]; then
        echo "$(echo "scale=2; $size_kb/1024" | bc)MB"
    else
        echo "${size_kb}KB"
    fi
}

# Function to clear cache directory
clear_cache_dir() {
    local dir=$1
    local name=$2
    local size_before=$(get_size "$dir")

    # Ensure size_before is a valid number
    if [ -z "$size_before" ] || ! [[ "$size_before" =~ ^[0-9]+$ ]]; then
        size_before=0
    fi

    if [ "$size_before" -gt 0 ]; then
        echo -e "${BLUE}🗑️  Clearing $name...${NC}"
        rm -rf "$dir"/* 2>/dev/null || true
        local size_after=$(get_size "$dir")
        local freed=$((size_before - size_after))
        TOTAL_FREED=$((TOTAL_FREED + freed))

        if [ "$freed" -gt 0 ]; then
            echo -e "${GREEN}✅ Freed $(format_size $freed) from $name${NC}"
            echo "**$name:** Freed $(format_size $freed)" >> "$REPORT_FILE"
        else
            echo -e "${YELLOW}ℹ️  $name was already empty${NC}"
            echo "**$name:** Already empty" >> "$REPORT_FILE"
        fi
    else
        echo -e "${YELLOW}ℹ️  $name not found or empty${NC}"
        echo "**$name:** Not found" >> "$REPORT_FILE"
    fi
}

# Confirmation prompt
if [ "$SKIP_CONFIRM" = false ]; then
    echo -e "${YELLOW}⚠️  This will clear various Mac caches.${NC}"
    if [ "$AGGRESSIVE" = true ]; then
        echo -e "${RED}⚠️  AGGRESSIVE MODE: Will also clear system caches and browser data${NC}"
    fi
    echo ""
    read -p "Continue? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Cancelled.${NC}"
        exit 0
    fi
    echo ""
fi

# 1. User Library Caches
echo -e "${CYAN}## 1. User Library Caches${NC}"
cat >> "$REPORT_FILE" << EOF

## 1. User Library Caches

EOF

USER_CACHE_DIR="$HOME/Library/Caches"
if [ -d "$USER_CACHE_DIR" ]; then
    echo -e "${BLUE}📂 Analyzing user caches...${NC}"

    # Clear common application caches (safe)
    CACHE_DIRS=(
        "$HOME/Library/Caches/com.apple.Safari"
        "$HOME/Library/Caches/com.google.Chrome"
        "$HOME/Library/Caches/com.mozilla.firefox"
        "$HOME/Library/Caches/com.microsoft.VSCode"
        "$HOME/Library/Caches/com.tinyspeck.slackmacgap"
        "$HOME/Library/Caches/com.spotify.client"
        "$HOME/Library/Caches/com.docker.docker"
        "$HOME/Library/Caches/Homebrew"
        "$HOME/Library/Caches/pip"
        "$HOME/Library/Caches/pnpm"
        "$HOME/Library/Caches/npm"
        "$HOME/Library/Caches/yarn"
    )

    for cache_dir in "${CACHE_DIRS[@]}"; do
        if [ -d "$cache_dir" ]; then
            app_name=$(basename "$cache_dir")
            clear_cache_dir "$cache_dir" "$app_name"
        fi
    done

    # Aggressive mode: clear all user caches
    if [ "$AGGRESSIVE" = true ]; then
        echo -e "${BLUE}🗑️  Clearing all user caches (aggressive mode)...${NC}"
        size_before=$(get_size "$USER_CACHE_DIR")
        find "$USER_CACHE_DIR" -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} + 2>/dev/null || true
        size_after=$(get_size "$USER_CACHE_DIR")
        freed=$((size_before - size_after))
        TOTAL_FREED=$((TOTAL_FREED + freed))
        echo -e "${GREEN}✅ Freed $(format_size $freed) from all user caches${NC}"
        echo "**All User Caches:** Freed $(format_size $freed)" >> "$REPORT_FILE"
    fi
else
    echo -e "${YELLOW}ℹ️  User cache directory not found${NC}"
fi
echo "" >> "$REPORT_FILE"

# 2. Development Tool Caches
echo -e "${CYAN}## 2. Development Tool Caches${NC}"
cat >> "$REPORT_FILE" << EOF

## 2. Development Tool Caches

EOF

# npm cache
if command -v npm &> /dev/null; then
    echo -e "${BLUE}📦 Clearing npm cache...${NC}"
    npm cache clean --force 2>/dev/null || true
    echo -e "${GREEN}✅ npm cache cleared${NC}"
    echo "**npm cache:** Cleared" >> "$REPORT_FILE"
fi

# pnpm cache
if command -v pnpm &> /dev/null; then
    echo -e "${BLUE}📦 Clearing pnpm cache...${NC}"
    pnpm store prune 2>/dev/null || true
    echo -e "${GREEN}✅ pnpm cache cleared${NC}"
    echo "**pnpm cache:** Cleared" >> "$REPORT_FILE"
fi

# yarn cache
if command -v yarn &> /dev/null; then
    echo -e "${BLUE}📦 Clearing yarn cache...${NC}"
    yarn cache clean 2>/dev/null || true
    echo -e "${GREEN}✅ yarn cache cleared${NC}"
    echo "**yarn cache:** Cleared" >> "$REPORT_FILE"
fi

# pip cache
if command -v pip &> /dev/null; then
    echo -e "${BLUE}🐍 Clearing pip cache...${NC}"
    pip cache purge 2>/dev/null || true
    echo -e "${GREEN}✅ pip cache cleared${NC}"
    echo "**pip cache:** Cleared" >> "$REPORT_FILE"
fi

# Homebrew cache
if command -v brew &> /dev/null; then
    echo -e "${BLUE}🍺 Clearing Homebrew cache...${NC}"
    size_before=$(get_size "$(brew --cache)")
    brew cleanup --prune=all 2>/dev/null || true
    size_after=$(get_size "$(brew --cache)")
    freed=$((size_before - size_after))
    TOTAL_FREED=$((TOTAL_FREED + freed))
    echo -e "${GREEN}✅ Freed $(format_size $freed) from Homebrew${NC}"
    echo "**Homebrew cache:** Freed $(format_size $freed)" >> "$REPORT_FILE"
fi

# Docker buildx cache (if exists)
if command -v docker &> /dev/null; then
    echo -e "${BLUE}🐳 Clearing Docker buildx cache...${NC}"
    docker buildx prune -af 2>/dev/null || true
    echo -e "${GREEN}✅ Docker buildx cache cleared${NC}"
    echo "**Docker buildx cache:** Cleared" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"

# 3. Xcode Derived Data (if Xcode is installed)
echo -e "${CYAN}## 3. Xcode Derived Data${NC}"
cat >> "$REPORT_FILE" << EOF

## 3. Xcode Derived Data

EOF

XCODE_DERIVED_DATA="$HOME/Library/Developer/Xcode/DerivedData"
if [ -d "$XCODE_DERIVED_DATA" ]; then
    size_before=$(get_size "$XCODE_DERIVED_DATA")
    echo -e "${BLUE}🔨 Clearing Xcode Derived Data...${NC}"
    rm -rf "$XCODE_DERIVED_DATA"/* 2>/dev/null || true
    size_after=$(get_size "$XCODE_DERIVED_DATA")
    freed=$((size_before - size_after))
    TOTAL_FREED=$((TOTAL_FREED + freed))
    echo -e "${GREEN}✅ Freed $(format_size $freed) from Xcode Derived Data${NC}"
    echo "**Xcode Derived Data:** Freed $(format_size $freed)" >> "$REPORT_FILE"
else
    echo -e "${YELLOW}ℹ️  Xcode Derived Data not found${NC}"
    echo "**Xcode Derived Data:** Not found" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 4. Project-specific caches
echo -e "${CYAN}## 4. Project-Specific Caches${NC}"
cat >> "$REPORT_FILE" << EOF

## 4. Project-Specific Caches

EOF

# Next.js cache
if [ -d "alpine-frontend/.next/cache" ]; then
    size_before=$(get_size "alpine-frontend/.next/cache")
    echo -e "${BLUE}⚡ Clearing Next.js cache...${NC}"
    rm -rf alpine-frontend/.next/cache/* 2>/dev/null || true
    size_after=$(get_size "alpine-frontend/.next/cache")
    freed=$((size_before - size_after))
    TOTAL_FREED=$((TOTAL_FREED + freed))
    echo -e "${GREEN}✅ Freed $(format_size $freed) from Next.js cache${NC}"
    echo "**Next.js cache:** Freed $(format_size $freed)" >> "$REPORT_FILE"
fi

# Turbo cache
if [ -d ".turbo" ]; then
    size_before=$(get_size ".turbo")
    echo -e "${BLUE}⚡ Clearing Turbo cache...${NC}"
    rm -rf .turbo/* 2>/dev/null || true
    size_after=$(get_size ".turbo")
    freed=$((size_before - size_after))
    TOTAL_FREED=$((TOTAL_FREED + freed))
    echo -e "${GREEN}✅ Freed $(format_size $freed) from Turbo cache${NC}"
    echo "**Turbo cache:** Freed $(format_size $freed)" >> "$REPORT_FILE"
fi

# Jest cache
if [ -d ".jest-cache" ]; then
    size_before=$(get_size ".jest-cache")
    echo -e "${BLUE}🧪 Clearing Jest cache...${NC}"
    rm -rf .jest-cache/* 2>/dev/null || true
    size_after=$(get_size ".jest-cache")
    freed=$((size_before - size_after))
    TOTAL_FREED=$((TOTAL_FREED + freed))
    echo -e "${GREEN}✅ Freed $(format_size $freed) from Jest cache${NC}"
    echo "**Jest cache:** Freed $(format_size $freed)" >> "$REPORT_FILE"
fi

# Python __pycache__
echo -e "${BLUE}🐍 Clearing Python __pycache__...${NC}"
PYCACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYCACHE_COUNT" -gt 0 ]; then
    find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    echo -e "${GREEN}✅ Removed $PYCACHE_COUNT __pycache__ directories${NC}"
    echo "**Python __pycache__:** Removed $PYCACHE_COUNT directories" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"

# 5. System caches (aggressive mode only)
if [ "$AGGRESSIVE" = true ]; then
    echo -e "${CYAN}## 5. System Caches (Aggressive Mode)${NC}"
    cat >> "$REPORT_FILE" << EOF

## 5. System Caches (Aggressive Mode)

EOF

    SYSTEM_CACHE_DIRS=(
        "/Library/Caches"
        "/private/var/folders"
    )

    for sys_cache in "${SYSTEM_CACHE_DIRS[@]}"; do
        if [ -d "$sys_cache" ] && [ -w "$sys_cache" ]; then
            echo -e "${RED}⚠️  Clearing system cache: $sys_cache${NC}"
            # Only clear user-writable parts
            find "$sys_cache" -user "$(whoami)" -type f -delete 2>/dev/null || true
            echo -e "${GREEN}✅ Cleared user-owned files in $sys_cache${NC}"
            echo "**$sys_cache:** Cleared user-owned files" >> "$REPORT_FILE"
        fi
    done
    echo "" >> "$REPORT_FILE"
fi

# 6. Browser caches (aggressive mode)
if [ "$AGGRESSIVE" = true ]; then
    echo -e "${CYAN}## 6. Browser Data (Aggressive Mode)${NC}"
    cat >> "$REPORT_FILE" << EOF

## 6. Browser Data (Aggressive Mode)

EOF

    # Safari
    if [ -d "$HOME/Library/Safari" ]; then
        echo -e "${BLUE}🌐 Clearing Safari data...${NC}"
        rm -rf "$HOME/Library/Safari/LocalStorage"/* 2>/dev/null || true
        rm -rf "$HOME/Library/Safari/Databases"/* 2>/dev/null || true
        echo -e "${GREEN}✅ Safari data cleared${NC}"
        echo "**Safari:** Data cleared" >> "$REPORT_FILE"
    fi

    # Chrome
    if [ -d "$HOME/Library/Application Support/Google/Chrome" ]; then
        echo -e "${BLUE}🌐 Clearing Chrome data...${NC}"
        rm -rf "$HOME/Library/Application Support/Google/Chrome/Default/Cache"/* 2>/dev/null || true
        rm -rf "$HOME/Library/Application Support/Google/Chrome/Default/Code Cache"/* 2>/dev/null || true
        echo -e "${GREEN}✅ Chrome data cleared${NC}"
        echo "**Chrome:** Data cleared" >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
fi

# Summary
cat >> "$REPORT_FILE" << EOF

## Summary

**Total Space Freed:** $(format_size $TOTAL_FREED)
**Mode:** $([ "$AGGRESSIVE" = true ] && echo "Aggressive" || echo "Standard")
**Completed:** $(date)

---

### Notes

- Standard mode clears safe, user-level caches
- Aggressive mode also clears system caches and browser data
- Some caches will be regenerated on next use
- Browser data clearing may require re-login to websites

EOF

echo ""
echo -e "${GREEN}✅ Cache clearing complete!${NC}"
echo -e "${BLUE}📊 Total space freed: $(format_size $TOTAL_FREED)${NC}"
echo -e "${BLUE}📄 Report saved to: $REPORT_FILE${NC}"
echo ""
echo -e "${YELLOW}💡 Tip: Run with --aggressive flag for deeper cleaning${NC}"
echo -e "${YELLOW}💡 Tip: Use --yes flag to skip confirmation prompt${NC}"
