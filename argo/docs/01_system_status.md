# Argo Trading Engine - System Status
**Generated:** Sun Nov  9 11:46:44 AM EST 2025
**Confidential & Proprietary**
**Owner:** Alpine Analytics LLC

## ⚡ Real-Time Health Check
```json
{
    "status": "healthy",
    "version": "6.0",
    "timestamp": "2025-11-09T16:46:44.716878Z",
    "uptime": "100%",
    "ai_enabled": true,
    "performance_tracking": true
}
```

## 📊 Trading Statistics
```json
{
    "total_signals": 1247,
    "win_rate": 96.3,
    "avg_confidence": 94.7,
    "premium_count": 623,
    "standard_count": 624
}
```

## 🐳 Container Status
```
NAME                         IMAGE                      COMMAND                  SERVICE    CREATED          STATUS                    PORTS
argo-production-argo-api-1   argo-production-argo-api   "uvicorn argo.api.se…"   argo-api   50 minutes ago   Up 50 minutes (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
argo-production-redis-1      redis:7-alpine             "docker-entrypoint.s…"   redis      50 minutes ago   Up 50 minutes             0.0.0.0:6380->6379/tcp, [::]:6380->6379/tcp
```

## 💻 System Resources
```
CPU Usage:  0.0%
Memory:     2.9Gi/30Gi
Disk:       35G/150G (24% used)
Uptime:     up 5 days, 9 hours, 33 minutes
```

## 📦 Container Resources
```
NAME                         CPU %     MEM USAGE / LIMIT    NET I/O
argo-production-argo-api-1   0.13%     41.8MiB / 30.6GiB    280kB / 209kB
argo-production-redis-1      0.39%     3.242MiB / 30.6GiB   1.74kB / 126B
```

## ✅ Service Availability
- API Endpoint: 200 (200 = OK)
- Redis: PONG
- AI Status: ACTIVE
