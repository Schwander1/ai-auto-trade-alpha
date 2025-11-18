# 24/7 Signal Generation Configuration

## Overview

The signal generation service now supports 24/7 continuous operation, ensuring signals are generated regardless of:
- Cursor application state (open/closed)
- Computer sleep/wake state
- Development vs production environment

## How It Works

By default, the service runs in **development mode** which pauses signal generation when:
- Cursor application is not running
- Computer appears to be asleep

**24/7 mode** disables these checks, allowing continuous signal generation.

## Enabling 24/7 Mode

### Option 1: Environment Variable (Recommended)

Set the environment variable before starting the service:

```bash
export ARGO_24_7_MODE=true
```

Or inline:
```bash
ARGO_24_7_MODE=true python3 start_service.py
```

### Option 2: Config File

Add to your `config.json`:

```json
{
  "trading": {
    "force_24_7_mode": true,
    ...
  }
}
```

### Option 3: Automatic (FastAPI)

When running via `main.py` (FastAPI), 24/7 mode is **enabled by default** unless explicitly disabled:

```bash
# 24/7 mode enabled automatically
python3 -m uvicorn argo.main:app --host 0.0.0.0 --port 8000

# To disable 24/7 mode
ARGO_24_7_MODE=false python3 -m uvicorn argo.main:app --host 0.0.0.0 --port 8000
```

## Startup Scripts

The following startup scripts have been updated to enable 24/7 mode:

1. **`start_service.py`** - Sets `ARGO_24_7_MODE=true`
2. **`scripts/start_service.sh`** - Exports `ARGO_24_7_MODE=true`
3. **`argo/main.py`** - Enables 24/7 mode by default

## Verification

Check logs for confirmation:

```
INFO:SignalGenerationService:🚀 24/7 mode enabled: Signal generation will run continuously
```

If you see this instead:
```
INFO:SignalGenerationService:💡 Development mode: Trading will pause when Cursor is closed or computer is asleep
```

Then 24/7 mode is **not** enabled. Check your environment variable or config.

## Disabling 24/7 Mode

To disable 24/7 mode and return to development mode:

```bash
export ARGO_24_7_MODE=false
```

Or in config.json:
```json
{
  "trading": {
    "force_24_7_mode": false
  }
}
```

## Production Deployment

For production deployments, 24/7 mode should always be enabled. The service automatically detects production environment, but you can force it:

```bash
export ARGO_ENVIRONMENT=production
export ARGO_24_7_MODE=true
```

## Notes

- **Simulation Mode**: The trading engine may show "simulation mode" if Alpaca is not configured. This does **not** affect signal generation - signals will still be generated 24/7.
- **Signal Generation vs Trade Execution**: 24/7 mode affects signal generation. Trade execution depends on `auto_execute` and trading engine configuration.
- **Performance**: 24/7 mode has no performance impact - it simply disables pause checks.

## Troubleshooting

**Signals not generating:**
1. Check logs for "24/7 mode enabled" message
2. Verify `ARGO_24_7_MODE=true` is set
3. Check that service is running: `ps aux | grep signal_generation`
4. Review logs: `tail -f argo/logs/service_*.log`

**Service pausing unexpectedly:**
- Verify 24/7 mode is enabled (see verification above)
- Check for daily loss limits or other risk management pauses
- Review `_trading_paused` status in logs

