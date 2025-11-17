# Security Guide

**Date:** January 15, 2025  
**Version:** 1.0  
**Status:** Complete Security Documentation

---

## Overview

This guide covers security architecture, best practices, and procedures for the Argo-Alpine trading platform.

---

## Security Architecture

### Secret Management

#### Local Development
- **Method:** `config.json` (acceptable for local)
- **Location:** `argo/config.json`
- **Note:** Never commit to git

#### Production
- **Method:** AWS Secrets Manager (primary)
- **Fallback:** Environment variables
- **Encryption:** AES-256 at rest, TLS in transit

### Secret Storage

**AWS Secrets Manager:**
- Service: `argo-alpine/argo/*`
- Secrets:
  - `alpaca-api-key-dev`
  - `alpaca-secret-key-dev`
  - `alpaca-api-key-production`
  - `alpaca-secret-key-production`
  - `alpaca-paper`

### Access Control

- IAM-based permissions
- Least privilege principle
- Audit logging via CloudTrail

---

## API Security

### CORS Configuration

**Current Setup:**
- Whitelist-based (no wildcards)
- Specific allowed origins only
- Credentials only from trusted domains

**Allowed Origins:**
- `http://localhost:3000` (local dev)
- `http://localhost:3001` (local dev)
- Production domains (configured)

### Rate Limiting

**Implementation:**
- Per-endpoint rate limiting
- IP-based tracking
- Configurable limits

**Limits:**
- Signal endpoints: 100 requests/minute
- Auth endpoints: 10 requests/minute
- Admin endpoints: 50 requests/minute

### Authentication

**Alpine Backend:**
- JWT tokens
- Token expiration
- Refresh tokens
- 2FA support (ready)

**Argo API:**
- API key authentication
- HMAC signature verification
- Request signing

---

## Input Validation

### Sanitization

**All user inputs are sanitized:**
- String sanitization (HTML escape, control chars)
- Email validation
- Symbol validation (alphanumeric, hyphens)
- Numeric validation (bounds checking)
- Path traversal prevention

### SQL Injection Prevention

- Parameterized queries only
- ORM usage (SQLAlchemy)
- No string concatenation in SQL
- Input validation before queries

### XSS Prevention

- HTML escaping
- Content Security Policy
- Sanitized output
- No inline scripts

---

## Data Protection

### Encryption

**At Rest:**
- Database encryption (PostgreSQL)
- AWS Secrets Manager (AES-256)
- File system encryption (production servers)

**In Transit:**
- TLS/SSL for all API calls
- HTTPS enforcement (HSTS)
- Encrypted database connections

### Database Security

- Encrypted connections
- Parameterized queries
- Access control
- Audit logging

---

## Security Headers

### Implemented Headers

- `Content-Security-Policy` - XSS protection
- `X-Frame-Options: DENY` - Clickjacking protection
- `X-Content-Type-Options: nosniff` - MIME sniffing protection
- `Strict-Transport-Security` - HTTPS enforcement
- `Referrer-Policy` - Referrer information control

---

## Error Handling

### Error Message Sanitization

**Production:**
- Generic error messages
- No stack traces
- No internal paths
- Request ID for tracking

**Development:**
- Detailed error messages
- Stack traces
- Full debugging info

### Logging

- Security events logged
- Failed login attempts tracked
- API abuse detection
- Anomaly detection

---

## Security Monitoring

### Security Events

**Monitored Events:**
- Failed authentication attempts
- API abuse patterns
- Unusual access patterns
- Security policy violations

### Alerts

- Failed login threshold exceeded
- API rate limit abuse
- Unauthorized access attempts
- Security configuration changes

---

## Security Audit Procedures

### Local Security Audit

```bash
./scripts/local_security_audit.sh
```

**Checks:**
- Hardcoded secrets
- CORS configuration
- Security headers
- Input validation
- SQL injection risks
- Rate limiting
- Authentication
- Error sanitization

### Comprehensive Security Audit

```bash
python scripts/security_audit_complete.py
```

**Checks:**
- All local audit checks
- Configuration security
- Dependency vulnerabilities
- Access control
- Encryption status

---

## Incident Response

### Security Incident Procedure

1. **Identify**
   - Detect security event
   - Assess severity
   - Document details

2. **Contain**
   - Isolate affected systems
   - Block malicious access
   - Preserve evidence

3. **Eradicate**
   - Remove threat
   - Patch vulnerabilities
   - Update security measures

4. **Recover**
   - Restore services
   - Verify security
   - Monitor closely

5. **Post-Incident**
   - Document incident
   - Review procedures
   - Update security measures

---

## Best Practices

### Development

1. **Never commit secrets**
   - Use .gitignore
   - Use environment variables
   - Use AWS Secrets Manager

2. **Validate all inputs**
   - Sanitize user input
   - Validate data types
   - Check bounds

3. **Use parameterized queries**
   - Never concatenate SQL
   - Use ORM methods
   - Validate inputs

4. **Handle errors securely**
   - Don't expose internals
   - Log securely
   - Generic error messages

### Production

1. **Use AWS Secrets Manager**
   - Centralized secret management
   - Automatic rotation
   - Audit logging

2. **Enable security headers**
   - All security headers enabled
   - HTTPS enforcement
   - CSP configured

3. **Monitor security events**
   - Log all security events
   - Set up alerts
   - Review regularly

4. **Regular security audits**
   - Run security audits
   - Review access logs
   - Update security measures

---

## Compliance

### Data Retention

- Signals: 7 years (compliance)
- Audit logs: 7 years
- Trade records: 7 years

### Audit Trail

- All signals logged with SHA-256
- Immutable audit logs
- Complete trade history
- Access logging

---

## Security Checklist

### Pre-Deployment

- [ ] No hardcoded secrets
- [ ] CORS properly configured
- [ ] Security headers enabled
- [ ] Input validation in place
- [ ] Rate limiting configured
- [ ] Authentication working
- [ ] Error messages sanitized
- [ ] Security audit passed

### Post-Deployment

- [ ] AWS Secrets Manager accessible
- [ ] Security headers verified
- [ ] Rate limiting tested
- [ ] Authentication tested
- [ ] Monitoring enabled
- [ ] Alerts configured

---

## Security Resources

### Documentation
- `docs/SECURITY_AUDIT_REPORT.md` - Security audit report
- `docs/SystemDocs/DEPLOYMENT_EXCLUSIONS.md` - Deployment security

### Scripts
- `scripts/local_security_audit.sh` - Local security audit
- `scripts/security_audit_complete.py` - Comprehensive audit

### Tools
- AWS Secrets Manager - Secret storage
- CloudTrail - Audit logging
- Security headers middleware - Header enforcement

---

**Last Updated:** January 15, 2025  
**Version:** 1.0

