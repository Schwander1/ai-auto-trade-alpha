# ✅ PostgreSQL Database Setup - Complete

All database setup files are ready! Follow these steps to complete the setup.

## 📋 What's Already Created

✅ **Prisma Schema** (`prisma/schema.prisma`)
- User model with all required fields
- Signal model (mirrors Argo structure)
- Session, Account, VerificationToken models (for NextAuth)

✅ **Database Client** (`lib/db.ts`)
- PrismaClient singleton
- Prevents multiple instances in development

✅ **Seed Script** (`prisma/seed.ts`)
- Creates test users with all tiers
- Uses bcryptjs for password hashing

✅ **Package Scripts** (in `package.json`)
- `npm run db:migrate` - Run migrations
- `npm run db:generate` - Generate Prisma Client
- `npm run db:seed` - Seed database
- `npm run db:studio` - Open Prisma Studio

## 🚀 Setup Steps

### Step 1: Create Database on Server (91.98.153.49)

**Option A: Using SQL file**

```bash
ssh root@91.98.153.49
cd /path/to/alpine-frontend
sudo -u postgres psql < docs/setup_database.sql
```

**Option B: Using setup script**

```bash
ssh root@91.98.153.49
cd /path/to/alpine-frontend
./setup_database.sh
```

**Option C: Manual SQL commands**

```bash
ssh root@91.98.153.49
sudo -u postgres psql
```

Then run:

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
SELECT datname FROM pg_database WHERE datname = 'alpine';
SELECT usename FROM pg_user WHERE usename = 'alpine_user';

-- Exit
\q
```

### Step 2: Create `.env.local` File

Create `.env.local` in the `alpine-frontend/` directory:

```bash
cd alpine-frontend
nano .env.local
```

Add this content (replace with your actual password):

```env
# Database
DATABASE_URL="postgresql://alpine_user:your_strong_password@91.98.153.49:5432/alpine"

# Argo API
NEXT_PUBLIC_ARGO_API_URL="http://178.156.194.174:8000"

# NextAuth
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key-here"
```

**Generate NEXTAUTH_SECRET:**
```bash
openssl rand -base64 32
```

### Step 3: Install Dependencies

```bash
cd alpine-frontend
npm install
```

### Step 4: Generate Prisma Client

```bash
npx prisma generate
```

### Step 5: Run Database Migration

```bash
npx prisma migrate dev --name init
```

This will:
- Create all tables (users, signals, sessions, accounts, etc.)
- Set up indexes
- Create migration history

### Step 6: Seed Database (Optional)

```bash
npx prisma db seed
```

This creates test users:
- `starter@alpineanalytics.com` / `password123` (STARTER tier)
- `professional@alpineanalytics.com` / `password123` (PROFESSIONAL tier)
- `institutional@alpineanalytics.com` / `password123` (INSTITUTIONAL tier)

### Step 7: Verify Setup

```bash
# Open Prisma Studio to view database
npx prisma studio
```

This opens a browser at `http://localhost:5555` where you can:
- View all tables
- Browse data
- Edit records

## 📊 Database Schema

After migration, you'll have these tables:

### `users`
- `id` (UUID, primary key)
- `email` (unique)
- `password_hash`
- `tier` (STARTER | PROFESSIONAL | INSTITUTIONAL)
- `subscription_start`
- `subscription_end`
- `created_at`
- `updated_at`

### `signals`
- `id` (String, primary key - Argo's signal ID)
- `symbol`
- `action` (BUY | SELL)
- `entry_price`
- `stop_loss`
- `take_profit`
- `confidence`
- `type` (PREMIUM | STANDARD)
- `timestamp`
- `hash` (SHA-256, unique)
- `regime` (Bull | Bear | Chop | Crisis)
- `regime_strength`
- `status` (pending | active | closed | expired)
- `outcome` (win | loss | expired)
- `exit_price`
- `pnl_pct`
- `exit_timestamp`
- `reasoning`
- `created_at`
- `updated_at`

### `sessions` (NextAuth)
- `id` (UUID)
- `session_token` (unique)
- `user_id` (foreign key to users)
- `expires`

### `accounts` (NextAuth - for OAuth)
- `id` (UUID)
- `user_id` (foreign key to users)
- `type`, `provider`, `provider_account_id`
- OAuth tokens and metadata

### `verification_tokens` (NextAuth)
- `identifier`
- `token` (unique)
- `expires`

## 🔧 Troubleshooting

### Connection Refused

1. Check PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

2. Check if listening on port 5432:
   ```bash
   sudo netstat -tlnp | grep 5432
   ```

3. Configure PostgreSQL for remote access (if needed):
   ```bash
   # Edit postgresql.conf
   sudo nano /etc/postgresql/*/main/postgresql.conf
   # Set: listen_addresses = '*'
   
   # Edit pg_hba.conf
   sudo nano /etc/postgresql/*/main/pg_hba.conf
   # Add: host alpine alpine_user 0.0.0.0/0 md5
   
   # Restart
   sudo systemctl restart postgresql
   ```

### Permission Denied

```sql
-- Grant additional privileges
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO alpine_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO alpine_user;
```

### Migration Errors

```bash
# Reset and retry
npx prisma migrate reset
npx prisma migrate dev --name init
```

### "Module not found: @prisma/client"

```bash
npx prisma generate
```

## ✅ Verification Checklist

- [ ] Database created on server
- [ ] User created with proper permissions
- [ ] `.env.local` file created with DATABASE_URL
- [ ] Dependencies installed (`npm install`)
- [ ] Prisma Client generated (`npx prisma generate`)
- [ ] Migration run successfully (`npx prisma migrate dev`)
- [ ] Database seeded (optional, `npx prisma db seed`)
- [ ] Prisma Studio opens and shows tables
- [ ] Can connect to database from application

## 📚 Additional Resources

- **Full Setup Guide:** `docs/DATABASE_SETUP.md`
- **Quick Setup:** `docs/QUICK_DATABASE_SETUP.md`
- **SQL Script:** `docs/setup_database.sql`
- **Setup Script:** `setup_database.sh`

## 🎉 Next Steps

After database setup:
1. ✅ Database ready
2. ⏭️ Test authentication (login/signup)
3. ⏭️ Test signal fetching
4. ⏭️ Deploy to production

