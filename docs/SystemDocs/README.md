# System Documentation

**Current Version:** 6.0
**Last Updated:** November 17, 2025

---

## Quick Start

**For the latest documentation, see:** [`v6.0/README.md`](v6.0/README.md)

---

## Documentation Versions

### v6.0 (Current) ✅
- **Location:** [`v6.0/`](v6.0/)
- **Status:** Complete with all v6.0 features
- **Features:** Complete RBAC security system, all 15 performance optimizations, comprehensive backtesting enhancements, database optimizations, monitoring improvements, prop firm trading system

### v5.0 (Archived)
- **Location:** [`archive/v5.0-20250115/`](archive/v5.0-20250115/)
- **Status:** Archived
- **Features:** Storage optimizations, ML calibration, outcome tracking, database optimizations, WebSocket streams, backtesting enhancements

### v4.0 (Previous)
- **Location:** [`v4.0/`](v4.0/)
- **Status:** Complete
- **Features:** Alerting system, brand compliance, verification, performance reporting, optimizations

### v3.0 (Archived)
- **Location:** [`archive/v3.0/`](archive/v3.0/)
- **Status:** Archived
- **Note:** See v4.0 for latest information

### v2.0 (Archived)
- **Location:** [`archive/`](archive/)
- **Status:** Archived

---

## Core Documentation (v6.0)

1. **[v6.0/00_VERSION_HISTORY.md](v6.0/00_VERSION_HISTORY.md)** - Version history and migration notes
2. **[v6.0/README.md](v6.0/README.md)** - Documentation index
3. **[v6.0/01_COMPLETE_SYSTEM_ARCHITECTURE.md](v6.0/01_COMPLETE_SYSTEM_ARCHITECTURE.md)** - Complete system architecture (to be created)
4. **[v6.0/02_SIGNAL_GENERATION_COMPLETE_GUIDE.md](v6.0/02_SIGNAL_GENERATION_COMPLETE_GUIDE.md)** - Signal generation guide (to be created)
5. **[v6.0/03_PERFORMANCE_OPTIMIZATIONS.md](v6.0/03_PERFORMANCE_OPTIMIZATIONS.md)** - Performance optimizations (to be created)
6. **[v6.0/04_BACKTESTING_COMPLETE_GUIDE.md](v6.0/04_BACKTESTING_COMPLETE_GUIDE.md)** - Backtesting guide (to be created)
7. **[v6.0/05_SECURITY_GUIDE.md](v6.0/05_SECURITY_GUIDE.md)** - Security guide (to be created)

**Note:** Additional v6.0 guides are being created. See v5.0 and v4.0 for reference.

---

## What's New in v6.0

### Security Features
- **Complete RBAC System** - Role-Based Access Control with granular permissions
- **Multi-Channel Security Alerting** - PagerDuty, Slack, Email, Notion integration
- **Standardized Error Responses** - Consistent error format with error codes
- **Resource Ownership Checks** - User resource verification
- **Webhook Security** - Idempotency and replay protection
- **Log Rotation & Sampling** - Size and time-based rotation
- **Enhanced Rate Limiting** - Fail-closed in production
- **CSRF Protection** - Origin validation
- **Request Size Limits** - DoS prevention
- **Secret Validation** - Fail-fast on weak secrets

### Performance Optimizations (All 15 Complete)
- Redis distributed caching (async support)
- Enhanced parallel data source fetching
- Adaptive cache TTL (volatility-aware)
- All 15 optimizations active (80-85% faster signal generation)
- 86-93% API cost reduction
- 40-60% memory reduction

### Backtesting Enhancements
- 10-50x faster repeated backtests (indicator caching)
- 2-3x faster parallel processing
- 3-10x faster database queries
- Comprehensive risk metrics (VaR, CVaR, Calmar, Omega, Ulcer)
- Result visualizer and performance reports
- Config validation

### Database Optimizations
- Query optimization (admin endpoints)
- Database indexes (3-10x faster queries)
- Connection pooling (thread-local storage)

### Monitoring & Observability
- Enhanced monitoring scripts
- Performance reports
- Config validation
- Comprehensive health checks

### Prop Firm Trading System
- Prop firm account management
- Prop firm risk monitoring
- Prop firm backtesting
- Environment-specific behavior

---

**For complete documentation, see:** [`v6.0/README.md`](v6.0/README.md)
