#!/bin/bash
# macOS Backtesting Environment Setup
# Optimized for M-series Macs (M1/M2/M3)

set -e

echo "🚀 Setting up macOS backtesting environment..."

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "📦 Installing pyenv..."
    brew install pyenv
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zprofile
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zprofile
    echo 'eval "$(pyenv init -)"' >> ~/.zprofile
    source ~/.zprofile
fi

# Install Python 3.12.0
echo "🐍 Installing Python 3.12.0..."
pyenv install 3.12.0 --skip-existing
pyenv local 3.12.0

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv argo_backtest_env
source argo_backtest_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip wheel setuptools

# Install optimized dependencies
echo "📥 Installing optimized dependencies..."
pip install polars[parquet]==1.20.0
pip install duckdb==1.1.0
pip install numba==0.59.0
pip install boto3==1.35.0
pip install scipy==1.14.0
pip install tqdm>=4.66.0

# Install other requirements
echo "📥 Installing other requirements..."
pip install -r argo/requirements.txt

# Add macOS optimizations to ~/.zprofile
echo "⚙️  Adding macOS optimizations..."
if ! grep -q "PYTHONOPTIMIZE" ~/.zprofile; then
    cat >> ~/.zprofile << 'EOF'

# Argo Backtesting Optimizations
export PYTHONOPTIMIZE=2
export NUMEXPR_NUM_THREADS=8
export VECLIB_MAXIMUM_THREADS=8
export OMP_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export MALLOC_TRIM_THRESHOLD_=131072
EOF
    echo "✅ Added optimizations to ~/.zprofile"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the environment:"
echo "  source argo_backtest_env/bin/activate"
echo ""
echo "To run backtests:"
echo "  python3 argo/scripts/run_comprehensive_backtest.py"

