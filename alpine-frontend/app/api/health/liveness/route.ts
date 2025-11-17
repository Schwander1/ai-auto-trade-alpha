import { NextResponse } from 'next/server'

/**
 * Kubernetes liveness probe endpoint
 * GET /api/health/liveness
 * 
 * Returns 200 if service is alive (quick check, no dependency verification)
 */
export async function GET() {
  try {
    // Quick check - just verify the service is responding
    return NextResponse.json(
      {
        status: 'alive',
        timestamp: new Date().toISOString(),
      },
      { status: 200 }
    )
  } catch (error) {
    console.error('Liveness check failed:', error)
    return NextResponse.json(
      {
        status: 'not_alive',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 503 }
    )
  }
}

