# NextAuth.js Authentication Setup

This document describes the authentication system for Alpine Analytics.

## Overview

Alpine uses NextAuth.js v4 with:
- **Credentials Provider**: Email/password authentication
- **JWT Sessions**: 30-day session duration
- **Route Protection**: Middleware protects `/dashboard` and `/signals` routes
- **Tier System**: STARTER, PROFESSIONAL, INSTITUTIONAL

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

This will install:
- `next-auth` - Authentication library
- `@next-auth/prisma-adapter` - Prisma adapter for NextAuth
- `bcryptjs` - Password hashing

### 2. Environment Variables

Add to `.env.local`:

```bash
# NextAuth Configuration
NEXTAUTH_URL="http://localhost:3000"  # Change to your production URL
NEXTAUTH_SECRET="your-secret-key-here"  # Generate with: openssl rand -base64 32

# Database (already configured)
DATABASE_URL="postgresql://user:pass@host:5432/alpine"
```

**Generate NEXTAUTH_SECRET:**
```bash
openssl rand -base64 32
```

### 3. Database Migration

After updating the schema with new tier names:

```bash
# Generate Prisma Client
npm run db:generate

# Create and run migration
npm run db:migrate

# Seed database with test users
npm run db:seed
```

### 4. Test Users

After seeding, you can login with:

- **STARTER Tier:**
  - Email: `starter@alpineanalytics.com`
  - Password: `password123`

- **PROFESSIONAL Tier:**
  - Email: `professional@alpineanalytics.com`
  - Password: `password123`

- **INSTITUTIONAL Tier:**
  - Email: `institutional@alpineanalytics.com`
  - Password: `password123`

## File Structure

```
alpine-frontend/
├── app/
│   ├── api/
│   │   └── auth/
│   │       ├── [...nextauth]/
│   │       │   └── route.ts      # NextAuth handler
│   │       └── signup/
│   │           └── route.ts      # Signup API endpoint
│   ├── login/
│   │   └── page.tsx              # Login page
│   ├── signup/
│   │   └── page.tsx              # Signup page
│   ├── dashboard/
│   │   └── page.tsx              # Protected dashboard
│   └── signals/
│       └── page.tsx              # Protected signals page
├── lib/
│   ├── auth.ts                   # Auth helper functions
│   └── db.ts                     # Prisma client
├── middleware.ts                 # Route protection
└── types/
    └── next-auth.d.ts            # NextAuth type definitions
```

## Usage

### Protecting Routes

Routes are automatically protected by middleware. To protect additional routes, update `middleware.ts`:

```typescript
export const config = {
  matcher: [
    '/dashboard/:path*',
    '/signals/:path*',
    '/your-new-route/:path*',  // Add here
  ],
}
```

### Using Auth Helpers in Server Components

```typescript
import { requireAuth, requireTier, getCurrentUser } from '@/lib/auth'

// Get current user (returns null if not authenticated)
const user = await getCurrentUser()

// Require authentication (redirects to /login if not authenticated)
const user = await requireAuth()

// Require specific tier (redirects to pricing if insufficient)
const user = await requireTier('PROFESSIONAL')
```

### Using Auth in Client Components

```typescript
'use client'

import { useSession, signIn, signOut } from 'next-auth/react'

export default function MyComponent() {
  const { data: session, status } = useSession()

  if (status === 'loading') return <div>Loading...</div>
  if (status === 'unauthenticated') return <div>Not logged in</div>

  return (
    <div>
      <p>Logged in as {session?.user?.email}</p>
      <p>Tier: {session?.user?.tier}</p>
      <button onClick={() => signOut()}>Sign Out</button>
    </div>
  )
}
```

### Checking Tier Access

```typescript
import { hasTierAccess } from '@/lib/auth'

const canAccess = hasTierAccess(user.tier, 'PROFESSIONAL')
// Returns true if user has PROFESSIONAL or INSTITUTIONAL tier
```

## Tier Hierarchy

1. **STARTER** - Basic access
2. **PROFESSIONAL** - Enhanced features
3. **INSTITUTIONAL** - Full access

The `requireTier()` function enforces tier requirements:
- `requireTier('PROFESSIONAL')` allows PROFESSIONAL and INSTITUTIONAL
- `requireTier('INSTITUTIONAL')` only allows INSTITUTIONAL

## Adding OAuth Providers (Future)

To add OAuth providers (Google, GitHub, etc.), update `app/api/auth/[...nextauth]/route.ts`:

```typescript
import GoogleProvider from 'next-auth/providers/google'

export const authOptions: NextAuthOptions = {
  // ... existing config
  providers: [
    CredentialsProvider({ /* ... */ }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
}
```

## Troubleshooting

### "NEXTAUTH_SECRET is not set"

Add `NEXTAUTH_SECRET` to your `.env.local` file.

### "Invalid credentials" error

- Verify user exists in database
- Check password hash is correct
- Ensure bcryptjs is installed

### Middleware not protecting routes

- Check `middleware.ts` matcher includes your route
- Verify middleware is in the root directory
- Restart Next.js dev server

### Session not persisting

- Check `NEXTAUTH_URL` matches your actual URL
- Verify cookies are enabled in browser
- Check browser console for errors

## Security Notes

1. **Never commit `.env.local`** to version control
2. **Use strong NEXTAUTH_SECRET** (32+ characters)
3. **Use HTTPS in production** for secure cookies
4. **Rate limit** signup/login endpoints (add later)
5. **Validate email** format on signup
6. **Enforce password strength** (already implemented)

## Next Steps

- [ ] Add email verification
- [ ] Add password reset functionality
- [ ] Add OAuth providers (Google, GitHub)
- [ ] Add rate limiting
- [ ] Add 2FA support
- [ ] Add session management UI

