# Documentation Rules

**Last Updated:** January 15, 2025  
**Version:** 2.0  
**Applies To:** All projects

---

## Overview

Documentation standards, formatting, and structure to ensure clear, maintainable documentation.

---

## Documentation Types

### Code Documentation

#### Docstrings (Python)
- **Format:** Google-style or NumPy-style
- **Required For:** All public functions, classes, modules
- **Example:**
  ```python
  def calculate_position_size(
      account_balance: float,
      signal_confidence: float,
      risk_pct: float = 0.1
  ) -> float:
      """
      Calculate position size based on account balance and signal confidence.
      
      Args:
          account_balance: Total account balance in USD
          signal_confidence: Signal confidence percentage (0-100)
          risk_pct: Risk percentage per trade (default: 0.1)
      
      Returns:
          Position size in USD
      
      Raises:
          ValueError: If confidence is negative or risk_pct is invalid
      
      Example:
          >>> calculate_position_size(10000, 80, 0.1)
          800.0
      """
      return account_balance * risk_pct * (signal_confidence / 100)
  ```

#### JSDoc/TSDoc (TypeScript)
- **Format:** JSDoc with @param, @returns, @throws
- **Required For:** All public functions, classes, interfaces
- **Example:**
  ```typescript
  /**
   * Calculates position size based on account balance and signal confidence.
   * 
   * @param accountBalance - Total account balance in USD
   * @param signalConfidence - Signal confidence percentage (0-100)
   * @param riskPct - Risk percentage per trade (default: 0.1)
   * @returns Position size in USD
   * @throws {ValueError} If confidence is negative or riskPct is invalid
   * 
   * @example
   * ```typescript
   * const size = calculatePositionSize(10000, 80, 0.1);
   * // Returns: 800.0
   * ```
   */
  function calculatePositionSize(
    accountBalance: number,
    signalConfidence: number,
    riskPct: number = 0.1
  ): number {
    return accountBalance * riskPct * (signalConfidence / 100);
  }
  ```

### README Files

#### Required Sections
- **Project Description:** What the project does
- **Installation:** How to install/setup
- **Usage:** How to use the project
- **Configuration:** Configuration options
- **Development:** How to develop/contribute
- **License:** License information

#### Example Structure
```markdown
# Project Name

Brief description of what the project does.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from project import main_function

result = main_function()
```

## Configuration

See `config.json.example` for configuration options.

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for development guidelines.

## License

MIT License
```

---

## Documentation Standards

### Comments

#### Rule: Explain WHY, not WHAT
- **BAD ❌:**
  ```python
  # Increment counter
  counter += 1
  ```

- **GOOD ✅:**
  ```python
  # Increment counter to track number of signals processed
  # This is used for rate limiting and monitoring
  counter += 1
  ```

#### When to Comment
- Complex algorithms
- Non-obvious business logic
- Workarounds for bugs
- Performance optimizations
- Assumptions and limitations

### Inline Comments
- **Rule:** Use sparingly, only when necessary
- **Action:** Make code self-documenting first
- **Use For:** Complex logic that can't be simplified

---

## API Documentation

### Endpoint Documentation

#### Required Information
- **Method:** HTTP method (GET, POST, etc.)
- **Path:** Endpoint path
- **Description:** What the endpoint does
- **Parameters:** Request parameters
- **Response:** Response format
- **Errors:** Possible error responses
- **Example:** Request/response example

#### Example
```markdown
### POST /api/signals

Create a new trading signal.

**Parameters:**
- `symbol` (string, required): Stock symbol
- `confidence` (number, required): Signal confidence (0-100)
- `entry_price` (number, required): Entry price

**Response:**
```json
{
  "id": "signal_123",
  "symbol": "AAPL",
  "confidence": 85.5,
  "entry_price": 150.25,
  "created_at": "2025-01-15T10:00:00Z"
}
```

**Errors:**
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Server error
```

---

## System Documentation

**Note:** For comprehensive SystemDocs management rules, see **[17_SYSTEM_DOCUMENTATION.md](17_SYSTEM_DOCUMENTATION.md)**.

### Architecture Documentation

#### Required Sections
- **Overview:** System architecture overview
- **Components:** Major components and their roles
- **Data Flow:** How data flows through the system
- **Dependencies:** External dependencies
- **Deployment:** Deployment architecture

### Operational Documentation

#### Required Sections
- **Setup:** How to set up the system
- **Configuration:** Configuration options
- **Monitoring:** How to monitor the system
- **Troubleshooting:** Common issues and solutions
- **Maintenance:** Maintenance procedures

---

## Documentation Organization

### File Structure

```
docs/
├── InvestorDocs/          # Investor documentation
├── TechnicalDocs/         # Technical documentation
├── SystemDocs/            # System documentation
│   ├── *COMPLETE_GUIDE.md # Comprehensive guides
│   └── ...
└── README.md              # Documentation index
```

### Naming Conventions

#### Documentation Files
- **Format:** `UPPERCASE_WITH_UNDERSCORES.md` or `v1.0_01_*.md`
- **Examples:**
  - `BACKTESTING_COMPLETE_GUIDE.md`
  - `v2.0_01_executive_summary.md`
  - `DEPLOYMENT_GUIDE.md`

#### Versioning
- **Format:** `v{major}.{minor}_{number}_{name}.md`
- **Examples:**
  - `v1.0_01_executive_summary.md`
  - `v2.0_01_executive_summary.md`

---

## Documentation Best Practices

### DO
- ✅ Document all public APIs
- ✅ Include examples in documentation
- ✅ Keep documentation up to date
- ✅ Use clear, concise language
- ✅ Include diagrams when helpful
- ✅ Document assumptions and limitations
- ✅ Provide troubleshooting guides
- ✅ Update documentation with code changes

### DON'T
- ❌ Document obvious code
- ❌ Leave outdated documentation
- ❌ Use jargon without explanation
- ❌ Skip examples
- ❌ Document implementation details (unless necessary)
- ❌ Forget to update documentation

---

## Documentation Maintenance

### When to Update
- **Code Changes:** Update docs when code changes
- **New Features:** Document new features immediately
- **Bug Fixes:** Update docs if behavior changes
- **Configuration Changes:** Update config documentation

### Review Process
- **Rule:** Review documentation during code review
- **Action:** Ensure docs match code
- **Check:** Examples still work

---

## Related Rules

- [01_DEVELOPMENT.md](01_DEVELOPMENT.md) - Development practices
- [09_WORKSPACE.md](09_WORKSPACE.md) - Workspace organization
- [17_SYSTEM_DOCUMENTATION.md](17_SYSTEM_DOCUMENTATION.md) - SystemDocs management (specific to docs/SystemDocs/)

