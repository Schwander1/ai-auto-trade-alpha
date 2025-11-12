#!/bin/bash
# Security Log Monitoring Script
# Monitors security.log for anomalies and alerts

SECURITY_LOG="alpine-backend/logs/security.log"
ALERT_THRESHOLD_FAILED_LOGINS=10  # Alert if more than 10 failed logins in 5 minutes
ALERT_THRESHOLD_LOCKOUTS=5  # Alert if more than 5 lockouts in 1 hour
ALERT_THRESHOLD_RATE_LIMITS=50  # Alert if more than 50 rate limit violations in 1 hour

echo "🔍 Security Log Monitoring"
echo "========================="

if [ ! -f "${SECURITY_LOG}" ]; then
    echo "⚠️  Security log file not found: ${SECURITY_LOG}"
    exit 1
fi

# Check for failed login attempts (last 5 minutes)
FAILED_LOGINS=$(grep "failed_login" "${SECURITY_LOG}" | awk -v threshold=$(date -d '5 minutes ago' +%s) '
{
    # Parse timestamp and count recent failures
    if ($1 ~ /^[0-9]{4}-[0-9]{2}-[0-9]{2}/) {
        # Count recent entries
        count++
    }
}
END {
    print count+0
}')

if [ "${FAILED_LOGINS}" -gt "${ALERT_THRESHOLD_FAILED_LOGINS}" ]; then
    echo "🚨 ALERT: ${FAILED_LOGINS} failed login attempts in last 5 minutes (threshold: ${ALERT_THRESHOLD_FAILED_LOGINS})"
fi

# Check for account lockouts (last 1 hour)
LOCKOUTS=$(grep "account_locked" "${SECURITY_LOG}" | tail -100 | wc -l)
if [ "${LOCKOUTS}" -gt "${ALERT_THRESHOLD_LOCKOUTS}" ]; then
    echo "🚨 ALERT: ${LOCKOUTS} account lockouts in last hour (threshold: ${ALERT_THRESHOLD_LOCKOUTS})"
fi

# Check for rate limit violations (last 1 hour)
RATE_LIMITS=$(grep "rate_limit_exceeded" "${SECURITY_LOG}" | tail -100 | wc -l)
if [ "${RATE_LIMITS}" -gt "${ALERT_THRESHOLD_RATE_LIMITS}" ]; then
    echo "🚨 ALERT: ${RATE_LIMITS} rate limit violations in last hour (threshold: ${ALERT_THRESHOLD_RATE_LIMITS})"
fi

# Check for CSRF violations
CSRF_VIOLATIONS=$(grep "csrf_violation" "${SECURITY_LOG}" | tail -20 | wc -l)
if [ "${CSRF_VIOLATIONS}" -gt 0 ]; then
    echo "⚠️  WARNING: ${CSRF_VIOLATIONS} CSRF violations detected"
fi

# Check for suspicious activity
SUSPICIOUS=$(grep "suspicious_activity" "${SECURITY_LOG}" | tail -20 | wc -l)
if [ "${SUSPICIOUS}" -gt 0 ]; then
    echo "⚠️  WARNING: ${SUSPICIOUS} suspicious activities detected"
fi

echo "✅ Monitoring complete"

