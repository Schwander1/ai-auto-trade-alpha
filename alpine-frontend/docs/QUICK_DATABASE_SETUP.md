# Quick PostgreSQL Database Setup for Alpine

## Step 1: Create Database on Server (91.98.153.49)

SSH into the server and run these SQL commands:

```bash
ssh root@91.98.153.49
sudo -u postgres psql
```

Then execute:

```sql
-- Create database
CREATE DATABASE alpine;

-- Create user (replace 'your_strong_password' with actual password)
CREATE USER alpine_user WITH PASSWORD 'your_strong_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE alpine TO alpine_user;

-- Connect to alpine database
\c alpine

-- Grant schema privileges (required for Prisma)
GRANT ALL ON SCHEMA public TO alpine_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO alpine_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO alpine_user;

-- Verify
\dt
\q
```

**Alternative: One-liner commands**

```bash
sudo -u postgres psql -c "CREATE DATABASE alpine;"
sudo -u postgres psql -c "CREATE USER alpine_user WITH PASSWORD 'your_strong_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE alpine TO alpine_user;"
sudo -u postgres psql -d alpine -c "GRANT ALL ON SCHEMA public TO alpine_user;"
sudo -u postgres psql -d alpine -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO alpine_user;"
sudo -u postgres psql -d alpine -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO alpine_user;"
```

## Step 2: Configure Environment Variables

Create `.env.local` in `alpine-frontend/` directory:

```bash
cd alpine-frontend
nano .env.local
```

Add:

```env
DATABASE_URL="postgresql://alpine_user:your_strong_password@91.98.153.49:5432/alpine"
NEXT_PUBLIC_ARGO_API_URL="http://178.156.194.174:8000"
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key-here"
```

**Generate NEXTAUTH_SECRET:**
```bash
openssl rand -base64 32
```

## Step 3: Run Prisma Setup

```bash
cd alpine-frontend

# Install dependencies (if not already done)
npm install

# Generate Prisma Client
npx prisma generate

# Create and run migration
npx prisma migrate dev --name init

# Seed database with test users (optional)
npx prisma db seed
```

## Step 4: Verify Setup

```bash
# Open Prisma Studio to view database
npx prisma studio
```

This opens a browser at `http://localhost:5555` where you can view tables and data.

## Test Database Connection

```bash
# Test connection
npx prisma db pull
```

If successful, you should see no errors.

## Troubleshooting

### Connection Refused

1. Check PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

2. Check if PostgreSQL is listening:
   ```bash
   sudo netstat -tlnp | grep 5432
   ```

3. If needed, configure PostgreSQL to accept connections:
   ```bash
   # Edit postgresql.conf
   sudo nano /etc/postgresql/*/main/postgresql.conf
   # Set: listen_addresses = '*'
   
   # Edit pg_hba.conf
   sudo nano /etc/postgresql/*/main/pg_hba.conf
   # Add: host alpine alpine_user 0.0.0.0/0 md5
   
   # Restart PostgreSQL
   sudo systemctl restart postgresql
   ```

### Permission Denied

```sql
-- Grant additional privileges
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO alpine_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO alpine_user;
```

### Migration Errors

If migration fails, reset and try again:

```bash
npx prisma migrate reset
npx prisma migrate dev --name init
```

## Expected Tables After Migration

After running migrations, you should have:

- `users` - User accounts
- `accounts` - OAuth accounts (NextAuth)
- `sessions` - User sessions (NextAuth)
- `verification_tokens` - Email verification tokens (NextAuth)
- `signals` - Cached trading signals
- `_prisma_migrations` - Migration history

## Test Users (After Seeding)

After running `npx prisma db seed`, you can login with:

- **STARTER:** `starter@alpineanalytics.com` / `password123`
- **PROFESSIONAL:** `professional@alpineanalytics.com` / `password123`
- **INSTITUTIONAL:** `institutional@alpineanalytics.com` / `password123`

