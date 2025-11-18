'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useSession } from 'next-auth/react'
import { fetchLatestSignals } from '@/lib/api'
import { useWebSocket } from './useWebSocket'
import type { Signal } from '@/types/signal'

/**
 * Hook return type
 */
interface UseSignalsReturn {
  /** Array of signals */
  signals: Signal[]
  /** Loading state */
  isLoading: boolean
  /** Error state */
  error: Error | null
  /** Manually refresh signals */
  refresh: () => Promise<void>
  /** Whether polling is active */
  isPolling: boolean
}

/**
 * Configuration options for useSignals hook
 */
interface UseSignalsOptions {
  /** Maximum number of signals to fetch */
  limit?: number
  /** Only fetch premium signals (95%+ confidence) */
  premiumOnly?: boolean
  /** Polling interval in milliseconds (default: 30000 = 30 seconds) */
  pollInterval?: number
  /** Whether to start polling immediately (default: true) */
  autoPoll?: boolean
  /** Whether to cache results (default: true) */
  cache?: boolean
  /** Whether to use WebSocket for real-time updates (default: true) */
  useWebSocket?: boolean
}

/**
 * Custom hook for fetching and polling trading signals from external signal provider API.
 * 
 * Features:
 * - Automatic polling every 30 seconds (configurable)
 * - Result caching to prevent unnecessary re-renders
 * - Loading and error states
 * - Manual refresh capability
 * 
 * @param options - Configuration options
 * @returns Object with signals, loading state, error state, and refresh function
 * 
 * @example
 * ```tsx
 * function SignalDashboard() {
 *   const { signals, isLoading, error, refresh } = useSignals({
 *     limit: 20,
 *     premiumOnly: false,
 *     pollInterval: 30000,
 *   })
 * 
 *   if (isLoading) return <div>Loading...</div>
 *   if (error) return <div>Error: {error.message}</div>
 * 
 *   return (
 *     <div>
 *       {signals.map(signal => (
 *         <SignalCard key={signal.id} signal={signal} />
 *       ))}
 *     </div>
 *   )
 * }
 * ```
 */
export function useSignals(options: UseSignalsOptions = {}): UseSignalsReturn {
  const {
    limit = 10,
    premiumOnly = false,
    pollInterval = 30000, // 30 seconds
    autoPoll = true,
    cache = true,
    useWebSocket: enableWebSocket = true,
  } = options

  const { data: session } = useSession()

  // State
  const [signals, setSignals] = useState<Signal[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<Error | null>(null)
  const [isPolling, setIsPolling] = useState<boolean>(autoPoll)

  // Refs for cleanup and caching
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)
  const cachedSignalsRef = useRef<Signal[]>([])
  const lastFetchTimeRef = useRef<number>(0)

  // Get WebSocket URL with token
  const getWebSocketUrl = useCallback(async () => {
    if (!session) return null
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'
    const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws'
    const wsHost = apiUrl.replace(/^https?:\/\//, '').replace(/\/$/, '')
    
    // Get JWT token from Next.js API route (which proxies to backend)
    try {
      const response = await fetch('/api/auth/token', {
        credentials: 'include',
      })
      if (response.ok) {
        const data = await response.json()
        const token = data.token || data.accessToken
        if (token) {
          return `${wsProtocol}://${wsHost}/ws/signals?token=${encodeURIComponent(token)}`
        }
      } else {
        // If token endpoint not available, try direct backend call
        // This requires the user to be logged in via the backend API
        console.warn('Token endpoint not available, WebSocket will use fallback auth')
      }
    } catch (err) {
      console.warn('Failed to get auth token for WebSocket:', err)
    }
    
    return null
  }, [session])
  
  const [wsUrl, setWsUrl] = useState<string | null>(null)
  
  // Fetch WebSocket URL with token
  useEffect(() => {
    if (enableWebSocket && session) {
      getWebSocketUrl().then(url => setWsUrl(url))
    } else {
      setWsUrl(null)
    }
  }, [enableWebSocket, session, getWebSocketUrl])

  // WebSocket connection
  const { isConnected: wsConnected, lastMessage: wsMessage } = useWebSocket({
    url: wsUrl || '',
    enabled: enableWebSocket && !!session && !!wsUrl,
    onMessage: useCallback((data: any) => {
      if (data.type === 'new_signal') {
        const newSignal = data.data as Signal
        
        // Check if signal matches filters
        if (premiumOnly && (!newSignal.type || !newSignal.type.toUpperCase().includes('PREMIUM'))) {
          return
        }
        
        // Add new signal to the beginning of the list
        setSignals(prev => {
          // Check if signal already exists
          if (prev.some(s => s.id === newSignal.id)) {
            return prev
          }
          
          // Add new signal and limit to specified limit
          const updated = [newSignal, ...prev].slice(0, limit)
          return updated
        })
      }
    }, [premiumOnly, limit]),
    onError: useCallback((err: Event) => {
      console.error('WebSocket error:', err)
      // Don't set error state for WebSocket errors, just log them
    }, []),
  })

  /**
   * Fetch signals from API
   */
  const fetchSignals = useCallback(async (abortSignal?: AbortSignal) => {
    try {
      setIsLoading(true)
      setError(null)

      // Cancel previous request if still pending
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }

      // Create new abort controller
      const controller = new AbortController()
      abortControllerRef.current = controller

      // Merge abort signals if provided
      if (abortSignal) {
        abortSignal.addEventListener('abort', () => controller.abort())
      }

      const fetchedSignals = await fetchLatestSignals(limit, premiumOnly, controller.signal)

      // Check if we should update (cache check)
      if (cache) {
        const signalsChanged = JSON.stringify(fetchedSignals) !== JSON.stringify(cachedSignalsRef.current)
        if (!signalsChanged && cachedSignalsRef.current.length > 0) {
          // No changes, skip update
          setIsLoading(false)
          return
        }
        cachedSignalsRef.current = fetchedSignals
      }

      setSignals(fetchedSignals)
      lastFetchTimeRef.current = Date.now()
      setError(null)
    } catch (err) {
      // Don't set error if request was aborted
      if (err instanceof Error && (err.name === 'AbortError' || err.message.includes('aborted'))) {
        return
      }

      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      console.error('Failed to fetch signals:', error)
    } finally {
      setIsLoading(false)
    }
  }, [limit, premiumOnly, cache])

  /**
   * Manual refresh function
   */
  const refresh = useCallback(async () => {
    await fetchSignals()
  }, [fetchSignals])

  /**
   * Setup polling interval
   */
  useEffect(() => {
    if (!isPolling || pollInterval <= 0) {
      return
    }

    // Initial fetch
    fetchSignals()

    // Setup interval
    intervalRef.current = setInterval(() => {
      fetchSignals()
    }, pollInterval)

    // Cleanup
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
        abortControllerRef.current = null
      }
    }
  }, [isPolling, pollInterval, fetchSignals])

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  return {
    signals,
    isLoading,
    error,
    refresh,
    isPolling,
  }
}

