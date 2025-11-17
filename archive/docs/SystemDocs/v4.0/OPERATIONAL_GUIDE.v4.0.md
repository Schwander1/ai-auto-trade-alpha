# Operational Guide

**Date:** January 15, 2025  
**Version:** 1.0  
**Status:** Complete Operational Procedures

---

## Overview

This guide covers day-to-day operations, startup procedures, monitoring, and troubleshooting for the Argo-Alpine trading platform.

---

## Startup Sequence

### Local Development Startup

1. **Environment Setup**
   ```bash
   ./scripts/local_setup.sh
   ```

2. **Health Check**
   ```bash
   ./scripts/local_health_check.sh
   ```

3. **Start Services**
   ```bash
   # Argo API
   cd argo
   source venv/bin/activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Alpine Backend (separate terminal)
   cd alpine-backend
   source venv/bin/activate
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 9001
   
   # Alpine Frontend (separate terminal)
   cd alpine-frontend
   npm run dev
   ```

4. **Verify Services**
   - Argo: http://localhost:8000/health
   - Alpine Backend: http://localhost:9001/health
   - Alpine Frontend: http://localhost:3000

### Production Startup

Production services should be running via systemd or similar. To restart:

```bash
# Argo
ssh root@178.156.194.174
cd /root/argo-production
source venv/bin/activate
pkill -f 'uvicorn main:app'
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/argo.log 2>&1 &
```

---

## Background Processes

### Signal Generation Service

**Status:** Automatically started with Argo API

**Process:**
- Runs every 5 seconds
- Generates signals for all monitored symbols
- Executes trades if `auto_execute: true`
- Monitors positions for stop-loss/take-profit

**Monitoring:**
```bash
# Check if running
ps aux | grep signal_generation

# View logs
tail -f /tmp/argo.log | grep SignalGeneration
```

### Position Monitoring

**Status:** Background task in SignalGenerationService

**Process:**
- Checks positions every 30 seconds
- Closes positions when stop-loss/take-profit hit
- Updates performance tracker

---

## Daily Operations

### Morning Checklist

1. **Check System Health**
   ```bash
   python argo/scripts/health_check_unified.py --level 3
   ```

2. **Verify Trading Status**
   ```bash
   python argo/scripts/check_account_status.py
   ```

3. **Review Overnight Trades**
   - Check Alpaca dashboard
   - Review position status
   - Check for any errors in logs

4. **Check Signal Generation**
   ```bash
   curl http://localhost:8000/api/signals/latest?limit=10
   ```

### During Trading Hours

1. **Monitor Signal Generation**
   - Signals generated every 5 seconds
   - Check confidence levels
   - Verify risk management is working

2. **Monitor Positions**
   - Check open positions
   - Verify stop-loss/take-profit orders
   - Monitor P&L

3. **Watch for Errors**
   - Monitor logs for errors
   - Check API response times
   - Verify data source connectivity

### End of Day

1. **Review Daily Performance**
   - Check daily P&L
   - Review trades executed
   - Verify risk limits were respected

2. **Check System Status**
   - Run health check
   - Verify all services running
   - Check for any warnings

3. **Backup (if needed)**
   - Database backups (automated)
   - Config backups
   - Log archives

---

## Monitoring

### Health Checks

**Local:**
```bash
./scripts/local_health_check.sh
python argo/scripts/health_check_unified.py --level 2
```

**Production:**
```bash
./scripts/full-health-check.sh
python argo/scripts/health_check_unified.py --level 3
```

### Key Metrics to Monitor

1. **Signal Generation**
   - Signals generated per hour
   - Average confidence
   - Signal quality (win rate)

2. **Trading Performance**
   - Total P&L
   - Win rate
   - Sharpe ratio
   - Max drawdown

3. **System Health**
   - API response times
   - Error rates
   - Data source availability
   - Database connectivity

4. **Risk Management**
   - Daily loss limit status
   - Drawdown percentage
   - Position count
   - Correlation limits

### Log Monitoring

**Argo Logs:**
```bash
tail -f /tmp/argo.log
# or locally
tail -f argo/logs/*.log
```

**Key Log Patterns:**
- `✅ Generated signal` - Signal generated
- `✅ Trade executed` - Trade executed
- `⏭️  Skipping` - Trade skipped (risk management)
- `❌ Error` - Errors to investigate

---

## Troubleshooting

### Signal Generation Not Working

**Symptoms:**
- No signals generated
- Low signal count

**Diagnosis:**
```bash
# Check signal service
python -c "from argo.core.signal_generation_service import SignalGenerationService; s = SignalGenerationService(); print(s.running)"

# Check data sources
python -c "from argo.core.signal_generation_service import SignalGenerationService; s = SignalGenerationService(); print(list(s.data_sources.keys()))"
```

**Solutions:**
- Verify data source API keys
- Check network connectivity
- Review data source logs

### Trading Not Executing

**Symptoms:**
- Signals generated but no trades
- `auto_execute` is true but nothing happens

**Diagnosis:**
```bash
# Check auto_execute setting
python -c "import json; print(json.load(open('argo/config.json'))['trading']['auto_execute'])"

# Check trading engine
python argo/scripts/check_account_status.py
```

**Solutions:**
- Verify `auto_execute: true` in config
- Check Alpaca connection
- Review risk management logs (may be blocking trades)
- Check daily loss limit status

### Alpaca Connection Issues

**Symptoms:**
- "Alpaca not connected"
- Trading engine errors

**Diagnosis:**
```bash
python argo/scripts/check_account_status.py
```

**Solutions:**
- Verify API keys in AWS Secrets Manager (production) or config.json (local)
- Check network connectivity
- Verify account status in Alpaca dashboard
- Check environment detection (dev vs prod)

### High Error Rate

**Symptoms:**
- Many errors in logs
- API failures

**Diagnosis:**
```bash
# Check error patterns
grep "❌\|ERROR\|Exception" /tmp/argo.log | tail -20
```

**Solutions:**
- Review specific error messages
- Check API rate limits
- Verify data source availability
- Check database connectivity

---

## Maintenance Tasks

### Weekly

1. **Review Performance Metrics**
   - Win rate trends
   - Return trends
   - Risk metrics

2. **Check System Health**
   - Run comprehensive health check
   - Review logs for patterns
   - Check for resource usage

3. **Update Documentation**
   - Document any changes
   - Update runbooks
   - Note any issues

### Monthly

1. **Performance Analysis**
   - Analyze trade performance
   - Review strategy effectiveness
   - Optimize parameters if needed

2. **Security Review**
   - Run security audit
   - Review access logs
   - Update secrets if needed

3. **System Optimization**
   - Review and optimize code
   - Update dependencies
   - Performance tuning

---

## Emergency Procedures

### Trading Paused

**If trading is paused due to daily loss limit:**

1. Review daily P&L
2. Check if limit is appropriate
3. Reset if needed (restart service)
4. Monitor closely

### Service Down

**If Argo API is down:**

1. Check service status: `ps aux | grep uvicorn`
2. Check logs: `tail -f /tmp/argo.log`
3. Restart service
4. Verify health check passes

### Data Source Failure

**If a data source fails:**

1. System continues with other sources
2. Check source API status
3. Verify API keys
4. Restart if needed

---

## Performance Optimization

### Signal Generation

- Optimize data source calls
- Cache frequently accessed data
- Batch API requests

### Trading Execution

- Optimize position sizing calculations
- Cache account/position data
- Reduce API calls

### Database

- Index frequently queried columns
- Archive old data
- Optimize queries

---

## Backup & Recovery

### Automated Backups

- Database backups (daily)
- Config backups
- Log rotation

### Manual Backup

```bash
# Backup database
cp argo/data/signals.db argo/data/backups/signals_$(date +%Y%m%d).db

# Backup config
cp argo/config.json argo/config.json.backup
```

### Recovery

1. Stop services
2. Restore from backup
3. Verify data integrity
4. Restart services
5. Run health checks

---

## Support & Escalation

### Common Issues

- See Troubleshooting section above
- Check logs first
- Review health check results

### Escalation

1. Check documentation
2. Review logs thoroughly
3. Run diagnostic scripts
4. Contact support if needed

---

**Last Updated:** January 15, 2025  
**Version:** 1.0

