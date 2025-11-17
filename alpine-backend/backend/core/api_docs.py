"""
API Documentation Enhancements
Provides utilities for enhancing OpenAPI/Swagger documentation.
"""
from typing import Dict, Any, Optional
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def enhance_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """
    Enhance OpenAPI schema with additional information.

    Args:
        app: FastAPI application

    Returns:
        Enhanced OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token authentication"
        },
        "OAuth2": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/api/v1/auth/token",
                    "scopes": {
                        "read": "Read access",
                        "write": "Write access"
                    }
                }
            }
        }
    }

    # Add common responses
    openapi_schema["components"]["responses"] = {
        "ValidationError": {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string", "example": "VALIDATION_ERROR"},
                                    "message": {"type": "string", "example": "Validation failed"},
                                    "details": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "UnauthorizedError": {
            "description": "Unauthorized access",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string", "example": "UNAUTHORIZED"},
                                    "message": {"type": "string", "example": "Unauthorized access"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "NotFoundError": {
            "description": "Resource not found",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string", "example": "NOT_FOUND"},
                                    "message": {"type": "string", "example": "Resource not found"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "RateLimitError": {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string", "example": "RATE_LIMIT_EXCEEDED"},
                                    "message": {"type": "string", "example": "Rate limit exceeded"},
                                    "details": {
                                        "type": "object",
                                        "properties": {
                                            "retry_after": {"type": "integer", "example": 60}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    # Add tags with descriptions
    openapi_schema["tags"] = [
        {
            "name": "auth",
            "description": "Authentication and authorization endpoints"
        },
        {
            "name": "signals",
            "description": "Trading signal endpoints - Get signals, history, and exports"
        },
        {
            "name": "users",
            "description": "User management endpoints"
        },
        {
            "name": "admin",
            "description": "Admin-only endpoints for analytics and user management"
        },
        {
            "name": "health",
            "description": "Health check and system status endpoints"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def add_example_responses(openapi_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add example responses to OpenAPI schema.

    Args:
        openapi_schema: OpenAPI schema dictionary

    Returns:
        Enhanced schema with examples
    """
    # This would add example responses to paths
    # Implementation depends on specific needs
    return openapi_schema
