# Production Deployment Guide 🚀

## Overview

Complete guide for deploying the Argo-Alpine trading system with all enhancements to production.

## Prerequisites

### System Requirements
- Python 3.11+
- 4GB+ RAM
- 10GB+ disk space
- Network access for API calls

### Required Packages
```bash
pip install numpy pandas dashscope zhipuai openai scikit-learn
```

### API Keys Configured
- ✅ GLM (Zhipu AI) API key
- ✅ DeepSeek API key
- ⏸️ Qwen API key (optional, when available)

## Pre-Deployment Checklist

- [x] All enhancements implemented
- [x] Configuration files updated
- [x] API keys configured
- [x] Dependencies installed
- [x] Health checks passing
- [x] Validation complete

## Deployment Methods

### Method 1: Direct Python Execution

**Start the service:**
```bash
cd /path/to/argo-alpine-workspace
PYTHONPATH=argo python3 -m argo.core.signal_generation_service
```

**Run in background:**
```bash
nohup PYTHONPATH=argo python3 -m argo.core.signal_generation_service > argo/logs/service.log 2>&1 &
```

**Stop the service:**
```bash
pkill -f signal_generation_service
```

### Method 2: Docker Deployment

**Build and run:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f
```

**Stop:**
```bash
docker-compose down
```

### Method 3: Systemd Service

**Create service file** `/etc/systemd/system/argo-signal.service`:
```ini
[Unit]
Description=Argo Signal Generation Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/argo-alpine-workspace
Environment="PYTHONPATH=/path/to/argo-alpine-workspace/argo"
ExecStart=/usr/bin/python3 -m argo.core.signal_generation_service
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable argo-signal
sudo systemctl start argo-signal
sudo systemctl status argo-signal
```

### Method 4: Using Deployment Script

```bash
./scripts/deploy_production.sh
```

## Configuration

### Environment Variables

Set these for production:

```bash
export PYTHONPATH=/path/to/argo-alpine-workspace/argo
export ARGO_CONFIG_PATH=/path/to/argo/config.json
export ARGO_LOG_LEVEL=INFO
```

### Config File

Ensure `argo/config.json` has:
- ✅ All API keys
- ✅ Feature flags enabled
- ✅ Enhancement settings
- ✅ Risk limits configured

## Monitoring

### Health Checks

**Run health check:**
```bash
./scripts/health_check.sh
```

**Check service status:**
```bash
# If using systemd
sudo systemctl status argo-signal

# If using Docker
docker-compose ps

# If running directly
ps aux | grep signal_generation_service
```

### Logs

**View logs:**
```bash
# Service logs
tail -f argo/logs/*.log

# Systemd logs
sudo journalctl -u argo-signal -f

# Docker logs
docker-compose logs -f
```

### Metrics

**Check baseline metrics:**
```bash
ls -lh argo/baselines/
cat argo/baselines/baseline_*.json
```

**View cost reports:**
```bash
PYTHONPATH=argo python3 -c "
from argo.core.data_sources.chinese_models_source import ChineseModelsDataSource
import json
with open('argo/config.json') as f:
    config = json.load(f)
chinese = config.get('chinese_models', {})
ds = ChineseModelsDataSource({
    'glm_api_key': chinese.get('glm', {}).get('api_key', ''),
    'glm_enabled': True,
    'baichuan_api_key': chinese.get('baichuan', {}).get('api_key', ''),
    'baichuan_enabled': True,
})
print(json.dumps(ds.get_cost_report(), indent=2))
"
```

## Performance Tuning

### Signal Generation Interval

Default: 5 seconds
- Adjust in `signal_generation_service.py`
- Balance between responsiveness and API costs

### Rate Limits

Configured in `config.json`:
- GLM: 30 requests/minute
- DeepSeek: 25 requests/minute
- Qwen: 20 requests/minute (when enabled)

### Caching

- Market hours: 120 seconds
- Off hours: 60 seconds
- Adjust in `config.json` → `chinese_models`

## Security

### API Key Management

**Production:**
- Use environment variables
- Use secrets manager (AWS Secrets Manager, etc.)
- Never commit keys to git

**Example:**
```bash
export GLM_API_KEY="your-key"
export DEEPSEEK_API_KEY="your-key"
```

### Network Security

- Configure firewall rules
- Use VPN if needed
- Monitor API access logs

## Troubleshooting

### Service Won't Start

1. Check Python version: `python3 --version`
2. Check dependencies: `pip list`
3. Check config: `cat argo/config.json | jq .`
4. Check logs: `tail -f argo/logs/*.log`

### API Errors

1. Verify API keys are correct
2. Check rate limits
3. Verify network connectivity
4. Check account credits (DeepSeek)

### Performance Issues

1. Check system resources: `htop`
2. Review cache hit rates
3. Adjust rate limits
4. Monitor API response times

## Backup & Recovery

### Backup Configuration

```bash
# Backup config
cp argo/config.json argo/config.json.backup

# Backup baselines
tar -czf baselines_backup.tar.gz argo/baselines/
```

### Recovery

```bash
# Restore config
cp argo/config.json.backup argo/config.json

# Restore baselines
tar -xzf baselines_backup.tar.gz
```

## Updates

### Updating the System

1. Backup current configuration
2. Pull latest code
3. Update dependencies: `pip install -r argo/requirements.txt`
4. Run health check
5. Restart service

### Adding Qwen (When Ready)

1. Get DashScope API key
2. Add to `config.json`:
   ```json
   "qwen": {
     "api_key": "YOUR_KEY",
     "enabled": true
   }
   ```
3. Restart service

## Support

### Logs Location
- `argo/logs/` - Application logs
- `argo/baselines/` - Metrics baselines
- `argo/reports/` - Validation reports

### Documentation
- `NEXT_STEPS_ACTION_PLAN.md` - Next steps
- `VALIDATION_COMPLETE_SUMMARY.md` - Validation results
- `FINAL_SYSTEM_STATUS.md` - System status

---

**Status**: ✅ Ready for Production Deployment

