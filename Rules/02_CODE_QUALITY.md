# Code Quality Rules

**Last Updated:** January 15, 2025  
**Version:** 2.0  
**Applies To:** All projects

---

## Overview

Code quality standards, review process, and refactoring guidelines to ensure maintainable, scalable, and reliable code.

---

## Architecture & Design Principles

### SOLID Principles

#### Single Responsibility Principle (SRP)
- **Rule:** Each class/function should have one reason to change
- **Example:**
  ```python
  # BAD ❌
  class SignalProcessor:
      def generate_signal(self): pass
      def execute_trade(self): pass
      def send_email(self): pass
  
  # GOOD ✅
  class SignalGenerator:
      def generate_signal(self): pass
  
  class TradeExecutor:
      def execute_trade(self): pass
  
  class EmailService:
      def send_email(self): pass
  ```

#### Open/Closed Principle (OCP)
- **Rule:** Open for extension, closed for modification
- **Action:** Use inheritance, composition, or strategy patterns

#### Liskov Substitution Principle (LSP)
- **Rule:** Subtypes must be substitutable for their base types
- **Action:** Ensure derived classes don't break base class contracts

#### Interface Segregation Principle (ISP)
- **Rule:** Clients shouldn't depend on interfaces they don't use
- **Action:** Create specific interfaces rather than large general ones

#### Dependency Inversion Principle (DIP)
- **Rule:** Depend on abstractions, not concretions
- **Action:** Use dependency injection and interfaces

---

## Design Patterns

### When to Use Patterns

#### Factory Pattern
- **Use When:** Creating objects with complex initialization
- **Example:** Creating different trading engines based on environment

#### Strategy Pattern
- **Use When:** Multiple algorithms for the same task
- **Example:** Different position sizing strategies

#### Observer Pattern
- **Use When:** One-to-many dependency between objects
- **Example:** Signal subscribers notifying multiple handlers

#### Repository Pattern
- **Use When:** Abstracting data access
- **Example:** Database operations for signals

---

## Separation of Concerns

### Layer Boundaries

#### Presentation Layer
- **Responsibility:** User interface, API endpoints
- **Should NOT:** Contain business logic

#### Business Logic Layer
- **Responsibility:** Core functionality, rules, validation
- **Should NOT:** Know about database or UI details

#### Data Access Layer
- **Responsibility:** Database operations, data persistence
- **Should NOT:** Contain business rules

### Example:
```python
# BAD ❌ - Business logic in API endpoint
@app.post("/signals")
def create_signal(data):
    if data['confidence'] < 75:
        return {"error": "Low confidence"}
    # ... database operations here

# GOOD ✅ - Separation of concerns
@app.post("/signals")
def create_signal(data):
    signal = signal_service.create_signal(data)
    return signal

class SignalService:
    def create_signal(self, data):
        self._validate_signal(data)
        return self._repository.save(data)
```

---

## Coupling & Cohesion

### Low Coupling
- **Rule:** Modules should have minimal dependencies on each other
- **Action:** Use interfaces, dependency injection, event-driven architecture

### High Cohesion
- **Rule:** Elements within a module should be closely related
- **Action:** Group related functionality together

---

## Scalability

### Horizontal Scaling
- **Rule:** Design for stateless services
- **Action:** Store state in databases, caches, or message queues

### Resource Efficiency
- **Rule:** Optimize memory and CPU usage
- **Action:** Use connection pooling, lazy loading, caching

---

## Maintainability

### Code Readability
- **Rule:** Code should be self-documenting
- **Action:** Use descriptive names, clear structure, minimal comments

### Ease of Modification
- **Rule:** Changes should be localized
- **Action:** Follow SOLID principles, use abstractions

### Ease of Extension
- **Rule:** New features shouldn't require modifying existing code
- **Action:** Use interfaces, plugins, configuration

---

## Code Review Process

**See:** [30_CODE_REVIEW.md](30_CODE_REVIEW.md) for comprehensive code review process, PR templates, and review guidelines.

### Basic Review Checklist

#### Architecture & Design
- [ ] Follows SOLID principles
- [ ] Appropriate design patterns used
- [ ] Clear separation of concerns
- [ ] Low coupling, high cohesion
- [ ] Scalable design

#### Code Structure
- [ ] Functions under 50 lines
- [ ] Max 3-4 parameters per function
- [ ] Max 3-4 levels of nesting
- [ ] No code duplication (DRY)
- [ ] No dead code

#### Error Handling
- [ ] All operations that can fail are wrapped
- [ ] Specific exception types used
- [ ] Meaningful error messages
- [ ] Proper logging with context
- [ ] No silent failures

#### Security
- [ ] Input validation at boundaries
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] No hardcoded secrets
- [ ] Proper authentication/authorization

#### Performance
- [ ] No N+1 query problems
- [ ] Appropriate caching used
- [ ] Async operations for I/O
- [ ] Optimized algorithms (no O(n²) where avoidable)
- [ ] Connection pooling used

#### Testing
- [ ] Unit tests for business logic
- [ ] Integration tests for critical paths
- [ ] Edge cases covered
- [ ] Test isolation maintained
- [ ] 95%+ coverage for critical paths

#### Documentation
- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] Examples provided
- [ ] README updated if needed

---

## Priority Levels

### Critical
- Security vulnerabilities
- Data loss risks
- Production-breaking bugs
- Missing error handling

### High
- Performance issues
- Maintainability problems
- Missing tests for critical paths
- Architectural concerns

### Medium
- Code quality improvements
- Test coverage gaps
- Documentation gaps
- Style inconsistencies

### Low
- Minor style issues
- Optional optimizations
- Nice-to-have improvements

---

## Automatic Refactoring Suggestions

### Long Functions
- **Trigger:** Functions >50 lines
- **Action:** Extract into smaller functions
- **Example:**
  ```python
  # BAD ❌
  def process_signal(signal):
      # 80 lines of code
      pass
  
  # GOOD ✅
  def process_signal(signal):
      validated = validate_signal(signal)
      enriched = enrich_signal(validated)
      return execute_signal(enriched)
  ```

### Complex Conditionals
- **Trigger:** Deeply nested or complex conditionals
- **Action:** Extract into named functions
- **Example:**
  ```python
  # BAD ❌
  if user.is_authenticated and user.has_subscription and signal.confidence > 75 and market.is_open:
      execute_trade()
  
  # GOOD ✅
  if can_execute_trade(user, signal, market):
      execute_trade()
  ```

### Magic Numbers
- **Trigger:** Hardcoded numeric values
- **Action:** Extract to named constants
- **Example:**
  ```python
  # BAD ❌
  if confidence > 75:
      execute()
  
  # GOOD ✅
  MIN_CONFIDENCE_THRESHOLD = 75
  if confidence > MIN_CONFIDENCE_THRESHOLD:
      execute()
  ```

### Code Smells
- **God Objects:** Classes doing too much
- **Feature Envy:** Methods using other objects' data excessively
- **Long Parameter Lists:** Too many parameters
- **Data Clumps:** Groups of data that should be objects

---

## Code Quality Metrics

### Target Metrics
- **Cyclomatic Complexity:** <10 per function
- **Test Coverage:** 95%+ for critical paths, 80%+ overall
- **Code Duplication:** <3%
- **Technical Debt Ratio:** <5%

### Tools
- **Python:** pylint, mypy, coverage.py
- **TypeScript:** ESLint, TypeScript compiler, Jest coverage

---

## Refactoring Guidelines

### When to Refactor
- Before adding new features
- When fixing bugs
- During code reviews
- When code smells are detected

### Refactoring Safety
- **Rule:** Always have tests before refactoring
- **Action:** Run tests after each refactoring step
- **Goal:** Small, incremental changes

### Refactoring Checklist
- [ ] Tests pass before refactoring
- [ ] Understand the code being refactored
- [ ] Make small, incremental changes
- [ ] Run tests after each change
- [ ] Commit frequently
- [ ] Document significant changes

---

## Related Rules

- [01_DEVELOPMENT.md](01_DEVELOPMENT.md) - Development practices
- [03_TESTING.md](03_TESTING.md) - Testing requirements
- [07_SECURITY.md](07_SECURITY.md) - Security practices
- [19_CONTINUOUS_OPTIMIZATION.md](19_CONTINUOUS_OPTIMIZATION.md) - Continuous optimization and world-class excellence mindset (complements this rule)

