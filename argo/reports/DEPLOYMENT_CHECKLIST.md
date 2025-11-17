# Alpine Sync Deployment Checklist

**Date:** 2025-01-27  
**Status:** Ready for Deployment

## Pre-Deployment

### Code Verification
- [x] Alpine sync service implemented (`argo/argo/core/alpine_sync.py`)
- [x] Integration into signal generation service complete
- [x] Configuration documentation created
- [x] Test script created
- [x] Dependencies added to requirements.txt (httpx)
- [x] No linter errors
- [x] All files committed

### Configuration Preparation
- [ ] Generate API key: `openssl rand -hex 32`
- [ ] Store API key securely (AWS Secrets Manager recommended)
- [ ] Document API key location

---

## Deployment Steps

### Step 1: Update Dependencies

On Argo production server:

```bash
cd /root/argo-production
pip install httpx>=0.25.0
# Or update all requirements:
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

**Option A: Environment Variables**

Create/update `/root/argo-production/.env`:

```bash
# Alpine Backend Sync Configuration
ALPINE_API_URL=http://91.98.153.49:8001
ARGO_API_KEY=<generated-api-key>
ALPINE_SYNC_ENABLED=true
```

**Option B: AWS Secrets Manager**

Store secrets in AWS Secrets Manager:
- `argo-alpine/argo/argo-api-key`: `<generated-api-key>`
- `argo-alpine/argo/alpine-api-url`: `http://91.98.153.49:8001`

### Step 3: Configure Alpine Backend

Ensure Alpine backend has matching API key:

**Environment Variable:**
```bash
EXTERNAL_SIGNAL_API_KEY=<same-generated-api-key>
```

Or in AWS Secrets Manager:
- `argo-alpine/alpine-backend/argo-api-key`: `<same-generated-api-key>`

### Step 4: Deploy Code

```bash
# On Argo production server
cd /root/argo-production
git pull  # Or deploy via your deployment method

# Verify new files exist
ls -la argo/core/alpine_sync.py
ls -la scripts/test_alpine_sync.py
```

### Step 5: Verify Setup

```bash
# Run verification script
python3 scripts/verify_alpine_sync_setup.py

# Should see:
# ✅ Setup verification complete!
```

### Step 6: Test Sync

```bash
# Run test script
python3 scripts/test_alpine_sync.py

# Should see:
# ✅ Signal synced successfully!
```

### Step 7: Restart Service

```bash
# Restart Argo service (method depends on your setup)
# If using systemd:
sudo systemctl restart argo-signal-service

# If using screen/tmux:
# Stop and restart the service

# If using Docker:
docker-compose restart argo
```

### Step 8: Monitor Logs

```bash
# Watch Argo logs
tail -f logs/*.log | grep -i alpine

# Should see:
# ✅ Alpine sync service initialized: http://91.98.153.49:8001
# ✅ Signal synced to Alpine: <signal_id> (<symbol> <action>)
```

### Step 9: Verify in Alpine

**Check Alpine Backend Logs:**
```bash
# On Alpine server
docker logs alpine-backend-1 | grep -i "signal synced"

# Should see:
# ✅ Signal synced from external provider: <symbol> <action> (<id>)
```

**Check Alpine Database:**
```sql
-- Connect to Alpine database
SELECT * FROM signals 
ORDER BY created_at DESC 
LIMIT 10;
```

---

## Post-Deployment Verification

### Functional Tests

1. **Signal Generation Test**
   - Wait for next signal generation cycle (every 5 seconds)
   - Verify signal appears in Argo SQLite database
   - Verify signal appears in Alpine PostgreSQL database

2. **Sync Health Test**
   - Check that sync service is running
   - Verify no sync errors in logs
   - Confirm signals are syncing within 1-2 seconds

3. **Error Handling Test**
   - Temporarily stop Alpine backend
   - Verify Argo continues generating signals
   - Verify errors are logged but don't crash service
   - Restart Alpine backend
   - Verify sync resumes automatically

### Monitoring

- [ ] Set up log monitoring for sync errors
- [ ] Monitor sync success rate
- [ ] Set up alerts for sync failures
- [ ] Track signal sync latency

---

## Rollback Plan

If issues occur:

1. **Disable Sync (Quick Fix)**
   ```bash
   # Set environment variable
   export ALPINE_SYNC_ENABLED=false
   
   # Restart service
   sudo systemctl restart argo-signal-service
   ```

2. **Revert Code (If Needed)**
   ```bash
   # Revert to previous commit
   git revert <commit-hash>
   # Or restore from backup
   ```

3. **Verify Rollback**
   - Check that signal generation still works
   - Verify no errors in logs
   - Confirm signals are still stored in Argo database

---

## Troubleshooting

### Issue: "httpx not installed"
**Solution:**
```bash
pip install httpx>=0.25.0
```

### Issue: "Alpine sync disabled (missing configuration)"
**Solution:**
- Set `ALPINE_API_URL` and `ARGO_API_KEY` environment variables
- Or configure in `config.json`

### Issue: "Authentication failed"
**Solution:**
- Verify `ARGO_API_KEY` in Argo matches `EXTERNAL_SIGNAL_API_KEY` in Alpine
- Check API key is correct (no extra spaces, correct format)

### Issue: "Connection error - Alpine backend unreachable"
**Solution:**
- Verify Alpine backend is running
- Check network connectivity: `curl http://91.98.153.49:8001/health`
- Verify firewall rules allow connection

### Issue: "Timeout syncing signal"
**Solution:**
- Check Alpine backend performance
- Verify network latency
- Check Alpine backend logs for errors

---

## Success Criteria

Deployment is successful when:

- [x] Code deployed to production
- [ ] Dependencies installed
- [ ] Configuration set correctly
- [ ] Verification script passes
- [ ] Test sync successful
- [ ] Service restarted
- [ ] Signals syncing to Alpine backend
- [ ] No errors in logs
- [ ] Signals visible in Alpine database
- [ ] Monitoring in place

---

## Support

For issues:
1. Check logs: `tail -f logs/*.log | grep -i alpine`
2. Run verification: `python3 scripts/verify_alpine_sync_setup.py`
3. Run test: `python3 scripts/test_alpine_sync.py`
4. Review documentation: `docs/ALPINE_SYNC_CONFIGURATION.md`

---

## Notes

- Sync is non-blocking (doesn't slow down signal generation)
- Failed syncs don't prevent signal generation
- Sync failures are logged but don't crash the service
- Signals are always stored in Argo database first
- Sync happens asynchronously after storage

