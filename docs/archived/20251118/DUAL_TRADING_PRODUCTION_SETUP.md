# Dual Trading Production Setup Guide

## Overview

This guide ensures both **Prop Firm** and **Argo** trading execute simultaneously on production.

## Architecture

The system runs **two separate service instances**:
1. **Argo Trading Service** (port 8000) - Standard trading with Argo account
2. **Prop Firm Trading Service** (port 8001) - Prop firm trading with stricter rules

Both services:
- Share the same signal generation logic
- Use different Alpaca accounts
- Apply different risk management rules
- Execute trades independently

## Configuration

### 1. Argo Trading Config (`/root/argo-production-green/config.json`)

```json
{
  "trading": {
    "auto_execute": true,
    "force_24_7_mode": true,
    "min_confidence": 75.0,
    "position_size_pct": 10
  },
  "prop_firm": {
    "enabled": false
  },
  "alpaca": {
    "api_key": "YOUR_ARGO_API_KEY",
    "secret_key": "YOUR_ARGO_SECRET_KEY",
    "paper": true
  }
}
```

### 2. Prop Firm Trading Config (`/root/argo-production-prop-firm/config.json`)

```json
{
  "trading": {
    "auto_execute": true,
    "force_24_7_mode": true,
    "min_confidence": 75.0
  },
  "prop_firm": {
    "enabled": true,
    "account": "prop_firm_test",
    "risk_limits": {
      "max_drawdown_pct": 2.0,
      "daily_loss_limit_pct": 4.5,
      "max_position_size_pct": 3.0,
      "min_confidence": 82.0,
      "max_positions": 3,
      "max_stop_loss_pct": 1.5
    },
    "monitoring": {
      "enabled": true,
      "check_interval_seconds": 5,
      "alert_on_warning": true,
      "auto_shutdown": true
    }
  },
  "alpaca": {
    "prop_firm_test": {
      "api_key": "YOUR_PROP_FIRM_API_KEY",
      "secret_key": "YOUR_PROP_FIRM_SECRET_KEY",
      "account_name": "Prop Firm Test Account",
      "paper": true
    }
  }
}
```

## Setup Steps

### Step 1: Run Configuration Script

```bash
./enable_dual_trading_production.sh
```

This script:
- ✅ Enables `auto_execute` for both configs
- ✅ Enables `force_24_7_mode` for both configs
- ✅ Enables prop firm mode in prop firm config
- ✅ Disables prop firm mode in Argo config
- ✅ Sets up risk limits for prop firm

### Step 2: Add Alpaca Credentials

Edit both config files and add your Alpaca API credentials:

**Argo Config:**
```json
"alpaca": {
  "api_key": "YOUR_ARGO_API_KEY",
  "secret_key": "YOUR_ARGO_SECRET_KEY"
}
```

**Prop Firm Config:**
```json
"alpaca": {
  "prop_firm_test": {
    "api_key": "YOUR_PROP_FIRM_API_KEY",
    "secret_key": "YOUR_PROP_FIRM_SECRET_KEY"
  }
}
```

### Step 3: Start Services

#### Option A: Manual Start

**Argo Service (port 8000):**
```bash
cd /root/argo-production-green
export ARGO_CONFIG_PATH=/root/argo-production-green/config.json
export ARGO_24_7_MODE=true
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

**Prop Firm Service (port 8001):**
```bash
cd /root/argo-production-prop-firm
export ARGO_CONFIG_PATH=/root/argo-production-prop-firm/config.json
export ARGO_24_7_MODE=true
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 1
```

#### Option B: Systemd Services

Create systemd service files (see below) and start:

```bash
systemctl start argo-trading.service
systemctl start argo-trading-prop-firm.service
systemctl enable argo-trading.service
systemctl enable argo-trading-prop-firm.service
```

### Step 4: Verify Services

```bash
# Check Argo service
curl http://localhost:8000/health | python3 -m json.tool

# Check Prop Firm service
curl http://localhost:8001/health | python3 -m json.tool

# Check trading status
curl http://localhost:8000/api/v1/trading/status | python3 -m json.tool
curl http://localhost:8001/api/v1/trading/status | python3 -m json.tool
```

## Systemd Service Files

### `/etc/systemd/system/argo-trading.service`

```ini
[Unit]
Description=Argo Trading Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-green
Environment="ARGO_CONFIG_PATH=/root/argo-production-green/config.json"
Environment="ARGO_24_7_MODE=true"
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/argo-trading-prop-firm.service`

```ini
[Unit]
Description=Argo Prop Firm Trading Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/argo-production-prop-firm
Environment="ARGO_CONFIG_PATH=/root/argo-production-prop-firm/config.json"
Environment="ARGO_24_7_MODE=true"
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --workers 1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Verification

### Check Both Services Are Running

```bash
# Check processes
ps aux | grep uvicorn

# Check ports
netstat -tlnp | grep -E "8000|8001"

# Check health
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Monitor Logs

```bash
# Argo service logs
tail -f /root/argo-production-green/logs/service_*.log

# Prop Firm service logs
tail -f /root/argo-production-prop-firm/logs/service_*.log

# Watch for trade execution
tail -f /root/argo-production-*/logs/service_*.log | grep -E "Trade executed|order_id"
```

### Verify Trading Execution

```bash
# Check Argo trading status
curl http://localhost:8000/api/v1/trading/status | python3 -m json.tool

# Check Prop Firm trading status
curl http://localhost:8001/api/v1/trading/status | python3 -m json.tool

# Check recent signals
curl http://localhost:8000/api/signals/latest?limit=5 | python3 -m json.tool
curl http://localhost:8001/api/signals/latest?limit=5 | python3 -m json.tool
```

## Key Differences

| Feature | Argo Trading | Prop Firm Trading |
|---------|-------------|-------------------|
| **Port** | 8000 | 8001 |
| **Config Path** | `/root/argo-production-green/config.json` | `/root/argo-production-prop-firm/config.json` |
| **Prop Firm Mode** | Disabled | Enabled |
| **Min Confidence** | 75% | 82% |
| **Max Positions** | 5 | 3 |
| **Position Size** | 10% | 3% |
| **Max Drawdown** | 20% | 2% |
| **Daily Loss Limit** | 5% | 4.5% |
| **Account** | Standard Argo account | Prop firm test account |

## Troubleshooting

### Service Not Starting

1. Check config files exist and are valid JSON
2. Check Alpaca credentials are set
3. Check ports 8000 and 8001 are available
4. Check logs for errors

### Trades Not Executing

1. Verify `auto_execute: true` in both configs
2. Check `force_24_7_mode: true` is set
3. Verify Alpaca accounts are connected
4. Check risk validation logs
5. Verify signals meet confidence thresholds

### Prop Firm Trades Blocked

1. Check prop firm risk limits are not exceeded
2. Verify position count < max_positions (3)
3. Check confidence >= 82%
4. Verify daily loss limit not exceeded
5. Check drawdown < 2%

## Maintenance

### Restart Services

```bash
# Restart both services
systemctl restart argo-trading.service
systemctl restart argo-trading-prop-firm.service

# Or manually
pkill -f "uvicorn.*main:app"
# Then start both services again
```

### Update Configuration

1. Edit config files
2. Restart services to load new config
3. Verify changes with health checks

### Monitor Performance

- Check both services' health endpoints regularly
- Monitor trade execution logs
- Track portfolio performance for both accounts
- Review risk metrics for prop firm account

## Summary

✅ **Both services configured and enabled**
✅ **Auto-execute enabled for both**
✅ **24/7 mode enabled for both**
✅ **Separate Alpaca accounts configured**
✅ **Different risk limits applied**
✅ **Services run independently on different ports**

Both trading modes will execute trades simultaneously when signals meet their respective criteria.

