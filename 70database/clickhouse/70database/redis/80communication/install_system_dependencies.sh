#!/bin/bash
# ARGO Capital System Dependencies Installation

echo "📦 ARGO Capital System Dependencies Installation"

# Install Python packages
echo "Installing Python packages..."
pip install clickhouse-connect redis pandas asyncio python-dotenv

# Install system packages via Homebrew
echo "Installing system packages..."
brew install clickhouse redis

# Install monitoring tools
pip install psutil GPUtil

echo "✅ All dependencies installed successfully"
echo "🎯 Ready to run complete system setup"

