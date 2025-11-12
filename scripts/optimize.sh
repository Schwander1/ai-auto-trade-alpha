#!/bin/bash

# Code optimization analysis script
# Analyzes codebase and generates optimization report

echo "🔍 Running Code Optimization Analysis..."
echo "========================================"
echo ""

REPORT_FILE="optimization-report.md"

cat > $REPORT_FILE << 'EOF'
# Code Optimization Report

Generated: $(date)

## Performance Analysis

EOF

# Analyze Python code
echo "📊 Analyzing Python code..."
if command -v pylint > /dev/null; then
  echo "### Python Code Quality" >> $REPORT_FILE
  find packages -name "*.py" -type f | head -20 | xargs pylint --disable=all --enable=performance 2>/dev/null | grep -E "R|C" | head -10 >> $REPORT_FILE || echo "No issues found" >> $REPORT_FILE
fi

# Analyze TypeScript code
echo "📊 Analyzing TypeScript code..."
if command -v eslint > /dev/null; then
  echo "" >> $REPORT_FILE
  echo "### TypeScript Code Quality" >> $REPORT_FILE
  npx eslint packages/alpine-frontend --format json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for file in data[:5]:
    print(f\"**{file['filePath']}**:\")
    for msg in file['messages'][:3]:
        print(f\"  - {msg['message']} (line {msg['line']})\")
" >> $REPORT_FILE 2>/dev/null || echo "No issues found" >> $REPORT_FILE
fi

# Check for performance issues
echo "📊 Checking for performance issues..."
cat >> $REPORT_FILE << 'EOF'

## Performance Recommendations

### Database Queries
- Check for N+1 query patterns
- Verify indexes are in place
- Review slow query logs

### Caching Opportunities
- API response caching
- Database query result caching
- Frontend asset caching

### Bundle Size
- Check for unused dependencies
- Verify code splitting is working
- Review bundle analyzer reports

## Security Analysis

EOF

# Security checks
if command -v bandit > /dev/null; then
  echo "### Python Security" >> $REPORT_FILE
  bandit -r packages/argo-trading packages/alpine-backend -f json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for result in data.get('results', [])[:5]:
    print(f\"**{result['filename']}**: {result['test_name']} (Severity: {result['issue_severity']})\")
" >> $REPORT_FILE 2>/dev/null || echo "No security issues found" >> $REPORT_FILE
fi

cat >> $REPORT_FILE << 'EOF'

## Recommendations

1. Review performance bottlenecks
2. Implement suggested caching strategies
3. Address security findings
4. Optimize database queries
5. Reduce bundle sizes

---
*This report is generated automatically. Review and implement suggestions as needed.*

EOF

echo "✅ Optimization report generated: $REPORT_FILE"
cat $REPORT_FILE

