/**
 * API client for fetching signals from external signal provider.
 * Includes retry logic and error handling.
 */

import type { Signal } from '@/types/signal'

const EXTERNAL_SIGNAL_API_BASE_URL = process.env.NEXT_PUBLIC_EXTERNAL_SIGNAL_API_URL || process.env.NEXT_PUBLIC_ARGO_API_URL || 'http://178.156.194.174:8000'

const DEFAULT_RETRY_ATTEMPTS = 3
const DEFAULT_RETRY_DELAY = 1000 // 1 second

/**
 * API Error class for better error handling
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: unknown
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

/**
 * Retry configuration
 */
interface RetryConfig {
  maxAttempts?: number
  delay?: number
  backoff?: boolean
}

/**
 * Sleep utility for retry delays
 */
const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Fetch with retry logic
 */
async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retryConfig: RetryConfig = {}
): Promise<Response> {
  const {
    maxAttempts = DEFAULT_RETRY_ATTEMPTS,
    delay = DEFAULT_RETRY_DELAY,
    backoff = true,
  } = retryConfig

  let lastError: Error | null = null

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const response = await fetch(url, {
        ...options,
        signal: options.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      })

      // If successful, return immediately
      if (response.ok) {
        return response
      }

      // If 4xx error (client error), don't retry
      if (response.status >= 400 && response.status < 500) {
        const errorData = await response.json().catch(() => ({}))
        throw new ApiError(
          `Client error: ${response.statusText}`,
          response.status,
          errorData
        )
      }

      // For 5xx errors or network errors, throw to trigger retry
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
    } catch (error) {
      // Don't retry if request was aborted
      if (error instanceof Error && error.name === 'AbortError') {
        throw error
      }

      lastError = error instanceof Error ? error : new Error(String(error))

      // Don't retry on last attempt
      if (attempt === maxAttempts) {
        break
      }

      // Calculate delay with exponential backoff if enabled
      const retryDelay = backoff ? delay * Math.pow(2, attempt - 1) : delay

      // Wait before retrying
      await sleep(retryDelay)
    }
  }

  // If we get here, all retries failed
  throw lastError || new Error('Request failed after retries')
}

/**
 * Fetch latest trading signals from external signal provider API
 * 
 * @param limit - Maximum number of signals to fetch (default: 10)
 * @param premiumOnly - If true, only fetch premium signals (95%+ confidence)
 * @param signal - Optional AbortSignal to cancel the request
 * @returns Promise resolving to array of Signal objects
 * @throws ApiError if request fails after retries
 * 
 * @example
 * ```typescript
 * const signals = await fetchLatestSignals(20, true)
 * ```
 */
export async function fetchLatestSignals(
  limit: number = 10,
  premiumOnly: boolean = false,
  signal?: AbortSignal
): Promise<Signal[]> {
  try {
    const params = new URLSearchParams({
      limit: limit.toString(),
      premium_only: premiumOnly.toString(),
    })

    const url = `${EXTERNAL_SIGNAL_API_BASE_URL}/api/signals/latest?${params.toString()}`

    const response = await fetchWithRetry(url, {
      method: 'GET',
      signal,
    })

    const data = await response.json()

    // Validate response is an array
    if (!Array.isArray(data)) {
      throw new ApiError('Invalid response format: expected array', response.status, data)
    }

    // Type assertion - in production, you might want to validate each signal
    return data as Signal[]
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }

    // Wrap unknown errors
    throw new ApiError(
      error instanceof Error ? error.message : 'Failed to fetch signals',
      undefined,
      error
    )
  }
}

/**
 * Fetch a single signal by ID from external signal provider API
 * 
 * @param id - Signal ID to fetch
 * @returns Promise resolving to Signal object
 * @throws ApiError if signal not found or request fails
 * 
 * @example
 * ```typescript
 * const signal = await fetchSignalById('SIG_20241111_123456')
 * ```
 */
export async function fetchSignalById(id: string): Promise<Signal> {
  try {
    // Note: This endpoint may not exist yet in the backend
    // If it doesn't exist, you may need to fetch all signals and filter
    const url = `${EXTERNAL_SIGNAL_API_BASE_URL}/api/signals/${id}`

    const response = await fetchWithRetry(url, {
      method: 'GET',
    })

    if (response.status === 404) {
      throw new ApiError(`Signal with ID ${id} not found`, 404)
    }

    const data = await response.json()

    // Validate response is an object
    if (typeof data !== 'object' || data === null || Array.isArray(data)) {
      throw new ApiError('Invalid response format: expected signal object', response.status, data)
    }

    return data as Signal
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }

    // Wrap unknown errors
    throw new ApiError(
      error instanceof Error ? error.message : 'Failed to fetch signal',
      undefined,
      error
    )
  }
}

/**
 * Health check for external signal provider API
 * 
 * @returns Promise resolving to health status
 */
export async function checkApiHealth(): Promise<{ status: string; version?: string }> {
  try {
    const url = `${EXTERNAL_SIGNAL_API_BASE_URL}/health`
    const response = await fetchWithRetry(url, {
      method: 'GET',
    }, { maxAttempts: 1 }) // Don't retry health checks

    return await response.json()
  } catch (error) {
    throw new ApiError(
      'API health check failed',
      undefined,
      error
    )
  }
}

