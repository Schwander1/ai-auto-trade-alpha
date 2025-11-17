#!/bin/bash
# Clean up backup files created during brand system updates

echo "🧹 Cleaning up backup files..."

COMPONENT_DIR="../alpine-frontend/components"

# Remove all backup files
find "$COMPONENT_DIR" -name "*.bak*" -type f -delete

echo "✅ Backup files cleaned up!"

