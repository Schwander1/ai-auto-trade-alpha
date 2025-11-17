# API Design & Versioning Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** All API endpoints (Argo Capital, Alpine Analytics LLC)

---

## Overview

Comprehensive API design standards, versioning strategy, and documentation requirements to ensure consistent, maintainable, and well-documented APIs.

**Strategic Context:** API design aligns with scalability and reliability goals defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md).

---

## API Design Principles

### RESTful Design

**Rule:** Follow REST principles for all APIs

**Principles:**
- Use HTTP methods correctly (GET, POST, PUT, DELETE, PATCH)
- Use nouns for resources, not verbs
- Use plural nouns for collections
- Use hierarchical URLs for nested resources
- Return appropriate HTTP status codes

**Examples:**
```python
# GOOD ✅
GET    /api/v1/signals           # List signals
GET    /api/v1/signals/{id}      # Get signal
POST   /api/v1/signals           # Create signal
PUT    /api/v1/signals/{id}      # Update signal
DELETE /api/v1/signals/{id}      # Delete signal

# BAD ❌
POST   /api/v1/getSignals        # Verb in URL
GET    /api/v1/signal            # Singular for collection
POST   /api/v1/createSignal      # Verb in URL
```

---

## API Versioning

### Versioning Strategy

**Rule:** Use URL-based versioning for all APIs

**Format:** `/api/v{major}/...`

**Examples:**
- `/api/v1/signals`
- `/api/v2/signals`
- `/api/v1/users/profile`

### Version Numbering

**Major Version (v1, v2, v3):**
- Increment for breaking changes
- Breaking changes include:
  - Removing endpoints
  - Removing required fields
  - Changing field types
  - Changing authentication requirements
  - Changing response structure significantly

**Minor Changes (same version):**
- Adding new endpoints
- Adding optional fields
- Adding new response fields
- Bug fixes
- Performance improvements

### Backward Compatibility

**Rule:** Maintain backward compatibility for at least 2 major versions

**Requirements:**
- Old versions must continue working
- Document deprecation timeline (minimum 6 months)
- Provide migration guides
- Support both versions during transition

**Deprecation Process:**
1. Mark version as deprecated in documentation
2. Add deprecation headers to responses
3. Notify API consumers (minimum 3 months notice)
4. Remove after deprecation period

---

## Request/Response Formats

### Request Format

**Rule:** Use JSON for all request bodies

**Content-Type:** `application/json`

**Example:**
```python
@router.post("/api/v1/signals")
async def create_signal(signal: SignalCreate):
    # signal is automatically validated by Pydantic
    pass
```

### Response Format

**Rule:** Use consistent JSON response structure

**Success Response:**
```json
{
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

**Error Response:**
```json
{
  "error": {
    "type": "ValidationError",
    "message": "Invalid signal confidence",
    "code": "INVALID_CONFIDENCE",
    "details": {
      "field": "confidence",
      "value": 150,
      "constraint": "Must be between 0 and 100"
    }
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

---

## Error Response Standardization

### HTTP Status Codes

**Rule:** Use appropriate HTTP status codes

**2xx Success:**
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST (resource created)
- `204 No Content` - Successful DELETE

**4xx Client Errors:**
- `400 Bad Request` - Invalid request format/validation
- `401 Unauthorized` - Missing/invalid authentication
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Resource conflict (e.g., duplicate)
- `422 Unprocessable Entity` - Validation errors
- `429 Too Many Requests` - Rate limit exceeded

**5xx Server Errors:**
- `500 Internal Server Error` - Unexpected server error
- `502 Bad Gateway` - Upstream service error
- `503 Service Unavailable` - Service temporarily unavailable
- `504 Gateway Timeout` - Upstream service timeout

### Error Response Structure

**Rule:** All errors must use standardized error response format
- **Implementation:** `backend/core/error_responses.py`
- **Requirements:**
  - Error code (standardized codes: AUTH_xxx, AUTHZ_xxx, VALIDATION_xxx, etc.)
  - Error type (authentication_error, authorization_error, validation_error, etc.)
- Human-readable message
- Request ID (for traceability)
  - Field name (for validation errors)
  - Additional details (optional)

**Standard Error Codes:**
- `AUTH_001` - Invalid or expired token
- `AUTH_002` - Token blacklisted
- `AUTH_003` - Invalid credentials
- `AUTHZ_001` - Insufficient permissions
- `AUTHZ_002` - Admin access required
- `AUTHZ_003` - Resource ownership required
- `VALIDATION_001` - Invalid input format
- `RATE_001` - Rate limit exceeded
- `CSRF_001` - CSRF token missing
- `RESOURCE_001` - Resource not found
- `SERVER_001` - Internal server error

**Example:**
```python
from backend.core.error_responses import create_error_response, ErrorCodes

raise create_error_response(
    ErrorCodes.AUTHZ_001,
    "Insufficient permissions",
    status_code=403,
    request=request
)
```

**Legacy Example (for reference):**
```python
from fastapi import HTTPException

raise HTTPException(
    status_code=422,
    detail={
        "type": "ValidationError",
        "message": "Signal confidence must be between 0 and 100",
        "code": "INVALID_CONFIDENCE",
        "details": {
            "field": "confidence",
            "value": 150,
            "constraint": "0 <= confidence <= 100"
        }
    }
)
```

---

## Request ID & Traceability

### Request ID Generation

**Rule:** Generate unique request ID for every request

**Implementation:**
- Generate UUID v4 for each request
- Include in response headers: `X-Request-ID`
- Include in response body: `meta.request_id`
- Log with all log entries for traceability

**Example:**
```python
from fastapi import Request
import uuid

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

---

## Rate Limiting & Throttling

### Rate Limiting Strategy

**Rule:** Implement rate limiting for all public APIs

**Requirements:**
- Per-user/IP rate limits
- Different limits for authenticated vs anonymous
- Rate limit headers in responses
- Graceful handling of rate limit exceeded

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

**Rate Limit Response:**
```json
{
  "error": {
    "type": "RateLimitExceeded",
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "code": "RATE_LIMIT_EXCEEDED",
    "retry_after": 60
  }
}
```

### Rate Limit Configuration

**Recommended Limits:**
- **Authenticated Users:** 100 requests/minute
- **Anonymous Users:** 10 requests/minute
- **Trading Endpoints:** 10 requests/minute (stricter)
- **Admin Endpoints:** 1000 requests/minute

---

## API Documentation

### OpenAPI/Swagger Requirements

**Rule:** All APIs must have OpenAPI/Swagger documentation

**Requirements:**
- Auto-generated from code (FastAPI does this automatically)
- Include request/response examples
- Document all error responses
- Include authentication requirements
- Document rate limits

**Access:**
- Development: `/docs` (Swagger UI)
- Development: `/redoc` (ReDoc)
- Production: Disabled or restricted

### Documentation Standards

**Rule:** Document all endpoints with:
- Description of purpose
- Request parameters (path, query, body)
- Response formats (success and error)
- Authentication requirements
- Rate limits
- Example requests/responses

**Example:**
```python
@router.post(
    "/api/v1/signals",
    response_model=SignalResponse,
    status_code=201,
    summary="Create a new trading signal",
    description="Creates a new trading signal with validation",
    responses={
        201: {"description": "Signal created successfully"},
        400: {"description": "Invalid request"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"}
    }
)
async def create_signal(signal: SignalCreate):
    """Create a new trading signal."""
    pass
```

---

## Input Validation

### Validation Rules

**Rule:** Validate all inputs at API boundaries

**Requirements:**
- Use Pydantic models for validation
- Validate types, ranges, formats
- Provide clear error messages
- Return 422 for validation errors

**Example:**
```python
from pydantic import BaseModel, Field, validator

class SignalCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10, regex="^[A-Z]+$")
    confidence: float = Field(..., ge=0, le=100)
    entry_price: float = Field(..., gt=0)
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not v.isupper():
            raise ValueError('Symbol must be uppercase')
        return v
```

---

## Pagination

### Pagination Strategy

**Rule:** Implement pagination for list endpoints

**Format:** Cursor-based or offset-based

**Cursor-Based (Recommended):**
```
GET /api/v1/signals?cursor=abc123&limit=20
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "cursor": "def456",
    "limit": 20,
    "has_more": true
  }
}
```

**Offset-Based (Alternative):**
```
GET /api/v1/signals?page=1&per_page=20
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

### Pagination Limits

**Rule:** Enforce maximum page size

**Default:** 20 items per page
**Maximum:** 100 items per page
**Minimum:** 1 item per page

---

## Filtering & Sorting

### Filtering

**Rule:** Support filtering via query parameters

**Format:** `?field=value&field2=value2`

**Example:**
```
GET /api/v1/signals?symbol=AAPL&confidence_min=75
```

### Sorting

**Rule:** Support sorting via query parameter

**Format:** `?sort=field:direction`

**Example:**
```
GET /api/v1/signals?sort=confidence:desc&sort=created_at:asc
```

**Directions:** `asc` or `desc`
**Default:** `created_at:desc`

---

## Authentication & Authorization

### Authentication

**Rule:** Use JWT tokens for API authentication

**Implementation:**
- Bearer token in Authorization header
- Token expiration (15 minutes for access, 7 days for refresh)
- Refresh token mechanism
- Secure token storage (httpOnly cookies for web)

**Header Format:**
```
Authorization: Bearer <token>
```

### Authorization

**Rule:** Implement role-based access control (RBAC)

**Roles:**
- `admin` - Full access
- `user` - Standard user access
- `readonly` - Read-only access

**Implementation:**
```python
from fastapi import Depends, HTTPException, status
from backend.auth.dependencies import get_current_user, require_role

@router.delete("/api/v1/signals/{id}")
async def delete_signal(
    id: str,
    current_user: User = Depends(require_role("admin"))
):
    pass
```

---

## API Deprecation Process

### Deprecation Timeline

**Rule:** Follow structured deprecation process

**Timeline:**
1. **Announcement:** Mark as deprecated in docs (6+ months before removal)
2. **Warning Headers:** Add `Deprecation: true` and `Sunset: <date>` headers
3. **Notification:** Notify all API consumers (3+ months before removal)
4. **Removal:** Remove after deprecation period

**Deprecation Headers:**
```
Deprecation: true
Sunset: Sat, 15 Jul 2025 00:00:00 GMT
Link: <https://api.example.com/docs/v2>; rel="successor-version"
```

---

## Performance Requirements

### Response Time Targets

**Rule:** Meet performance targets for all endpoints

**Targets:**
- **Simple GET:** < 100ms
- **Complex GET:** < 500ms
- **POST/PUT:** < 200ms
- **DELETE:** < 100ms

### Optimization Strategies

- Use database indexes
- Implement caching where appropriate
- Use async operations for I/O
- Paginate large result sets
- Optimize database queries

---

## Testing Requirements

### API Testing

**Rule:** Test all API endpoints

**Required Tests:**
- Unit tests for request/response handling
- Integration tests for full request flow
- Error case testing (400, 401, 403, 404, 422, 500)
- Rate limiting tests
- Authentication/authorization tests

**See:** [03_TESTING.md](03_TESTING.md) for testing standards

---

## Related Rules

- **Security:** [07_SECURITY.md](07_SECURITY.md) - Authentication, input validation
- **Error Handling:** [29_ERROR_HANDLING.md](29_ERROR_HANDLING.md) - Error handling patterns
- **Performance:** [28_PERFORMANCE.md](28_PERFORMANCE.md) - Performance optimization
- **Code Quality:** [02_CODE_QUALITY.md](02_CODE_QUALITY.md) - Code quality standards
- **Backend Rules:** [12A_ARGO_BACKEND.md](12A_ARGO_BACKEND.md), [12B_ALPINE_BACKEND.md](12B_ALPINE_BACKEND.md)

---

**Note:** API design is critical for maintainability, scalability, and developer experience. Always follow these standards when creating or modifying APIs. Breaking changes must follow the deprecation process.

