# Execution Dashboard Setup Guide

## Overview

The Execution Dashboard is a private, admin-only dashboard for monitoring signal execution, queue status, and account states across Argo and Prop Firm executors.

## Features

- **Smart Queuing System**: Automatically queues signals that can't execute immediately
- **Account State Monitoring**: Real-time monitoring of account buying power and positions
- **Execution Metrics**: Track execution rates, queue status, and signal flow
- **Admin-Only Access**: Secure access restricted to administrators

## Setup

### 1. Environment Variables

#### Argo Backend (.env)
```bash
# Admin API Key for execution dashboard
ADMIN_API_KEY=your-secret-admin-key-here-change-this

# Argo API URL (if different from default)
ARGO_API_URL=http://178.156.194.174:8000
```

#### Alpine Frontend (.env.local)
```bash
# Admin API Key (for server-side API routes)
ADMIN_API_KEY=your-secret-admin-key-here-change-this

# Argo API URL
NEXT_PUBLIC_ARGO_API_URL=http://178.156.194.174:8000
ARGO_API_URL=http://178.156.194.174:8000
```

### 2. Database Setup

The queue system automatically creates its database table on first use. The database is located at:
- Production: `/root/argo-production/data/signals_unified.db`
- Development: `{workspace}/argo/data/signals_unified.db`

### 3. Admin Role Setup

Make your user an admin in the database:

```sql
-- Connect to your database
-- This assumes you have a roles table

-- First, ensure admin role exists
INSERT INTO roles (name, description, is_system)
VALUES ('admin', 'Administrator role', true)
ON CONFLICT (name) DO NOTHING;

-- Then assign admin role to your user
-- Replace 'your-email@example.com' with your actual email
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u, roles r
WHERE u.email = 'your-email@example.com'
  AND r.name = 'admin'
ON CONFLICT DO NOTHING;
```

### 4. Start Services

The monitoring services start automatically when the Argo service starts. They run in the background and:
- Check queue every 30 seconds
- Monitor account states every 60 seconds
- Process ready signals automatically

## Access

### Dashboard URL
```
https://alpineanalytics.ai/execution
```

### API Endpoints (Admin Only)
```
GET /api/v1/execution/metrics      - Get execution metrics
GET /api/v1/execution/queue        - Get queue status
GET /api/v1/execution/account-states - Get account states
GET /api/v1/execution/recent-activity - Get recent activity
GET /api/v1/execution/dashboard    - Get HTML dashboard
```

All endpoints require:
- Authentication (logged in user)
- Admin role
- `X-Admin-API-Key` header (for direct API access)

## How It Works

### Signal Queuing

1. Signal is generated and distributed to executors
2. If executor rejects signal (e.g., no buying power, no position):
   - Signal is automatically queued
   - Conditions are tracked (e.g., "needs $1,000 buying power")
3. Queue monitor checks conditions every 30 seconds
4. When conditions are met, signal status changes to "ready"
5. Signal can then be executed automatically

### Account State Monitoring

1. Monitor checks account states every 60 seconds
2. Detects changes (buying power, positions, portfolio value)
3. Triggers queue processing when changes detected
4. Ready signals are automatically executed

### Execution Dashboard

1. Admin logs in to Alpine frontend
2. Navigates to `/execution`
3. Dashboard displays:
   - Execution rate
   - Queue status (pending, ready, executing, executed)
   - Account states for all executors
   - Recent activity

## Security

- **Authentication Required**: Must be logged in
- **Admin Role Required**: Only admins can access
- **API Key Protection**: Backend API requires admin key
- **Private Dashboard**: Not accessible to regular users

## Troubleshooting

### Dashboard shows "Admin Access Required"
- Check that your user has admin role in database
- Verify you're logged in
- Check browser console for errors

### Queue not processing
- Check that monitoring services are running
- Verify account states are being fetched
- Check logs for errors

### API returns 403
- Verify `ADMIN_API_KEY` is set correctly
- Check that `X-Admin-API-Key` header is included
- Ensure user has admin role

## Monitoring

The system automatically:
- Monitors queue every 30 seconds
- Monitors account states every 60 seconds
- Processes ready signals
- Logs all activity

Check logs for:
- Queue processing activity
- Account state changes
- Signal execution
- Errors

## Next Steps

1. Set environment variables
2. Make your user admin
3. Restart services
4. Access dashboard at `/execution`
5. Monitor execution metrics
