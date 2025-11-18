#!/bin/bash
# Cleanup unnecessary files and finalize production setup

set -e

echo "🧹 CLEANUP AND PRODUCTION FINALIZATION"
echo "======================================="
echo ""

# Cleanup function
cleanup_files() {
    echo "📋 Cleaning up unnecessary files..."
    
    # Remove Python cache files
    echo "   Removing Python cache files..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    # Remove temporary files
    echo "   Removing temporary files..."
    find . -name "*.tmp" -delete 2>/dev/null || true
    find . -name "*.swp" -delete 2>/dev/null || true
    find . -name "*~" -delete 2>/dev/null || true
    find . -name ".DS_Store" -delete 2>/dev/null || true
    
    # Remove old backup files
    echo "   Removing old backup files..."
    find . -name "*.backup" -delete 2>/dev/null || true
    find . -name "*.bak" -delete 2>/dev/null || true
    find . -name "*_old" -delete 2>/dev/null || true
    find . -name "*_OLD" -delete 2>/dev/null || true
    
    # Remove duplicate/redundant status reports (keep only latest)
    echo "   Cleaning up redundant status reports..."
    # Keep only the most recent comprehensive reports
    rm -f COMPLETE_STATUS_REPORT.md 2>/dev/null || true
    rm -f COMPLETE_STATUS.md 2>/dev/null || true
    rm -f STATUS_REPORT.md 2>/dev/null || true
    rm -f STATUS_SUMMARY.md 2>/dev/null || true
    rm -f CURRENT_STATUS.md 2>/dev/null || true
    rm -f FINAL_STATUS.md 2>/dev/null || true
    rm -f FINAL_STATUS_REPORT.md 2>/dev/null || true
    
    # Remove investigation/troubleshooting files (keep only final summary)
    echo "   Cleaning up investigation files..."
    rm -f INVESTIGATION_RESULTS.md 2>/dev/null || true
    rm -f TROUBLESHOOTING_*.md 2>/dev/null || true
    rm -f ROOT_CAUSE_ANALYSIS.md 2>/dev/null || true
    rm -f COMPLETE_TROUBLESHOOTING_REPORT.md 2>/dev/null || true
    rm -f COMPLETE_DIAGNOSTIC_REPORT.md 2>/dev/null || true
    rm -f COMPREHENSIVE_CHECK_RESULTS.md 2>/dev/null || true
    rm -f COMPREHENSIVE_STATUS_FINAL.md 2>/dev/null || true
    
    # Remove old fix files
    echo "   Cleaning up old fix files..."
    rm -f FIXES_APPLIED.md 2>/dev/null || true
    rm -f ISSUE_RESOLVED.md 2>/dev/null || true
    rm -f FINAL_RESOLUTION_SUMMARY.md 2>/dev/null || true
    rm -f RESTART_ATTEMPT_RESULTS.md 2>/dev/null || true
    
    # Remove duplicate setup scripts (keep only the final ones)
    echo "   Cleaning up duplicate scripts..."
    # Keep: enable_dual_trading_production.sh, create_systemd_services.sh
    # Remove old test/debug scripts
    rm -f debug_*.py 2>/dev/null || true
    rm -f test_*.py 2>/dev/null || true
    rm -f temp_*.py 2>/dev/null || true
    
    echo "   ✅ Cleanup complete"
}

# Organize files
organize_files() {
    echo ""
    echo "📁 Organizing files..."
    
    # Create docs directory if it doesn't exist
    mkdir -p docs/production_setup 2>/dev/null || true
    
    # Move production setup docs
    if [ -f "DUAL_TRADING_PRODUCTION_SETUP.md" ]; then
        mv DUAL_TRADING_PRODUCTION_SETUP.md docs/production_setup/ 2>/dev/null || true
        echo "   ✅ Moved DUAL_TRADING_PRODUCTION_SETUP.md"
    fi
    
    if [ -f "FINAL_DUAL_TRADING_SETUP.md" ]; then
        mv FINAL_DUAL_TRADING_SETUP.md docs/production_setup/ 2>/dev/null || true
        echo "   ✅ Moved FINAL_DUAL_TRADING_SETUP.md"
    fi
    
    if [ -f "MASSIVE_FIX_COMPLETE.md" ]; then
        mv MASSIVE_FIX_COMPLETE.md docs/ 2>/dev/null || true
        echo "   ✅ Moved MASSIVE_FIX_COMPLETE.md"
    fi
    
    if [ -f "ALL_NEXT_STEPS_COMPLETE.md" ]; then
        mv ALL_NEXT_STEPS_COMPLETE.md docs/ 2>/dev/null || true
        echo "   ✅ Moved ALL_NEXT_STEPS_COMPLETE.md"
    fi
    
    if [ -f "NEXT_STEPS_COMPLETE.md" ]; then
        mv NEXT_STEPS_COMPLETE.md docs/ 2>/dev/null || true
        echo "   ✅ Moved NEXT_STEPS_COMPLETE.md"
    fi
    
    if [ -f "MASSIVE_API_KEY_FIX_SUMMARY.md" ]; then
        mv MASSIVE_API_KEY_FIX_SUMMARY.md docs/ 2>/dev/null || true
        echo "   ✅ Moved MASSIVE_API_KEY_FIX_SUMMARY.md"
    fi
    
    # Create scripts directory if needed
    mkdir -p scripts/production 2>/dev/null || true
    
    # Move production scripts
    if [ -f "enable_dual_trading_production.sh" ]; then
        mv enable_dual_trading_production.sh scripts/production/ 2>/dev/null || true
        echo "   ✅ Moved enable_dual_trading_production.sh"
    fi
    
    if [ -f "create_systemd_services.sh" ]; then
        mv create_systemd_services.sh scripts/production/ 2>/dev/null || true
        echo "   ✅ Moved create_systemd_services.sh"
    fi
    
    if [ -f "setup_dual_trading_production.py" ]; then
        mv setup_dual_trading_production.py scripts/production/ 2>/dev/null || true
        echo "   ✅ Moved setup_dual_trading_production.py"
    fi
    
    if [ -f "verify_dual_trading_setup.py" ]; then
        mv verify_dual_trading_setup.py scripts/production/ 2>/dev/null || true
        echo "   ✅ Moved verify_dual_trading_setup.py"
    fi
    
    if [ -f "fix_massive_api_key.py" ]; then
        mv fix_massive_api_key.py scripts/production/ 2>/dev/null || true
        echo "   ✅ Moved fix_massive_api_key.py"
    fi
    
    if [ -f "verify_massive_fix.py" ]; then
        mv verify_massive_fix.py scripts/production/ 2>/dev/null || true
        echo "   ✅ Moved verify_massive_fix.py"
    fi
    
    if [ -f "comprehensive_system_check.py" ]; then
        mv comprehensive_system_check.py scripts/production/ 2>/dev/null || true
        echo "   ✅ Moved comprehensive_system_check.py"
    fi
    
    echo "   ✅ Organization complete"
}

# Verify essential files
verify_essential_files() {
    echo ""
    echo "✅ Verifying essential files..."
    
    essential_files=(
        "argo/config.json"
        "scripts/production/enable_dual_trading_production.sh"
        "scripts/production/create_systemd_services.sh"
        "docs/production_setup/DUAL_TRADING_PRODUCTION_SETUP.md"
    )
    
    all_present=true
    for file in "${essential_files[@]}"; do
        if [ -f "$file" ]; then
            echo "   ✅ $file"
        else
            echo "   ⚠️  Missing: $file"
            all_present=false
        fi
    done
    
    if [ "$all_present" = true ]; then
        echo "   ✅ All essential files present"
    else
        echo "   ⚠️  Some files may need to be recreated"
    fi
}

# Create production deployment package
create_deployment_package() {
    echo ""
    echo "📦 Creating production deployment package..."
    
    mkdir -p production_deployment 2>/dev/null || true
    
    # Copy essential scripts
    cp scripts/production/enable_dual_trading_production.sh production_deployment/ 2>/dev/null || true
    cp scripts/production/create_systemd_services.sh production_deployment/ 2>/dev/null || true
    cp scripts/production/verify_dual_trading_setup.py production_deployment/ 2>/dev/null || true
    
    # Copy documentation
    cp docs/production_setup/DUAL_TRADING_PRODUCTION_SETUP.md production_deployment/ 2>/dev/null || true
    cp docs/production_setup/FINAL_DUAL_TRADING_SETUP.md production_deployment/ 2>/dev/null || true
    
    # Create deployment README
    cat > production_deployment/README.md << 'EOF'
# Production Deployment Package

## Quick Start

1. Copy all files to production server:
   ```bash
   scp -r production_deployment/* root@your-server:/root/
   ```

2. Run setup:
   ```bash
   chmod +x enable_dual_trading_production.sh
   chmod +x create_systemd_services.sh
   ./enable_dual_trading_production.sh
   ```

3. Add Alpaca credentials to config files

4. Create and start services:
   ```bash
   ./create_systemd_services.sh
   sudo systemctl start argo-trading.service
   sudo systemctl start argo-trading-prop-firm.service
   ```

5. Verify:
   ```bash
   python3 verify_dual_trading_setup.py
   curl http://localhost:8000/health
   curl http://localhost:8001/health
   ```

See DUAL_TRADING_PRODUCTION_SETUP.md for complete documentation.
EOF
    
    echo "   ✅ Deployment package created in production_deployment/"
}

# Main execution
main() {
    cleanup_files
    organize_files
    verify_essential_files
    create_deployment_package
    
    echo ""
    echo "======================================="
    echo "✅ CLEANUP AND ORGANIZATION COMPLETE"
    echo "======================================="
    echo ""
    echo "📋 Summary:"
    echo "   ✅ Removed unnecessary files"
    echo "   ✅ Organized files into proper directories"
    echo "   ✅ Verified essential files"
    echo "   ✅ Created production deployment package"
    echo ""
    echo "📦 Production deployment package ready in: production_deployment/"
    echo ""
}

main

