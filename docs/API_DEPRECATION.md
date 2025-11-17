# API Deprecation Strategy

Comprehensive strategy for deprecating and versioning APIs while maintaining backward compatibility.

## Table of Contents

1. [Overview](#overview)
2. [Deprecation Policy](#deprecation-policy)
3. [Versioning Strategy](#versioning-strategy)
4. [Deprecation Process](#deprecation-process)
5. [Migration Guides](#migration-guides)
6. [Communication Plan](#communication-plan)

---

## Overview

### Principles

- **Backward Compatibility**: Maintain compatibility during deprecation period
- **Clear Communication**: Notify users well in advance
- **Smooth Migration**: Provide migration guides and tools
- **Gradual Sunset**: Phased removal of deprecated features

### Current API Versions

- **v1**: Current stable version (all endpoints)
- **v2**: Future version (planned)

---

## Deprecation Policy

### Deprecation Timeline

1. **Announcement**: 6 months before deprecation
2. **Deprecation**: Feature marked as deprecated, still functional
3. **Sunset**: Feature removed (after deprecation period)

### Minimum Deprecation Period

- **Major Changes**: 12 months
- **Minor Changes**: 6 months
- **Security Issues**: 30 days (if critical)

### Deprecation Notice Format

All deprecated endpoints include:

```json
{
  "deprecated": true,
  "deprecation_date": "2025-01-15",
  "sunset_date": "2026-01-15",
  "replacement": "/api/v2/new-endpoint",
  "migration_guide": "https://docs.example.com/migration/v1-to-v2"
}
```

HTTP Headers:
```
Deprecation: true
Sunset: Sat, 15 Jan 2026 00:00:00 GMT
Link: </api/v2/new-endpoint>; rel="successor-version"
```

---

## Versioning Strategy

### URL Versioning

- **Current**: `/api/v1/...`
- **Future**: `/api/v2/...`
- **Legacy**: `/api/...` (redirects to v1)

### Version Lifecycle

1. **Development**: `/api/v2-beta/...` (internal testing)
2. **Beta**: `/api/v2-beta/...` (public beta)
3. **Stable**: `/api/v2/...` (production)
4. **Deprecated**: `/api/v1/...` (with deprecation headers)
5. **Sunset**: Removed

### Version Support Matrix

| Version | Status | Support Until | Notes |
|---------|--------|---------------|-------|
| v1 | Stable | TBD | Current version |
| v2-beta | Beta | TBD | Testing phase |
| Legacy | Deprecated | 2025-12-31 | Redirects to v1 |

---

## Deprecation Process

### Step 1: Planning

1. **Identify** endpoints/features to deprecate
2. **Design** replacement (if applicable)
3. **Document** reasons for deprecation
4. **Estimate** migration effort for users

### Step 2: Announcement

1. **Update Documentation**: Mark as deprecated
2. **Add Headers**: Include deprecation headers in responses
3. **Blog Post**: Announce on company blog
4. **Email Users**: Notify affected users
5. **Update Changelog**: Document in release notes

### Step 3: Implementation

1. **Create Replacement**: Implement v2 endpoint (if applicable)
2. **Add Warnings**: Log deprecation warnings
3. **Monitor Usage**: Track usage of deprecated endpoints
4. **Provide Migration Tools**: Scripts, guides, examples

### Step 4: Sunset

1. **Final Warning**: 30 days before sunset
2. **Remove Endpoint**: After sunset date
3. **Update Documentation**: Remove deprecated endpoints
4. **Archive**: Keep historical documentation

---

## Migration Guides

### Example: Migrating from v1 to v2

#### Endpoint: `/api/v1/signals` → `/api/v2/signals`

**v1 Request**:
```bash
GET /api/v1/signals?limit=10&premium_only=true
```

**v2 Request**:
```bash
GET /api/v2/signals?limit=10&tier=premium
```

**Changes**:
- `premium_only` parameter renamed to `tier`
- `tier` accepts: `free`, `premium`, `elite`

**Migration Script**:
```python
# v1 code
response = requests.get(
    'https://api.example.com/api/v1/signals',
    params={'limit': 10, 'premium_only': True}
)

# v2 code
response = requests.get(
    'https://api.example.com/api/v2/signals',
    params={'limit': 10, 'tier': 'premium'}
)
```

### Automated Migration Tool

Create `scripts/api-migration/migrate-v1-to-v2.py`:

```python
#!/usr/bin/env python3
"""Migrate API calls from v1 to v2"""
import re
import sys

def migrate_endpoint(url):
    """Migrate endpoint URL"""
    # Replace v1 with v2
    url = re.sub(r'/api/v1/', '/api/v2/', url)
    return url

def migrate_params(params):
    """Migrate request parameters"""
    if 'premium_only' in params:
        params['tier'] = 'premium' if params['premium_only'] else 'free'
        del params['premium_only']
    return params

if __name__ == '__main__':
    # Read code file
    with open(sys.argv[1]) as f:
        code = f.read()

    # Migrate endpoints
    code = migrate_endpoint(code)

    # Write migrated code
    with open(sys.argv[1] + '.migrated', 'w') as f:
        f.write(code)
```

---

## Communication Plan

### Channels

1. **API Documentation**: Deprecation notices in docs
2. **Email**: Direct emails to API users
3. **Blog**: Company blog posts
4. **Changelog**: Release notes
5. **Status Page**: Public status page updates

### Timeline Example

**6 Months Before**:
- Blog post: "Upcoming API Changes"
- Email to all API users
- Documentation updated

**3 Months Before**:
- Reminder email
- Migration guide published
- Migration tools released

**1 Month Before**:
- Final warning email
- Status page update
- Support available for migration

**Sunset Date**:
- Endpoint removed
- Redirect to v2 (if applicable)
- Support for migration issues

---

## Implementation

### FastAPI Deprecation Decorator

Create `backend/core/deprecation.py`:

```python
"""API deprecation utilities"""
from functools import wraps
from datetime import datetime
from fastapi import Response

def deprecated(
    sunset_date: str,
    replacement: str = None,
    migration_guide: str = None
):
    """Mark endpoint as deprecated"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            response: Response = kwargs.get('response') or args[0]

            # Add deprecation headers
            response.headers['Deprecation'] = 'true'
            response.headers['Sunset'] = sunset_date

            if replacement:
                response.headers['Link'] = f'<{replacement}>; rel="successor-version"'

            # Call original function
            return await func(*args, **kwargs)

        # Add deprecation info to OpenAPI schema
        wrapper.__deprecated__ = True
        wrapper.__sunset_date__ = sunset_date
        wrapper.__replacement__ = replacement
        wrapper.__migration_guide__ = migration_guide

        return wrapper
    return decorator
```

### Usage Example

```python
from backend.core.deprecation import deprecated

@router.get("/api/v1/signals")
@deprecated(
    sunset_date="Sat, 15 Jan 2026 00:00:00 GMT",
    replacement="/api/v2/signals",
    migration_guide="https://docs.example.com/migration/v1-to-v2"
)
async def get_signals_v1():
    """Deprecated: Use /api/v2/signals instead"""
    # ... implementation ...
```

---

## Monitoring

### Track Deprecated Endpoint Usage

```python
# Log deprecation warnings
logger.warning(
    f"Deprecated endpoint used: {request.url.path}",
    extra={
        "endpoint": request.url.path,
        "user_id": user.id if user else None,
        "ip": request.client.host
    }
)
```

### Metrics

Track:
- Usage count of deprecated endpoints
- Users still using deprecated endpoints
- Migration progress

---

## Best Practices

1. **Plan Ahead**: Start deprecation process early
2. **Communicate Clearly**: Provide clear migration paths
3. **Provide Tools**: Migration scripts and guides
4. **Monitor Usage**: Track adoption of new versions
5. **Be Flexible**: Extend deprecation period if needed
6. **Support Users**: Help with migration issues

---

## Resources

- [RFC 8594: The Sunset HTTP Header Field](https://tools.ietf.org/html/rfc8594)
- [API Versioning Best Practices](https://restfulapi.net/versioning/)
