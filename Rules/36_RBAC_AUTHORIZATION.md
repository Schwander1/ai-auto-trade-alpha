# RBAC & Authorization Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** Alpine Backend

---

## Overview

Role-Based Access Control (RBAC) system for fine-grained authorization. All authorization must use the RBAC system.

**See Also:** [07_SECURITY.md](07_SECURITY.md) for security rules, [26_API_DESIGN.md](26_API_DESIGN.md) for API design.

---

## RBAC System Architecture

### Components

- **Models:** `backend/models/role.py` - Role, Permission models
- **Utilities:** `backend/core/rbac.py` - RBAC helper functions
- **API:** `backend/api/roles.py` - Role management endpoints
- **Migration:** `backend/migrations/add_rbac_tables.py` - Database schema

### Database Schema

- **roles** - Role definitions
- **permissions** - Permission definitions
- **user_roles** - User-role associations (many-to-many)
- **role_permissions** - Role-permission associations (many-to-many)

---

## Default Roles

### Admin
- **Description:** Full system access
- **Permissions:**
  - All user permissions (read, write, delete)
  - All admin permissions (read, write, analytics, users, revenue)
  - All signal permissions (read, write, delete)
  - All subscription permissions (read, write)
  - Role management

### Moderator
- **Description:** User management and content moderation
- **Permissions:**
  - User read, write
  - Admin read, users
  - Signal read

### Support
- **Description:** Read-only access to user data
- **Permissions:**
  - User read
  - Admin read
  - Signal read

### User
- **Description:** Standard user access
- **Permissions:**
  - Signal read
  - Subscription read

---

## Permission System

### Permission Enum

**Location:** `backend/models/role.py` - `PermissionEnum`

**Categories:**
- **User Management:** `user:read`, `user:write`, `user:delete`
- **Admin:** `admin:read`, `admin:write`, `admin:analytics`, `admin:users`, `admin:revenue`
- **Signals:** `signal:read`, `signal:write`, `signal:delete`
- **Subscriptions:** `subscription:read`, `subscription:write`
- **Role Management:** `role:manage` (super admin only)

---

## Usage

### Checking Permissions

**In Endpoints:**
```python
from backend.core.rbac import require_permission, PermissionEnum

@router.get("/admin/users")
async def get_users(
    current_user: User = Depends(require_permission(PermissionEnum.ADMIN_USERS))
):
    ...
```

**In Code:**
```python
from backend.core.rbac import has_permission, PermissionEnum

if has_permission(user, PermissionEnum.ADMIN_WRITE):
    # Perform admin action
    ...
```

### Checking Roles

**In Endpoints:**
```python
from backend.core.rbac import require_role

@router.get("/admin/analytics")
async def get_analytics(
    current_user: User = Depends(require_role("admin"))
):
    ...
```

**In Code:**
```python
from backend.core.rbac import is_admin

if is_admin(user):
    # Perform admin action
    ...
```

---

## Resource Ownership

### Rule: Verify Ownership for User Resources

**Implementation:** `backend/core/resource_ownership.py`

**Usage:**
```python
from backend.core.resource_ownership import verify_resource_ownership

@router.get("/signals/{signal_id}")
async def get_signal(
    signal_id: int,
    signal: Signal = Depends(verify_resource_ownership(
        Signal, "user_id", "signal_id"
    )),
    current_user: User = Depends(get_current_user)
):
    return signal
```

**Requirements:**
- Users can only access their own resources
- Log unauthorized access attempts
- Return 403 Forbidden for ownership violations
- Use for all user-specific resources

---

## Initialization

### Database Migration

**Rule:** Run RBAC migration before first deployment

```bash
cd alpine-backend/backend
python migrations/add_rbac_tables.py
```

### Initialize Default Roles

**Rule:** Initialize default roles and permissions

**Via API:**
```bash
POST /api/v1/roles/initialize
Authorization: Bearer <admin_token>
```

**Programmatically:**
```python
from backend.core.rbac import initialize_default_roles
from backend.core.database import get_db

db = next(get_db())
initialize_default_roles(db)
```

---

## Role Management API

### Get All Roles
```bash
GET /api/v1/roles
Authorization: Bearer <admin_token>
```

### Assign Role to User
```bash
POST /api/v1/roles/assign
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "user_id": 123,
  "role_name": "admin"
}
```

### Remove Role from User
```bash
DELETE /api/v1/roles/remove
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "user_id": 123,
  "role_name": "moderator"
}
```

**Requirements:**
- Requires `role:manage` permission
- Cannot remove last admin user
- System roles cannot be deleted

---

## Best Practices

### DO
- ✅ Use RBAC for all authorization
- ✅ Use granular permissions (not just roles)
- ✅ Check permissions at endpoint level
- ✅ Verify resource ownership for user resources
- ✅ Initialize default roles on deployment
- ✅ Log all authorization decisions
- ✅ Use `require_permission()` for endpoint protection

### DON'T
- ❌ Hardcode role checks (use RBAC)
- ❌ Skip ownership verification
- ❌ Grant excessive permissions
- ❌ Delete system roles
- ❌ Remove last admin user
- ❌ Bypass RBAC checks

---

## Migration from Legacy Authorization

### Backward Compatibility

**Legacy Admin Check:**
```python
# OLD (still works, but deprecated)
from backend.api.admin import is_admin

if is_admin(user):
    ...
```

**New RBAC Check:**
```python
# NEW (preferred)
from backend.core.rbac import has_role

if has_role(user, "admin"):
    ...
```

**Migration Path:**
1. Update endpoints to use `require_permission()` or `require_role()`
2. Assign roles to existing users
3. Remove legacy admin email checks
4. Update all authorization logic to use RBAC

---

## Security Considerations

### Role Assignment
- **Rule:** Only admins can assign roles
- **Requirement:** Requires `role:manage` permission
- **Logging:** All role assignments logged as security events

### Permission Checks
- **Rule:** Always check permissions, never trust client
- **Requirement:** Verify permissions server-side
- **Performance:** Use eager loading for user roles

### Resource Ownership
- **Rule:** Always verify ownership for user resources
- **Requirement:** Use `verify_resource_ownership()` helper
- **Logging:** Log unauthorized access attempts

---

## Related Rules

- [07_SECURITY.md](07_SECURITY.md) - Security rules and authorization
- [26_API_DESIGN.md](26_API_DESIGN.md) - API design and error responses
- [30_CODE_REVIEW.md](30_CODE_REVIEW.md) - Code review checklist

