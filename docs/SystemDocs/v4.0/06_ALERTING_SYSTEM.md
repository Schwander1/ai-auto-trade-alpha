# Multi-Channel Alerting System Guide

**Date:** January 15, 2025  
**Version:** 4.0  
**Status:** ✅ Complete

---

## Executive Summary

The Multi-Channel Alerting System provides comprehensive alerting capabilities for critical system events. It supports multiple channels (PagerDuty, Slack, Email, Notion) with automatic failover and rich formatting.

---

## Overview

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Alerting Service (Core)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │  AlertingService                                  │   │
│  │  - Channel Management                             │   │
│  │  - Severity Routing                               │   │
│  │  - Format Conversion                              │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│         ┌────────────────┼────────────────┐             │
│         │                │                │             │
│         ▼                ▼                ▼             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│  │PagerDuty │    │  Slack   │    │  Email   │         │
│  │(Critical)│    │  (All)   │    │  (All)   │         │
│  └──────────┘    └──────────┘    └──────────┘         │
│         │                │                │             │
│         └────────────────┼────────────────┘             │
│                          │                               │
│                          ▼                               │
│                   ┌──────────┐                          │
│                   │  Notion  │                          │
│                   │  (All)   │                          │
│                   └──────────┘                          │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

```bash
# PagerDuty
PAGERDUTY_ENABLED=true
PAGERDUTY_INTEGRATION_KEY=your-integration-key

# Slack
SLACK_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email
EMAIL_ALERTS_ENABLED=true
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your-email@example.com
EMAIL_SMTP_PASSWORD=your-app-password
EMAIL_FROM=alerts@argocapital.com
EMAIL_TO=ops@argocapital.com,oncall@argocapital.com

# Notion
NOTION_ALERTS_ENABLED=true
```

### AWS Secrets Manager

The system automatically loads credentials from AWS Secrets Manager if available:

- `pagerduty-integration-key`
- `slack-webhook-url`
- `email-smtp-user`
- `email-smtp-password`

---

## Usage

### Basic Usage

```python
from argo.core.alerting import get_alerting_service

alerting = get_alerting_service()

alerting.send_alert(
    title="Signal Integrity Verification Failure",
    message="5 out of 1000 signals failed integrity verification",
    severity="critical",
    details={
        "total_checked": 1000,
        "failed_count": 5,
        "success_rate": "99.5%"
    },
    source="argo-integrity-monitor"
)
```

### Severity Levels

- **critical** - Sent to all channels including PagerDuty
- **warning** - Sent to Slack, Email, Notion
- **info** - Sent to Slack, Email, Notion

---

## Channel Details

### PagerDuty

**When:** Critical alerts only  
**Format:** PagerDuty Events API v2  
**Features:**
- Automatic incident creation
- On-call escalation
- Incident tracking

**Configuration:**
1. Create PagerDuty service
2. Get integration key
3. Set `PAGERDUTY_INTEGRATION_KEY` environment variable

### Slack

**When:** All alerts  
**Format:** Rich Slack message format  
**Features:**
- Color-coded by severity
- Rich formatting
- Field attachments

**Configuration:**
1. Create Slack webhook
2. Set `SLACK_WEBHOOK_URL` environment variable

### Email

**When:** All alerts  
**Format:** HTML and plain text  
**Features:**
- HTML formatting
- Multiple recipients
- SMTP authentication

**Configuration:**
1. Configure SMTP settings
2. Set email environment variables
3. Use app passwords for Gmail

### Notion

**When:** All alerts  
**Format:** Notion Command Center integration  
**Features:**
- Automatic logging
- Searchable history
- Team collaboration

**Configuration:**
1. Set up Notion integration
2. Configure `NOTION_API_KEY`
3. Enable `NOTION_ALERTS_ENABLED`

---

## Integration Examples

### Integrity Monitor

```python
# argo/argo/compliance/integrity_monitor.py
from argo.core.alerting import get_alerting_service

def _trigger_alert(self, results: Dict):
    alerting = get_alerting_service()
    
    alerting.send_alert(
        title="Signal Integrity Verification Failure",
        message=f"{results['failed']} out of {results['checked']} signals failed",
        severity="critical",
        details={
            "total_checked": results['checked'],
            "failed_count": results['failed'],
            "success_rate": f"{((results['checked'] - results['failed']) / results['checked'] * 100):.2f}%"
        },
        source="argo-integrity-monitor"
    )
```

---

## Best Practices

1. **Use Appropriate Severity**
   - Critical: System failures, data corruption
   - Warning: Performance degradation, high error rates
   - Info: Status updates, routine notifications

2. **Include Context**
   - Always include relevant details
   - Provide actionable information
   - Include timestamps and identifiers

3. **Test Alerting**
   - Test each channel separately
   - Verify alert formatting
   - Confirm delivery

4. **Monitor Alerting**
   - Track alert volume
   - Monitor delivery success rates
   - Review alert effectiveness

---

## Troubleshooting

### Alerts Not Sending

1. Check environment variables are set
2. Verify AWS Secrets Manager access
3. Check network connectivity
4. Review logs for errors

### PagerDuty Not Working

1. Verify integration key is correct
2. Check PagerDuty service is active
3. Verify API endpoint is accessible

### Email Not Sending

1. Verify SMTP credentials
2. Check firewall rules
3. Use app passwords for Gmail
4. Verify recipient addresses

### Slack Not Working

1. Verify webhook URL is correct
2. Check webhook is not revoked
3. Verify Slack workspace access

---

## Performance

- **Alert Delivery Time:** <10 seconds
- **Concurrent Alerts:** Supports multiple simultaneous alerts
- **Retry Logic:** Automatic retry on failure
- **Rate Limiting:** Built-in rate limiting per channel

---

## Security

- Credentials stored in AWS Secrets Manager
- Environment variable fallback
- No credentials in code
- Encrypted transmission (HTTPS/SMTP TLS)

---

**Related Documentation:**
- `04_SYSTEM_MONITORING_COMPLETE_GUIDE.md` - Monitoring overview
- `01_COMPLETE_SYSTEM_ARCHITECTURE.md` - System architecture

