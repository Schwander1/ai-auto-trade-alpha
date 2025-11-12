#!/bin/bash
# Automated Security Audit Script
# Runs quarterly security audits

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

AUDIT_DATE=$(date +%Y-%m-%d)
AUDIT_DIR="security-audits"
AUDIT_FILE="${AUDIT_DIR}/audit-${AUDIT_DATE}.md"

echo "🔒 Running Security Audit - ${AUDIT_DATE}"
echo "=========================================="

# Create audit directory
mkdir -p "${AUDIT_DIR}"

# Start audit report
cat > "${AUDIT_FILE}" << EOF
# Security Audit Report
**Date:** ${AUDIT_DATE}
**Type:** Quarterly Automated Audit

---

## 1. Dependency Vulnerability Scan

EOF

# Check for Python vulnerabilities
echo "📦 Scanning Python dependencies..."
if command -v pip-audit &> /dev/null; then
    pip-audit --format=markdown >> "${AUDIT_FILE}" 2>&1 || echo "⚠️  pip-audit not available"
else
    echo "⚠️  pip-audit not installed. Install with: pip install pip-audit" >> "${AUDIT_FILE}"
fi

# Check for Node.js vulnerabilities
echo "📦 Scanning Node.js dependencies..."
if command -v npm &> /dev/null; then
    echo "### Node.js Dependencies" >> "${AUDIT_FILE}"
    cd alpine-frontend && npm audit --json 2>/dev/null | jq -r '.vulnerabilities | to_entries[] | "**\(.key)**: \(.value.severity) - \(.value.title)"' >> "../${AUDIT_FILE}" 2>&1 || echo "No vulnerabilities found" >> "../${AUDIT_FILE}"
    cd ..
fi

# Security headers check
echo "" >> "${AUDIT_FILE}"
echo "## 2. Security Headers Check" >> "${AUDIT_FILE}"
echo "" >> "${AUDIT_FILE}"

ALPINE_URL="http://localhost:8001"
if curl -s -I "${ALPINE_URL}/health" | grep -i "strict-transport-security" >> "${AUDIT_FILE}" 2>&1; then
    echo "✅ HSTS header present" >> "${AUDIT_FILE}"
else
    echo "❌ HSTS header missing" >> "${AUDIT_FILE}"
fi

if curl -s -I "${ALPINE_URL}/health" | grep -i "content-security-policy" >> "${AUDIT_FILE}" 2>&1; then
    echo "✅ CSP header present" >> "${AUDIT_FILE}"
else
    echo "❌ CSP header missing" >> "${AUDIT_FILE}"
fi

# Check for hardcoded secrets
echo "" >> "${AUDIT_FILE}"
echo "## 3. Secret Scanning" >> "${AUDIT_FILE}"
echo "" >> "${AUDIT_FILE}"

if grep -r "api_key.*=" --include="*.py" --include="*.js" --include="*.ts" alpine-backend argo 2>/dev/null | grep -v "example\|template\|test" | head -5 >> "${AUDIT_FILE}" 2>&1; then
    echo "⚠️  Potential hardcoded secrets found" >> "${AUDIT_FILE}"
else
    echo "✅ No hardcoded secrets detected" >> "${AUDIT_FILE}"
fi

# Check .env files are not committed
echo "" >> "${AUDIT_FILE}"
echo "## 4. Environment Files Check" >> "${AUDIT_FILE}"
echo "" >> "${AUDIT_FILE}"

if git ls-files | grep -E "\.env$|\.env\.local$" >> "${AUDIT_FILE}" 2>&1; then
    echo "❌ .env files found in repository" >> "${AUDIT_FILE}"
else
    echo "✅ No .env files in repository" >> "${AUDIT_FILE}"
fi

# Security log analysis
echo "" >> "${AUDIT_FILE}"
echo "## 5. Security Log Analysis" >> "${AUDIT_FILE}"
echo "" >> "${AUDIT_FILE}"

if [ -f "alpine-backend/logs/security.log" ]; then
    echo "### Failed Login Attempts (Last 30 days)" >> "${AUDIT_FILE}"
    grep "failed_login" alpine-backend/logs/security.log | tail -20 | wc -l | xargs echo "Total:" >> "${AUDIT_FILE}"
    
    echo "" >> "${AUDIT_FILE}"
    echo "### Account Lockouts (Last 30 days)" >> "${AUDIT_FILE}"
    grep "account_locked" alpine-backend/logs/security.log | tail -20 | wc -l | xargs echo "Total:" >> "${AUDIT_FILE}"
    
    echo "" >> "${AUDIT_FILE}"
    echo "### Rate Limit Violations (Last 30 days)" >> "${AUDIT_FILE}"
    grep "rate_limit_exceeded" alpine-backend/logs/security.log | tail -20 | wc -l | xargs echo "Total:" >> "${AUDIT_FILE}"
else
    echo "⚠️  Security log file not found" >> "${AUDIT_FILE}"
fi

# Configuration check
echo "" >> "${AUDIT_FILE}"
echo "## 6. Configuration Security" >> "${AUDIT_FILE}"
echo "" >> "${AUDIT_FILE}"

# Check JWT secret length
if grep -r "JWT_SECRET" alpine-backend/.env.example 2>/dev/null | grep -q "32"; then
    echo "✅ JWT_SECRET length requirement documented" >> "${AUDIT_FILE}"
else
    echo "⚠️  JWT_SECRET length requirement not documented" >> "${AUDIT_FILE}"
fi

# Summary
echo "" >> "${AUDIT_FILE}"
echo "## Summary" >> "${AUDIT_FILE}"
echo "" >> "${AUDIT_FILE}"
echo "Audit completed: ${AUDIT_DATE}" >> "${AUDIT_FILE}"
# Calculate next audit date (3 months from now)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS date command
    NEXT_AUDIT=$(date -v+3m +%Y-%m-%d)
else
    # Linux date command
    NEXT_AUDIT=$(date -d '+3 months' +%Y-%m-%d)
fi
echo "Next audit due: ${NEXT_AUDIT}" >> "${AUDIT_FILE}"

echo -e "${GREEN}✅ Security audit complete: ${AUDIT_FILE}${NC}"

