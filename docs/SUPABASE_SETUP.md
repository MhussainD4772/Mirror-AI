# Supabase Setup Guide for Phase 5.1

This guide walks you through all the Supabase configuration needed for email authentication and multi-user support.

## Prerequisites

- A Supabase project (create one at https://supabase.com if you don't have one)
- Access to your Supabase dashboard

---

## Step 1: Run the Database Migration

You need to run the SQL migration to add the `user_id` column and enable Row Level Security (RLS).

### Option A: Using Supabase SQL Editor (Recommended)

1. Go to your Supabase Dashboard
2. Navigate to **SQL Editor** (left sidebar)
3. Click **New Query**
4. Copy and paste the entire contents of `docs/migrations/05_add_user_to_entries.sql`
5. Click **Run** (or press `Cmd/Ctrl + Enter`)

### Option B: Using Supabase CLI

```bash
# If you have Supabase CLI installed
supabase db push
# Or manually run the SQL file
supabase db execute -f docs/migrations/05_add_user_to_entries.sql
```

**What this does:**
- Adds `user_id` column to `entries` table
- Links it to `auth.users(id)` with CASCADE delete
- Enables Row Level Security (RLS)
- Creates policies so users can only access their own entries

---

## Step 2: Enable Email Authentication

1. Go to **Authentication** → **Providers** in your Supabase dashboard
2. Find **Email** in the list
3. Make sure it's **Enabled** (toggle should be ON)
4. Click on **Email** to configure settings:

### Email Settings:

**For Development (Recommended):**
- ✅ **Enable email confirmations**: OFF (for faster testing)
  - This allows users to sign up and immediately log in without email confirmation
  - Your signup page will redirect to dashboard automatically

**For Production:**
- ✅ **Enable email confirmations**: ON (more secure)
  - Users must confirm their email before logging in
  - Your signup page will redirect to login, and users confirm via email

**Other Settings:**
- **Secure email change**: ON (recommended)
- **Double confirm email changes**: ON (recommended for production)

---

## Step 3: Configure Email Templates (Optional but Recommended)

1. Go to **Authentication** → **Email Templates**
2. Customize the templates if desired:
   - **Confirm signup** - Sent when email confirmation is enabled
   - **Magic Link** - For passwordless login
   - **Change Email Address** - When user changes email
   - **Reset Password** - For password resets

For development, you can leave these as default.

---

## Step 4: Set Up Site URL (Important!)

1. Go to **Authentication** → **URL Configuration**
2. Set **Site URL** to your frontend URL:
   - Development: `http://localhost:3000`
   - Production: `https://your-domain.com`

3. Add **Redirect URLs**:
   - `http://localhost:3000/**` (for development)
   - `https://your-domain.com/**` (for production)
   - `http://localhost:3000/dashboard`
   - `http://localhost:3000/login`

This ensures Supabase knows where to redirect users after authentication.

---

## Step 5: Verify Environment Variables

Make sure your `.env` files have the correct Supabase credentials:

### Backend `.env` (in `backend/` directory):
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
```

### Frontend `.env.local` (in `frontend/` directory):
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

**Where to find these:**
1. Go to **Project Settings** → **API** in Supabase dashboard
2. Copy:
   - **Project URL** → `SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_URL`
   - **anon/public key** → `SUPABASE_ANON_KEY` / `NEXT_PUBLIC_SUPABASE_ANON_KEY`

---

## Step 6: Test the Setup

### 1. Test Signup
- Go to `http://localhost:3000/signup`
- Create a new account
- Should redirect to dashboard (if email confirmation is OFF)
- Or check email for confirmation link (if email confirmation is ON)

### 2. Test Login
- Go to `http://localhost:3000/login`
- Log in with your credentials
- Should redirect to dashboard

### 3. Test Reflection Creation
- Create a reflection on the home page
- Check Supabase dashboard → **Table Editor** → `entries` table
- Verify the entry has a `user_id` matching your user ID

### 4. Test Multi-User Isolation
- Create a second account
- Create reflections with that account
- Verify each user only sees their own reflections in the dashboard

---

## Troubleshooting

### "Authorization header is required" error
- Make sure you're logged in
- Check browser console for auth errors
- Verify `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` are set correctly

### "Row Level Security policy violation"
- Make sure you ran the migration SQL
- Check that RLS is enabled: `ALTER TABLE entries ENABLE ROW LEVEL SECURITY;`
- Verify policies exist in **Authentication** → **Policies**

### Users can see other users' data
- RLS policies might not be working
- Check that policies use `auth.uid() = user_id`
- Verify `user_id` column exists and has foreign key constraint

### Signup redirects to login instead of dashboard
- Email confirmation is enabled in Supabase
- Either disable it (for dev) or handle email confirmation flow
- Check **Authentication** → **Providers** → **Email** settings

### "Invalid or expired token" error
- Token might have expired
- Try logging out and logging back in
- Check that backend has correct `SUPABASE_URL` and `SUPABASE_ANON_KEY`

---

## Security Checklist

Before going to production:

- [ ] Email confirmations enabled
- [ ] Site URL set correctly
- [ ] Redirect URLs configured
- [ ] RLS policies tested and working
- [ ] Environment variables secured (not in git)
- [ ] CORS configured properly in backend
- [ ] Rate limiting considered (Supabase has built-in limits)

---

## Next Steps

Once everything is working:

1. Test with multiple users
2. Verify data isolation
3. Test logout/login flow
4. Check that old entries (with NULL user_id) are handled correctly
5. Consider adding password reset functionality
6. Set up email templates for production

---

## Quick Reference

**Supabase Dashboard Links:**
- SQL Editor: `https://supabase.com/dashboard/project/[project-id]/sql`
- Authentication: `https://supabase.com/dashboard/project/[project-id]/auth/providers`
- Table Editor: `https://supabase.com/dashboard/project/[project-id]/editor`
- API Settings: `https://supabase.com/dashboard/project/[project-id]/settings/api`

**Migration File:**
- Location: `docs/migrations/05_add_user_to_entries.sql`
- Also in: `backend/migrations/05_add_user_to_entries.sql`

