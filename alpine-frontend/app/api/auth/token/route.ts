/**
 * API route to get JWT token for WebSocket authentication
 * Proxies the request to the backend with proper authentication
 */
import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth/next'
import { authOptions } from '@/lib/auth'

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
    
    // For now, we'll need to get the token from the backend
    // This requires the user to have a valid session with the backend
    // You may need to store the backend JWT token in the NextAuth session
    // or create a separate endpoint that exchanges NextAuth session for backend token
    
    // TODO: Implement proper token exchange
    // For now, return an error indicating this needs to be implemented
    return NextResponse.json(
      { error: 'Token endpoint not fully implemented. Please use login endpoint to get token.' },
      { status: 501 }
    )
  } catch (error) {
    console.error('Token endpoint error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

