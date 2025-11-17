# Testing Rules

**Last Updated:** January 15, 2025  
**Version:** 2.0  
**Applies To:** All projects

---

## Overview

Testing requirements, coverage standards, and test organization to ensure code reliability and prevent regressions.

---

## Test Coverage Requirements

### Minimum Coverage
- **Critical Paths:** 95%+ coverage required
- **Overall Codebase:** 80%+ coverage required
- **New Code:** 100% coverage required (no exceptions)

### What to Test
- **Business Logic:** All business rules and calculations
- **Error Handling:** All error paths and edge cases
- **API Endpoints:** All endpoints with various inputs
- **Critical Functions:** All functions that affect trading or user data

### What NOT to Test
- **Third-party libraries:** Assume they work correctly
- **Framework code:** Test your code, not the framework
- **Trivial getters/setters:** Unless they contain logic

---

## Test Types

### Unit Tests
- **Purpose:** Test individual functions/methods in isolation
- **Scope:** Single function or class
- **Dependencies:** Mocked or stubbed
- **Speed:** Fast (<100ms per test)
- **Example:**
  ```python
  def test_calculate_position_size():
      balance = 10000.0
      confidence = 80.0
      risk_pct = 0.1
      
      result = calculate_position_size(balance, confidence, risk_pct)
      
      assert result == 800.0
  ```

### Integration Tests
- **Purpose:** Test interactions between components
- **Scope:** Multiple components working together
- **Dependencies:** Real databases, APIs (or test doubles)
- **Speed:** Moderate (<1s per test)
- **Example:**
  ```python
  def test_signal_generation_flow():
      # Test signal generation with real data sources
      signal = signal_service.generate_signal("AAPL")
      assert signal.symbol == "AAPL"
      assert signal.confidence > 0
  ```

### End-to-End (E2E) Tests
- **Purpose:** Test complete user flows
- **Scope:** Entire system from user action to result
- **Dependencies:** Full stack (test environment)
- **Speed:** Slow (<10s per test)
- **Example:**
  ```python
  def test_user_can_subscribe_and_receive_signals():
      # Test complete subscription and signal delivery flow
      user = create_user()
      subscribe(user, "premium")
      signal = generate_signal()
      assert signal_delivered_to_user(user, signal)
  ```

---

## Test Organization

### File Structure

#### Python
```
tests/
├── unit/
│   ├── test_signal_generation.py
│   ├── test_risk_management.py
│   └── test_position_sizing.py
├── integration/
│   ├── test_trading_flow.py
│   └── test_api_endpoints.py
└── e2e/
    └── test_user_journey.py
```

#### TypeScript
```
__tests__/
├── unit/
│   ├── signal-card.test.tsx
│   └── utils.test.ts
├── integration/
│   └── api.test.ts
└── e2e/
    └── dashboard.spec.ts
```

### Naming Conventions

#### Test Files
- **Python:** `test_*.py` or `*_test.py`
- **TypeScript:** `*.test.ts`, `*.test.tsx`, `*.spec.ts`

#### Test Functions
- **Format:** `test_should_[expected_behavior]_when_[condition]`
- **Examples:**
  ```python
  def test_should_return_error_when_confidence_too_low():
      pass
  
  def test_should_execute_trade_when_all_conditions_met():
      pass
  
  def test_should_reject_order_when_insufficient_balance():
      pass
  ```

---

## Test Data

### Test Fixtures
- **Rule:** Use factories, fixtures, or mocks for test data
- **Avoid:** Hardcoded values in tests
- **Example:**
  ```python
  # GOOD ✅
  @pytest.fixture
  def sample_signal():
      return Signal(
          symbol="AAPL",
          confidence=85.0,
          entry_price=150.0
      )
  
  def test_signal_validation(sample_signal):
      assert validate_signal(sample_signal) == True
  ```

### Test Isolation
- **Rule:** Tests must be independent and repeatable
- **Action:** Reset state between tests
- **Never:** Depend on test execution order

### Mocking
- **Rule:** Mock external dependencies
- **Use For:** APIs, databases, file systems, time
- **Example:**
  ```python
  @patch('alpaca.tradeapi.REST')
  def test_execute_trade(mock_alpaca):
      mock_alpaca.return_value.submit_order.return_value = {"id": "123"}
      result = execute_trade(signal)
      assert result.order_id == "123"
  ```

---

## Edge Cases & Boundary Conditions

### What to Test

#### Boundary Values
- **Min/Max:** Test at boundaries (0, 1, max, min)
- **Example:**
  ```python
  def test_position_sizing_boundaries():
      # Test minimum
      assert calculate_position_size(0, 75, 0.1) == 0
      # Test maximum
      assert calculate_position_size(1000000, 100, 1.0) <= MAX_POSITION_SIZE
  ```

#### Invalid Inputs
- **Null/None:** Test with None values
- **Empty:** Test with empty strings/lists
- **Wrong Types:** Test with incorrect types
- **Example:**
  ```python
  def test_validate_signal_invalid_inputs():
      with pytest.raises(ValueError):
          validate_signal(None)
      with pytest.raises(ValueError):
          validate_signal("")
      with pytest.raises(TypeError):
          validate_signal(123)
  ```

#### Error Conditions
- **Network Failures:** Test API failures
- **Database Errors:** Test DB connection issues
- **Permission Errors:** Test authorization failures
- **Example:**
  ```python
  def test_trade_execution_handles_api_failure():
      with patch('alpaca.tradeapi.REST') as mock_api:
          mock_api.side_effect = APIError("Connection failed")
          with pytest.raises(TradeExecutionError):
              execute_trade(signal)
  ```

---

## Test Quality Standards

### Test Readability
- **Rule:** Tests should be self-documenting
- **Action:** Use descriptive names and clear structure
- **Structure:** Arrange-Act-Assert (AAA) pattern

### Test Maintainability
- **Rule:** Tests should be easy to update
- **Action:** Use fixtures, factories, and helper functions
- **Avoid:** Duplication between tests

### Test Performance
- **Rule:** Tests should run quickly
- **Target:** Unit tests <100ms, Integration <1s, E2E <10s
- **Action:** Use mocks, avoid real I/O where possible

---

## Test Execution

### Running Tests

#### Python (pytest)
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_signal_generation.py

# Run with coverage
pytest --cov=argo --cov-report=html

# Run specific test
pytest tests/unit/test_signal_generation.py::test_should_validate_signal
```

#### TypeScript (Jest)
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test signal-card.test.tsx

# Run in watch mode
npm test -- --watch
```

### Continuous Integration
- **Rule:** All tests must pass before merge
- **Action:** Run full test suite on CI/CD
- **Coverage:** Enforce minimum coverage thresholds

---

## Test Documentation

### Test Descriptions
- **Rule:** Describe what the test verifies
- **Format:** Clear, concise description
- **Example:**
  ```python
  def test_should_reject_trade_when_daily_loss_limit_exceeded():
      """
      Verifies that trades are rejected when the daily loss limit
      has been exceeded, preventing further losses.
      """
      # Test implementation
  ```

### Test Examples
- **Rule:** Include examples in test documentation
- **Action:** Show expected behavior with examples

---

## Testing Best Practices

### DO
- ✅ Write tests before fixing bugs (regression tests)
- ✅ Test one thing per test
- ✅ Use descriptive test names
- ✅ Keep tests simple and focused
- ✅ Mock external dependencies
- ✅ Test edge cases and error conditions
- ✅ Maintain test data separately
- ✅ Run tests frequently

### DON'T
- ❌ Test implementation details
- ❌ Write tests that depend on each other
- ❌ Use real APIs/databases in unit tests
- ❌ Ignore failing tests
- ❌ Write tests that are hard to understand
- ❌ Skip tests for "simple" code
- ❌ Commit code without tests

---

## Test Coverage Tools

### Python
- **Tool:** coverage.py
- **Command:** `pytest --cov=argo --cov-report=html`
- **Report:** HTML report in `htmlcov/`

### TypeScript
- **Tool:** Jest coverage
- **Command:** `npm test -- --coverage`
- **Report:** Coverage report in `coverage/`

---

## Related Rules

- [01_DEVELOPMENT.md](01_DEVELOPMENT.md) - Development practices
- [02_CODE_QUALITY.md](02_CODE_QUALITY.md) - Code quality standards
- [07_SECURITY.md](07_SECURITY.md) - Security practices

