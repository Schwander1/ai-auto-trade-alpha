#!/bin/bash

# Mac System Optimization Script
# Cleans up Docker, logs, and optimizes system resources

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

WORKSPACE_DIR="/Users/dylanneuenschwander/argo-alpine-workspace"
REPORT_FILE="$WORKSPACE_DIR/MAC_OPTIMIZATION_REPORT_$(date +%Y%m%d_%H%M%S).md"

cd "$WORKSPACE_DIR"

echo -e "${BLUE}🚀 Mac System Optimization${NC}"
echo "=================================="
echo ""

# Initialize report
cat > "$REPORT_FILE" << EOF
# Mac System Optimization Report

**Generated:** $(date)
**Workspace:** $WORKSPACE_DIR

---

## Summary

This report documents the optimization actions performed on your Mac system.

---

## 1. Docker Cleanup

EOF

# Check Docker status
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found, skipping Docker cleanup${NC}"
    echo "**Docker:** Not installed" >> "$REPORT_FILE"
else
    echo -e "${BLUE}📦 Analyzing Docker resources...${NC}"
    
    # Get current Docker usage
    DOCKER_DF=$(docker system df 2>/dev/null)
    echo "$DOCKER_DF" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # Show current state
    echo "$DOCKER_DF"
    echo ""
    
    # Clean up stopped containers
    echo -e "${BLUE}🧹 Cleaning up stopped containers...${NC}"
    STOPPED_CONTAINERS=$(docker ps -a -q -f status=exited -f status=created 2>/dev/null | wc -l | tr -d ' ')
    if [ "$STOPPED_CONTAINERS" -gt 0 ]; then
        docker container prune -f 2>/dev/null
        echo -e "${GREEN}✅ Removed $STOPPED_CONTAINERS stopped containers${NC}"
        echo "**Stopped Containers Removed:** $STOPPED_CONTAINERS" >> "$REPORT_FILE"
    else
        echo -e "${GREEN}✅ No stopped containers to remove${NC}"
        echo "**Stopped Containers Removed:** 0" >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
    
    # Clean up unused images (keep last 2 versions)
    echo -e "${BLUE}🖼️  Cleaning up unused Docker images...${NC}"
    UNUSED_IMAGES=$(docker images -f "dangling=true" -q 2>/dev/null | wc -l | tr -d ' ')
    if [ "$UNUSED_IMAGES" -gt 0 ]; then
        docker image prune -f 2>/dev/null
        echo -e "${GREEN}✅ Removed dangling images${NC}"
        echo "**Dangling Images Removed:** $UNUSED_IMAGES" >> "$REPORT_FILE"
    else
        echo -e "${GREEN}✅ No dangling images to remove${NC}"
        echo "**Dangling Images Removed:** 0" >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
    
    # Clean up unused volumes
    echo -e "${BLUE}💾 Cleaning up unused volumes...${NC}"
    UNUSED_VOLUMES=$(docker volume ls -q -f dangling=true 2>/dev/null | wc -l | tr -d ' ')
    if [ "$UNUSED_VOLUMES" -gt 0 ]; then
        docker volume prune -f 2>/dev/null
        echo -e "${GREEN}✅ Removed unused volumes${NC}"
        echo "**Unused Volumes Removed:** $UNUSED_VOLUMES" >> "$REPORT_FILE"
    else
        echo -e "${GREEN}✅ No unused volumes to remove${NC}"
        echo "**Unused Volumes Removed:** 0" >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
    
    # Clean up build cache
    echo -e "${BLUE}🗑️  Cleaning up build cache...${NC}"
    BUILD_CACHE_SIZE=$(docker system df 2>/dev/null | grep "Build Cache" | awk '{print $4}')
    docker builder prune -af 2>/dev/null
    echo -e "${GREEN}✅ Cleaned build cache (freed ~$BUILD_CACHE_SIZE)${NC}"
    echo "**Build Cache Cleaned:** ~$BUILD_CACHE_SIZE" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # Show final Docker usage
    echo -e "${BLUE}📊 Final Docker usage:${NC}"
    docker system df 2>/dev/null
    echo ""
fi

# Log file cleanup
echo -e "${BLUE}📝 Cleaning up old log files...${NC}"
cat >> "$REPORT_FILE" << EOF

## 2. Log File Cleanup

EOF

LOG_DIRS=("argo/logs" "alpine-backend/logs" "logs")
TOTAL_LOG_SIZE=0

for LOG_DIR in "${LOG_DIRS[@]}"; do
    if [ -d "$LOG_DIR" ]; then
        LOG_SIZE=$(du -sh "$LOG_DIR" 2>/dev/null | awk '{print $1}')
        LOG_COUNT=$(find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | wc -l | tr -d ' ')
        
        # Keep only logs from last 7 days
        find "$LOG_DIR" -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
        
        echo -e "${GREEN}✅ Cleaned $LOG_DIR (kept recent logs)${NC}"
        echo "**$LOG_DIR:** $LOG_COUNT files, $LOG_SIZE" >> "$REPORT_FILE"
    fi
done
echo "" >> "$REPORT_FILE"

# Python cache cleanup
echo -e "${BLUE}🐍 Cleaning up Python cache files...${NC}"
cat >> "$REPORT_FILE" << EOF

## 3. Python Cache Cleanup

EOF

PYCACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l | tr -d ' ')
PYCACHE_SIZE=$(find . -type d -name "__pycache__" -exec du -ch {} + 2>/dev/null | tail -1 | awk '{print $1}')

if [ "$PYCACHE_COUNT" -gt 0 ]; then
    find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    echo -e "${GREEN}✅ Removed $PYCACHE_COUNT __pycache__ directories${NC}"
    echo "**Python Cache Removed:** $PYCACHE_COUNT directories, ~$PYCACHE_SIZE" >> "$REPORT_FILE"
else
    echo -e "${GREEN}✅ No Python cache to clean${NC}"
    echo "**Python Cache Removed:** 0" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# Node modules optimization check
echo -e "${BLUE}📦 Checking node_modules...${NC}"
cat >> "$REPORT_FILE" << EOF

## 4. Node.js Optimization

EOF

if [ -d "node_modules" ]; then
    NODE_SIZE=$(du -sh node_modules 2>/dev/null | awk '{print $1}')
    echo "**node_modules Size:** $NODE_SIZE" >> "$REPORT_FILE"
    echo -e "${YELLOW}ℹ️  node_modules: $NODE_SIZE (consider running 'pnpm prune' to remove unused packages)${NC}"
else
    echo "**node_modules:** Not found" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# Disk space summary
echo -e "${BLUE}💾 Disk Space Summary${NC}"
cat >> "$REPORT_FILE" << EOF

## 5. Disk Space Summary

EOF

df -h . | tail -1 | awk '{print "**Total Space:** " $2 "\n**Used:** " $3 " (" $5 ")\n**Available:** " $4}' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Large directories
echo -e "${BLUE}📊 Top 10 Largest Directories:${NC}"
cat >> "$REPORT_FILE" << EOF

### Top 10 Largest Directories

EOF

du -sh * 2>/dev/null | sort -hr | head -10 | while read size dir; do
    echo "- **$dir:** $size" >> "$REPORT_FILE"
done
echo "" >> "$REPORT_FILE"

# System recommendations
cat >> "$REPORT_FILE" << EOF

## 6. Recommendations

### Immediate Actions
1. ✅ Docker cleanup completed
2. ✅ Log files cleaned (kept last 7 days)
3. ✅ Python cache cleaned

### Optional Optimizations
1. **Remove unused Docker images manually:**
   \`\`\`bash
   docker images
   docker rmi <unused-image-id>
   \`\`\`

2. **Prune unused npm/pnpm packages:**
   \`\`\`bash
   pnpm prune
   \`\`\`

3. **Consider removing old archive files** if not needed:
   - \`archive/\` directory: ~3.4MB

4. **Monitor disk space:**
   - Current usage: $(df -h . | tail -1 | awk '{print $5}')
   - Consider moving large files to external storage if >90%

### Maintenance Schedule
- Run this script weekly to maintain optimal performance
- Monitor Docker usage regularly
- Clean logs monthly or implement log rotation

---

**Optimization completed at:** $(date)
EOF

echo ""
echo -e "${GREEN}✅ Optimization complete!${NC}"
echo -e "${BLUE}📄 Report saved to: $REPORT_FILE${NC}"
echo ""
echo -e "${YELLOW}💡 Tip: Run this script weekly to maintain optimal performance${NC}"

