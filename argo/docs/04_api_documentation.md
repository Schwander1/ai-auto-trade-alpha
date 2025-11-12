# Argo API Documentation
**Generated:** Sun Nov  9 11:46:48 AM EST 2025

## 🔗 Endpoints

### GET /health
```json
{
  "status": "healthy",
  "version": "6.0",
  "ai_enabled": true
}
```

### GET /api/stats
```json
{
  "total_signals": 1247,
  "win_rate": 96.3,
  "avg_confidence": 94.7
}
```

### GET /api/signals/latest
Query Parameters:
- limit: int (default: 10)
- premium_only: bool (default: false)

Response: Array of signal objects
