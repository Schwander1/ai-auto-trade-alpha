# Database Migrations & Schema Changes Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** All database changes (Argo Capital, Alpine Analytics LLC)

---

## Overview

Comprehensive rules for database migrations, schema changes, and data management to ensure data integrity, zero-downtime deployments, and safe rollbacks.

**Strategic Context:** Database stability aligns with reliability goals defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md).

---

## Migration Principles

### Core Principles

1. **Never Modify Existing Migrations** - Once committed, migrations are immutable
2. **Forward and Backward Compatible** - Migrations must be reversible
3. **Test Before Production** - Always test migrations in staging
4. **Zero-Downtime** - Design migrations for zero-downtime deployments
5. **Atomic Operations** - Each migration should be a single atomic operation

---

## Migration File Naming

### Naming Convention

**Rule:** Use timestamped, descriptive migration names

**Format:** `{timestamp}_{description}.py` or `{timestamp}_{description}.sql`

**Examples:**
```
20250115_001_add_signal_confidence_index.py
20250115_002_create_user_subscriptions_table.py
20250120_003_add_trade_audit_columns.py
```

**Components:**
- **Timestamp:** `YYYYMMDD_HHMM` or sequential `YYYYMMDD_###`
- **Description:** Brief, descriptive name in snake_case
- **Extension:** `.py` for Alembic, `.sql` for raw SQL

---

## Migration Structure

### Python Migrations (Alembic)

**Rule:** Use Alembic for Python projects

**Structure:**
```python
"""add signal confidence index

Revision ID: abc123def456
Revises: xyz789ghi012
Create Date: 2025-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123def456'
down_revision = 'xyz789ghi012'
branch_labels = None
depends_on = None

def upgrade():
    # Migration logic here
    op.create_index(
        'idx_signal_confidence',
        'signals',
        ['confidence'],
        unique=False
    )

def downgrade():
    # Rollback logic here
    op.drop_index('idx_signal_confidence', table_name='signals')
```

### SQL Migrations

**Rule:** Use raw SQL only when necessary

**Structure:**
```sql
-- Migration: add signal confidence index
-- Created: 2025-01-15 10:30:00
-- Revisions: abc123def456

-- UP Migration
CREATE INDEX idx_signal_confidence ON signals(confidence);

-- DOWN Migration (commented)
-- DROP INDEX idx_signal_confidence;
```

---

## Migration Types

### 1. Additive Changes (Safe)

**Rule:** Additive changes are generally safe

**Examples:**
- Adding new tables
- Adding new columns (nullable)
- Adding indexes
- Adding constraints (if data already valid)

**Best Practice:**
```python
def upgrade():
    # Add nullable column first
    op.add_column('signals', sa.Column('new_field', sa.String(255), nullable=True))
    
    # Backfill data if needed
    # op.execute("UPDATE signals SET new_field = 'default' WHERE new_field IS NULL")
    
    # Make non-nullable later (separate migration)
    # op.alter_column('signals', 'new_field', nullable=False)
```

### 2. Destructive Changes (Risky)

**Rule:** Destructive changes require careful planning

**Examples:**
- Dropping columns
- Dropping tables
- Removing indexes
- Changing column types
- Adding NOT NULL constraints

**Process:**
1. Deploy code that doesn't use the column
2. Wait for deployment to complete
3. Create migration to remove column
4. Deploy migration

### 3. Data Migrations

**Rule:** Separate data migrations from schema migrations

**Process:**
1. Schema migration (add column, table, etc.)
2. Data migration (backfill, transform data)
3. Schema migration (add constraints, remove old columns)

**Example:**
```python
# Migration 1: Add new column
def upgrade():
    op.add_column('users', sa.Column('email_normalized', sa.String(255), nullable=True))

# Migration 2: Backfill data
def upgrade():
    op.execute("""
        UPDATE users 
        SET email_normalized = LOWER(TRIM(email))
        WHERE email_normalized IS NULL
    """)

# Migration 3: Add constraint
def upgrade():
    op.alter_column('users', 'email_normalized', nullable=False)
    op.create_unique_constraint('uq_users_email_normalized', 'users', ['email_normalized'])
```

---

## Zero-Downtime Migration Patterns

### Adding Columns

**Rule:** Add columns in multiple steps for zero-downtime

**Step 1:** Add nullable column
```python
op.add_column('signals', sa.Column('new_field', sa.String(255), nullable=True))
```

**Step 2:** Deploy code that writes to new column

**Step 3:** Backfill existing data
```python
op.execute("UPDATE signals SET new_field = 'default' WHERE new_field IS NULL")
```

**Step 4:** Make column non-nullable (if needed)
```python
op.alter_column('signals', 'new_field', nullable=False)
```

### Removing Columns

**Rule:** Remove columns in multiple steps

**Step 1:** Deploy code that doesn't use the column

**Step 2:** Wait for deployment to complete (verify no usage)

**Step 3:** Remove column
```python
op.drop_column('signals', 'old_field')
```

### Changing Column Types

**Rule:** Use multiple steps for type changes

**Step 1:** Add new column with new type
```python
op.add_column('signals', sa.Column('confidence_new', sa.Float(), nullable=True))
```

**Step 2:** Copy data from old to new column
```python
op.execute("UPDATE signals SET confidence_new = CAST(confidence AS FLOAT)")
```

**Step 3:** Deploy code that uses new column

**Step 4:** Drop old column, rename new
```python
op.drop_column('signals', 'confidence')
op.alter_column('signals', 'confidence_new', new_column_name='confidence')
```

---

## Index Management

### Creating Indexes

**Rule:** Create indexes concurrently to avoid locking

**PostgreSQL:**
```python
op.execute("CREATE INDEX CONCURRENTLY idx_signal_confidence ON signals(confidence)")
```

**Note:** CONCURRENTLY requires separate transaction, handle in migration carefully

### Dropping Indexes

**Rule:** Drop indexes concurrently when possible

```python
op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_signal_confidence")
```

---

## Foreign Key Constraints

### Adding Foreign Keys

**Rule:** Add foreign keys after data exists and is valid

**Process:**
1. Ensure all data satisfies constraint
2. Add foreign key constraint
3. Handle violations gracefully

**Example:**
```python
def upgrade():
    # Ensure data is valid first
    op.execute("""
        DELETE FROM signals 
        WHERE user_id NOT IN (SELECT id FROM users)
    """)
    
    # Add foreign key
    op.create_foreign_key(
        'fk_signals_user_id',
        'signals',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )
```

### Removing Foreign Keys

**Rule:** Remove foreign keys before dropping referenced tables

```python
def upgrade():
    op.drop_constraint('fk_signals_user_id', 'signals', type_='foreignkey')
```

---

## Testing Migrations

### Pre-Migration Testing

**Rule:** Test all migrations before production

**Required Tests:**
1. **Upgrade Test:** Run migration on test database
2. **Downgrade Test:** Rollback migration, verify state
3. **Data Integrity Test:** Verify data after migration
4. **Performance Test:** Check query performance after migration
5. **Application Test:** Run application tests against migrated database

### Testing Process

```bash
# 1. Create test database
createdb test_db

# 2. Run migrations up to previous version
alembic upgrade head-1

# 3. Load test data
python scripts/load_test_data.py

# 4. Run new migration
alembic upgrade head

# 5. Verify data integrity
python scripts/verify_migration.py

# 6. Test rollback
alembic downgrade -1

# 7. Verify rollback
python scripts/verify_rollback.py
```

---

## Production Migration Process

### Pre-Migration Checklist

- [ ] Migration tested in staging
- [ ] Rollback tested and verified
- [ ] Backup created
- [ ] Migration reviewed by team
- [ ] Deployment window scheduled
- [ ] Rollback plan documented
- [ ] Monitoring in place

### Migration Execution

**Rule:** Follow structured migration process

**Steps:**
1. **Backup Database**
   ```bash
   pg_dump -Fc database_name > backup_$(date +%Y%m%d_%H%M%S).dump
   ```

2. **Verify Backup**
   ```bash
   pg_restore --list backup_file.dump
   ```

3. **Run Migration**
   ```bash
   alembic upgrade head
   ```

4. **Verify Migration**
   - Check migration status
   - Verify schema changes
   - Run smoke tests
   - Monitor application logs

5. **Monitor**
   - Watch error rates
   - Monitor query performance
   - Check application health

### Rollback Procedure

**Rule:** Have rollback plan ready

**If Migration Fails:**
1. Stop application (if needed)
2. Run rollback: `alembic downgrade -1`
3. Verify database state
4. Restart application
5. Investigate issue
6. Fix migration
7. Retry after testing

**If Application Issues After Migration:**
1. Deploy previous code version
2. If issues persist, consider rollback
3. Rollback migration if necessary
4. Investigate root cause

---

## Migration Best Practices

### Do's

✅ **DO:**
- Keep migrations small and focused
- Test migrations thoroughly
- Document complex migrations
- Use transactions when possible
- Add indexes for new foreign keys
- Consider performance impact
- Plan for rollback

### Don'ts

❌ **DON'T:**
- Modify existing migrations
- Mix schema and data changes unnecessarily
- Add NOT NULL constraints without default
- Drop columns without removing code first
- Run migrations manually in production
- Skip testing migrations
- Ignore migration failures

---

## Migration Tools

### Alembic (Python)

**Rule:** Use Alembic for Python/FastAPI projects

**Setup:**
```python
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:pass@localhost/dbname

# alembic/env.py
from backend.core.database import Base
target_metadata = Base.metadata
```

**Commands:**
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Review generated migration
# Edit if needed

# Run migration
alembic upgrade head

# Rollback
alembic downgrade -1

# Check status
alembic current
alembic history
```

### Prisma (TypeScript)

**Rule:** Use Prisma migrations for TypeScript/Next.js projects

**Commands:**
```bash
# Create migration
npx prisma migrate dev --name description

# Apply migration
npx prisma migrate deploy

# Reset database (dev only)
npx prisma migrate reset
```

---

## Schema Change Guidelines

### Column Changes

**Adding Columns:**
- Start with nullable
- Backfill data
- Make non-nullable later (if needed)

**Removing Columns:**
- Remove from code first
- Wait for deployment
- Remove column in migration

**Changing Types:**
- Add new column
- Copy data
- Switch code to new column
- Remove old column

### Table Changes

**Creating Tables:**
- Define all columns
- Add indexes
- Add constraints
- Consider partitioning for large tables

**Dropping Tables:**
- Remove all references first
- Drop foreign keys
- Drop indexes
- Drop table

---

## Data Migration Patterns

### Backfilling Data

**Rule:** Backfill in batches for large datasets

```python
def upgrade():
    # Backfill in batches
    batch_size = 1000
    offset = 0
    
    while True:
        result = op.execute(f"""
            UPDATE signals 
            SET new_field = 'default'
            WHERE new_field IS NULL
            AND id IN (
                SELECT id FROM signals 
                WHERE new_field IS NULL
                LIMIT {batch_size} OFFSET {offset}
            )
        """)
        
        if result.rowcount == 0:
            break
        
        offset += batch_size
```

### Data Transformation

**Rule:** Transform data carefully, preserve original

```python
def upgrade():
    # Add new column
    op.add_column('users', sa.Column('email_normalized', sa.String(255)))
    
    # Transform data
    op.execute("""
        UPDATE users 
        SET email_normalized = LOWER(TRIM(email))
    """)
    
    # Verify transformation
    # (add verification queries)
```

---

## Related Rules

- **Deployment:** [04_DEPLOYMENT.md](04_DEPLOYMENT.md) - Deployment process
- **Testing:** [03_TESTING.md](03_TESTING.md) - Testing requirements
- **Performance:** [28_PERFORMANCE.md](28_PERFORMANCE.md) - Query optimization
- **Error Handling:** [29_ERROR_HANDLING.md](29_ERROR_HANDLING.md) - Error handling
- **Backend Rules:** [12A_ARGO_BACKEND.md](12A_ARGO_BACKEND.md), [12B_ALPINE_BACKEND.md](12B_ALPINE_BACKEND.md)

---

**Note:** Database migrations are critical for data integrity and system stability. Always follow these rules to ensure safe, reliable schema changes. When in doubt, test thoroughly and plan for rollback.

