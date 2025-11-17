# Complete Troubleshooting & Recovery Guide

**Date:** January 15, 2025  
**Version:** 2.0  
**Status:** Complete Implementation Guide

---

## Executive Summary

This document provides a comprehensive troubleshooting and recovery guide for the Argo-Alpine trading system. It covers common issues, how to diagnose them, how to fix them, and how to recover from failures. **This guide is essential for maintaining system reliability and minimizing downtime.**

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Diagnostic Process](#diagnostic-process)
3. [Common Issues & Solutions](#common-issues--solutions)
4. [Recovery Procedures](#recovery-procedures)
5. [Prevention Strategies](#prevention-strategies)
6. [Emergency Procedures](#emergency-procedures)

---

## System Overview

### Purpose

The troubleshooting and recovery system provides **systematic approaches** to:
- Diagnose issues quickly
- Fix problems efficiently
- Recover from failures
- Prevent future issues

### Key Principles

1. **Diagnose First**: Understand the problem before fixing
2. **Fix Root Cause**: Don't just treat symptoms
3. **Document Everything**: Learn from issues
4. **Test Recovery**: Ensure fixes work
5. **Prevent Recurrence**: Update processes

---

## Diagnostic Process

### Step 1: Identify the Issue

**Questions to Ask**:
1. What is not working?
2. When did it start?
3. What changed recently?
4. Is it affecting all components or specific ones?

**Tools**:
- Health check scripts
- System logs
- Monitoring dashboards
- Error messages

---

### Step 2: Gather Information

**Information to Collect**:
1. Error messages and logs
2. System status (health checks)
3. Recent changes (config, code, deployments)
4. Component status (trading engine, signal service, etc.)
5. Performance metrics

**Commands**:
```bash
# Health check
python argo/scripts/health_check_unified.py --level 3

# System verification
python argo/scripts/verify_system.py

# Check logs
tail -f argo/logs/trading/*.log
tail -f argo/logs/signals.log
```

---

### Step 3: Isolate the Problem

**Process**:
1. Identify affected components
2. Test components individually
3. Check dependencies
4. Verify configuration

**Tools**:
- Component-specific health checks
- Manual testing
- Configuration validation

---

### Step 4: Determine Root Cause

**Process**:
1. Analyze error messages
2. Review logs for patterns
3. Check configuration changes
4. Verify external dependencies

**Common Root Causes**:
- Configuration errors
- API failures
- Network issues
- Code bugs
- Resource exhaustion

---

### Step 5: Implement Fix

**Process**:
1. Fix root cause
2. Test fix in isolation
3. Verify fix works
4. Deploy fix carefully

**Best Practices**:
- Test before deploying
- Make incremental changes
- Document the fix
- Monitor after deployment

---

## Common Issues & Solutions

### Issue Category 1: Trading Engine Issues

#### Issue: Trading engine not connecting to Alpaca

**Symptoms**:
- Health check fails for trading engine
- "Alpaca not connected" error
- No orders executing

**Diagnosis**:
```bash
# Check API credentials
python argo/scripts/check_account_status.py

# Check environment
python -c "from argo.core.environment import detect_environment; print(detect_environment())"

# Check config
cat argo/config.json | grep -A 10 alpaca
```

**Root Causes**:
1. Invalid API credentials
2. Wrong environment (dev vs. prod)
3. Network connectivity issues
4. Alpaca API downtime

**Solutions**:
1. **Invalid Credentials**:
   - Verify API keys in config.json or AWS Secrets Manager
   - Check key format (should be PK... for paper trading)
   - Regenerate keys if needed

2. **Wrong Environment**:
   - Check environment detection: `detect_environment()`
   - Verify correct account selected
   - Check config.json structure (dev/production keys)

3. **Network Issues**:
   - Test connectivity: `ping api.alpaca.markets`
   - Check firewall rules
   - Verify proxy settings

4. **API Downtime**:
   - Check Alpaca status page
   - Wait for service restoration
   - Use simulation mode as fallback

**Prevention**:
- Monitor Alpaca API status
- Set up connection health checks
- Use retry logic with exponential backoff

---

#### Issue: Orders not executing

**Symptoms**:
- Signals generated but no trades
- "Skipping" messages in logs
- No order IDs returned

**Diagnosis**:
```bash
# Check risk management status
grep "Skipping" argo/logs/trading/*.log

# Check account status
python argo/scripts/check_account_status.py

# Check risk limits
python -c "from argo.core.signal_generation_service import SignalGenerationService; s = SignalGenerationService(); print(s._trading_paused)"
```

**Root Causes**:
1. Risk limits triggered
2. Market closed (for stocks)
3. Insufficient buying power
4. Auto-execute disabled

**Solutions**:
1. **Risk Limits Triggered**:
   - Check daily loss limit: `_trading_paused` flag
   - Check drawdown: `max_drawdown_pct`
   - Check correlation limits: `max_correlated_positions`
   - Wait for limits to reset or adjust limits

2. **Market Closed**:
   - Check market hours (stocks: 9:30 AM - 4:00 PM ET)
   - Use crypto for 24/7 trading
   - Wait for market open

3. **Insufficient Buying Power**:
   - Check account balance
   - Reduce position sizes
   - Close existing positions

4. **Auto-Execute Disabled**:
   - Check `config.json` → `trading.auto_execute`
   - Set to `true` to enable
   - Restart signal service

**Prevention**:
- Monitor risk limit status
- Set up alerts for trading pauses
- Regular account balance checks

---

### Issue Category 2: Signal Generation Issues

#### Issue: No signals being generated

**Symptoms**:
- No signals in database
- Signal generation service running but no output
- Health check shows signal service OK but no signals

**Diagnosis**:
```bash
# Check signal service logs
tail -f argo/logs/signals.log

# Check data sources
python -c "from argo.core.signal_generation_service import SignalGenerationService; s = SignalGenerationService(); print(s.data_sources)"

# Check consensus threshold
grep "consensus_threshold" argo/config.json
```

**Root Causes**:
1. Consensus threshold too high
2. Data sources failing
3. Min confidence too high
4. Service not running

**Solutions**:
1. **Consensus Threshold Too High**:
   - Lower `consensus_threshold` in config.json (try 70%)
   - Test with backtesting
   - Monitor signal generation rate

2. **Data Sources Failing**:
   - Check API keys for each source
   - Test data source connectivity
   - Check rate limits
   - Verify service status

3. **Min Confidence Too High**:
   - Lower `min_confidence` in config.json (try 70%)
   - Test with backtesting
   - Monitor win rate

4. **Service Not Running**:
   - Check if signal service is running
   - Restart signal service
   - Check for crashes in logs

**Prevention**:
- Monitor signal generation rate
- Set up alerts for no signals
- Regular data source health checks

---

#### Issue: Low signal quality (low win rate)

**Symptoms**:
- Signals generated but low win rate
- Many losing trades
- Confidence scores not accurate

**Diagnosis**:
```bash
# Check win rate
python -c "from argo.core.signal_tracker import SignalTracker; t = SignalTracker(); # Query win rate"

# Check data source weights
grep -A 5 "strategy" argo/config.json

# Check consensus calculation
# Review signal generation logs
```

**Root Causes**:
1. Data source weights suboptimal
2. Consensus threshold too low
3. Regime detection inaccurate
4. Market conditions changed

**Solutions**:
1. **Optimize Data Source Weights**:
   - Run backtesting to test different weights
   - Measure source performance
   - Update weights in config.json
   - Test with walk-forward validation

2. **Increase Consensus Threshold**:
   - Increase `consensus_threshold` (try 80%)
   - Test with backtesting
   - Monitor signal count vs. quality

3. **Improve Regime Detection**:
   - Review regime detection accuracy
   - Test regime-specific strategies
   - Optimize regime classification

4. **Adjust for Market Conditions**:
   - Review current market regime
   - Adjust strategy for regime
   - Test regime-specific optimizations

**Prevention**:
- Regular backtesting
- Monitor win rate continuously
- Optimize weights monthly

---

### Issue Category 3: Risk Management Issues

#### Issue: Trading paused due to daily loss limit

**Symptoms**:
- "Trading paused due to daily loss limit" in logs
- No new trades executing
- Daily P&L negative

**Diagnosis**:
```bash
# Check daily loss
python -c "from argo.core.signal_generation_service import SignalGenerationService; s = SignalGenerationService(); # Check _trading_paused"

# Check account equity
python argo/scripts/check_account_status.py
```

**Root Causes**:
1. Daily loss exceeded limit
2. Limit too tight
3. Strategy underperforming

**Solutions**:
1. **Wait for Reset**:
   - Daily loss limit resets at start of new trading day
   - Wait until next day
   - Trading will resume automatically

2. **Adjust Limit** (if too tight):
   - Increase `daily_loss_limit_pct` in config.json
   - Test with backtesting
   - Monitor impact on risk

3. **Improve Strategy**:
   - Review recent trades
   - Optimize signal quality
   - Adjust risk parameters

**Prevention**:
- Monitor daily P&L
- Set appropriate limits
- Regular strategy optimization

---

#### Issue: Max drawdown exceeded

**Symptoms**:
- "Max drawdown exceeded" in logs
- Trading paused
- Portfolio declined from peak

**Diagnosis**:
```bash
# Check drawdown
python -c "from argo.core.signal_generation_service import SignalGenerationService; s = SignalGenerationService(); # Check peak equity and current equity"

# Check account status
python argo/scripts/check_account_status.py
```

**Root Causes**:
1. Portfolio declined too much
2. Limit too tight
3. Strategy underperforming

**Solutions**:
1. **Wait for Recovery**:
   - Drawdown resets when portfolio recovers
   - Wait for drawdown < limit
   - Trading will resume automatically

2. **Adjust Limit** (if too tight):
   - Increase `max_drawdown_pct` in config.json
   - Test with backtesting
   - Monitor impact on risk

3. **Improve Strategy**:
   - Review strategy performance
   - Optimize signal quality
   - Adjust risk parameters

**Prevention**:
- Monitor drawdown continuously
- Set appropriate limits
- Regular strategy optimization

---

### Issue Category 4: Configuration Issues

#### Issue: Configuration not loading

**Symptoms**:
- Default values used instead of config
- Changes not taking effect
- Config file not found errors

**Diagnosis**:
```bash
# Check config path
python -c "from argo.core.environment import detect_environment; print(detect_environment())"
ls -la argo/config.json

# Check config structure
python -c "import json; print(json.load(open('argo/config.json')))"
```

**Root Causes**:
1. Config file not found
2. Invalid JSON syntax
3. Wrong config path
4. Environment detection issue

**Solutions**:
1. **Config File Not Found**:
   - Verify config.json exists
   - Check file path
   - Create config.json if missing

2. **Invalid JSON**:
   - Validate JSON syntax
   - Fix syntax errors
   - Test with JSON validator

3. **Wrong Config Path**:
   - Check environment detection
   - Verify config path logic
   - Set ARGO_CONFIG_PATH if needed

4. **Environment Detection**:
   - Check environment detection
   - Verify environment-specific config
   - Test environment switching

**Prevention**:
- Validate config on startup
- Test config changes
- Document config structure

---

### Issue Category 5: Data Source Issues

#### Issue: Data source API failures

**Symptoms**:
- "Data source failed" errors
- Missing data in signals
- Lower signal quality

**Diagnosis**:
```bash
# Check data source status
python -c "from argo.core.signal_generation_service import SignalGenerationService; s = SignalGenerationService(); print(s.data_sources)"

# Check API keys
grep -A 2 "massive\|alpha_vantage\|x_api\|sonar" argo/config.json
```

**Root Causes**:
1. Invalid API keys
2. Rate limit exceeded
3. Service downtime
4. Network issues

**Solutions**:
1. **Invalid API Keys**:
   - Verify API keys in config.json
   - Check key format
   - Regenerate keys if needed

2. **Rate Limit Exceeded**:
   - Check rate limits
   - Reduce request frequency
   - Upgrade API plan if needed

3. **Service Downtime**:
   - Check service status pages
   - Wait for restoration
   - Use fallback data sources

4. **Network Issues**:
   - Test connectivity
   - Check firewall rules
   - Verify proxy settings

**Prevention**:
- Monitor data source health
- Set up rate limit alerts
- Use multiple data sources

---

## Recovery Procedures

### Procedure 1: Service Restart

**When to Use**: Service crashed, unresponsive, or configuration changed

**Steps**:
1. Stop service
2. Check logs for errors
3. Fix any issues found
4. Restart service
5. Verify health check passes

**Commands**:
```bash
# Stop service (if running as process)
pkill -f signal_generation_service

# Restart service
python argo/main.py

# Verify health
python argo/scripts/health_check_unified.py --level 2
```

---

### Procedure 2: Configuration Recovery

**When to Use**: Configuration corrupted or invalid

**Steps**:
1. Backup current config
2. Restore from backup or default
3. Validate JSON syntax
4. Test configuration
5. Restart services

**Commands**:
```bash
# Backup current config
cp argo/config.json argo/config.json.backup

# Restore from backup
cp argo/config.json.backup argo/config.json

# Validate JSON
python -c "import json; json.load(open('argo/config.json'))"

# Test configuration
python argo/scripts/verify_system.py
```

---

### Procedure 3: Database Recovery

**When to Use**: Database corrupted or data lost

**Steps**:
1. Stop services
2. Backup current database
3. Restore from backup
4. Verify data integrity
5. Restart services

**Commands**:
```bash
# Backup database
cp argo/data/signals.db argo/data/signals.db.backup

# Restore from backup
cp argo/data/signals.db.backup argo/data/signals.db

# Verify integrity
sqlite3 argo/data/signals.db "PRAGMA integrity_check;"
```

---

### Procedure 4: Full System Recovery

**When to Use**: Multiple components failed or system-wide issue

**Steps**:
1. Stop all services
2. Run comprehensive health check
3. Identify all issues
4. Fix issues systematically
5. Restart services one by one
6. Verify each component
7. Run full system test

**Commands**:
```bash
# Stop all services
pkill -f argo
pkill -f alpine

# Health check
python argo/scripts/health_check_unified.py --level 3

# Fix issues (see specific solutions above)

# Restart services
python argo/main.py

# Verify
python argo/scripts/verify_system.py
```

---

## Prevention Strategies

### 1. Regular Health Checks

**Why**: Early detection of issues

**How**: Run Level 2 checks daily, Level 3 weekly

**Benefit**: Prevents issues before they impact operations

---

### 2. Automated Monitoring

**Why**: Continuous visibility

**How**: Set up automated health checks every 5 minutes

**Benefit**: Real-time issue detection

---

### 3. Configuration Validation

**Why**: Prevents config errors

**How**: Validate config on startup, test changes

**Benefit**: Prevents configuration-related issues

---

### 4. Regular Backups

**Why**: Quick recovery from data loss

**How**: Daily backups of config, database, code

**Benefit**: Fast recovery from failures

---

### 5. Documentation

**Why**: Learn from issues

**How**: Document all issues, root causes, solutions

**Benefit**: Prevents repeat issues

---

### 6. Testing

**Why**: Catch issues before production

**How**: Test all changes, use staging environment

**Benefit**: Prevents production issues

---

### 7. Gradual Rollouts

**Why**: Minimize impact of issues

**How**: Deploy changes gradually, monitor closely

**Benefit**: Limits impact of problems

---

## Emergency Procedures

### Emergency: Trading Engine Down

**Priority**: HIGH - No trades executing

**Steps**:
1. Check Alpaca API status
2. Verify API credentials
3. Test connectivity
4. Restart trading engine
5. Verify orders executing

**Time to Fix**: < 5 minutes

---

### Emergency: Signal Generation Stopped

**Priority**: HIGH - No signals for customers

**Steps**:
1. Check signal service status
2. Verify data sources
3. Check consensus threshold
4. Restart signal service
5. Verify signals generating

**Time to Fix**: < 10 minutes

---

### Emergency: Risk Limits Constantly Triggered

**Priority**: MEDIUM - Trading paused

**Steps**:
1. Check account status
2. Review recent trades
3. Analyze risk limits
4. Adjust limits if needed
5. Resume trading

**Time to Fix**: < 15 minutes

---

### Emergency: System-Wide Failure

**Priority**: CRITICAL - Complete system down

**Steps**:
1. Stop all services
2. Run comprehensive diagnostics
3. Identify root cause
4. Fix systematically
5. Restart services
6. Verify full system

**Time to Fix**: < 30 minutes

---

## Quick Reference: Troubleshooting

### Diagnostic Commands

```bash
# Health check
python argo/scripts/health_check_unified.py --level 3

# System verification
python argo/scripts/verify_system.py

# Trading verification
python argo/scripts/verify_trading_system.py

# Check account status
python argo/scripts/check_account_status.py

# Check logs
tail -f argo/logs/trading/*.log
tail -f argo/logs/signals.log
```

### Common Fixes

| Issue | Quick Fix |
|-------|-----------|
| Trading engine not connected | Check API credentials, restart service |
| No signals generated | Lower consensus threshold, check data sources |
| Trading paused | Check risk limits, wait for reset |
| Config not loading | Validate JSON, check file path |
| Data source failures | Check API keys, verify connectivity |

---

## Conclusion

Troubleshooting and recovery are **essential for maintaining system reliability**. Following systematic diagnostic and recovery procedures minimizes downtime and prevents issues from recurring.

**Key Takeaways**:
1. Diagnose before fixing
2. Fix root causes, not symptoms
3. Document everything
4. Test recovery procedures
5. Prevent recurrence

**Remember**: Preparation and systematic approaches are key to quick recovery.

---

**For Questions**:  
Troubleshooting: support@alpineanalytics.com  
**Emergency**: emergency@alpineanalytics.com

