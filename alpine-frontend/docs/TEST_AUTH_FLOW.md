# Testing NextAuth.js Authentication Flow

This guide walks through testing the complete authentication flow end-to-end.

## Prerequisites

1. ✅ Database is set up and migrated
2. ✅ `.env.local` has `DATABASE_URL` and `NEXTAUTH_SECRET`
3. ✅ Dependencies installed (`npm install`)
4. ✅ Prisma Client generated (`npx prisma generate`)

## Step 1: Seed Test Users

```bash
cd alpine-frontend
npx prisma db seed
```

This creates:
- `starter@alpineanalytics.com` / `password123` (STARTER tier)
- `professional@alpineanalytics.com` / `password123` (PROFESSIONAL tier)
- `institutional@alpineanalytics.com` / `password123` (INSTITUTIONAL tier)

## Step 2: Start Development Server

```bash
npm run dev
```

Server should start at `http://localhost:3000`

## Step 3: Test Signup Flow

1. **Navigate to Signup Page**
   - Go to: `http://localhost:3000/signup`
   - Should see signup form

2. **Create New Account**
   - Email: `test@example.com`
   - Password: `Test1234` (must meet requirements)
   - Confirm Password: `Test1234`
   - Click "Create Account"
   - Should see success message and redirect to login

3. **Verify User Created**
   ```bash
   npx prisma studio
   ```
   - Open `http://localhost:5555`
   - Check `users` table for new user
   - Verify password is hashed (not plain text)

## Step 4: Test Login Flow

1. **Navigate to Login Page**
   - Go to: `http://localhost:3000/login`
   - Or use seeded user: `starter@alpineanalytics.com` / `password123`

2. **Login with Credentials**
   - Enter email and password
   - Click "Sign In"
   - Should redirect to `/dashboard`

3. **Verify Session**
   - Dashboard should show:
     - User email in header
     - User tier badge
     - Sign Out button
   - Check browser DevTools → Application → Cookies
     - Should see `next-auth.session-token` cookie

## Step 5: Test Protected Routes

1. **Access Dashboard (Authenticated)**
   - Should see dashboard with signals
   - User info displayed in header

2. **Test Route Protection**
   - Sign out
   - Try to access `http://localhost:3000/dashboard`
   - Should redirect to `/login`
   - Try to access `http://localhost:3000/signals`
   - Should redirect to `/login`

3. **Access After Login**
   - Login again
   - Should be able to access `/dashboard` and `/signals`

## Step 6: Test Sign Out

1. **Sign Out from Dashboard**
   - Click "Sign Out" button
   - Should redirect to home page (`/`)
   - Session cookie should be removed

2. **Verify Sign Out**
   - Try accessing `/dashboard` again
   - Should redirect to `/login`

## Step 7: Test Error Cases

### Invalid Credentials
1. Go to `/login`
2. Enter wrong email/password
3. Should show error: "Invalid email or password"

### Weak Password (Signup)
1. Go to `/signup`
2. Enter password that doesn't meet requirements
3. Should show validation error

### Password Mismatch (Signup)
1. Go to `/signup`
2. Enter different passwords
3. Should show: "Passwords do not match"

### Duplicate Email (Signup)
1. Try to signup with existing email
2. Should show: "User with this email already exists"

## Step 8: Test Session Persistence

1. **Login**
   - Login with valid credentials

2. **Refresh Page**
   - Press F5 or refresh browser
   - Should remain logged in
   - Session should persist

3. **Close and Reopen Browser**
   - Close browser tab
   - Reopen and go to `/dashboard`
   - Should still be logged in (session cookie persists)

## Step 9: Test Tier Information

1. **Login with Different Tiers**
   - Login as `starter@alpineanalytics.com`
   - Check tier badge shows "STARTER"
   - Logout
   - Login as `professional@alpineanalytics.com`
   - Check tier badge shows "PROFESSIONAL"
   - Logout
   - Login as `institutional@alpineanalytics.com`
   - Check tier badge shows "INSTITUTIONAL"

## Step 10: Verify Database State

```bash
npx prisma studio
```

Check:
- ✅ `users` table has all test users
- ✅ `sessions` table has active sessions (if logged in)
- ✅ Passwords are hashed (not plain text)
- ✅ User tiers are correct

## Expected Behavior Summary

### ✅ Working Correctly If:

1. **Signup**
   - ✅ Creates user in database
   - ✅ Password is hashed
   - ✅ Redirects to login after success
   - ✅ Shows validation errors for invalid input

2. **Login**
   - ✅ Authenticates with correct credentials
   - ✅ Rejects invalid credentials
   - ✅ Creates session
   - ✅ Redirects to dashboard

3. **Protected Routes**
   - ✅ Redirects unauthenticated users to login
   - ✅ Allows authenticated users to access
   - ✅ Shows user info in dashboard

4. **Sign Out**
   - ✅ Removes session
   - ✅ Redirects to home
   - ✅ Prevents access to protected routes

5. **Session Management**
   - ✅ Persists across page refreshes
   - ✅ Includes user tier in session
   - ✅ Session expires after 30 days

## Troubleshooting

### "NEXTAUTH_SECRET is not set"
- Add `NEXTAUTH_SECRET` to `.env.local`
- Generate with: `openssl rand -base64 32`

### "Invalid credentials" but password is correct
- Check password is hashed in database
- Verify bcryptjs is working
- Check database connection

### Middleware not redirecting
- Verify `middleware.ts` is in root directory
- Check matcher includes your routes
- Restart dev server

### Session not persisting
- Check `NEXTAUTH_URL` matches actual URL
- Verify cookies are enabled
- Check browser console for errors

### "Module not found: next-auth"
- Run `npm install`
- Verify `next-auth` is in `package.json`

## Manual API Testing

### Test Signup API

```bash
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test2@example.com","password":"Test1234"}'
```

### Test NextAuth Endpoint

```bash
# Get CSRF token
curl http://localhost:3000/api/auth/csrf

# Sign in (requires CSRF token)
curl -X POST http://localhost:3000/api/auth/callback/credentials \
  -H "Content-Type: application/json" \
  -d '{"email":"starter@alpineanalytics.com","password":"password123","csrfToken":"YOUR_CSRF_TOKEN"}'
```

## Success Criteria

✅ All test cases pass
✅ Users can signup and login
✅ Protected routes are protected
✅ Sessions persist correctly
✅ Sign out works
✅ User tier is displayed
✅ Error handling works
✅ Database state is correct

## Next Steps After Testing

- [ ] Add email verification
- [ ] Add password reset
- [ ] Add OAuth providers
- [ ] Add rate limiting
- [ ] Add 2FA support

