# Improvements Quick Start Guide

**All improvements have been implemented!** Here's how to use them:

---

## 🚀 Quick Setup

### 1. Install systemd Service (Recommended)
```bash
sudo ./scripts/install-systemd-service.sh
```

This provides:
- Automatic restart on failure
- Start on boot
- Process management
- Log management

### 2. Deploy Updated Code
```bash
./commands/deploy argo
```

The deployment script now:
- Cleans up duplicate processes automatically
- Verifies single instance per port
- Prevents deployment issues

### 3. Verify Health
```bash
# Check overall health
curl http://178.156.194.174:8000/api/v1/health | jq

# Check data source health
curl http://178.156.194.174:8000/api/v1/health | jq '.services.data_sources'
```

### 4. View Metrics
```bash
# Prometheus metrics
curl http://178.156.194.174:8000/metrics | grep argo_data_source

# Check specific metrics
curl http://178.156.194.174:8000/metrics | grep -E "argo_data_source_status|argo_data_source_success_rate"
```

---

## 📊 Grafana Dashboard

### Import Dashboard
1. Open Grafana (usually at `http://your-server:3000`)
2. Go to **Dashboards** > **Import**
3. Upload: `infrastructure/monitoring/grafana/dashboards/argo-trading-dashboard.json`
4. Select Prometheus datasource
5. Click **Import**

### Dashboard Features
- **Signals Generated** - Real-time signal generation rate
- **Data Source Health** - Status of all data sources
- **Signal Generation Duration** - P95/P99 latencies
- **Data Source Success Rate** - Success rates per source
- **API Request Rate** - API usage metrics
- **Active Positions** - Current trading positions
- **Data Source Errors** - Error tracking
- **System Resources** - CPU, Memory, Disk usage

---

## 🔍 Monitoring

### Health Check Endpoint
```bash
GET /api/v1/health
```

Returns:
- Overall system status
- Data source health summary
- System resource usage
- Service status

### Data Source Health
Each data source is monitored for:
- Success/failure rates
- Request latency
- Consecutive failures
- Error types

**Unhealthy Detection:**
- 5+ consecutive failures → Unhealthy
- No success in 5+ minutes → Degraded

---

## 🛠️ Configuration

### Config File Location
The system automatically detects the correct config file:
1. `/root/argo-production-green/config.json` (current)
2. `/root/argo-production-blue/config.json` (blue)
3. `/root/argo-production/config.json` (legacy)
4. Local `config.json` (development)

### API Key Resolution
Keys are resolved in this order:
1. AWS Secrets Manager
2. Environment variables
3. Config.json

**Exception:** Massive API prefers config.json (can override in code)

---

## 📝 Logging

### Structured Logging (Optional)
Enable JSON logging:
```python
from argo.core.enhanced_logging import setup_enhanced_logging
setup_enhanced_logging(use_json=True, level="INFO")
```

### Correlation IDs
All logs include request correlation IDs for tracing:
```python
from argo.core.enhanced_logging import set_request_id
request_id = set_request_id()
```

---

## 🔧 Service Management

### systemd Commands
```bash
# Status
sudo systemctl status argo-trading

# Restart
sudo systemctl restart argo-trading

# Stop
sudo systemctl stop argo-trading

# Start
sudo systemctl start argo-trading

# View logs
sudo journalctl -u argo-trading -f
```

---

## 📈 Key Metrics

### Data Source Metrics
- `argo_data_source_status` - Health (1=healthy, 0=unhealthy)
- `argo_data_source_success_rate` - Success rate (0-1)
- `argo_data_source_errors_total` - Error counts
- `argo_data_source_request_duration_seconds` - Latency

### Signal Metrics
- `argo_signals_generated_total` - Total signals
- `argo_signal_generation_duration_seconds` - Generation time
- `argo_signal_confidence` - Confidence levels

### System Metrics
- `argo_system_cpu_usage_percent` - CPU usage
- `argo_system_memory_usage_percent` - Memory usage
- `argo_system_disk_usage_percent` - Disk usage

---

## 🚨 Alerts (Recommended)

Set up alerts for:
- `argo_data_source_status == 0` - Unhealthy data source
- `argo_data_source_success_rate < 0.9` - Low success rate
- `rate(argo_data_source_errors_total[5m]) > 0.1` - High error rate
- `argo_system_cpu_usage_percent > 90` - High CPU
- `argo_system_memory_usage_percent > 90` - High memory

---

## ✅ Verification Checklist

- [ ] systemd service installed and running
- [ ] Health endpoint shows data source status
- [ ] Metrics endpoint returns data source metrics
- [ ] Grafana dashboard imported and working
- [ ] No duplicate processes running
- [ ] Config file detected correctly
- [ ] API keys resolving correctly

---

## 📚 Documentation

- **Full Details:** `docs/IMPROVEMENTS_IMPLEMENTATION_COMPLETE.md`
- **Original Suggestions:** `docs/IMPROVEMENT_SUGGESTIONS.md`
- **System Monitoring:** `docs/SystemDocs/SYSTEM_MONITORING_COMPLETE_GUIDE.md`

---

**Status:** ✅ All improvements implemented and ready for use!

