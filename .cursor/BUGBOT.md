# Bugbot Review Guidelines

**Project:** Argo → Alpine Monorepo  
**Last Updated:** January 15, 2025

---

## Overview

This file provides Bugbot with project-specific review guidelines. For complete rules, see the `Rules/` directory and `.cursorrules/` directory.

---

## Critical Rules to Enforce

### Security
- ✅ Never commit secrets to version control
- ✅ Use AWS Secrets Manager for production secrets
- ✅ Validate all inputs at system boundaries
- ✅ Use parameterized queries (never concatenate SQL)
- ✅ Redact PII in logs
- ✅ Proper authentication/authorization on all endpoints

### Code Quality
- ✅ Follow SOLID principles
- ✅ Functions under 50 lines (ideal: 20-30 lines)
- ✅ Max 3-4 parameters per function
- ✅ Max 3-4 levels of nesting
- ✅ No code duplication (DRY principle)
- ✅ No dead code (unused imports, commented code, etc.)

### Naming Conventions (MANDATORY)

**Python:**
- Functions: `snake_case` with `verb_noun` pattern (e.g., `calculate_position_size()`)
- Classes: `PascalCase` (e.g., `SignalGenerationService`)
- Variables: `snake_case` (e.g., `signal_confidence`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MIN_CONFIDENCE_THRESHOLD`)

**TypeScript/JavaScript:**
- Files: `kebab-case.tsx` (e.g., `signal-card.tsx`)
- Components: `PascalCase` (e.g., `SignalCard`)
- Functions: `camelCase` (e.g., `calculateConfidence()`)
- Variables: `camelCase` (e.g., `signalList`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_ENDPOINT`)

**Reject:**
- Generic names (`data`, `temp`, `helper`)
- Abbreviations (`conf`, `calc`, `proc`)
- Names that don't indicate purpose

### Error Handling
- ✅ All operations that can fail must be wrapped in try/catch
- ✅ Use specific exception types (not generic `Exception`)
- ✅ Provide meaningful, actionable error messages
- ✅ Log errors with context (user ID, request ID, stack trace)
- ✅ Never fail silently

### Testing
- ✅ 95%+ test coverage for critical paths
- ✅ Unit tests for all business logic
- ✅ Integration tests for critical paths
- ✅ Edge cases must be covered
- ✅ Tests must be isolated and deterministic

### Performance
- ✅ No N+1 query problems
- ✅ Use async/await for I/O operations
- ✅ Implement caching where appropriate
- ✅ Optimize algorithms (avoid O(n²) where possible)
- ✅ Use connection pooling

### Documentation
- ✅ Public APIs must have docstrings
- ✅ Complex logic must be explained
- ✅ Examples provided for public APIs
- ✅ README updated when needed

---

## Project-Specific Rules

### Monorepo Structure
- ✅ Never mix `argo/` and `alpine-*/` changes in single commit
- ✅ `alpine-backend/` and `alpine-frontend/` deploy together
- ✅ Changes to `packages/` require testing ALL projects

### Trading System (Argo)
- ✅ All trades must pass 7-layer risk management
- ✅ Minimum confidence threshold: 75%
- ✅ SHA-256 verification required for all signals
- ✅ Environment-aware (dev vs prod account switching)

### Deployment
- ✅ 10 safety gates must pass before production deployment
- ✅ Code must be identical between dev and prod
- ✅ Local-only files never deployed
- ✅ Health checks required after deployment

---

## Common Issues to Flag

### Security Issues
- Hardcoded secrets or API keys
- SQL injection vulnerabilities
- XSS vulnerabilities
- Missing input validation
- Insecure authentication

### Code Smells
- Functions >50 lines
- God objects (classes doing too much)
- Long parameter lists (>4 parameters)
- Deep nesting (>4 levels)
- Magic numbers (hardcoded values)
- Code duplication

### Naming Violations
- Generic names (`data`, `temp`, `helper`)
- Abbreviations (`conf`, `calc`)
- Names that don't indicate purpose
- Inconsistent naming patterns

### Missing Requirements
- Missing error handling
- Missing tests
- Missing documentation
- Missing type hints/annotations
- Missing input validation

---

## Rules Reference

For complete rules, see:
- **Rules Directory:** `Rules/` (25+ rule files)
- **Cursor Rules:** `.cursorrules/` directory
- **Quick Reference:** `Rules/README.md`

---

## Review Priorities

### Critical (Must Fix)
- Security vulnerabilities
- Data loss risks
- Production-breaking bugs
- Missing error handling in critical paths

### High (Should Fix)
- Performance issues
- Maintainability problems
- Missing tests for critical paths
- Architectural concerns

### Medium (Nice to Fix)
- Code quality improvements
- Test coverage gaps
- Documentation gaps
- Style inconsistencies

---

**Note:** Bugbot should reference the complete rules in `Rules/` directory for detailed guidelines and examples.

