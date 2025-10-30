#!/bin/bash
# ARGO Capital API Credentials Configuration

# Trading API Credentials (replace with your actual credentials)
export ALPACA_API_KEY="your_alpaca_api_key_here"
export ALPACA_SECRET_KEY="your_alpaca_secret_key_here"
export ALPACA_BASE_URL="https://paper-api.alpaca.markets"  # Use paper trading for testing

# Market Data API
export ALPHA_VANTAGE_API_KEY="your_alpha_vantage_key_here"

# Optional: Other trading APIs
export IEX_CLOUD_API_KEY="your_iex_cloud_key_here"
export POLYGON_API_KEY="your_polygon_api_key_here"

# ARGO Capital Configuration
export ARGO_ENVIRONMENT="development"
export ARGO_RISK_LEVEL="conservative"

echo "✅ ARGO Capital API credentials configured for $ARGO_ENVIRONMENT environment"
echo "🔒 Using $ARGO_RISK_LEVEL risk management settings"
