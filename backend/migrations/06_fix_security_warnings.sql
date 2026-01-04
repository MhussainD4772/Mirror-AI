-- Migration: Fix Common Security Warnings
-- Description: Ensures RLS is enabled, policies exist, and foreign keys are correct
-- Run this in Supabase SQL Editor if Security Advisor shows warnings

-- Step 1: Ensure user_id column exists with foreign key
DO $$ 
BEGIN
    -- Check if user_id column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'entries' AND column_name = 'user_id'
    ) THEN
        -- Add user_id column if it doesn't exist
        ALTER TABLE entries
        ADD COLUMN user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE;
    ELSE
        -- Ensure foreign key constraint exists
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE table_name = 'entries' 
            AND constraint_name LIKE '%user_id%'
            AND constraint_type = 'FOREIGN KEY'
        ) THEN
            -- Add foreign key constraint if missing
            ALTER TABLE entries
            ADD CONSTRAINT entries_user_id_fkey 
            FOREIGN KEY (user_id) 
            REFERENCES auth.users(id) 
            ON DELETE CASCADE;
        END IF;
    END IF;
END $$;

-- Step 2: Enable Row Level Security
ALTER TABLE entries ENABLE ROW LEVEL SECURITY;

-- Step 3: Drop existing policies if they exist (to recreate them correctly)
DROP POLICY IF EXISTS "Users can select their reflections" ON entries;
DROP POLICY IF EXISTS "Users can insert their reflections" ON entries;
DROP POLICY IF EXISTS "Users can update their reflections" ON entries;
DROP POLICY IF EXISTS "Users can delete their reflections" ON entries;

-- Step 4: Create RLS policies
-- SELECT: Users can view only their own reflections
CREATE POLICY "Users can select their reflections"
ON entries FOR SELECT
USING (auth.uid() = user_id);

-- INSERT: Users can insert only their own reflections
CREATE POLICY "Users can insert their reflections"
ON entries FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- UPDATE: Users can update only their own reflections
CREATE POLICY "Users can update their reflections"
ON entries FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- DELETE: Users can delete only their own reflections
CREATE POLICY "Users can delete their reflections"
ON entries FOR DELETE
USING (auth.uid() = user_id);

-- Step 5: Create index on user_id for better query performance
CREATE INDEX IF NOT EXISTS idx_entries_user_id ON entries(user_id);

-- Step 6: Create index on created_at for sorting/filtering
CREATE INDEX IF NOT EXISTS idx_entries_created_at ON entries(created_at DESC);

-- Verification queries (run these to check everything worked)
-- Check RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE tablename = 'entries';

-- Check policies exist:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
-- FROM pg_policies WHERE tablename = 'entries';

-- Check foreign key exists:
-- SELECT conname, confrelid::regclass 
-- FROM pg_constraint 
-- WHERE conrelid = 'entries'::regclass AND contype = 'f';

