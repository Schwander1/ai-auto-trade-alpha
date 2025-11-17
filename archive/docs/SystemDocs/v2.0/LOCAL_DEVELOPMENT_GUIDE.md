# Local Development Guide

**Date:** January 15, 2025  
**Version:** 1.0

---

## Overview

Complete guide for local development setup, testing, and validation before production deployment.

---

## Quick Start

### 1. Initial Setup

```bash
# Run complete local setup
./scripts/local_setup.sh
```

This will:
- Verify Python environment
- Create virtual environment
- Install dependencies
- Setup databases
- Verify configuration
- Check Alpaca connection

### 2. Health Check

```bash
# Run comprehensive health check
./scripts/local_health_check.sh
```

### 3. Security Audit

```bash
# Run security audit
./scripts/local_security_audit.sh
```

### 4. Test Trade (Optional)

```bash
# Execute a test trade
python argo/scripts/execute_test_trade.py

# Enable full trading (after test trade passes)
python argo/scripts/enable_full_trading.py
```

---

## Development Workflow

### Daily Development

1. **Start Services**
   ```bash
   # Terminal 1: Argo API
   cd argo && source venv/bin/activate
   uvicorn main:app --reload --port 8000
   
   # Terminal 2: Alpine Backend
   cd alpine-backend && source venv/bin/activate
   uvicorn backend.main:app --reload --port 9001
   
   # Terminal 3: Alpine Frontend
   cd alpine-frontend
   npm run dev
   ```

2. **Make Changes**
   - Edit code
   - Test locally
   - Run health checks

3. **Validate Before Commit**
   ```bash
   ./scripts/pre_deployment_validation.sh
   ```

### Testing

**Run Backtests:**
```bash
python argo/scripts/run_local_backtests.py
```

**Run Health Checks:**
```bash
python argo/scripts/health_check_unified.py --level 3
```

**Run Security Audit:**
```bash
python scripts/security_audit_complete.py
```

---

## Local vs Production

### What Stays Local

- Test trade scripts
- Local setup scripts
- Local documentation
- Test files
- Development configs

### What Goes to Production

- Core application code
- Production scripts
- Health check tools
- Monitoring scripts
- Backtesting framework

### Environment Detection

The system automatically detects environment:
- Local: Uses dev Alpaca account
- Production: Uses production Alpaca account

---

## Troubleshooting

See `OPERATIONAL_GUIDE.md` for detailed troubleshooting.

---

**Last Updated:** January 15, 2025

