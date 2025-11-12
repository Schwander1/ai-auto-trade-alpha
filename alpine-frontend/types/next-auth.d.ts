/**
 * NextAuth type definitions for Alpine Analytics
 */

import 'next-auth'
import { UserTier } from '@prisma/client'

declare module 'next-auth' {
  interface Session {
    user: {
      id: string
      email: string
      tier: UserTier
    }
  }

  interface User {
    id: string
    email: string
    tier: UserTier
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    id: string
    email: string
    tier: UserTier
  }
}

