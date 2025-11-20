#!/bin/bash
# Environment URL configuration
# Centralized configuration for all environment URLs

get_environment_urls() {
    local env="${1:-local}"

    case "$env" in
        production)
            echo "ARGO_URL=http://178.156.194.174:8000"
            echo "ALPINE_BACKEND_URL=http://91.98.153.49:8001"
            echo "ALPINE_FRONTEND_URL=http://91.98.153.49:3000"
            ;;
        staging)
            # Add staging URLs when available
            echo "ARGO_URL=http://staging-argo.example.com:8000"
            echo "ALPINE_BACKEND_URL=http://staging-alpine.example.com:8001"
            echo "ALPINE_FRONTEND_URL=http://staging-alpine.example.com:3000"
            ;;
        local|*)
            echo "ARGO_URL=http://localhost:8000"
            echo "ALPINE_BACKEND_URL=http://localhost:9001"
            echo "ALPINE_FRONTEND_URL=http://localhost:3000"
            ;;
    esac
}

# Load environment URLs into current shell
load_environment_urls() {
    local env="${1:-local}"
    eval $(get_environment_urls "$env")
}
