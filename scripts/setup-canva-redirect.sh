#!/bin/bash
# Helper script to set up local redirect URI for Canva OAuth

echo "🔧 Canva OAuth Redirect URI Setup"
echo ""
echo "For local development, Canva requires:"
echo "  ✅ http://127.0.0.1:<port> (allowed)"
echo "  ❌ http://localhost:<port> (NOT allowed)"
echo ""
echo "📋 Steps to configure in Canva Developer Portal:"
echo ""
echo "1. Go to: https://www.canva.com/developers/"
echo "2. Open your integration"
echo "3. Navigate to: Authentication → Authorized redirects"
echo "4. Add redirect URL: http://127.0.0.1:3000/auth/canva/callback"
echo "5. Save changes"
echo ""
echo "Then set the environment variable:"
echo "  export CANVA_REDIRECT_URI=\"http://127.0.0.1:3000/auth/canva/callback\""
echo ""
echo "Or use the script with:"
echo "  CANVA_REDIRECT_URI=\"http://127.0.0.1:3000/auth/canva/callback\" python3 scripts/canva_oauth2.py --auth"
echo ""

