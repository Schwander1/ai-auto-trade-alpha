-- PostgreSQL Database Setup for Alpine Analytics
-- Run these commands on server 91.98.153.49
-- 
-- Usage:
--   sudo -u postgres psql < setup_database.sql
--   OR
--   psql -U postgres -f setup_database.sql

-- Create database
CREATE DATABASE alpine;

-- Create user (REPLACE 'your_password' with a strong password)
CREATE USER alpine_user WITH PASSWORD 'your_password';

-- Grant privileges on database
GRANT ALL PRIVILEGES ON DATABASE alpine TO alpine_user;

-- Connect to the alpine database
\c alpine

-- Grant schema privileges (required for Prisma)
GRANT ALL ON SCHEMA public TO alpine_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO alpine_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO alpine_user;

-- Verify setup
SELECT datname FROM pg_database WHERE datname = 'alpine';
SELECT usename FROM pg_user WHERE usename = 'alpine_user';

-- Exit
\q

