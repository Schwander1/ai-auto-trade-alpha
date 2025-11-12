#!/bin/bash
# PostgreSQL Database Setup Script for Alpine Analytics
# Run on server: 91.98.153.49

set -e

echo "🚀 Setting up PostgreSQL database for Alpine Analytics..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root or postgres user
if [ "$EUID" -ne 0 ] && [ "$USER" != "postgres" ]; then 
    echo -e "${RED}Please run as root or postgres user${NC}"
    exit 1
fi

# Database configuration
DB_NAME="alpine"
DB_USER="alpine_user"
DB_PASSWORD="${ALPINE_DB_PASSWORD:-}"

# Prompt for password if not set
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}Enter password for database user 'alpine_user':${NC}"
    read -s DB_PASSWORD
    echo
fi

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}Password cannot be empty${NC}"
    exit 1
fi

echo "📦 Creating database and user..."

# Create database
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database already exists"

# Create user
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "User already exists"

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Grant schema privileges
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;"

echo -e "${GREEN}✅ Database setup complete!${NC}"
echo
echo "📝 Connection string:"
echo "   postgresql://$DB_USER:****@91.98.153.49:5432/$DB_NAME"
echo
echo "💡 Add to .env.local:"
echo "   DATABASE_URL=\"postgresql://$DB_USER:$DB_PASSWORD@91.98.153.49:5432/$DB_NAME\""
echo

