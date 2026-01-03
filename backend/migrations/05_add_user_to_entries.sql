-- Migration: Add user_id to entries table and enable RLS
-- Date: 2025-11-16
-- Description: Adds authentication support by linking entries to users and enabling row-level security

-- Add user_id column with foreign key to auth.users
ALTER TABLE entries
ADD COLUMN IF NOT EXISTS user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE;

-- Set existing entries to NULL (legacy data)
UPDATE entries SET user_id = NULL WHERE user_id IS NULL;

-- Enable Row Level Security
ALTER TABLE entries ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Users can select their reflections" ON entries;
DROP POLICY IF EXISTS "Users can insert their reflections" ON entries;
DROP POLICY IF EXISTS "Users can update their reflections" ON entries;
DROP POLICY IF EXISTS "Users can delete their reflections" ON entries;

-- Create policy: Users can view only their own reflections
CREATE POLICY "Users can select their reflections"
ON entries FOR SELECT
USING (auth.uid() = user_id);

-- Create policy: Users can insert only their own reflections
CREATE POLICY "Users can insert their reflections"
ON entries FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Create policy: Users can update only their own reflections
CREATE POLICY "Users can update their reflections"
ON entries FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Create policy: Users can delete only their own reflections
CREATE POLICY "Users can delete their reflections"
ON entries FOR DELETE
USING (auth.uid() = user_id);

