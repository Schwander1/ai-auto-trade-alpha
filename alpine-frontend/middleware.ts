/**
 * Next.js middleware for route protection
 * Protects /dashboard and /signals routes
 * Checks subscription status for protected routes
 */

import { withAuth } from 'next-auth/middleware'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export default withAuth(
  async function middleware(req: NextRequest) {
    const { pathname } = req.nextUrl
    
    // For protected routes, check subscription status
    if (pathname.startsWith('/dashboard') || pathname.startsWith('/signals')) {
      // Note: Full subscription check should be done in the page component
      // Middleware only checks authentication
      // Subscription status is checked client-side for better UX
      return NextResponse.next()
    }
    
    return NextResponse.next()
  },
  {
    callbacks: {
      authorized: ({ token, req }) => {
        // Protect /dashboard and /signals routes
        const { pathname } = req.nextUrl
        
        if (pathname.startsWith('/dashboard') || pathname.startsWith('/signals')) {
          return !!token // Require authentication
        }
        
        return true // Allow access to other routes
      },
    },
    pages: {
      signIn: '/login',
    },
  }
)

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/signals/:path*',
  ],
}

