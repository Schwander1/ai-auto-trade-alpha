# Development Rules

**Last Updated:** January 15, 2025  
**Version:** 2.0  
**Applies To:** All projects (Argo Capital, Alpine Analytics LLC Backend, Alpine Analytics LLC Frontend)

---

## Overview

Core development practices, coding standards, and **automatic naming conventions** that apply across all projects. Naming conventions are **MANDATORY** and **automatically enforced** - code that doesn't follow these standards will be rejected.

**Strategic Context:** All development decisions should align with strategic goals defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md).

**Context Reference:** For understanding recent development decisions and context, see [23_CONVERSATION_LOGGING.md](23_CONVERSATION_LOGGING.md). Conversation logs (LOCAL ONLY) may contain recent decisions and implementation details that provide context for current work.

---

## Naming Conventions (MANDATORY - AUTOMATIC ENFORCEMENT)

### Core Principle: Obvious and Self-Documenting

**Rule:** All names must be **obvious** and **self-documenting**. A developer should understand what something does just by reading its name.

**Enforcement:** 
- Code reviews MUST reject code that doesn't follow naming conventions
- Linters MUST flag naming violations
- Automated checks MUST verify naming compliance

### Python (Argo, Alpine Backend)

#### Functions
- **Format:** `snake_case` with `verb_noun` pattern
- **Examples:**
  ```python
  def calculate_total()
  def fetch_user_data()
  def validate_signal()
  def execute_trade()
  ```

#### Classes
- **Format:** `PascalCase` with `Noun` or `NounVerb` pattern
- **Examples:**
  ```python
  class SignalGenerationService
  class PaperTradingEngine
  class WeightedConsensusEngine
  class UserService
  ```

#### Variables
- **Format:** `snake_case` with descriptive names
- **Examples:**
  ```python
  user_count = 10
  is_authenticated = True
  signal_confidence = 0.95
  account_balance = 10000.0
  ```

#### Constants
- **Format:** `UPPER_SNAKE_CASE`
- **Examples:**
  ```python
  MAX_RETRY_ATTEMPTS = 3
  API_TIMEOUT_SECONDS = 30
  DEFAULT_POSITION_SIZE_PCT = 10
  MIN_CONFIDENCE_THRESHOLD = 75.0
  ```

#### Modules/Packages
- **Format:** `snake_case`
- **Examples:**
  ```python
  signal_generation_service.py
  paper_trading_engine.py
  weighted_consensus_engine.py
  ```

### TypeScript/JavaScript (Alpine Frontend)

#### Files
- **Format:** `kebab-case.tsx` or `kebab-case.ts`
- **Examples:**
  ```typescript
  signal-card.tsx
  dashboard-layout.tsx
  use-websocket.ts
  api-client.ts
  ```

#### Components
- **Format:** `PascalCase`
- **Examples:**
  ```typescript
  export default function SignalCard() {}
  export function DashboardLayout() {}
  export function UserProfile() {}
  ```

#### Functions
- **Format:** `camelCase`
- **Examples:**
  ```typescript
  function calculateConfidence() {}
  const fetchSignalData = async () => {}
  const validateInput = (value: string) => {}
  ```

#### Variables
- **Format:** `camelCase`
- **Examples:**
  ```typescript
  const signalList = []
  const isLoading = false
  const userCount = 10
  ```

#### Constants
- **Format:** `UPPER_SNAKE_CASE`
- **Examples:**
  ```typescript
  const API_ENDPOINT = 'https://api.alpineanalytics.com'
  const MAX_RETRY_ATTEMPTS = 3
  const DEFAULT_TIMEOUT_MS = 5000
  ```

#### Types/Interfaces
- **Format:** `PascalCase`
- **Examples:**
  ```typescript
  interface SignalData {}
  type UserRole = 'free' | 'pro' | 'premium'
  type SignalStatus = 'pending' | 'active' | 'closed'
  ```

#### Boolean Variables
- **Format:** `camelCase` with `is/has/should` prefix
- **Examples:**
  ```typescript
  const isAuthenticated = true
  const hasSubscription = false
  const shouldShowModal = true
  const canTrade = false
  ```

---

## Uniform Naming Standards (AUTOMATIC ENFORCEMENT)

### Naming Pattern Quick Reference

#### Python Functions
**Pattern:** `verb_noun` or `verb_noun_adjective`
- ✅ `calculate_position_size()` - Clear action and object
- ✅ `validate_signal_confidence()` - Clear validation target
- ✅ `fetch_user_data()` - Clear data retrieval
- ❌ `process()` - Too vague (REJECT)
- ❌ `do_stuff()` - Not descriptive (REJECT)
- ❌ `calc()` - Abbreviation unclear (REJECT)

**Enforcement:** Reject any function name that doesn't clearly indicate action and object.

#### Python Classes
**Pattern:** `Noun` or `NounVerb` (Service, Manager, Engine, Handler)
- ✅ `SignalGenerationService` - Clear purpose
- ✅ `RiskManager` - Clear management role
- ✅ `PaperTradingEngine` - Clear engine type
- ❌ `Helper` - Too generic (REJECT)
- ❌ `Utils` - Not descriptive (REJECT)
- ❌ `MyClass` - Meaningless (REJECT)

**Enforcement:** Reject any class name that doesn't clearly indicate purpose.

#### Variables
**Pattern:** `noun` or `adjective_noun` (descriptive, no abbreviations)
- ✅ `signal_confidence` - Clear what it represents
- ✅ `account_balance` - Clear financial value
- ✅ `is_trading_enabled` - Clear boolean state
- ❌ `conf` - Abbreviation unclear (REJECT)
- ❌ `data` - Too generic (REJECT)
- ❌ `temp` - Meaningless (REJECT)

**Enforcement:** Reject any variable name that uses abbreviations or is too generic.

#### Constants
**Pattern:** `CATEGORY_SPECIFIC_NAME`
- ✅ `MAX_POSITION_SIZE_PCT` - Clear maximum value
- ✅ `MIN_CONFIDENCE_THRESHOLD` - Clear minimum threshold
- ✅ `API_TIMEOUT_SECONDS` - Clear timeout value
- ❌ `MAX_SIZE` - What size? (REJECT)
- ❌ `THRESHOLD` - What threshold? (REJECT)
- ❌ `TIMEOUT` - What timeout? (REJECT)

**Enforcement:** Reject any constant name that doesn't include category and specific name.

#### Files and Modules
**Pattern:** `feature_purpose` or `component_type`
- ✅ `signal_generation_service.py` - Clear service purpose
- ✅ `risk_manager.py` - Clear management component
- ✅ `paper_trading_engine.py` - Clear engine type
- ❌ `utils.py` - Too generic (REJECT)
- ❌ `helpers.py` - Not descriptive (REJECT)
- ❌ `misc.py` - Meaningless (REJECT)

**Enforcement:** Reject any file name that is too generic or doesn't indicate purpose.

### Naming by Feature/Component

#### Trading Components
- `*_trading_engine.py` - Trading execution
- `*_order_manager.py` - Order management
- `*_position_manager.py` - Position tracking
- `*_risk_manager.py` - Risk management

#### Signal Components
- `*_signal_generator.py` - Signal generation
- `*_signal_tracker.py` - Signal tracking
- `*_signal_validator.py` - Signal validation

#### Data Components
- `*_data_source.py` - Data source integration
- `*_data_aggregator.py` - Data aggregation
- `*_data_validator.py` - Data validation

### Boolean Naming

**Pattern:** `is_*`, `has_*`, `should_*`, `can_*`, `will_*`
- ✅ `is_trading_enabled` - Clear state
- ✅ `has_active_positions` - Clear possession
- ✅ `should_execute_trade` - Clear decision
- ✅ `can_place_order` - Clear capability
- ❌ `trading` - Ambiguous (REJECT)
- ❌ `active` - Not clear what's active (REJECT)

**Enforcement:** Reject any boolean variable that doesn't use proper prefix.

### Collection Naming

**Pattern:** `noun_plural` or `noun_list`, `noun_dict`
- ✅ `signals` - Clear collection
- ✅ `user_list` - Clear list type
- ✅ `position_dict` - Clear dictionary type
- ❌ `data` - Too generic (REJECT)
- ❌ `items` - Not descriptive (REJECT)

**Enforcement:** Reject any collection name that is too generic.

### Function Parameter Naming

**Pattern:** Match variable naming, be explicit
- ✅ `signal: Signal` - Clear type and purpose
- ✅ `account_balance: float` - Clear financial value
- ✅ `min_confidence: float = 75.0` - Clear threshold
- ❌ `s: Signal` - Abbreviation unclear (REJECT)
- ❌ `val: float` - Too generic (REJECT)

**Enforcement:** Reject any parameter name that uses abbreviations or is too generic.

### Automatic Naming Validation

**Rule:** Before accepting any code:
1. **Check function names** - Must follow `verb_noun` pattern
2. **Check class names** - Must follow `Noun` or `NounVerb` pattern
3. **Check variable names** - Must be descriptive, no abbreviations
4. **Check constant names** - Must include category and specific name
5. **Check file names** - Must indicate feature/purpose
6. **Check boolean names** - Must use proper prefix
7. **Check collection names** - Must be descriptive

**Rejection Criteria:**
- Any name that is too generic
- Any name that uses abbreviations
- Any name that doesn't indicate purpose
- Any name that is ambiguous

---

## Code Structure

### Function Size
- **Ideal:** Under 20-30 lines
- **Maximum:** 50 lines
- **If longer:** Extract into smaller functions

### Parameters
- **Maximum:** 3-4 parameters
- **If more:** Use objects/dictionaries/configuration objects
- **Example:**
  ```python
  # BAD ❌
  def create_user(name, email, password, role, status, created_at, updated_at):
      pass
  
  # GOOD ✅
  def create_user(user_data: UserData):
      pass
  ```

### Nesting
- **Maximum:** 3-4 levels deep
- **If deeper:** Extract functions to reduce depth
- **Example:**
  ```python
  # BAD ❌
  if condition1:
      if condition2:
          if condition3:
              if condition4:
                  do_something()
  
  # GOOD ✅
  if all_conditions_met():
      do_something()
  ```

### DRY Principle
- **Rule:** Eliminate code duplication
- **Action:** Extract common logic into reusable functions
- **Example:**
  ```python
  # BAD ❌
  def validate_signal_1():
      if signal.confidence < 75:
          raise ValueError("Low confidence")
  
  def validate_signal_2():
      if signal.confidence < 75:
          raise ValueError("Low confidence")
  
  # GOOD ✅
  def validate_confidence(signal, threshold=75):
      if signal.confidence < threshold:
          raise ValueError(f"Low confidence: {signal.confidence}")
  ```

---

## Code Style & Formatting

### Python
- **Style Guide:** PEP 8
- **Formatter:** Black (88-100 char line length)
- **Linter:** Ruff, mypy
- **Indentation:** 4 spaces
- **Line Length:** 88-100 characters

### TypeScript/JavaScript
- **Style Guide:** Airbnb Style Guide
- **Formatter:** Prettier (100-120 char line length)
- **Linter:** ESLint
- **Indentation:** 2 spaces
- **Line Length:** 100-120 characters

### Type Hints/Annotations
- **Python:** Required for all function parameters and return values
- **TypeScript:** Strict mode enabled, no `any` types
- **Example:**
  ```python
  def calculate_position_size(
      account_balance: float,
      signal_confidence: float,
      risk_pct: float = 0.1
  ) -> float:
      return account_balance * risk_pct * (signal_confidence / 100)
  ```

---

## Error Handling

**See:** [29_ERROR_HANDLING.md](29_ERROR_HANDLING.md) for comprehensive error handling rules, resilience patterns, and recovery strategies.

### Basic Error Handling

### Comprehensive Coverage
- **Rule:** Implement try-catch blocks for all operations that can fail
- **Why:** Prevents unhandled exceptions and improves reliability

### Specific Exceptions
- **Rule:** Use specific exception types, not generic `Exception` or `Error`
- **Python Examples:**
  ```python
  # BAD ❌
  try:
      value = int(input)
  except Exception:
      pass
  
  # GOOD ✅
  try:
      value = int(input)
  except ValueError:
      logger.error(f"Invalid integer: {input}")
  except TypeError:
      logger.error(f"Invalid type: {type(input)}")
  ```

### Error Messages
- **Rule:** Provide meaningful, actionable error messages with context
- **Example:**
  ```python
  # BAD ❌
  raise ValueError("Error")
  
  # GOOD ✅
  raise ValueError(
      f"Signal confidence {signal.confidence}% below minimum threshold "
      f"{MIN_CONFIDENCE_THRESHOLD}% for symbol {signal.symbol}"
  )
  ```

### Logging
- **Rule:** Log errors appropriately with context
- **Include:** User ID, request ID, stack trace, relevant data
- **Example:**
  ```python
  try:
      execute_trade(signal)
  except TradeExecutionError as e:
      logger.error(
          f"Trade execution failed for signal {signal.id}",
          extra={
              "signal_id": signal.id,
              "symbol": signal.symbol,
              "error": str(e),
              "traceback": traceback.format_exc()
          }
      )
      raise
  ```

### Never Fail Silently
- **Rule:** Always handle errors explicitly
- **Action:** Log or propagate appropriately
- **Never:** Use bare `except:` or ignore errors

---

## Input Validation

### System Boundaries
- **Rule:** Validate all inputs at system boundaries
- **Locations:** API endpoints, function parameters, user inputs
- **Example:**
  ```python
  def execute_trade(signal: Signal) -> TradeResult:
      # Validate at function entry
      if not signal:
          raise ValueError("Signal cannot be None")
      if signal.confidence < MIN_CONFIDENCE_THRESHOLD:
          raise ValueError(f"Confidence too low: {signal.confidence}")
      if not signal.symbol:
          raise ValueError("Symbol is required")
      
      # Proceed with execution
      return _execute_trade_internal(signal)
  ```

---

## Dead Code Removal

### What to Remove
- Unused imports
- Commented-out code
- Unreachable code paths
- Unused variables
- Unused functions/classes

### Before Committing
- **Rule:** Remove all dead code
- **Why:** Reduces confusion and maintenance burden

---

## Version Control

### Commit Messages
- **Format:** Conventional Commits
- **Pattern:** `type(scope): description`
- **Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`
- **Examples:**
  ```
  feat(signals): add confidence threshold validation
  fix(trading): resolve position sizing calculation error
  docs(api): update endpoint documentation
  refactor(risk): extract correlation check into separate function
  test(signals): add unit tests for signal generation
  ```

### Atomic Commits
- **Rule:** Keep commits atomic and focused
- **One logical change per commit**
- **Why:** Easier to review, revert, and understand history

### Issue References
- **Rule:** Reference issue/ticket numbers in commits
- **Format:** `fix(auth): resolve login issue (#123)`

### Never Commit
- Credentials
- API keys
- Passwords
- Personal information
- Large binaries (use Git LFS or external storage)

---

## Dependencies

### Updates
- **Rule:** Keep dependencies up to date
- **Action:** Regularly audit for security vulnerabilities

### Security Audits
- **Python:** `pip-audit`, `safety`
- **Node.js:** `npm audit`
- **Frequency:** Before each release

### Minimal Dependencies
- **Rule:** Avoid unnecessary dependencies
- **Prefer:** Standard library when possible
- **Why:** Reduces attack surface and maintenance burden

### Version Pinning
- **Rule:** Pin versions for reproducibility
- **Files:** `requirements.txt`, `package-lock.json`
- **Why:** Ensures consistent builds across environments

---

## Performance Considerations

### Database Queries
- **Rule:** Optimize queries, avoid N+1 problems
- **Action:** Use eager loading where appropriate

### Async Operations
- **Rule:** Use async/await for I/O operations
- **Applies To:** Database calls, API calls, file operations
- **Example:**
  ```python
  # GOOD ✅
  async def fetch_signals():
      async with aiohttp.ClientSession() as session:
          async with session.get(API_URL) as response:
              return await response.json()
  ```

### Loop Optimization
- **Rule:** Avoid unnecessary computations in loops
- **Action:** Move invariants outside loops

### Complexity
- **Rule:** Consider time and space complexity
- **Action:** Optimize O(n²) or worse algorithms

---

## Quick Reference

### Python Checklist
- [ ] Functions use `snake_case`
- [ ] Classes use `PascalCase`
- [ ] Constants use `UPPER_SNAKE_CASE`
- [ ] Type hints on all functions
- [ ] Functions under 50 lines
- [ ] Specific exception handling
- [ ] Meaningful error messages
- [ ] No dead code

### TypeScript Checklist
- [ ] Files use `kebab-case`
- [ ] Components use `PascalCase`
- [ ] Functions use `camelCase`
- [ ] No `any` types
- [ ] Strict mode enabled
- [ ] Proper error handling
- [ ] No dead code

---

**Related Rules:**
- [02_CODE_QUALITY.md](02_CODE_QUALITY.md) - Code quality standards
- [03_TESTING.md](03_TESTING.md) - Testing requirements
- [07_SECURITY.md](07_SECURITY.md) - Security practices
- [12A_ARGO_BACKEND.md](12A_ARGO_BACKEND.md) - Argo Capital backend practices
- [12B_ALPINE_BACKEND.md](12B_ALPINE_BACKEND.md) - Alpine Analytics LLC backend practices
- [11_FRONTEND.md](11_FRONTEND.md) - Frontend-specific practices

