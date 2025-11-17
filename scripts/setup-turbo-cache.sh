#!/bin/bash
# Setup Turbo Remote Cache
# Usage: ./scripts/setup-turbo-cache.sh [vercel|self-hosted|s3]

set -e

CACHE_TYPE="${1:-vercel}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "⚡ Setting up Turbo Remote Cache"
echo "================================="
echo "Cache Type: $CACHE_TYPE"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo "ℹ️  $1"
}

case "$CACHE_TYPE" in
    vercel)
        print_info "Setting up Vercel Remote Cache..."
        
        # Check if Turbo is installed
        if ! command -v turbo &> /dev/null; then
            print_info "Installing Turbo CLI..."
            npm install -g turbo
        fi
        
        # Login to Vercel
        print_info "Logging in to Vercel..."
        if npx turbo login; then
            print_success "Logged in to Vercel"
        else
            echo "❌ Failed to login to Vercel"
            exit 1
        fi
        
        # Link to Vercel team
        print_info "Linking to Vercel team..."
        if npx turbo link; then
            print_success "Linked to Vercel team"
        else
            echo "❌ Failed to link to Vercel team"
            exit 1
        fi
        
        # Test cache
        print_info "Testing cache..."
        cd "$PROJECT_ROOT"
        if pnpm build 2>&1 | grep -q "FULL TURBO\|cache hit"; then
            print_success "Turbo cache is working!"
        else
            print_info "First build complete. Second build will use cache."
        fi
        ;;
        
    self-hosted)
        print_info "Setting up Self-Hosted Remote Cache..."
        
        read -p "Enter cache server URL (e.g., http://your-server:8080): " CACHE_URL
        read -p "Enter team name: " TEAM_NAME
        read -sp "Enter token: " TOKEN
        echo
        
        export TURBO_REMOTE_CACHE_URL="$CACHE_URL"
        export TURBO_TEAM="$TEAM_NAME"
        export TURBO_TOKEN="$TOKEN"
        
        print_info "Testing connection..."
        cd "$PROJECT_ROOT"
        if pnpm build; then
            print_success "Self-hosted cache configured!"
        else
            echo "❌ Failed to connect to cache server"
            exit 1
        fi
        
        print_info "Add these to your environment:"
        echo "  export TURBO_REMOTE_CACHE_URL=$CACHE_URL"
        echo "  export TURBO_TEAM=$TEAM_NAME"
        echo "  export TURBO_TOKEN=$TOKEN"
        ;;
        
    s3)
        print_info "Setting up S3-Based Remote Cache..."
        
        read -p "Enter S3 bucket name: " BUCKET_NAME
        read -p "Enter AWS region: " AWS_REGION
        read -p "Enter AWS Access Key ID: " AWS_ACCESS_KEY
        read -sp "Enter AWS Secret Access Key: " AWS_SECRET_KEY
        echo
        
        export TURBO_REMOTE_CACHE_URL="s3://$BUCKET_NAME/turbo-cache"
        export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY"
        export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_KEY"
        export AWS_REGION="$AWS_REGION"
        
        print_info "Testing S3 connection..."
        cd "$PROJECT_ROOT"
        if pnpm build; then
            print_success "S3 cache configured!"
        else
            echo "❌ Failed to connect to S3"
            exit 1
        fi
        
        print_info "Add these to your environment:"
        echo "  export TURBO_REMOTE_CACHE_URL=s3://$BUCKET_NAME/turbo-cache"
        echo "  export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY"
        echo "  export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY"
        echo "  export AWS_REGION=$AWS_REGION"
        ;;
        
    *)
        echo "❌ Invalid cache type: $CACHE_TYPE"
        echo "Usage: $0 [vercel|self-hosted|s3]"
        exit 1
        ;;
esac

echo ""
print_success "Turbo cache setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Test cache: pnpm build (second build should be faster)"
echo "2. Configure CI/CD with cache credentials"
echo "3. Monitor cache hit rates"

