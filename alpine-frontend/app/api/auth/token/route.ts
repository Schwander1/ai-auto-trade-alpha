/**
 * API route to get JWT token for WebSocket authentication
 * Exchanges NextAuth session for backend JWT token
 */
import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth/next'
import { authOptions } from '@/lib/auth'
import { db } from '@/lib/db'

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // Get backend API URL
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'
    
    // Get user from database to verify they exist
    const user = await db.user.findUnique({
      where: { id: session.user.id },
      select: { id: true, email: true, tier: true }
    })
    
    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }

    // Call backend to get JWT token
    // We'll use the backend's login endpoint or create a token exchange endpoint
    try {
      // First, try to get token from backend using user credentials
      // Since we have the user ID, we can create a token exchange
      const response = await fetch(`${apiUrl}/api/v1/auth/token`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // We need to authenticate with the backend
          // For now, we'll need to store backend credentials or use a service account
        },
        // Include cookies if backend uses cookie-based auth
        credentials: 'include',
      })

      if (response.ok) {
        const data = await response.json()
        return NextResponse.json({
          token: data.token,
          expires_in: data.expires_in || 86400
        })
      } else {
        // If direct token endpoint doesn't work, we need to login to backend
        // This requires the user's password, which we don't have in the session
        // Alternative: Store backend JWT in NextAuth session during initial login
        // For now, return error with instructions
        return NextResponse.json(
          { 
            error: 'Backend authentication required',
            message: 'Please ensure backend JWT token is stored in session during login'
          },
          { status: 503 }
        )
      }
    } catch (fetchError) {
      console.error('Backend token fetch error:', fetchError)
      return NextResponse.json(
        { error: 'Failed to connect to backend' },
        { status: 503 }
      )
    }
  } catch (error) {
    console.error('Token endpoint error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

