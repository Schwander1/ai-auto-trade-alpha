# Unified Architecture Deployment Guide

**Date:** November 18, 2025  
**Version:** 3.0  
**Status:** Production Deployment Guide

---

## Overview

This guide provides step-by-step instructions for deploying the unified architecture to production.

---

## Prerequisites

- Production server access (SSH)
- Root or sudo access
- Python 3.8+ installed
- Systemd available
- Existing Argo services (for migration)

---

## Step 1: Backup Existing Data

```bash
# Create backup directory
BACKUP_DIR="/root/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup existing databases
cp /root/argo-production-green/data/signals.db "$BACKUP_DIR/signals_argo.db" 2>/dev/null || true
cp /root/argo-production-prop-firm/data/signals.db "$BACKUP_DIR/signals_prop_firm.db" 2>/dev/null || true
cp /root/argo-production/data/signals.db "$BACKUP_DIR/signals_legacy.db" 2>/dev/null || true
cp /root/argo-production-blue/data/signals.db "$BACKUP_DIR/signals_blue.db" 2>/dev/null || true

# Backup configurations
cp /root/argo-production-green/config.json "$BACKUP_DIR/config_argo.json" 2>/dev/null || true
cp /root/argo-production-prop-firm/config.json "$BACKUP_DIR/config_prop_firm.json" 2>/dev/null || true

echo "✅ Backups created in: $BACKUP_DIR"
```

---

## Step 2: Create Unified Directory Structure

```bash
# Create unified production directory
mkdir -p /root/argo-production-unified/{data,logs,argo}

# Set permissions
chmod 755 /root/argo-production-unified
chmod 755 /root/argo-production-unified/{data,logs,argo}
```

---

## Step 3: Deploy Code

```bash
# Clone or copy code to unified directory
# (Assuming code is in workspace)
cd /path/to/argo-alpine-workspace

# Copy argo code
rsync -av --exclude='__pycache__' --exclude='*.pyc' \
    argo/ /root/argo-production-unified/argo/

# Copy scripts
rsync -av scripts/ /root/argo-production-unified/scripts/
```

---

## Step 4: Run Database Migration

```bash
cd /root/argo-production-unified

# Run migration script
python3 scripts/migrate_to_unified_database.py

# Verify migration
sqlite3 /root/argo-production-unified/data/signals_unified.db \
    "SELECT COUNT(*) as total, COUNT(DISTINCT service_type) as services FROM signals;"
```

---

## Step 5: Create Configuration Files

### Unified Signal Generator Config

```bash
cat > /root/argo-production-unified/config.json << 'EOF'
{
  "signal_generation": {
    "enabled": true,
    "interval_seconds": 5,
    "symbols": ["AAPL", "NVDA", "TSLA", "MSFT", "BTC-USD", "ETH-USD"],
    "min_confidence": 60.0,
    "price_change_threshold": 0.001,
    "distribute_to": ["argo", "prop_firm"]
  },
  "database": {
    "path": "/root/argo-production-unified/data/signals_unified.db",
    "unified": true
  },
  "data_sources": {
    "weights": {
      "alpaca_pro": 0.40,
      "massive": 0.40,
      "yfinance": 0.25,
      "alpha_vantage": 0.25,
      "x_sentiment": 0.20,
      "sonar": 0.15
    }
  },
  "trading": {
    "auto_execute": false
  }
}
EOF
```

### Update Executor Configs

**Argo Executor:**
```bash
# Update /root/argo-production-green/config.json
# Add executor section if not present
```

**Prop Firm Executor:**
```bash
# Update /root/argo-production-prop-firm/config.json
# Ensure prop_firm.enabled = true
```

---

## Step 6: Create Systemd Services

### Signal Generator Service

```bash
cat > /etc/systemd/system/argo-signal-generator.service << 'EOF'
[Unit]
Description=Argo Unified Signal Generator
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-unified
Environment="ARGO_CONFIG_PATH=/root/argo-production-unified/config.json"
Environment="ARGO_24_7_MODE=true"
Environment="PYTHONPATH=/root/argo-production-unified/argo"
ExecStart=/usr/bin/python3 -m uvicorn argo.main:app --host 0.0.0.0 --port 7999
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### Argo Executor Service

```bash
cat > /etc/systemd/system/argo-trading-executor.service << 'EOF'
[Unit]
Description=Argo Trading Executor
After=network.target argo-signal-generator.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-green
Environment="EXECUTOR_ID=argo"
Environment="EXECUTOR_CONFIG_PATH=/root/argo-production-green/config.json"
Environment="PORT=8000"
Environment="PYTHONPATH=/root/argo-production-green/argo"
ExecStart=/usr/bin/python3 -m uvicorn argo.core.trading_executor:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### Prop Firm Executor Service

```bash
cat > /etc/systemd/system/argo-prop-firm-executor.service << 'EOF'
[Unit]
Description=Argo Prop Firm Trading Executor
After=network.target argo-signal-generator.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-prop-firm
Environment="EXECUTOR_ID=prop_firm"
Environment="EXECUTOR_CONFIG_PATH=/root/argo-production-prop-firm/config.json"
Environment="PORT=8001"
Environment="PYTHONPATH=/root/argo-production-prop-firm/argo"
ExecStart=/usr/bin/python3 -m uvicorn argo.core.trading_executor:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

---

## Step 7: Enable and Start Services

```bash
# Reload systemd
systemctl daemon-reload

# Enable services
systemctl enable argo-signal-generator.service
systemctl enable argo-trading-executor.service
systemctl enable argo-prop-firm-executor.service

# Start services in order
systemctl start argo-signal-generator.service
sleep 5
systemctl start argo-trading-executor.service
sleep 5
systemctl start argo-prop-firm-executor.service

# Check status
systemctl status argo-signal-generator.service
systemctl status argo-trading-executor.service
systemctl status argo-prop-firm-executor.service
```

---

## Step 8: Verify Deployment

### Check Service Health

```bash
# Signal generator
curl http://localhost:7999/health

# Argo executor
curl http://localhost:8000/health

# Prop Firm executor
curl http://localhost:8001/health
```

### Check Signal Generation

```bash
# Monitor logs
journalctl -u argo-signal-generator.service -f

# Check database
sqlite3 /root/argo-production-unified/data/signals_unified.db \
    "SELECT COUNT(*) FROM signals WHERE created_at >= datetime('now', '-5 minutes');"
```

### Check Signal Distribution

```bash
# Check executor logs
journalctl -u argo-trading-executor.service -f
journalctl -u argo-prop-firm-executor.service -f
```

---

## Step 9: Stop Old Services (After Verification)

```bash
# Stop old services (if running)
systemctl stop argo-trading.service 2>/dev/null || true
systemctl stop argo-trading-prop-firm.service 2>/dev/null || true

# Disable old services
systemctl disable argo-trading.service 2>/dev/null || true
systemctl disable argo-trading-prop-firm.service 2>/dev/null || true
```

---

## Step 10: Monitoring Setup

### Signal Rate Monitor

```bash
# Run monitor in background
nohup python3 /root/argo-production-unified/argo/argo/monitoring/signal_rate_monitor.py > /root/argo-production-unified/logs/monitor.log 2>&1 &
```

### Log Monitoring

```bash
# Watch all services
journalctl -u argo-signal-generator.service -u argo-trading-executor.service -u argo-prop-firm-executor.service -f
```

---

## Rollback Procedure

If issues occur:

```bash
# Stop new services
systemctl stop argo-signal-generator.service
systemctl stop argo-trading-executor.service
systemctl stop argo-prop-firm-executor.service

# Start old services
systemctl start argo-trading.service
systemctl start argo-trading-prop-firm.service

# Restore databases from backup
cp "$BACKUP_DIR/signals_argo.db" /root/argo-production-green/data/signals.db
cp "$BACKUP_DIR/signals_prop_firm.db" /root/argo-production-prop-firm/data/signals.db
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
journalctl -u argo-signal-generator.service -n 50

# Check permissions
ls -la /root/argo-production-unified/

# Check Python path
python3 -c "import sys; print(sys.path)"
```

### No Signals Generated

```bash
# Check service status
systemctl status argo-signal-generator.service

# Check database
sqlite3 /root/argo-production-unified/data/signals_unified.db "SELECT COUNT(*) FROM signals;"

# Check config
cat /root/argo-production-unified/config.json
```

### Executors Not Receiving Signals

```bash
# Check distributor logs
journalctl -u argo-signal-generator.service | grep -i distributor

# Check executor health
curl http://localhost:8000/health
curl http://localhost:8001/health

# Check network connectivity
curl http://localhost:7999/health
```

---

## Post-Deployment Checklist

- [ ] All services running
- [ ] Health checks passing
- [ ] Signals being generated
- [ ] Signals being distributed
- [ ] Trades being executed
- [ ] Monitoring active
- [ ] Logs being written
- [ ] Database accessible
- [ ] Old services stopped
- [ ] Backups verified

---

## Related Documentation

- [docs/UNIFIED_ARCHITECTURE_COMPLETE_GUIDE.md](../docs/UNIFIED_ARCHITECTURE_COMPLETE_GUIDE.md)
- [Rules/13_TRADING_OPERATIONS.md](../Rules/13_TRADING_OPERATIONS.md)

---

**Last Updated:** November 18, 2025  
**Version:** 3.0

