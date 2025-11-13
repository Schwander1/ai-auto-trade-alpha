# System Backup Documentation

## Backup Structure

All backups are stored in the `backups/` directory with timestamped folders.

### Backup Contents

Each backup includes:

1. **Git Repository State**
   - Recent commits (`git_recent_commits.txt`)
   - Current status (`git_status.txt`)
   - Branch information (`git_branches.txt`)
   - Remote repositories (`git_remotes.txt`)

2. **Codebase Backup**
   - Compressed tar.gz archive of entire codebase
   - Excludes: venv, node_modules, __pycache__, logs, databases
   - Includes: All source code, scripts, documentation

3. **Configuration Files**
   - Environment file examples (.env.example)
   - Docker configurations (docker-compose.yml, Dockerfile)
   - Package files (requirements.txt, package.json)
   - TypeScript/JavaScript configs (tsconfig.json)

4. **Deployment State**
   - Health check results for all services
   - Process status
   - Service availability snapshots

5. **AWS Secrets Manager Metadata**
   - Secret count and names
   - Configuration status
   - (Note: Actual secret values are NOT backed up for security)

6. **Documentation**
   - All markdown files
   - Documentation directories
   - System documentation

7. **System Information**
   - OS and system details
   - Software versions
   - Disk space information

8. **Production Server States**
   - Argo production server status
   - Alpine production server status
   - Service logs and configurations

## Restore Instructions

### Restore Codebase
```bash
cd /path/to/restore/location
tar -xzf backups/backup_YYYYMMDD_HHMMSS.tar.gz
cd backup_YYYYMMDD_HHMMSS
tar -xzf codebase_backup.tar.gz
```

### Restore Git State
```bash
# View recent commits
cat backups/backup_YYYYMMDD_HHMMSS/git_recent_commits.txt

# Check what was committed
cat backups/backup_YYYYMMDD_HHMMSS/git_status.txt
```

### Restore Configuration Files
```bash
cd backups/backup_YYYYMMDD_HHMMSS/configs
# Copy specific config files back to their locations
cp -r ./* /path/to/project/
```

## Security Notes

⚠️ **IMPORTANT:**
- Secret values are NOT included in backups
- AWS Secrets Manager secrets remain in AWS (metadata only backed up)
- Environment files with actual secrets are excluded
- Always verify backup contents before sharing

## Backup Frequency

Recommended backup schedule:
- **Daily:** Automated backups before major deployments
- **Weekly:** Full system backups
- **Before Major Changes:** Always backup before:
  - Major code refactoring
  - Infrastructure changes
  - Database migrations
  - Production deployments

## Backup Verification

To verify a backup:
```bash
cd backups/backup_YYYYMMDD_HHMMSS
cat MANIFEST.txt
tar -tzf codebase_backup.tar.gz | head -20
```

## Backup Cleanup

To clean up old backups (keep last 30 days):
```bash
find backups/ -name "backup_*" -type d -mtime +30 -exec rm -rf {} \;
find backups/ -name "backup_*.tar.gz" -mtime +30 -delete
```

## Latest Backup

Check the most recent backup:
```bash
ls -lth backups/ | head -5
```

