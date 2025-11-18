# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies for health checks and database connectivity
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code preserving the backend/ package structure
# This allows imports like "from backend.core.config" to work
COPY . /app/backend/

# Copy and make entrypoint script executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Set PYTHONPATH so imports work correctly
ENV PYTHONPATH=/app:$PYTHONPATH

EXPOSE 8000

# Use entrypoint script to wait for dependencies
ENTRYPOINT ["/entrypoint.sh"]

# Run uvicorn with backend.main:app since main.py is now at /app/backend/main.py
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
