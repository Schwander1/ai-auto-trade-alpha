# Security Rules

**Last Updated:** January 15, 2025  
**Version:** 2.0  
**Applies To:** All projects

---

## Overview

Security best practices and vulnerability prevention rules. These are **non-negotiable** and must be followed.

---

## Secrets Management

### Never Commit Secrets

#### What NOT to Commit
- ❌ API keys
- ❌ Passwords
- ❌ Database credentials
- ❌ JWT secrets
- ❌ Private keys
- ❌ Access tokens

#### What TO Commit
- ✅ `config.json.example` (templates)
- ✅ `.env.example` (templates)
- ✅ Documentation of required secrets

### Secret Storage

**See:** [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) for environment-specific secret management

#### Production
- **Use:** AWS Secrets Manager (environment-specific secrets)
- **Access:** Each entity should have its own secrets_manager implementation
- **⚠️ DEPRECATED:** `packages/shared/` violates entity separation (Rule 10)
- **Pattern:** `alpaca-api-key-production`, `alpaca-secret-key-production`

#### Development
- **Use:** `config.json` (local, not committed)
- **Fallback:** Environment variables
- **Never:** Hardcode in code or commit to version control

#### Secret Validation
- **Rule:** Fail fast if default/weak secrets detected
- **Requirements:**
  - Validate secrets on startup
  - Reject default secret values in production
  - Check for common weak secrets (e.g., "change_me", "secret", "password")
  - Fail fast in production if secrets are missing or weak
  - Warn in development but allow operation

---

## Input Validation & Sanitization

### SQL Injection Prevention

#### Rule: Never concatenate SQL
- **BAD ❌:**
  ```python
  query = f"SELECT * FROM users WHERE id = {user_id}"
  ```

- **GOOD ✅:**
  ```python
  query = "SELECT * FROM users WHERE id = :user_id"
  cursor.execute(query, {"user_id": user_id})
  ```

#### Use Parameterized Queries
- **Python:** Use SQLAlchemy ORM or parameterized queries
- **TypeScript:** Use Prisma ORM or parameterized queries

### XSS Prevention

#### Rule: Escape all user input
- **Backend:** Sanitize before storing
- **Frontend:** Escape before rendering
- **Use:** Framework-provided escaping functions

#### Content Security Policy
- **Rule:** Implement CSP headers
- **Action:** Restrict script sources, inline scripts

---

## Authentication & Authorization

### Authentication

#### JWT Tokens
- **Rule:** Use secure JWT implementation
- **Requirements:**
  - Strong secret key (from AWS Secrets Manager)
  - Short expiration times
  - Refresh token mechanism
  - Secure storage (httpOnly cookies)
  - **CRITICAL:** Token blacklist check on every authenticated request
  - **CRITICAL:** Single source of truth for `get_current_user()` - no duplicates

#### Password Security
- **Rule:** Never store plaintext passwords
- **Use:** bcrypt or Argon2 hashing
- **Requirements:**
  - Minimum 12 characters
  - Salt each password
  - Use strong hashing algorithm

### Authorization

#### Rule: Check permissions for every action
- **Action:** Verify user has permission before executing
- **Pattern:** Role-based or permission-based access control
- **CRITICAL:** All admin endpoints MUST require authentication
- **CRITICAL:** Never expose endpoints without authentication checks

#### Role-Based Access Control (RBAC)
- **Rule:** Use RBAC system for all authorization
- **Implementation:** `backend/core/rbac.py`, `backend/models/role.py`
- **Requirements:**
  - All users have roles (default: "user")
  - Roles have permissions (granular access control)
  - Use `require_permission()` dependency for endpoint protection
  - Use `require_role()` dependency for role-based access
  - Default roles: admin, moderator, support, user
  - System roles cannot be deleted
  - Initialize default roles on first deployment
- **Usage:**
  ```python
  from backend.core.rbac import require_permission, PermissionEnum
  
  @router.get("/admin/users")
  async def get_users(
      current_user: User = Depends(require_permission(PermissionEnum.ADMIN_USERS))
  ):
      ...
  ```
- **Database:** RBAC tables created via migration (`backend/migrations/add_rbac_tables.py`)

#### Resource Ownership
- **Rule:** Verify resource ownership for user-specific resources
- **Implementation:** `backend/core/resource_ownership.py`
- **Requirements:**
  - Users can only access their own resources
  - Use `verify_resource_ownership()` for ownership checks
  - Log unauthorized access attempts
  - Return 403 Forbidden for ownership violations
- **Usage:**
  ```python
  from backend.core.resource_ownership import verify_resource_ownership
  
  signal = await verify_resource_ownership(
      resource_id=signal_id,
      resource_model=Signal,
      user_id_field="user_id",
      current_user=current_user,
      db=db
  )
  ```

#### Least Privilege
- **Rule:** Grant minimum necessary permissions
- **Action:** Review and restrict access regularly

#### Endpoint Security Requirements
- **Rule:** All endpoints must have explicit authentication/authorization
- **Requirements:**
  - Use router-based endpoints (`backend/api/*`) for full security features
  - Legacy endpoints in `main.py` are deprecated - migrate to routers
  - Admin endpoints must check admin status, not just authentication
  - Test endpoints must be disabled in production or require admin access
  - Resource ownership checks for user-specific endpoints

---

## API Security

### Rate Limiting

#### Rule: Implement rate limiting on all APIs
- **Public APIs:** Stricter limits
- **Authenticated APIs:** Higher limits
- **Use:** Redis-based rate limiting
- **CRITICAL:** Fail-closed in production (reject requests if Redis fails)
- **CRITICAL:** Use Redis-based rate limiting everywhere (no in-memory fallback in production)
- **Requirements:**
  - Consistent rate limits across all endpoints
  - Document rate limit policies
  - Return rate limit headers in responses

### CORS Configuration

#### Rule: Restrict CORS to known origins
- **Production:** Only allow production frontend domain
- **Development:** Allow localhost for development
- **Never:** Use `*` for allowed origins
- **CRITICAL:** CSRF origin validation must check against allowed origins
- **Requirements:**
  - Validate Origin header in CSRF middleware
  - Reject requests from unauthorized origins
  - Use configuration-based origin lists (not hardcoded)

### Input Validation

#### Rule: Validate all inputs at API boundaries
- **Type checking:** Ensure correct data types
- **Range validation:** Check min/max values
- **Format validation:** Verify formats (email, URL, etc.)
- **Sanitization:** Remove dangerous characters
- **CRITICAL:** Request size limits to prevent DoS attacks
- **Requirements:**
  - Limit request body size (e.g., 10MB max)
  - Validate all query parameters
  - Sanitize all user inputs consistently
  - Use Pydantic models for request validation

---

## Data Protection

### Encryption

#### At Rest
- **Rule:** Encrypt sensitive data in database
- **Use:** Database encryption or application-level encryption
- **Examples:** Passwords, API keys, personal information

#### In Transit
- **Rule:** Always use TLS/SSL
- **Requirements:**
  - TLS 1.2 or higher
  - Valid SSL certificates
  - HTTPS for all API endpoints

### Data Minimization

#### Rule: Only collect necessary data
- **Action:** Don't store data you don't need
- **Retention:** Delete data when no longer needed
- **Privacy:** Respect user privacy

---

## Dependency Security

### Security Audits

#### Regular Audits
- **Python:** `pip-audit`, `safety`
- **Node.js:** `npm audit`
- **Frequency:** Before each release

#### Update Dependencies
- **Rule:** Keep dependencies up to date
- **Action:** Regularly update and test
- **Priority:** Security patches first

### Minimal Dependencies
- **Rule:** Avoid unnecessary dependencies
- **Action:** Review and remove unused packages
- **Why:** Reduces attack surface

---

## Logging & Monitoring

### Secure Logging

#### Rule: Never log sensitive data
- **Never Log:**
  - Passwords
  - API keys
  - Credit card numbers
  - Personal information

#### Structured Logging
- **Use:** Structured logging format
- **Include:** Request IDs, user IDs (hashed), timestamps
- **Sanitize:** Remove sensitive data before logging
- **CRITICAL:** PII redaction must be comprehensive
- **Requirements:**
  - Redact PII patterns (passwords, tokens, emails, etc.)
  - Limit response body logging size (prevent memory issues)
  - Use proper streaming for response body logging
  - Implement log rotation (size and time-based)
  - Never expose stack traces in production error messages

#### Log Rotation
- **Rule:** Implement log rotation to prevent disk space issues
- **Implementation:** `backend/core/security_logging.py`
- **Requirements:**
  - Size-based rotation: 10MB per file, 5 backup files
  - Time-based rotation: Daily rotation, 30 days retention
  - Use `RotatingFileHandler` for security logs
  - Apply to all log files (security, request, application)

#### Log Sampling
- **Rule:** Sample high-volume endpoint logs
- **Implementation:** `backend/core/request_logging.py`
- **Requirements:**
  - Sample 1% of health check requests
  - Sample 10% of metrics requests
  - Always log errors (status >= 400)
  - Always log security events
  - Configure sampling rates per endpoint pattern

### Security Monitoring

#### Rule: Monitor for security events
- **Track:**
  - Failed login attempts
  - Unauthorized access attempts
  - Unusual API usage patterns
  - Security-related errors

#### Security Event Alerting
- **Rule:** Use centralized security alerting system
- **Implementation:** `backend/core/alerting.py`
- **Channels:** PagerDuty, Slack, Email
- **Requirements:**
  - Automatic alerting on threshold violations
  - Configurable thresholds per event type
  - Alert on: failed logins, rate limit abuse, CSRF violations, unauthorized access, account lockouts
  - Integration with security logging
- **Configuration:**
  - `SECURITY_ALERTS_ENABLED=true`
  - `PAGERDUTY_ENABLED`, `SLACK_ENABLED`, `EMAIL_ALERTS_ENABLED`
  - Set appropriate API keys/webhooks
- **Thresholds:**
  - Failed login: 5 in 5 minutes
  - Rate limit: 10 in 1 minute
  - CSRF violation: 3 in 1 minute
  - Unauthorized access: 3 in 5 minutes

#### Alerts
- **Rule:** Set up alerts for security events
- **Action:** Immediate notification for critical events

---

## Error Handling

### Secure Error Messages

#### Rule: Don't expose sensitive information in errors
- **BAD ❌:**
  ```python
  raise ValueError(f"Database connection failed: {password}")
  ```

- **GOOD ✅:**
  ```python
  logger.error("Database connection failed", extra={"error": "connection_error"})
  raise ValueError("Database connection failed. Please contact support.")
  ```

### Error Logging
- **Rule:** Log errors securely
- **Include:** Error type, timestamp, request ID
- **Exclude:** Sensitive data, stack traces (in production)

---

## Webhook Security

### Webhook Idempotency
- **Rule:** Prevent duplicate webhook processing
- **Implementation:** `backend/api/webhooks.py`
- **Requirements:**
  - Redis-based event tracking (24-hour TTL)
  - Check idempotency before processing
  - Mark events as processed after successful handling
  - Return success for duplicate events (idempotent)

### Webhook Replay Protection
- **Rule:** Prevent replay attacks on webhooks
- **Implementation:** `backend/api/webhooks.py`
- **Requirements:**
  - Validate event timestamp (5-minute window)
  - Reject events older than threshold
  - Log replay attempts as security events
  - Use event creation timestamp from webhook provider

## Security Checklist

### Before Deployment
- [ ] No secrets in code
- [ ] No default/weak secrets (fail fast if detected)
- [ ] All inputs validated
- [ ] Request size limits configured (10MB)
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] Authentication implemented
- [ ] Authorization checked (all admin endpoints secured)
- [ ] RBAC system initialized
- [ ] Resource ownership checks implemented
- [ ] No duplicate authentication logic
- [ ] Token blacklist checked on all authenticated requests
- [ ] Rate limiting configured (fail-closed in production)
- [ ] CSRF protection with origin validation
- [ ] CORS properly configured
- [ ] TLS/SSL enabled
- [ ] Dependencies audited
- [ ] Security monitoring enabled
- [ ] Security event alerting configured
- [ ] Log rotation configured (size and time-based)
- [ ] Log sampling configured for high-volume endpoints
- [ ] PII redaction in logs verified
- [ ] Webhook idempotency implemented
- [ ] Webhook replay protection implemented

### Regular Reviews
- [ ] Review access permissions
- [ ] Audit dependencies
- [ ] Review logs for security events
- [ ] Test security controls
- [ ] Update security documentation

---

## Security Best Practices

### DO
- ✅ Use AWS Secrets Manager for production secrets
- ✅ Validate all inputs
- ✅ Use parameterized queries
- ✅ Implement rate limiting
- ✅ Use strong authentication
- ✅ Encrypt sensitive data
- ✅ Monitor security events
- ✅ Keep dependencies updated
- ✅ Follow least privilege principle
- ✅ Regular security audits

### DON'T
- ❌ Commit secrets to version control
- ❌ Hardcode credentials
- ❌ Concatenate SQL queries
- ❌ Trust user input
- ❌ Log sensitive data
- ❌ Expose sensitive information in errors
- ❌ Skip security checks
- ❌ Use weak passwords
- ❌ Ignore security alerts
- ❌ Deploy without security review

---

## Related Rules

- [06_CONFIGURATION.md](06_CONFIGURATION.md) - Configuration management
- [05_ENVIRONMENT.md](05_ENVIRONMENT.md) - Environment management
- [04_DEPLOYMENT.md](04_DEPLOYMENT.md) - Deployment procedures

