'use client'

import { useState, useEffect } from 'react'

export interface TradingEnvironment {
  environment: 'development' | 'production'
  trading_mode: 'dev' | 'production' | 'prop_firm' | 'simulation'
  account_name: string | null
  account_number?: string
  portfolio_value?: number
  buying_power?: number
  prop_firm_enabled: boolean
  alpaca_connected: boolean
  account_status?: string | null
}

interface UseTradingEnvironmentReturn {
  status: TradingEnvironment | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

/**
 * Hook to fetch and manage trading environment status
 * Automatically refreshes every 30 seconds
 */
export function useTradingEnvironment(): UseTradingEnvironmentReturn {
  const [status, setStatus] = useState<TradingEnvironment | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStatus = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('/api/v1/trading/status', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication required')
        } else if (response.status === 503) {
          throw new Error('Trading status service unavailable')
        } else {
          throw new Error(`Failed to fetch trading status: ${response.statusText}`)
        }
      }

      const data = await response.json()
      setStatus(data)
      setError(null)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      setStatus(null)
      console.error('Failed to fetch trading environment status:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Initial fetch
    fetchStatus()

    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchStatus, 30000)

    return () => clearInterval(interval)
  }, [])

  return {
    status,
    loading,
    error,
    refresh: fetchStatus,
  }
}

