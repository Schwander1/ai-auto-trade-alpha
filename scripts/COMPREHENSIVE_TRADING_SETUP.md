# Comprehensive Trading Setup - Both Argo and Prop Firm

**Date:** January 2025
**Status:** Setup Guide for Ensuring Both Systems Are Trading

---

## Current Status

### ✅ Working
- **Argo Executor:** Running on port 8000
- **Signal Generation:** Active and generating signals
- **Signal Database:** 2,267 signals in last 24 hours

### ⚠️ Needs Attention
- **Prop Firm Executor:** Not running on port 8001
- **24/7 Mode:** Needs to be enabled for continuous signal generation
- **Signal Execution:** Signals are being generated but not executed

---

## Quick Fix Commands

### 1. Start Prop Firm Executor

```bash
# Option 1: Using the script
cd /Users/dylanneuenschwander/argo-alpine-workspace
./scripts/start_prop_firm_executor.sh

# Option 2: Manual start
cd argo
export EXECUTOR_ID=prop_firm
export EXECUTOR_CONFIG_PATH=config.json
export PORT=8001
export PYTHONPATH=$(pwd)
export ARGO_24_7_MODE=true
python3 -m uvicorn argo.core.trading_executor:app --host 0.0.0.0 --port 8001
```

### 2. Enable 24/7 Mode

```bash
# Set environment variable before starting services
export ARGO_24_7_MODE=true

# Or add to your shell profile (~/.zshrc or ~/.bashrc)
echo 'export ARGO_24_7_MODE=true' >> ~/.zshrc
source ~/.zshrc
```

### 3. Verify Both Are Running

```bash
# Check Argo Executor
curl http://localhost:8000/api/v1/trading/status

# Check Prop Firm Executor
curl http://localhost:8001/api/v1/trading/status

# Run comprehensive check
python scripts/ensure_both_trading.py
```

---

## Configuration Requirements

### Signal Generation Service
- **Port:** 7999 (unified generator) or 8000 (legacy)
- **24/7 Mode:** Must be enabled for continuous generation
- **Auto-execute:** Should be enabled for automatic trading

### Argo Executor
- **Port:** 8000
- **Config:** `argo/config.json`
- **Min Confidence:** 75%
- **Auto-execute:** Enabled

### Prop Firm Executor
- **Port:** 8001
- **Config:** `argo/config.json` (with prop_firm section)
- **Min Confidence:** 82%
- **Auto-execute:** Enabled

---

## Troubleshooting

### Prop Firm Executor Won't Start

1. **Check if port 8001 is already in use:**
   ```bash
   lsof -i :8001
   ```

2. **Check logs:**
   ```bash
   tail -f /tmp/prop_firm_executor.log
   ```

3. **Verify config file exists:**
   ```bash
   ls -la argo/config.json
   ```

4. **Test import:**
   ```bash
   cd argo
   python3 -c "from argo.core.trading_executor import app; print('OK')"
   ```

### Signals Not Being Executed

1. **Check auto_execute setting:**
   - Verify `config.json` has `"auto_execute": true` in trading section
   - Check signal generation service logs

2. **Check market hours:**
   - If market is closed, ensure 24/7 mode is enabled
   - Crypto signals should work 24/7 regardless

3. **Check confidence thresholds:**
   - Argo: 75% minimum
   - Prop Firm: 82% minimum

4. **Check risk validation:**
   - Review executor logs for risk validation failures
   - Check position limits and daily loss limits

---

## Monitoring

### View Recent Signals
```bash
python scripts/show_recent_signals.py 20
```

### Check Service Status
```bash
python scripts/diagnose_and_fix_signal_generation.py
```

### Monitor Both Executors
```bash
python scripts/ensure_both_trading.py
```

---

## Next Steps

1. ✅ Start Prop Firm executor
2. ✅ Enable 24/7 mode
3. ✅ Verify both executors are receiving signals
4. ✅ Monitor signal execution
5. ✅ Check for any errors in logs

---

**Last Updated:** January 2025
