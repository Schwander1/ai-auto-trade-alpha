"""Security event alerting service"""
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from backend.core.config import settings

logger = logging.getLogger(__name__)

# Alert thresholds
ALERT_THRESHOLDS = {
    "failed_login": {"count": 5, "window": 300},  # 5 failed logins in 5 minutes
    "rate_limit": {"count": 10, "window": 60},  # 10 rate limit violations in 1 minute
    "csrf_violation": {"count": 3, "window": 60},  # 3 CSRF violations in 1 minute
    "unauthorized_access": {"count": 3, "window": 300},  # 3 unauthorized access attempts in 5 minutes
}

# Alert configuration
ALERT_CONFIG = {
    "enabled": os.getenv("SECURITY_ALERTS_ENABLED", "true").lower() == "true",
    "pagerduty_enabled": os.getenv("PAGERDUTY_ENABLED", "false").lower() == "true",
    "slack_enabled": os.getenv("SLACK_ENABLED", "false").lower() == "true",
    "email_enabled": os.getenv("EMAIL_ALERTS_ENABLED", "false").lower() == "true",
    "pagerduty_api_key": os.getenv("PAGERDUTY_API_KEY", ""),
    "slack_webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
    "alert_email": os.getenv("ALERT_EMAIL", ""),
}

# In-memory event tracking (in production, use Redis)
_event_tracking: Dict[str, list] = defaultdict(list)


def _should_alert(event_type: str, identifier: str) -> bool:
    """Check if alert should be triggered based on thresholds"""
    if not ALERT_CONFIG["enabled"]:
        return False
    
    threshold = ALERT_THRESHOLDS.get(event_type)
    if not threshold:
        return False
    
    key = f"{event_type}:{identifier}"
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=threshold["window"])
    
    # Filter events within window
    events = [e for e in _event_tracking[key] if e > window_start]
    _event_tracking[key] = events
    
    # Check if threshold exceeded
    if len(events) >= threshold["count"]:
        # Clear events to prevent duplicate alerts
        _event_tracking[key] = []
        return True
    
    return False


def _send_pagerduty_alert(event_type: str, message: str, details: Dict[str, Any]):
    """Send alert to PagerDuty"""
    if not ALERT_CONFIG["pagerduty_enabled"] or not ALERT_CONFIG["pagerduty_api_key"]:
        return
    
    try:
        import httpx
        severity = "critical" if event_type in ["account_locked", "unauthorized_access"] else "error"
        
        payload = {
            "routing_key": ALERT_CONFIG["pagerduty_api_key"],
            "event_action": "trigger",
            "payload": {
                "summary": f"Security Alert: {message}",
                "severity": severity,
                "source": "alpine-backend",
                "custom_details": details
            }
        }
        
        # In production, use async httpx
        # For now, just log
        logger.critical(f"PAGERDUTY ALERT: {message} - {details}")
    except Exception as e:
        logger.error(f"Failed to send PagerDuty alert: {e}")


def _send_slack_alert(event_type: str, message: str, details: Dict[str, Any]):
    """Send alert to Slack"""
    if not ALERT_CONFIG["slack_enabled"] or not ALERT_CONFIG["slack_webhook_url"]:
        return
    
    try:
        import httpx
        color = "danger" if event_type in ["account_locked", "unauthorized_access"] else "warning"
        
        payload = {
            "text": f"🚨 Security Alert: {message}",
            "attachments": [{
                "color": color,
                "fields": [
                    {"title": "Event Type", "value": event_type, "short": True},
                    {"title": "Time", "value": datetime.now(timezone.utc).isoformat(), "short": True},
                ],
                "footer": "Alpine Backend Security",
                "ts": int(datetime.now(timezone.utc).timestamp())
            }]
        }
        
        # Add details as fields
        for key, value in details.items():
            payload["attachments"][0]["fields"].append({
                "title": key.replace("_", " ").title(),
                "value": str(value),
                "short": True
            })
        
        # In production, use async httpx
        # For now, just log
        logger.critical(f"SLACK ALERT: {message} - {details}")
    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")


def _send_email_alert(event_type: str, message: str, details: Dict[str, Any]):
    """Send alert via email"""
    if not ALERT_CONFIG["email_enabled"] or not ALERT_CONFIG["alert_email"]:
        return
    
    try:
        # In production, use SendGrid or similar
        # For now, just log
        logger.critical(f"EMAIL ALERT to {ALERT_CONFIG['alert_email']}: {message} - {details}")
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}")


def send_security_alert(
    event_type: str,
    message: str,
    identifier: str,
    details: Optional[Dict[str, Any]] = None
):
    """
    Send security alert if threshold exceeded
    
    Args:
        event_type: Type of security event
        message: Alert message
        identifier: Unique identifier (email, IP, user_id)
        details: Additional alert details
    """
    if not ALERT_CONFIG["enabled"]:
        return
    
    # Track event
    _event_tracking[f"{event_type}:{identifier}"].append(datetime.now(timezone.utc))
    
    # Check if alert should be sent
    if not _should_alert(event_type, identifier):
        return
    
    # Prepare alert details
    alert_details = details or {}
    alert_details.update({
        "event_type": event_type,
        "identifier": identifier,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Send alerts via all configured channels
    _send_pagerduty_alert(event_type, message, alert_details)
    _send_slack_alert(event_type, message, alert_details)
    _send_email_alert(event_type, message, alert_details)
    
    logger.critical(f"SECURITY ALERT TRIGGERED: {event_type} - {message} - {alert_details}")

