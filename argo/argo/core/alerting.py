#!/usr/bin/env python3
"""
Alerting System
Supports multiple alert channels: PagerDuty, Slack, Email, Notion
"""
import os
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from datetime import datetime
import requests
from urllib.parse import quote

logger = logging.getLogger(__name__)


class AlertingService:
    """Multi-channel alerting service for critical system events"""
    
    def __init__(self):
        self.pagerduty_enabled = os.getenv("PAGERDUTY_ENABLED", "false").lower() == "true"
        self.pagerduty_integration_key = os.getenv("PAGERDUTY_INTEGRATION_KEY", "")
        self.pagerduty_api_url = "https://events.pagerduty.com/v2/enqueue"
        
        self.slack_enabled = os.getenv("SLACK_ENABLED", "false").lower() == "true"
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
        
        self.email_enabled = os.getenv("EMAIL_ALERTS_ENABLED", "false").lower() == "true"
        self.email_smtp_host = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
        self.email_smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.email_smtp_user = os.getenv("EMAIL_SMTP_USER", "")
        self.email_smtp_password = os.getenv("EMAIL_SMTP_PASSWORD", "")
        self.email_from = os.getenv("EMAIL_FROM", self.email_smtp_user)
        self.email_to = os.getenv("EMAIL_TO", "").split(",") if os.getenv("EMAIL_TO") else []
        
        self.notion_enabled = os.getenv("NOTION_ALERTS_ENABLED", "false").lower() == "true"
        
        # Try to load from AWS Secrets Manager if available
        self._load_secrets()
    
    def _load_secrets(self):
        """Load alerting secrets from AWS Secrets Manager if available"""
        try:
            from argo.utils.secrets_manager import get_secret
            
            # PagerDuty
            if not self.pagerduty_integration_key:
                self.pagerduty_integration_key = get_secret("pagerduty-integration-key", service="argo", default="")
                if self.pagerduty_integration_key:
                    self.pagerduty_enabled = True
            
            # Slack
            if not self.slack_webhook_url:
                self.slack_webhook_url = get_secret("slack-webhook-url", service="argo", default="")
                if self.slack_webhook_url:
                    self.slack_enabled = True
            
            # Email
            if not self.email_smtp_user:
                self.email_smtp_user = get_secret("email-smtp-user", service="argo", default="")
            if not self.email_smtp_password:
                self.email_smtp_password = get_secret("email-smtp-password", service="argo", default="")
            if not self.email_to and os.getenv("EMAIL_TO"):
                self.email_to = os.getenv("EMAIL_TO").split(",")
            
            if self.email_smtp_user and self.email_smtp_password and self.email_to:
                self.email_enabled = True
                
        except ImportError:
            pass  # Secrets manager not available
        except Exception as e:
            logger.warning(f"Failed to load alerting secrets: {e}")
    
    def send_alert(self, 
                   title: str,
                   message: str,
                   severity: str = "critical",
                   details: Optional[Dict] = None,
                   source: str = "argo-integrity-monitor"):
        """
        Send alert to all enabled channels
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity (critical, warning, info)
            details: Additional details dictionary
            source: Alert source identifier
        """
        alert_data = {
            "title": title,
            "message": message,
            "severity": severity,
            "details": details or {},
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        results = {
            "pagerduty": False,
            "slack": False,
            "email": False,
            "notion": False
        }
        
        # Send to PagerDuty (critical only)
        if severity == "critical" and self.pagerduty_enabled:
            results["pagerduty"] = self._send_pagerduty(alert_data)
        
        # Send to Slack
        if self.slack_enabled:
            results["slack"] = self._send_slack(alert_data)
        
        # Send to Email
        if self.email_enabled:
            results["email"] = self._send_email(alert_data)
        
        # Send to Notion
        if self.notion_enabled:
            results["notion"] = self._send_notion(alert_data)
        
        # Log results
        enabled_channels = [k for k, v in results.items() if v]
        if enabled_channels:
            logger.info(f"✅ Alert sent to: {', '.join(enabled_channels)}")
        else:
            logger.warning("⚠️  No alert channels enabled or configured")
        
        return results
    
    def _send_pagerduty(self, alert_data: Dict) -> bool:
        """Send alert to PagerDuty"""
        try:
            payload = {
                "routing_key": self.pagerduty_integration_key,
                "event_action": "trigger",
                "payload": {
                    "summary": alert_data["title"],
                    "source": alert_data["source"],
                    "severity": alert_data["severity"],
                    "custom_details": {
                        "message": alert_data["message"],
                        **alert_data["details"]
                    }
                }
            }
            
            response = requests.post(
                self.pagerduty_api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            logger.info("✅ PagerDuty alert sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send PagerDuty alert: {e}")
            return False
    
    def _send_slack(self, alert_data: Dict) -> bool:
        """Send alert to Slack"""
        try:
            # Determine color based on severity
            color_map = {
                "critical": "#FF0000",  # Red
                "warning": "#FFA500",   # Orange
                "info": "#36A2EB"       # Blue
            }
            color = color_map.get(alert_data["severity"], "#808080")
            
            # Build Slack message
            slack_payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": alert_data["title"],
                        "text": alert_data["message"],
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert_data["severity"].upper(),
                                "short": True
                            },
                            {
                                "title": "Source",
                                "value": alert_data["source"],
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": alert_data["timestamp"],
                                "short": False
                            }
                        ],
                        "footer": "Argo Capital Integrity Monitor",
                        "ts": int(datetime.fromisoformat(alert_data["timestamp"].replace("Z", "+00:00")).timestamp())
                    }
                ]
            }
            
            # Add details if present
            if alert_data["details"]:
                details_text = "\n".join([f"• {k}: {v}" for k, v in alert_data["details"].items()])
                slack_payload["attachments"][0]["fields"].append({
                    "title": "Details",
                    "value": details_text,
                    "short": False
                })
            
            response = requests.post(
                self.slack_webhook_url,
                json=slack_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            logger.info("✅ Slack alert sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send Slack alert: {e}")
            return False
    
    def _send_email(self, alert_data: Dict) -> bool:
        """Send alert via email"""
        try:
            if not self.email_to:
                logger.warning("⚠️  No email recipients configured")
                return False
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{alert_data['severity'].upper()}] {alert_data['title']}"
            msg["From"] = self.email_from
            msg["To"] = ", ".join(self.email_to)
            
            # Build email body
            text_body = f"""
{alert_data['title']}

{alert_data['message']}

Severity: {alert_data['severity'].upper()}
Source: {alert_data['source']}
Timestamp: {alert_data['timestamp']}

Details:
{json.dumps(alert_data['details'], indent=2) if alert_data['details'] else 'None'}

---
Argo Capital Integrity Monitor
"""
            
            html_body = f"""
<html>
<head></head>
<body>
    <h2 style="color: {'red' if alert_data['severity'] == 'critical' else 'orange' if alert_data['severity'] == 'warning' else 'blue'};">
        {alert_data['title']}
    </h2>
    <p>{alert_data['message']}</p>
    <hr>
    <p><strong>Severity:</strong> {alert_data['severity'].upper()}</p>
    <p><strong>Source:</strong> {alert_data['source']}</p>
    <p><strong>Timestamp:</strong> {alert_data['timestamp']}</p>
    <h3>Details:</h3>
    <pre>{json.dumps(alert_data['details'], indent=2) if alert_data['details'] else 'None'}</pre>
    <hr>
    <p><em>Argo Capital Integrity Monitor</em></p>
</body>
</html>
"""
            
            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.email_smtp_host, self.email_smtp_port) as server:
                server.starttls()
                server.login(self.email_smtp_user, self.email_smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email alert sent to {len(self.email_to)} recipient(s)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email alert: {e}")
            return False
    
    def _send_notion(self, alert_data: Dict) -> bool:
        """Send alert to Notion Command Center"""
        try:
            from argo.integrations.notion_command_center import command_center
            
            # Use existing Notion integration
            command_center.log_alert(
                f"{alert_data['title']}: {alert_data['message']}",
                severity=alert_data["severity"]
            )
            logger.info("✅ Notion alert sent successfully")
            return True
            
        except ImportError:
            logger.warning("⚠️  Notion integration not available")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send Notion alert: {e}")
            return False


# Global instance
_alerting_service = None

def get_alerting_service() -> AlertingService:
    """Get or create global alerting service instance"""
    global _alerting_service
    if _alerting_service is None:
        _alerting_service = AlertingService()
    return _alerting_service

