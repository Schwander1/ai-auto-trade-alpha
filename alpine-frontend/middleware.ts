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
    const token = req.nextauth.token

    // Admin-only routes
    if (pathname.startsWith('/execution')) {
      // Check if user is admin
      const isAdmin = (token as any)?.isAdmin === true
      if (!isAdmin) {
        // Redirect to dashboard with error message
        const url = req.nextUrl.clone()
        url.pathname = '/dashboard'
        url.searchParams.set('error', 'admin_required')
        return NextResponse.redirect(url)
      }
    }

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
        const { pathname } = req.nextUrl

        // Admin-only routes
        if (pathname.startsWith('/execution')) {
          return (token as any)?.isAdmin === true
        }

        // Protected routes (require authentication)
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
    '/execution/:path*',  // Add execution dashboard
  ],
}
