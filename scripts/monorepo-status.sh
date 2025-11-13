#!/bin/bash
# Monorepo Status Command

echo "📊 MONOREPO STATUS"
echo "=================="
echo ""

echo "Git Status:"
git status --short | head -10 || echo "  No changes"

echo ""
echo "Recent Commits:"
git log --oneline -5

echo ""
echo "Branch: $(git branch --show-current)"

echo ""
echo "Project Status:"
echo "  Argo: $(test -d argo && echo '✅' || echo '❌')"
echo "  Alpine Backend: $(test -d alpine-backend && echo '✅' || echo '❌')"
echo "  Alpine Frontend: $(test -d alpine-frontend && echo '✅' || echo '❌')"
echo "  Packages: $(test -d packages && echo '✅' || echo '❌')"
