# Alpine Backend Test Suite

Comprehensive test suite for Alpine Backend API endpoints.

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_input_sanitizer.py
│   ├── test_response_formatter.py
│   ├── test_pydantic_validators.py
│   └── test_rate_limit_headers.py
├── integration/             # Integration tests
│   ├── test_endpoint_security.py
│   ├── test_rate_limiting.py
│   ├── test_error_handling.py
│   ├── test_input_validation.py
│   └── test_endpoint_validation.py
└── security/                # Security tests
    ├── test_penetration.py
    ├── test_rate_limit_bypass.py
    ├── test_input_fuzzing.py
    └── test_auth_authorization.py
```

## Running Tests

### All Tests
```bash
cd alpine-backend
pytest
```

### By Category
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Security tests only
pytest tests/security/
```

### With Coverage
```bash
pytest --cov=backend --cov-report=html --cov-report=term
```

### Specific Test
```bash
pytest tests/unit/test_input_sanitizer.py::TestSanitizeString::test_html_escaping
```

## Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only security tests
pytest -m security
```

## Coverage Target

- **Target:** 95%+
- **Current:** Run `pytest --cov=backend` to see current coverage

## Test Categories

### Unit Tests
- Input sanitization functions
- Response formatter functions
- Pydantic validators
- Rate limit header generation

### Integration Tests
- Endpoint security (XSS, SQL injection, path traversal)
- Rate limiting behavior
- Error handling
- Input validation

### Security Tests
- Penetration testing
- Rate limit bypass attempts
- Input fuzzing
- Authentication/authorization testing

