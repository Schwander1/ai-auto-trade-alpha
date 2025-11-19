# Configuration Examples

This document provides comprehensive configuration examples for the Argo-Alpine trading signal platform.

---

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Argo Configuration](#argo-configuration)
3. [Alpine Configuration](#alpine-configuration)
4. [AWS Secrets Manager](#aws-secrets-manager)
5. [Database Configuration](#database-configuration)
6. [Monitoring Configuration](#monitoring-configuration)
7. [Compliance Configuration](#compliance-configuration)

---

## Environment Variables

### Production Environment

**Argo Production (`/root/argo-production/.env`):**
```bash
# Environment
ENV=production

# Alpaca Trading API (from AWS Secrets Manager)
ALPACA_API_KEY=your-api-key
ALPACA_SECRET_KEY=your-secret-key

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# 24/7 Trading Mode
ARGO_24_7_MODE=true

# Alpine Sync
ALPINE_API_URL=http://91.98.153.49:8001
ARGO_API_KEY=your-shared-api-key
ALPINE_SYNC_ENABLED=true

# Logging
LOG_LEVEL=INFO
DEBUG=false

# Executor Configuration
EXECUTOR_ID=argo
EXECUTOR_CONFIG_PATH=/root/argo-production-green/config.json
PORT=8000
```

**Prop Firm Executor (`/root/argo-production-prop-firm/.env`):**
```bash
ENV=production
EXECUTOR_ID=prop_firm
EXECUTOR_CONFIG_PATH=/root/argo-production-prop-firm/config.json
PORT=8001
ARGO_24_7_MODE=true
```

**Alpine Backend (`.env`):**
```bash
# Environment
ENV=production

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/alpine

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET=your-jwt-secret-key

# AWS
AWS_REGION=us-east-1

# External Signal API
EXTERNAL_SIGNAL_API_KEY=your-shared-api-key

# CORS
CORS_ORIGINS=http://localhost:3000,https://alpineanalytics.com

# Logging
LOG_LEVEL=INFO
```

**Alpine Frontend (`.env.local`):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_WS_URL=ws://localhost:8001
```

### Development Environment

**Argo Development:**
```bash
ENV=development
LOG_LEVEL=DEBUG
DEBUG=true
ARGO_24_7_MODE=false
```

**Alpine Development:**
```bash
ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/alpine_dev
LOG_LEVEL=DEBUG
DEBUG=true
```

---

## Argo Configuration

### Complete `config.json` Example

**Location:** `/root/argo-production-unified/config.json`

```json
{
  "signal_generation": {
    "enabled": true,
    "interval_seconds": 5,
    "symbols": {
      "stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
      "crypto": ["BTC-USD", "ETH-USD", "SOL-USD"]
    }
  },
  "data_sources": {
    "massive": {
      "api_key": "your-massive-api-key",
      "enabled": true
    },
    "alpha_vantage": {
      "api_key": "your-alpha-vantage-key",
      "enabled": true
    },
    "x_api": {
      "bearer_token": "your-x-api-token",
      "enabled": true
    },
    "sonar": {
      "api_key": "your-sonar-key",
      "enabled": true
    }
  },
  "alpaca": {
    "dev": {
      "api_key": "dev-key",
      "secret_key": "dev-secret",
      "paper": true,
      "account_name": "dev-account"
    },
    "production": {
      "api_key": "prod-key",
      "secret_key": "prod-secret",
      "paper": true,
      "account_name": "prod-account"
    }
  },
  "strategy": {
    "use_multi_source": true,
    "weight_massive": 0.40,
    "weight_alpha_vantage": 0.25,
    "weight_x_sentiment": 0.20,
    "weight_sonar": 0.15,
    "consensus_threshold": 75.0
  },
  "trading": {
    "min_confidence": 75.0,
    "consensus_threshold": 75.0,
    "profit_target": 0.05,
    "stop_loss": 0.03,
    "position_size_pct": 10,
    "max_position_size_pct": 15,
    "max_correlated_positions": 3,
    "max_drawdown_pct": 10,
    "daily_loss_limit_pct": 5.0,
    "auto_execute": true,
    "use_limit_orders": false,
    "limit_order_offset_pct": 0.001,
    "max_retry_attempts": 3,
    "retry_delay_seconds": 1,
    "enable_position_monitoring": true,
    "enable_performance_tracking": true
  },
  "prop_firm": {
    "enabled": true,
    "risk_limits": {
      "min_confidence": 82.0,
      "max_daily_loss_pct": 5.0,
      "max_position_size_pct": 10,
      "skip_crisis_regime": true
    }
  },
  "alpine": {
    "api_url": "http://91.98.153.49:8001",
    "api_key": "your-shared-api-key",
    "sync_enabled": true
  },
  "backtest": {
    "data_source": "yfinance",
    "data_path": "argo/data/historical",
    "cache_enabled": true,
    "symbols": {
      "stocks": ["AAPL", "MSFT", "GOOGL"],
      "crypto": ["BTC-USD", "ETH-USD"]
    },
    "walk_forward": {
      "enabled": true,
      "train_days": 252,
      "test_days": 63,
      "step_days": 21
    },
    "optimization": {
      "enabled": true,
      "method": "grid_search",
      "max_iterations": 1000
    },
    "metrics": {
      "include_advanced": true,
      "regime_analysis": true,
      "monte_carlo_runs": 1000
    },
    "execution": {
      "slippage_pct": 0.001,
      "commission_pct": 0.001
    }
  }
}
```

### Prop Firm Configuration

**Location:** `/root/argo-production-prop-firm/config.json`

```json
{
  "trading": {
    "min_confidence": 82.0,
    "position_size_pct": 10,
    "max_position_size_pct": 10,
    "daily_loss_limit_pct": 5.0,
    "auto_execute": true
  },
  "prop_firm": {
    "enabled": true,
    "risk_limits": {
      "min_confidence": 82.0,
      "max_daily_loss_pct": 5.0,
      "max_position_size_pct": 10,
      "skip_crisis_regime": true,
      "max_positions": 5
    }
  },
  "alpaca": {
    "production": {
      "api_key": "prop-firm-key",
      "secret_key": "prop-firm-secret",
      "paper": true,
      "account_name": "prop-firm-account"
    }
  }
}
```

---

## Alpine Configuration

### Backend Settings

**File:** `alpine-backend/backend/core/config.py` (uses Pydantic Settings)

**Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/alpine

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET=your-256-bit-secret-key

# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# External API
EXTERNAL_SIGNAL_API_KEY=shared-secret-key

# CORS
CORS_ORIGINS=http://localhost:3000,https://alpineanalytics.com

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

### Frontend Configuration

**File:** `alpine-frontend/.env.local`

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_WS_URL=ws://localhost:8001

# Feature Flags
NEXT_PUBLIC_ENABLE_TRADING=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true

# Analytics
NEXT_PUBLIC_GA_ID=your-google-analytics-id
```

---

## AWS Secrets Manager

### Secret Structure

**Argo Secrets:**
```
argo-alpine/argo/alpaca-api-key
argo-alpine/argo/alpaca-secret-key
argo-alpine/argo/argo-api-key
argo-alpine/argo/alpine-api-url
```

**Alpine Secrets:**
```
argo-alpine/alpine/database-url
argo-alpine/alpine/jwt-secret
argo-alpine/alpine/external-signal-api-key
```

### Example Secret JSON

**Alpaca Credentials:**
```json
{
  "api_key": "PKXXXXXXXXXXXXXXXX",
  "secret_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "paper": true,
  "account_name": "production-account"
}
```

**Database URL:**
```json
{
  "database_url": "postgresql://user:password@host:5432/database",
  "pool_size": 20,
  "max_overflow": 10
}
```

---

## Database Configuration

### PostgreSQL (Alpine)

**Connection String:**
```
postgresql://user:password@host:5432/alpine?sslmode=require
```

**Connection Pool Settings:**
```python
{
  "pool_size": 20,
  "max_overflow": 10,
  "pool_timeout": 30,
  "pool_recycle": 3600
}
```

### SQLite (Argo)

**Database Path:**
```
/root/argo-production/data/signals_unified.db
```

**Connection Settings:**
```python
{
  "timeout": 10.0,
  "check_same_thread": False,
  "isolation_level": None
}
```

---

## Monitoring Configuration

### Prometheus

**File:** `infrastructure/monitoring/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'argo'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  - job_name: 'alpine-backend'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: '/metrics'
```

### Grafana Dashboard

**Import from:** `infrastructure/monitoring/grafana-dashboards/compliance-dashboard.json`

**Data Source:**
- Name: Prometheus
- URL: http://localhost:9090
- Access: Server (Default)

---

## Compliance Configuration

### Backup Configuration

**S3 Bucket:**
```bash
BUCKET_NAME=argo-alpine-backups
AWS_REGION=us-east-1
BACKUP_RETENTION_DAYS=2555  # 7 years
```

**Cron Job:**
```bash
# Daily backup at 2 AM UTC
0 2 * * * cd /root/argo-production && python argo/argo/compliance/daily_backup.py >> logs/backup.log 2>&1
```

### Integrity Monitoring

**Cron Jobs:**
```bash
# Hourly integrity check
0 * * * * cd /root/argo-production && python argo/argo/compliance/integrity_monitor.py >> logs/integrity.log 2>&1

# Daily full integrity check
0 3 * * * cd /root/argo-production && python argo/argo/compliance/integrity_monitor.py full >> logs/integrity.log 2>&1
```

### Audit Logging

**Database Table:** `signal_audit_log`

**Configuration:**
- Automatic logging via database triggers
- Retention: 7 years
- Immutable (triggers prevent modification)

---

## Validation

### Check Configuration

**Argo:**
```bash
python -c "from argo.core.config import load_config; print(load_config())"
```

**Alpine:**
```bash
python -c "from backend.core.config import settings; print(settings.dict())"
```

### Environment Validation

```bash
# Validate Argo environment
./scripts/check-env.sh argo

# Validate Alpine environment
./scripts/check-env.sh alpine
```

---

## Security Best Practices

1. **Never commit secrets** - Use AWS Secrets Manager or environment variables
2. **Rotate keys regularly** - Update API keys every 90 days
3. **Use least privilege** - Grant minimum required permissions
4. **Enable encryption** - Use SSL/TLS for all connections
5. **Monitor access** - Log all configuration changes
6. **Backup secrets** - Store encrypted backups of critical keys

---

## Troubleshooting

### Common Issues

**Issue: Configuration not loading**
- Check file paths and permissions
- Verify environment variables are set
- Check AWS Secrets Manager access

**Issue: Database connection failed**
- Verify connection string format
- Check network connectivity
- Verify credentials

**Issue: API keys not working**
- Verify keys are correct
- Check key permissions
- Verify account status

---

## Additional Resources

- [Configuration Management Guide](../Documentation/SystemDocs/CONFIGURATION_MANAGEMENT_COMPLETE_GUIDE.md)
- [Environment Setup](../Rules/05_ENVIRONMENT.md)
- [AWS Secrets Manager Setup](../Documentation/SystemDocs/AWS_SECRETS_MANAGER_SETUP.md)
- [Deployment Guide](../Documentation/DEPLOYMENT_GUIDE.md)
