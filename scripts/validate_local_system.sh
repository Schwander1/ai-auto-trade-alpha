#!/bin/bash
# Complete local system validation before deployment

set -e

echo "🔍 COMPLETE LOCAL SYSTEM VALIDATION"
echo "===================================="
echo ""

# Run all validation steps
echo "Running pre-deployment validation..."
./scripts/pre_deployment_validation.sh

echo ""
echo "✅ Local system validation complete!"

