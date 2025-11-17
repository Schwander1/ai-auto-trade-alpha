import { NextResponse } from 'next/server'

/**
 * Kubernetes readiness probe endpoint
 * GET /api/health/readiness
 * 
 * Returns 200 only if service is ready to handle traffic
 */
export async function GET() {
  try {
    // Quick check - verify service is responding
    // In a more complex setup, you might check:
    // - Database connectivity
    // - External API connectivity
    // - Cache connectivity
    
    return NextResponse.json(
      {
        status: 'ready',
        timestamp: new Date().toISOString(),
      },
      { status: 200 }
    )
  } catch (error) {
    console.error('Readiness check failed:', error)
    return NextResponse.json(
      {
        status: 'not_ready',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 503 }
    )
  }
}

