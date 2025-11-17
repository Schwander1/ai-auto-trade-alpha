# Complete Configuration Management Guide

**Date:** January 15, 2025  
**Version:** 2.0  
**Status:** Complete Implementation Guide

---

## Executive Summary

This document provides a comprehensive guide to configuration management in the Argo-Alpine system. It explains how configuration works, how to manage it across environments, what affects what, and how to prevent configuration-related issues.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Configuration Structure](#configuration-structure)
3. [Environment Management](#environment-management)
4. [Configuration Parameters](#configuration-parameters)
5. [What Affects What](#what-affects-what)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## System Overview

### Purpose

Configuration management ensures **consistent, correct settings** across dev and production environments while preventing configuration-related issues.

### Key Features

- **Environment-Aware**: Automatic dev/prod detection
- **Centralized**: Single config.json file
- **Secure**: AWS Secrets Manager for production
- **Validated**: Configuration validation on startup
- **Versioned**: Configuration changes tracked

---

## Configuration Structure

### File Location

**Primary**: `argo/config.json`

**Fallback Order**:
1. Environment variable: `ARGO_CONFIG_PATH`
2. Production path: `/root/argo-production/config.json`
3. Dev path: `argo/config.json` (workspace root)

### Configuration Sections

```json
{
  "massive": { "api_key": "...", "enabled": true },
  "alpha_vantage": { "api_key": "...", "enabled": true },
  "x_api": { "bearer_token": "...", "enabled": true },
  "sonar": { "api_key": "...", "enabled": true },
  "alpaca": {
    "dev": { "api_key": "...", "secret_key": "...", "paper": true },
    "production": { "api_key": "...", "secret_key": "...", "paper": true }
  },
  "strategy": {
    "use_multi_source": true,
    "weight_massive": 0.40,
    "weight_alpha_vantage": 0.25,
    "weight_x_sentiment": 0.20,
    "weight_sonar": 0.15
  },
  "trading": {
    "min_confidence": 75.0,
    "consensus_threshold": 75.0,
    "profit_target": 0.05,
    "stop_loss": 0.03,
    "position_size_pct": 10,
    "max_position_size_pct": 15,
    "max_correlated_positions": 3,
    "max_drawdown_pct": 10,
    "daily_loss_limit_pct": 5.0,
    "auto_execute": true,
    "use_limit_orders": false,
    "limit_order_offset_pct": 0.001,
    "max_retry_attempts": 3,
    "retry_delay_seconds": 1,
    "enable_position_monitoring": true,
    "enable_performance_tracking": true
  },
  "backtest": {
    "data_source": "yfinance",
    "data_path": "argo/data/historical",
    "cache_enabled": true,
    "symbols": { "stocks": [...], "crypto": [...] },
    "walk_forward": { "enabled": true, "train_days": 252, "test_days": 63, "step_days": 21 },
    "optimization": { "enabled": true, "method": "grid_search", "max_iterations": 1000 },
    "metrics": { "include_advanced": true, "regime_analysis": true, "monte_carlo_runs": 1000 },
    "execution": { "slippage_pct": 0.001, "commission_pct": 0.001 }
  }
}
```

---

## Environment Management

### Environment Detection

**Process**:
1. Check `ENV` environment variable
2. Check file path (contains "production" or "dev")
3. Check hostname
4. Default to "development"

**Priority Order**:
1. Environment variable: `ENV=production` or `ENV=development`
2. File path: `/root/argo-production/` → production
3. Hostname: Contains "prod" → production
4. Default: development

**Code**: `argo/argo/core/environment.py`

---

### Configuration Loading

**Process**:
1. Detect environment
2. Load config.json
3. Select Alpaca account (dev or production)
4. Load AWS Secrets Manager (production)
5. Fallback to config.json if secrets not available

**Fallback Chain**:
1. AWS Secrets Manager (production)
2. config.json (dev/production)
3. Environment variables
4. Defaults (hardcoded)

---

## Configuration Parameters

### Data Source Configuration

**Section**: `massive`, `alpha_vantage`, `x_api`, `sonar`

**Parameters**:
- `api_key` / `bearer_token`: API credentials
- `enabled`: Enable/disable source (true/false)

**What Affects**: Signal generation quality, data availability

**How to Change**: Update in config.json, restart service

---

### Alpaca Configuration

**Section**: `alpaca.dev` and `alpaca.production`

**Parameters**:
- `api_key`: Alpaca API key
- `secret_key`: Alpaca secret key
- `paper`: Paper trading mode (true/false)
- `account_name`: Account identifier

**What Affects**: Trading execution, account selection

**How to Change**: 
- Dev: Update config.json
- Production: Update AWS Secrets Manager

**Security**: Production keys in AWS Secrets Manager only

---

### Strategy Configuration

**Section**: `strategy`

**Parameters**:
- `use_multi_source`: Enable multi-source (true/false)
- `weight_massive`: Weight for Massive source (0-1)
- `weight_alpha_vantage`: Weight for Alpha Vantage (0-1)
- `weight_x_sentiment`: Weight for X Sentiment (0-1)
- `weight_sonar`: Weight for Sonar AI (0-1)

**What Affects**: Signal quality, win rate

**How to Change**: Update weights, test with backtesting, deploy

**Validation**: Weights should sum to ~1.0

---

### Trading Configuration

**Section**: `trading`

**Key Parameters**:

**Signal Quality**:
- `min_confidence`: Minimum signal confidence (default: 75.0)
- `consensus_threshold`: Consensus requirement (default: 75.0)

**Position Sizing**:
- `position_size_pct`: Base position size (default: 10)
- `max_position_size_pct`: Maximum position size (default: 15)

**Risk Management**:
- `stop_loss`: Stop loss per trade (default: 0.03 = 3%)
- `profit_target`: Take profit per trade (default: 0.05 = 5%)
- `max_correlated_positions`: Correlation limit (default: 3)
- `max_drawdown_pct`: Maximum drawdown (default: 10)
- `daily_loss_limit_pct`: Daily loss limit (default: 5.0)

**Execution**:
- `auto_execute`: Auto-execute signals (default: true)
- `use_limit_orders`: Use limit vs. market orders (default: false)
- `limit_order_offset_pct`: Limit order offset (default: 0.001 = 0.1%)
- `max_retry_attempts`: Retry attempts (default: 3)
- `retry_delay_seconds`: Retry delay (default: 1)

**Monitoring**:
- `enable_position_monitoring`: Enable position monitoring (default: true)
- `enable_performance_tracking`: Enable performance tracking (default: true)

**What Affects**: Trading execution, risk management, profitability

**How to Change**: Update in config.json, restart service

---

### Backtest Configuration

**Section**: `backtest`

**Parameters**:
- `data_source`: Data source (default: "yfinance")
- `data_path`: Historical data path (default: "argo/data/historical")
- `cache_enabled`: Enable caching (default: true)
- `symbols`: List of symbols to backtest
- `walk_forward`: Walk-forward testing parameters
- `optimization`: Optimization parameters
- `metrics`: Metrics calculation parameters
- `execution`: Execution cost parameters

**What Affects**: Backtesting accuracy, optimization results

**How to Change**: Update in config.json, no restart needed

---

## What Affects What

### Configuration Changes → System Behavior

**Signal Quality Parameters**:
- `min_confidence` → Signal quantity vs. quality
- `consensus_threshold` → Signal quantity vs. quality
- `strategy.weights` → Signal quality, win rate

**Trading Parameters**:
- `position_size_pct` → Risk and returns
- `stop_loss` / `profit_target` → Win rate vs. profitability
- `auto_execute` → Trading automation

**Risk Parameters**:
- `max_drawdown_pct` → Trading frequency
- `daily_loss_limit_pct` → Trading frequency
- `max_correlated_positions` → Diversification

---

## Troubleshooting

### Issue: Configuration not loading

**Symptoms**: Default values used, changes not taking effect

**Solutions**:
1. Verify config.json exists and is valid JSON
2. Check file path (environment detection)
3. Validate JSON syntax
4. Restart service after changes

---

### Issue: Wrong environment detected

**Symptoms**: Wrong Alpaca account used, wrong config loaded

**Solutions**:
1. Set `ENV` environment variable explicitly
2. Check file path (contains "production"?)
3. Verify hostname
4. Check environment detection logic

---

### Issue: AWS Secrets Manager not working

**Symptoms**: Falls back to config.json, production keys not loaded

**Solutions**:
1. Verify AWS credentials configured
2. Check IAM permissions
3. Verify secret names match
4. Test secret retrieval manually

---

## Best Practices

### 1. Validate Before Deploying

**Why**: Prevents configuration errors

**How**: Validate JSON syntax, test configuration

**Benefit**: Prevents startup failures

---

### 2. Version Control

**Why**: Track configuration changes

**How**: Commit config.json to git (without secrets)

**Benefit**: Easy rollback, change tracking

---

### 3. Environment Separation

**Why**: Prevents dev/prod confusion

**How**: Use environment detection, separate accounts

**Benefit**: Prevents accidental production changes

---

### 4. Secure Secrets

**Why**: Prevents credential exposure

**How**: Use AWS Secrets Manager for production

**Benefit**: Secure credential management

---

### 5. Document Changes

**Why**: Track what changed and why

**How**: Document all configuration changes

**Benefit**: Easier troubleshooting

---

### 6. Test Changes

**Why**: Prevents unexpected behavior

**How**: Test configuration changes in dev first

**Benefit**: Prevents production issues

---

### 7. Backup Configuration

**Why**: Quick recovery from errors

**How**: Backup config.json before changes

**Benefit**: Fast rollback capability

---

## Quick Reference: Configuration

### Critical Parameters

| Parameter | Default | Affects |
|-----------|---------|---------|
| `min_confidence` | 75.0 | Signal quality |
| `consensus_threshold` | 75.0 | Signal quantity |
| `position_size_pct` | 10 | Risk/returns |
| `stop_loss` | 0.03 | Win rate |
| `profit_target` | 0.05 | Profitability |
| `max_drawdown_pct` | 10 | Trading frequency |
| `daily_loss_limit_pct` | 5.0 | Trading frequency |

### Configuration Workflow

1. **Backup**: Backup current config
2. **Edit**: Make changes to config.json
3. **Validate**: Validate JSON syntax
4. **Test**: Test in dev environment
5. **Deploy**: Deploy to production
6. **Monitor**: Monitor system behavior
7. **Document**: Document changes

---

## Conclusion

Configuration management is **critical for system reliability**. Proper configuration ensures correct behavior across environments and prevents issues.

**Key Takeaways**:
1. Validate configuration before deploying
2. Use environment detection
3. Secure secrets properly
4. Test changes before production
5. Document all changes

**Remember**: Configuration errors can cause system-wide issues - validate carefully.

---

**For Questions**:  
Configuration: config@alpineanalytics.com  
**Technical Support**: tech@alpineanalytics.com

