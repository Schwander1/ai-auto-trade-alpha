#!/bin/bash
# Emergency Rollback Script

set -e

PROJECT="${1:-}"
VERSION="${2:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

main() {
    if [ -z "$PROJECT" ] || [ -z "$VERSION" ]; then
        echo "Usage: $0 [argo|alpine] [VERSION]"
        echo ""
        echo "Example: $0 argo v1.2.3"
        echo "Example: $0 alpine v2.1.2"
        exit 1
    fi
    
    echo "🔄 EMERGENCY ROLLBACK"
    echo "===================="
    echo "Project: $PROJECT"
    echo "Version: $VERSION"
    echo ""
    
    print_warning "This will rollback to version $VERSION"
    echo "Are you sure? (type 'yes' to confirm)"
    read -p "> " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        print_error "Rollback cancelled"
        exit 1
    fi
    
    # Checkout version
    if git checkout "$VERSION" 2>/dev/null; then
        print_success "Checked out version $VERSION"
        
        if [ "$PROJECT" = "argo" ]; then
            cd argo || exit 1
        elif [ "$PROJECT" = "alpine" ]; then
            cd alpine-backend || exit 1
        fi
        
        if command -v vercel &> /dev/null; then
            print_info "Deploying rollback..."
            vercel deploy --prod
        else
            print_warning "Vercel CLI not available"
        fi
        
        cd ..
    else
        print_error "Version $VERSION not found"
        exit 1
    fi
}

main "$@"
