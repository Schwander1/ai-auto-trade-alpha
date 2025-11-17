# Configuration Management Rules

**Last Updated:** January 15, 2025  
**Version:** 2.0  
**Applies To:** All projects

---

## Overview

Configuration management rules to ensure consistent, correct settings across dev and production environments.

---

## Configuration Sources

**See:** [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) for environment-specific configuration details

### Priority Order

1. **AWS Secrets Manager** (production, environment-specific secrets)
2. **Environment Variables** (fallback)
3. **config.json** (development/local)

### Automatic Source Selection

**Rule:** Configuration source is automatically selected based on environment
- Production: AWS Secrets Manager (primary)
- Development: `config.json` (local file)
- Fallback: Environment variables (both environments)

---

## Configuration Structure

### Argo Configuration (`argo/config.json`)

```json
{
  "trading": {
    "auto_execute": true,
    "min_confidence": 75.0,
    "consensus_threshold": 75.0,
    "profit_target": 0.05,
    "stop_loss": 0.03,
    "position_size_pct": 10,
    "max_position_size_pct": 15,
    "max_correlated_positions": 3,
    "max_drawdown_pct": 10,
    "daily_loss_limit_pct": 5.0
  },
  "alpaca": {
    "dev": {
      "api_key": "...",
      "secret_key": "...",
      "base_url": "https://paper-api.alpaca.markets"
    },
    "production": {
      "api_key": "FROM_AWS_SECRETS",
      "secret_key": "FROM_AWS_SECRETS",
      "base_url": "https://paper-api.alpaca.markets"
    }
  },
  "strategy": {
    "use_multi_source": true,
    "weight_massive": 0.4,
    "weight_alpha_vantage": 0.25,
    "weight_x_sentiment": 0.2,
    "weight_sonar": 0.15
  },
  "xai": {
    "api_key": "...",
    "enabled": true
  },
  "sonar": {
    "api_key": "...",
    "enabled": true
  },
  "massive": {
    "api_key": "...",
    "enabled": true
  },
  "alpha_vantage": {
    "api_key": "...",
    "enabled": true
  }
}
```

---

## Configuration Validation

### Required Fields

#### Trading Configuration
- `min_confidence`: Minimum signal confidence (0-100)
- `consensus_threshold`: Consensus requirement (0-100)
- `profit_target`: Profit target percentage (0-1)
- `stop_loss`: Stop loss percentage (0-1)
- `position_size_pct`: Default position size (0-100)
- `max_position_size_pct`: Maximum position size (0-100)

#### Alpaca Configuration
- `api_key`: Alpaca API key
- `secret_key`: Alpaca secret key
- `base_url`: Alpaca API base URL
- `paper`: Paper trading mode (true/false)

#### Data Source API Keys
- `xai.api_key`: xAI Grok API key (Option 2B optimized)
- `sonar.api_key`: Perplexity Sonar AI API key
- `massive.api_key`: Massive.com (Polygon.io) API key
- `alpha_vantage.api_key`: Alpha Vantage API key
- All data sources support `enabled: true/false` flag

### Validation Rules

#### Strategy Weights
- **Rule:** Weights should sum to ~1.0
- **Tolerance:** ±0.05
- **Action:** Normalize if needed

#### Trading Parameters
- **Rule:** All percentages must be positive
- **Rule:** `profit_target` > `stop_loss`
- **Rule:** `max_position_size_pct` >= `position_size_pct`

---

## Secrets Management

### AWS Secrets Manager

#### Setup
```bash
# Run setup script
./argo/scripts/setup_aws_secrets_manager.sh

# Or manually add secrets
python argo/scripts/add_alpaca_secrets_to_aws.py
```

#### Secret Names
- `argo/alpaca/dev/api_key`
- `argo/alpaca/dev/secret_key`
- `argo/alpaca/production/api_key`
- `argo/alpaca/production/secret_key`

#### Access Pattern
```python
# ⚠️ DEPRECATED: packages/shared violates entity separation (Rule 10)
# Each entity should have its own secrets_manager implementation
# from packages.shared.utils.secrets_manager import get_secret

# Get secret (with caching and fallback)
api_key = get_secret("argo/alpaca/production/api_key")
```

### Never Commit
- ❌ Actual `config.json` files with secrets
- ❌ `.env` files with secrets
- ❌ Hardcoded API keys
- ❌ Database passwords
- ❌ JWT secrets

### Always Commit
- ✅ `config.json.example` (template)
- ✅ `.env.example` (template)
- ✅ Documentation of required secrets

---

## Configuration Loading

### Pattern

```python
def load_config():
    env = detect_environment()
    
    # Load base config
    config = load_config_file("config.json")
    
    # Override with environment-specific values
    if env == "production":
        config["alpaca"]["production"]["api_key"] = get_secret(
            "argo/alpaca/production/api_key"
        )
    else:
        # Development: use config.json
        pass
    
    # Validate configuration
    validate_config(config)
    
    return config
```

---

## Configuration Best Practices

### DO
- ✅ Use `config.json.example` as template
- ✅ Validate all configuration on load
- ✅ Use environment-specific overrides
- ✅ Store secrets in AWS Secrets Manager (production)
- ✅ Document all configuration options
- ✅ Provide sensible defaults

### DON'T
- ❌ Commit actual secrets
- ❌ Hardcode configuration values
- ❌ Use production config in development
- ❌ Skip configuration validation
- ❌ Store secrets in code

---

## Configuration Documentation

### Required Documentation

#### For Each Configuration Option
- **Name:** Configuration key
- **Type:** Data type (string, number, boolean)
- **Default:** Default value
- **Description:** What it does
- **Range:** Valid values (if applicable)
- **Environment:** Dev/Prod/Both

### Example

```markdown
### min_confidence
- **Type:** float
- **Default:** 75.0
- **Description:** Minimum signal confidence percentage required for trade execution
- **Range:** 0.0 - 100.0
- **Environment:** Both
```

---

## Configuration Changes

### Making Changes

1. **Update `config.json.example`** with new option
2. **Update documentation** explaining the option
3. **Add validation** for the new option
4. **Test in development** first
5. **Deploy to production** with new default or secret

### Breaking Changes

- **Rule:** Avoid breaking changes when possible
- **Action:** Support old and new format during transition
- **Deprecation:** Mark old options as deprecated, remove in next major version

---

## Related Rules

- [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) - Environment-specific configuration
- [05_ENVIRONMENT.md](05_ENVIRONMENT.md) - Environment management
- [07_SECURITY.md](07_SECURITY.md) - Security practices
- [04_DEPLOYMENT.md](04_DEPLOYMENT.md) - Deployment procedures

