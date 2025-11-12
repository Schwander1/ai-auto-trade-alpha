-- Migration to add 2FA fields to users table
-- Run this directly on the production database

-- Add totp_secret column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS totp_secret VARCHAR(255);

-- Add totp_enabled column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS totp_enabled BOOLEAN DEFAULT FALSE;

-- Add backup_codes column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS backup_codes TEXT;

-- Add last_totp_used column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_totp_used TIMESTAMP WITH TIME ZONE;

-- Verify columns were added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'users' 
AND column_name IN ('totp_secret', 'totp_enabled', 'backup_codes', 'last_totp_used')
ORDER BY column_name;

