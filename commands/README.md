# Commands Reference

**Last Updated:** January 15, 2025  
**Version:** 1.0

---

## Overview

This directory contains comprehensive, explicit commands for managing the Argo-Alpine system. All commands use natural language syntax and require explicit environment specification.

---

## Quick Reference

### Production Deployment
```bash
./commands/deploy all to production          # Deploy both Argo & Alpine
./commands/deploy argo to production         # Deploy Argo only
./commands/deploy alpine to production       # Deploy Alpine only
```

### Health Checks
```bash
./commands/health check all production       # Check all production services
./commands/health check argo production      # Check Argo production
./commands/health check all                  # Check all local services
./commands/health check argo                 # Check Argo local
```

### Local Services
```bash
./commands/start all                         # Start all local services
./commands/start argo                        # Start Argo local
./commands/stop all                          # Stop all local services
./commands/restart argo                      # Restart Argo local
```

### Status Checks
```bash
./commands/status check all production       # Status of all production
./commands/status check argo production      # Status of Argo production
./commands/status check all                  # Status of all local
```

### Logs
```bash
./commands/logs view all production          # View all production logs
./commands/logs follow argo production       # Follow Argo production logs
./commands/logs view all                     # View all local logs
```

### Rollback
```bash
./commands/rollback argo production          # Rollback Argo production
./commands/rollback all production           # Rollback all production
```

---

## Command Details

### 1. Deploy Command

**Purpose:** Deploy services to production (production only)

**Syntax:**
```bash
./commands/deploy {project} to {environment}
```

**Examples:**
```bash
./commands/deploy all to production
./commands/deploy argo to production
./commands/deploy alpine to production
```

**Notes:**
- Only supports `production` environment
- For local development, use `./commands/start` instead
- Uses blue-green deployment for zero downtime

---

### 2. Health Command

**Purpose:** Check health of services

**Syntax:**
```bash
./commands/health check {project} {environment}
```

**Examples:**
```bash
# Production
./commands/health check all production
./commands/health check argo production
./commands/health check alpine production

# Local (environment optional)
./commands/health check all
./commands/health check argo
./commands/health check alpine
```

**Notes:**
- Checks API endpoints and service status
- Returns exit code 0 if all checks pass, 1 if any fail
- Environment defaults to `local` if not specified

---

### 3. Start Command

**Purpose:** Start local development services (local only)

**Syntax:**
```bash
./commands/start {project}
```

**Examples:**
```bash
./commands/start all
./commands/start argo
./commands/start alpine
```

**Notes:**
- Only works for local development
- Starts services in background
- Logs written to `/tmp/{service}-local.log`

---

### 4. Stop Command

**Purpose:** Stop local development services (local only)

**Syntax:**
```bash
./commands/stop {project}
```

**Examples:**
```bash
./commands/stop all
./commands/stop argo
./commands/stop alpine
```

**Notes:**
- Only works for local development
- Gracefully stops running services
- Stops Docker containers for Alpine

---

### 5. Restart Command

**Purpose:** Restart local development services (local only)

**Syntax:**
```bash
./commands/restart {project}
```

**Examples:**
```bash
./commands/restart all
./commands/restart argo
./commands/restart alpine
```

**Notes:**
- Stops and then starts services
- Useful for applying configuration changes

---

### 6. Status Command

**Purpose:** Check status of services

**Syntax:**
```bash
./commands/status check {project} {environment}
```

**Examples:**
```bash
# Production
./commands/status check all production
./commands/status check argo production

# Local (environment optional)
./commands/status check all
./commands/status check argo
```

**Notes:**
- Shows running status, PIDs, and health
- Environment defaults to `local` if not specified

---

### 7. Logs Command

**Purpose:** View or follow service logs

**Syntax:**
```bash
./commands/logs {action} {project} {environment}
```

**Examples:**
```bash
# Production
./commands/logs view all production
./commands/logs follow argo production

# Local (environment optional)
./commands/logs view all
./commands/logs follow argo
```

**Actions:**
- `view`: Show last 50 lines of logs
- `follow`: Follow logs in real-time (Ctrl+C to exit)

**Notes:**
- Environment defaults to `local` if not specified
- Production logs accessed via SSH

---

### 8. Rollback Command

**Purpose:** Rollback production deployments (production only)

**Syntax:**
```bash
./commands/rollback {project} production
```

**Examples:**
```bash
./commands/rollback argo production
./commands/rollback alpine production
./commands/rollback all production
```

**Notes:**
- Only supports `production` environment
- Switches to previous blue/green environment
- Use when issues detected after deployment

---

## Project Options

- `all`: Operate on both Argo and Alpine
- `argo`: Operate on Argo only
- `alpine`: Operate on Alpine only

---

## Environment Options

- `production`: Production servers (remote)
- `local`: Local development (default if omitted for local commands)

---

## Error Handling

All commands:
- Return exit code 0 on success
- Return exit code 1 on failure
- Display clear error messages
- Validate inputs before execution

---

## Service URLs

### Production
- Argo: http://178.156.194.174:8000
- Alpine: http://91.98.153.49:8001

### Local
- Argo: http://localhost:8000
- Alpine Backend: http://localhost:9001
- Alpine Frontend: http://localhost:3000

---

## Common Workflows

### Deploy to Production
```bash
# 1. Deploy
./commands/deploy all to production

# 2. Check health
./commands/health check all production

# 3. Monitor logs
./commands/logs follow all production
```

### Local Development
```bash
# 1. Start services
./commands/start all

# 2. Check health
./commands/health check all

# 3. View logs
./commands/logs view all

# 4. Stop when done
./commands/stop all
```

### Troubleshooting Production
```bash
# 1. Check status
./commands/status check all production

# 2. Check health
./commands/health check all production

# 3. View logs
./commands/logs view all production

# 4. Rollback if needed
./commands/rollback all production
```

---

## See Also

- [Rules/04_DEPLOYMENT.md](../Rules/04_DEPLOYMENT.md) - Deployment procedures
- [Rules/16_DEV_PROD_DIFFERENCES.md](../Rules/16_DEV_PROD_DIFFERENCES.md) - Environment differences
- [docs/SystemDocs/OPERATIONAL_GUIDE.md](../docs/SystemDocs/OPERATIONAL_GUIDE.md) - Operational procedures

