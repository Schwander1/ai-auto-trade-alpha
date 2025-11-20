#!/bin/bash
# Standardized error handling
# Source this file and call set_error_handling() to enable

set_error_handling() {
    set -euo pipefail  # Exit on error, undefined vars, pipe failures
    trap 'error_exit $? $LINENO' ERR
}

error_exit() {
    local exit_code=$1
    local line_number=$2

    # Source colors if available
    if [ -z "${RED:-}" ]; then
        RED='\033[0;31m'
        NC='\033[0m'
    fi

    echo -e "${RED}❌ Error at line $line_number (exit code $exit_code)${NC}" >&2
    exit $exit_code
}
