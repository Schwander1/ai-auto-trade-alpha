# Monitoring & Observability Rules

**Last Updated:** January 15, 2025  
**Version:** 3.0  
**Applies To:** All projects

---

## Overview

Monitoring, logging, metrics, and observability rules to ensure system health, performance tracking, and early issue detection.

---

## Health Checks

### Unified Health Check System

**Component:** `argo/scripts/health_check_unified.py`

#### Health Check Levels

**Level 1: Basic (4-6 checks)**
- Environment detection
- Trading engine connection
- Signal generation service
- Configuration loading

**Level 2: Standard (8-12 checks)**
- All Level 1 checks
- Risk management validation
- Position monitoring
- Order management
- Data source connectivity

**Level 3: Comprehensive (15-20 checks)**
- All Level 2 checks
- End-to-end integration
- Performance metrics
- Security validation
- Complete system test

#### Usage

```bash
# Basic health check
python argo/scripts/health_check_unified.py --level 1

# Standard health check
python argo/scripts/health_check_unified.py --level 2

# Comprehensive health check
python argo/scripts/health_check_unified.py --level 3
```

---

## Logging Standards

### Structured Logging

**Rule:** Use structured logging with context

**Python Example:**
```python
import logging

logger = logging.getLogger(__name__)

logger.info(
    "Signal generated",
    extra={
        "signal_id": signal.id,
        "symbol": signal.symbol,
        "confidence": signal.confidence,
        "event": "signal_generated"
    }
)
```

### Log Levels

**DEBUG:** Detailed information for debugging
- **Use For:** Development, troubleshooting
- **Production:** Disabled or minimal

**INFO:** General informational messages
- **Use For:** Normal operations, important events
- **Production:** Enabled

**WARNING:** Warning messages
- **Use For:** Recoverable issues, deprecations
- **Production:** Enabled

**ERROR:** Error messages
- **Use For:** Errors that don't stop execution
- **Production:** Enabled

**CRITICAL:** Critical errors
- **Use For:** System failures, data loss risks
- **Production:** Enabled, alerts triggered

### PII Redaction

**Rule:** Never log sensitive data

**Never Log:**
- Passwords
- API keys
- Credit card numbers
- Personal information
- JWT tokens (full tokens)

**Redaction Pattern:**
```python
def redact_sensitive_data(data: str) -> str:
    # Redact API keys
    data = re.sub(r'api[_-]?key["\s:=]+([a-zA-Z0-9_-]{20,})', r'api_key=***REDACTED***', data, flags=re.IGNORECASE)
    # Redact passwords
    data = re.sub(r'password["\s:=]+([^\s"]+)', r'password=***REDACTED***', data, flags=re.IGNORECASE)
    return data
```

### Request/Response Logging

**Rule:** Log all API requests/responses with PII redaction

**Include:**
- Request ID (for correlation)
- Endpoint
- Method
- Status code
- Response time
- Error messages (redacted)

**Exclude:**
- Request/response bodies with PII
- Full authentication tokens
- Sensitive headers

---

## Metrics & Observability

### Prometheus Metrics

**Component:** `alpine-backend/backend/core/metrics.py`

#### Metrics Tracked

**HTTP Metrics:**
- Request counts (by method, endpoint, status code)
- Request duration (histogram)
- Error counts (by status code, endpoint)

**Business Metrics:**
- Signal generation rate
- Trade execution rate
- User count
- Subscription count

**System Metrics:**
- Database query duration
- Cache hits/misses
- Rate limit violations
- API latency

#### Metrics Endpoint

**Location:** `/metrics`

**Format:** Prometheus exposition format

**Access:** Public endpoint (no authentication required)

---

## Monitoring Frequency

### Real-Time (Continuous)
- Signal generation
- Order execution
- Position monitoring
- Error rates

### Every 5 Minutes
- Component health checks
- Data source status
- Risk limit status
- API connectivity

### Every Hour
- System performance metrics
- Integration checks
- Security validation
- Database health

### Daily
- Complete health check (Level 3)
- System audit
- Performance review
- Log analysis

---

## Alerting

### Multi-Channel Alerting System

**Component:** `argo/argo/core/alerting.py` (Argo), `backend/core/alerting.py` (Alpine)

**Rule:** Use the centralized alerting service for all critical alerts

**Channels:**
- **PagerDuty:** Critical alerts only (automatic incident creation)
- **Slack:** All alerts (rich formatting, color-coded)
- **Email:** All alerts (HTML and plain text)
- **Notion:** All alerts (automatic logging to Command Center)

**Usage (Argo):**
```python
from argo.core.alerting import get_alerting_service

alerting = get_alerting_service()
alerting.send_alert(
    title="Alert Title",
    message="Alert message",
    severity="critical",  # or "warning", "info"
    details={"key": "value"},
    source="component-name"
)
```

**Usage (Alpine - Security Events):**
```python
from backend.core.alerting import send_security_alert

send_security_alert(
    event_type="failed_login",
    message="Multiple failed login attempts",
    identifier=email,
    details={"email": email, "ip_address": ip_address}
)
```

**Configuration:**
- Set environment variables for each channel
- AWS Secrets Manager integration for credentials
- Automatic failover if channel unavailable
- Threshold-based alerting (prevents alert fatigue)

**Severity Levels:**
- **critical:** Sent to all channels including PagerDuty
- **warning:** Sent to Slack, Email, Notion
- **info:** Sent to Slack, Email, Notion

**Security Event Alerting:**
- **Automatic:** Integrated with security logging
- **Thresholds:** Configurable per event type
- **Events:** Failed logins, rate limit abuse, CSRF violations, unauthorized access, account lockouts
- **Configuration:** `SECURITY_ALERTS_ENABLED`, `PAGERDUTY_ENABLED`, `SLACK_ENABLED`, `EMAIL_ALERTS_ENABLED`

**Best Practices:**
- Always include relevant details in alert
- Use appropriate severity level
- Test alerting channels regularly
- Monitor alert delivery success rates
- Configure thresholds to prevent alert fatigue

### Critical Alerts

**Immediate Notification:**
- Trading engine connection failure
- Account blocked
- Daily loss limit exceeded
- Max drawdown exceeded
- System downtime
- Data loss risk

### Warning Alerts

**Notification within 1 hour:**
- High error rate
- Slow API response
- Data source failures
- Low signal quality
- High latency

### Info Alerts

**Daily Summary:**
- System status
- Performance metrics
- Usage statistics

---

## Log Management

### Log Retention

**Development:**
- **Retention:** 7 days
- **Storage:** Local files
- **Rotation:** Daily

**Production:**
- **Retention:** 30 days
- **Storage:** Centralized logging (if available)
- **Rotation:** Daily
- **Archive:** Compressed archives after 7 days

### Log Locations

**Argo Logs:**
- Local: `argo/logs/*.log`
- Production: `/tmp/argo.log` or configured path

**Alpine Backend Logs:**
- Local: `alpine-backend/logs/*.log`
- Production: Configured log path

### Log Rotation

**Rule:** Rotate logs daily
- **Format:** `app.log.YYYY-MM-DD`
- **Compression:** Compress after 7 days
- **Cleanup:** Delete after retention period

---

## Performance Monitoring

### Key Metrics to Monitor

**Signal Generation:**
- Signals generated per hour
- Average confidence
- Signal quality (win rate)
- Generation latency

**Trading Performance:**
- Total P&L
- Win rate
- Sharpe ratio
- Max drawdown
- Average trade duration

**System Health:**
- API response times
- Error rates
- Data source availability
- Database connectivity
- Memory usage
- CPU usage

**Risk Management:**
- Daily loss limit status
- Drawdown percentage
- Position count
- Correlation limits
- Risk limit triggers

---

## Monitoring Tools

### Health Checks

**Scripts:**
- `argo/scripts/health_check_unified.py` - Unified health check
- `scripts/local_health_check.sh` - Local health check
- `scripts/full-health-check.sh` - Production health check

### Log Monitoring

**Commands:**
```bash
# Tail logs
tail -f argo/logs/*.log

# Search logs
grep "ERROR" argo/logs/*.log

# Count errors
grep -c "ERROR" argo/logs/*.log
```

### Metrics Access

**Prometheus:**
- Endpoint: `http://localhost:8000/metrics` (Alpine backend)
- Format: Prometheus exposition format
- Tools: Prometheus, Grafana

---

## Distributed Tracing

### Tracing Overview

**Rule:** Implement distributed tracing for request flow across services

**Purpose:**
- Track requests across service boundaries
- Identify performance bottlenecks
- Debug complex issues
- Understand service dependencies

### OpenTelemetry Integration

**Rule:** Use OpenTelemetry for tracing

**Implementation:**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Add span processor
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Use in code
def process_signal(signal):
    with tracer.start_as_current_span("process_signal") as span:
        span.set_attribute("signal.id", signal.id)
        span.set_attribute("signal.symbol", signal.symbol)
        # Process signal
        return result
```

### Trace Context Propagation

**Rule:** Propagate trace context across services

**Implementation:**
```python
from opentelemetry.propagate import inject, extract
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

# Inject trace context into HTTP headers
headers = {}
inject(headers)

# Extract trace context from HTTP headers
context = extract(headers)
```

### Span Attributes

**Rule:** Add relevant attributes to spans

**Standard Attributes:**
- Request ID
- User ID (if applicable)
- Service name
- Operation name
- Error information (if error)
- Performance metrics

**Example:**
```python
with tracer.start_as_current_span("execute_trade") as span:
    span.set_attribute("trade.symbol", signal.symbol)
    span.set_attribute("trade.confidence", signal.confidence)
    span.set_attribute("trade.amount", trade_amount)
    
    try:
        result = execute_trade(signal)
        span.set_attribute("trade.status", "success")
    except Exception as e:
        span.set_attribute("trade.status", "failed")
        span.set_attribute("error.message", str(e))
        span.record_exception(e)
        raise
```

---

## Structured Logging Standards

### Log Format

**Rule:** Use consistent structured log format

**Format:** JSON for production, human-readable for development

**JSON Format:**
```json
{
  "timestamp": "2025-01-15T10:30:00.123Z",
  "level": "INFO",
  "service": "argo-signal-service",
  "message": "Signal generated",
  "trace_id": "abc123def456",
  "span_id": "xyz789",
  "request_id": "req-123",
  "user_id": "user-456",
  "context": {
    "signal_id": "sig-789",
    "symbol": "AAPL",
    "confidence": 85.5
  }
}
```

### Correlation IDs

**Rule:** Use correlation IDs for request tracing

**IDs to Include:**
- **Trace ID:** Unique ID for entire request flow
- **Span ID:** Unique ID for current operation
- **Request ID:** Unique ID for HTTP request
- **User ID:** User making request (if applicable)

**Implementation:**
```python
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar('request_id', default=None)
trace_id_var: ContextVar[str] = ContextVar('trace_id', default=None)

def get_request_id() -> str:
    request_id = request_id_var.get()
    if not request_id:
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
    return request_id
```

### Log Aggregation

**Rule:** Use centralized log aggregation

**Tools:**
- **Development:** Local files
- **Production:** ELK Stack, Datadog, CloudWatch, etc.

**Benefits:**
- Centralized search
- Correlation across services
- Better analysis
- Alerting capabilities

---

## Best Practices

### DO
- ✅ Use structured logging with context
- ✅ Redact all PII before logging
- ✅ Include request IDs for correlation
- ✅ Monitor key metrics continuously
- ✅ Set up alerts for critical issues
- ✅ Rotate logs regularly
- ✅ Review logs daily
- ✅ Track performance metrics

### DON'T
- ❌ Log sensitive data
- ❌ Use unstructured log messages
- ❌ Ignore error logs
- ❌ Skip health checks
- ❌ Store logs indefinitely
- ❌ Log at DEBUG level in production
- ❌ Ignore performance degradation

---

## Related Rules

- [12_BACKEND.md](12_BACKEND.md) - Backend logging practices
- [13_TRADING_OPERATIONS.md](13_TRADING_OPERATIONS.md) - Trading monitoring
- [07_SECURITY.md](07_SECURITY.md) - Security logging

