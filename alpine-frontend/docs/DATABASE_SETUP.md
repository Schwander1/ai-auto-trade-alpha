# PostgreSQL Database Setup for Alpine Analytics

This document provides SQL commands and instructions for setting up the PostgreSQL database on the server.

## Prerequisites

- PostgreSQL installed on server (91.98.153.49)
- SSH access to the server
- Root or postgres user access

## Step 1: Create Database and User

SSH into the server and run the following SQL commands:

```bash
ssh root@91.98.153.49
```

Then connect to PostgreSQL:

```bash
sudo -u postgres psql
```

Or if PostgreSQL is running as a different user:

```bash
psql -U postgres
```

### SQL Commands

```sql
-- Create database
CREATE DATABASE alpine;

-- Create user (replace 'your_password' with a strong password)
CREATE USER alpine_user WITH PASSWORD 'your_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE alpine TO alpine_user;

-- Connect to the alpine database
\c alpine

-- Grant schema privileges (required for Prisma)
GRANT ALL ON SCHEMA public TO alpine_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO alpine_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO alpine_user;

-- Verify
\l
\du
```

### Alternative: Using psql directly

```bash
sudo -u postgres psql -c "CREATE DATABASE alpine;"
sudo -u postgres psql -c "CREATE USER alpine_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE alpine TO alpine_user;"
sudo -u postgres psql -d alpine -c "GRANT ALL ON SCHEMA public TO alpine_user;"
sudo -u postgres psql -d alpine -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO alpine_user;"
sudo -u postgres psql -d alpine -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO alpine_user;"
```

## Step 2: Configure PostgreSQL for Remote Access

If you need to connect from the Next.js application, ensure PostgreSQL is configured to accept connections:

### Edit `postgresql.conf`

```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

Find and uncomment/modify:

```
listen_addresses = '*'  # or 'localhost,91.98.153.49'
```

### Edit `pg_hba.conf`

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Add line for remote connections:

```
host    alpine    alpine_user    0.0.0.0/0    md5
```

Or for localhost only:

```
host    alpine    alpine_user    127.0.0.1/32    md5
```

### Restart PostgreSQL

```bash
sudo systemctl restart postgresql
# or
sudo service postgresql restart
```

## Step 3: Update Environment Variables

Create or update `.env.local` in the `alpine-frontend` directory:

```bash
cd /path/to/alpine-frontend
nano .env.local
```

Add:

```
DATABASE_URL="postgresql://alpine_user:your_password@91.98.153.49:5432/alpine"
```

**Security Note:** For production, use environment variables or a secrets manager. Never commit `.env.local` to version control.

## Step 4: Run Prisma Migrations

From the `alpine-frontend` directory:

```bash
# Install dependencies (if not already done)
npm install

# Generate Prisma Client
npx prisma generate

# Run migrations
npx prisma migrate dev --name init

# Seed the database (optional)
npm run db:seed
```

## Step 5: Verify Setup

### Check database connection:

```bash
npx prisma db pull
```

### View database in Prisma Studio:

```bash
npm run db:studio
```

This will open a browser at `http://localhost:5555` where you can view and edit data.

### Verify tables were created:

```sql
\c alpine
\dt
```

You should see:
- `users`
- `accounts`
- `sessions`
- `verification_tokens`
- `signals`

## Troubleshooting

### Connection Refused

If you get "connection refused":

1. Check PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

2. Check firewall rules:
   ```bash
   sudo ufw status
   sudo ufw allow 5432/tcp  # If needed
   ```

3. Verify PostgreSQL is listening:
   ```bash
   sudo netstat -tlnp | grep 5432
   ```

### Authentication Failed

1. Verify user exists:
   ```sql
   \du
   ```

2. Reset password:
   ```sql
   ALTER USER alpine_user WITH PASSWORD 'new_password';
   ```

3. Check `pg_hba.conf` configuration

### Permission Denied

1. Grant additional privileges:
   ```sql
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO alpine_user;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO alpine_user;
   ```

2. Make user owner (if needed):
   ```sql
   ALTER DATABASE alpine OWNER TO alpine_user;
   ```

## Security Best Practices

1. **Use strong passwords** for database users
2. **Limit network access** - only allow connections from trusted IPs
3. **Use SSL connections** in production:
   ```
   DATABASE_URL="postgresql://user:pass@host:5432/alpine?sslmode=require"
   ```
4. **Regular backups**:
   ```bash
   pg_dump -U alpine_user alpine > backup_$(date +%Y%m%d).sql
   ```
5. **Monitor connections**:
   ```sql
   SELECT * FROM pg_stat_activity;
   ```

## Backup and Restore

### Backup

```bash
pg_dump -U alpine_user -d alpine -F c -f alpine_backup.dump
```

### Restore

```bash
pg_restore -U alpine_user -d alpine alpine_backup.dump
```

## Next Steps

After database setup:

1. ✅ Database created and user configured
2. ✅ Environment variables set
3. ✅ Prisma migrations run
4. ✅ Database seeded with test users
5. ⏭️ Set up NextAuth.js for authentication
6. ⏭️ Implement user registration/login
7. ⏭️ Add subscription management

