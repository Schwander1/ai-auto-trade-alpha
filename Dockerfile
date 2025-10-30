FROM python:3.11-slim

# Set timezone and locale for trading
ENV TZ=America/New_York
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies optimized for trading
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    streamlit==1.28.0 \
    redis==5.0.1 \
    pandas==2.1.3 \
    numpy==1.25.2 \
    plotly==5.17.0 \
    requests==2.31.0 \
    python-dotenv==1.0.0 \
    yfinance==0.2.22 \
    scikit-learn==1.3.2 \
    alpaca-trade-api==3.1.1 \
    flask==3.0.0 \
    python-dateutil==2.8.2 \
    pytz==2023.3 \
    websockets==12.0 \
    aiohttp==3.8.6 \
    click \
    toml \
    psutil \
    schedule

# Copy ONLY the essential Python files (not everything)
COPY argo_dark_ultimate.py investor_dashboard.py risk_dashboard.py autoscheduler.py ./
COPY *.py ./

# Create non-root user for security
RUN useradd -m -u 1001 argo && chown -R argo:argo /app

# Expose trading ports
EXPOSE 8080 8501 8502 8503

# Health check for Streamlit apps
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health 2>/dev/null || curl -f http://localhost:8080/ || exit 1

# Switch to non-root user
USER argo

# Default command
CMD ["python", "--version"]
