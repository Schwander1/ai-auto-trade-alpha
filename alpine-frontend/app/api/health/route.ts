import { NextResponse } from 'next/server'

/**
 * Server-side health check endpoint for Alpine Frontend
 * GET /api/health
 * 
 * Returns health status including:
 * - Service status
 * - Build version
 * - Environment
 * - Timestamp
 */
export async function GET() {
  try {
    const healthStatus = {
      status: 'healthy',
      service: 'Alpine Frontend',
      version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
      environment: process.env.NODE_ENV || 'development',
      timestamp: new Date().toISOString(),
      build: {
        node_version: process.version,
        next_version: process.env.NEXT_RUNTIME || 'unknown',
      },
    }

    return NextResponse.json(healthStatus, { status: 200 })
  } catch (error) {
    console.error('Health check failed:', error)
    return NextResponse.json(
      {
        status: 'unhealthy',
        service: 'Alpine Frontend',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 503 }
    )
  }
}

