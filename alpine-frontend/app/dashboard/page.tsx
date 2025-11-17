'use client'

import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect, useState, useCallback, useMemo } from 'react'
import { useSignals } from '@/hooks/useSignals'
import SignalCard from '@/components/dashboard/SignalCard'
import dynamic from 'next/dynamic'
import Navigation from '@/components/dashboard/Navigation'

// Lazy load heavy chart and table components
const PerformanceChart = dynamic(() => import('@/components/dashboard/PerformanceChart'), {
  loading: () => <div className="h-64 animate-pulse bg-alpine-black-secondary rounded-lg" />,
  ssr: false  // Charts require browser APIs
})

const SymbolTable = dynamic(() => import('@/components/dashboard/SymbolTable'), {
  loading: () => <div className="h-96 animate-pulse bg-gray-800 rounded-lg" />,
  ssr: false
})
import { 
  TrendingUp, TrendingDown, DollarSign, Activity, 
  RefreshCw, AlertCircle, Loader2, BarChart3,
  ArrowRight, Signal as SignalIcon
} from 'lucide-react'
import Link from 'next/link'

// Type definitions for better type safety
interface DashboardStats {
  totalReturn?: number
  winRate?: number
  totalTrades?: number
  sharpeRatio?: number
}

interface EquityPoint {
  date: string
  value: number
}

interface Symbol {
  symbol: string
  name?: string
  [key: string]: unknown
}

/**
 * Main Dashboard Page - Overview with signals, stats, and portfolio
 * Optimized with proper TypeScript types, memoization, and error handling
 */
export default function DashboardPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [equityData, setEquityData] = useState<EquityPoint[]>([])
  const [symbols, setSymbols] = useState<Symbol[]>([])
  const [isLoadingStats, setIsLoadingStats] = useState(false)
  const [statsError, setStatsError] = useState<Error | null>(null)

  const { signals, isLoading, error, refresh, isPolling } = useSignals({
    limit: 10,
    premiumOnly: false,
    pollInterval: 30000,
    autoPoll: true,
    cache: true,
  })

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login')
    }
  }, [status, router])

  // Optimized fetch function with proper error handling
  const fetchStats = useCallback(async (abortSignal?: AbortSignal) => {
    if (!session) return
    
    setIsLoadingStats(true)
    setStatsError(null)
    
    try {
      const [statsRes, equityRes, symbolsRes] = await Promise.all([
        fetch('/api/performance/stats', { signal: abortSignal }).catch(() => null),
        fetch('/api/performance/equity-curve?period=30d', { signal: abortSignal }).catch(() => null),
        fetch('/api/symbols', { signal: abortSignal }).catch(() => null),
      ])

      // Process stats response
      if (statsRes?.ok) {
        const statsData = await statsRes.json()
        setStats(statsData as DashboardStats)
      } else if (statsRes && !statsRes.ok) {
        console.warn('Stats API returned error:', statsRes.status)
      }

      // Process equity data response
      if (equityRes?.ok) {
        const equityData = await equityRes.json()
        setEquityData((equityData.points || []) as EquityPoint[])
      } else if (equityRes && !equityRes.ok) {
        console.warn('Equity API returned error:', equityRes.status)
      }

      // Process symbols response
      if (symbolsRes?.ok) {
        const symbolsData = await symbolsRes.json()
        setSymbols((symbolsData.slice(0, 10) || []) as Symbol[])
      } else if (symbolsRes && !symbolsRes.ok) {
        console.warn('Symbols API returned error:', symbolsRes.status)
      }
    } catch (err) {
      // Don't set error if request was aborted
      if (err instanceof Error && err.name === 'AbortError') {
        return
      }
      const error = err instanceof Error ? err : new Error(String(err))
      setStatsError(error)
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setIsLoadingStats(false)
    }
  }, [session])

  useEffect(() => {
    if (!session) return

    const abortController = new AbortController()
    fetchStats(abortController.signal)

    // Cleanup: abort requests on unmount
    return () => {
      abortController.abort()
    }
  }, [session, fetchStats])

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-alpine-black-primary flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-alpine-neon-cyan animate-spin" />
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return null
  }

  return (
    <div className="min-h-screen bg-alpine-black-primary">
      {/* Navigation */}
      <Navigation />

      <main className="container mx-auto px-4 py-6 space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Win Rate"
            value={stats?.win_rate ? `${stats.win_rate.toFixed(1)}%` : '-'}
            icon={<TrendingUp className="w-5 h-5" />}
            trend={stats?.win_rate ? 'up' : undefined}
            color="alpine-neoncya-n"
          />
          <StatCard
            title="Total ROI"
            value={stats?.total_roi ? `${stats.total_roi.toFixed(1)}%` : '-'}
            icon={<DollarSign className="w-5 h-5" />}
            trend={stats?.total_roi > 0 ? 'up' : stats?.total_roi < 0 ? 'down' : undefined}
            color="alpine-neonpin-k"
          />
          <StatCard
            title="Active Signals"
            value={signals?.length || 0}
            icon={<SignalIcon className="w-5 h-5" />}
            color="alpine-neon-purple"
          />
          <StatCard
            title="Total Trades"
            value={stats?.total_trades || 0}
            icon={<Activity className="w-5 h-5" />}
            color="alpine-semanticsucces-s
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PerformanceChart data={equityData} type="equity" />
          <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-alpine-neon-cyan" />
              <h3 className="text-lg font-bold text-alpine-text-primary">Recent Activity</h3>
            </div>
            <div className="space-y-3">
              {signals?.slice(0, 5).map((signal: any) => (
                  <div key={signal.id} className="flex items-center justify-between p-3 bg-alpine-black-primary rounded-lg">
                  <div>
                    <div className="font-semibold text-alpine-text-primary ">{signal.symbol}</div>
                    <div className="text-sm text-alpine-text-secondary">{signal.action}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-alpine-text-primary ">
                      {signal.confidence.toFixed(1)}%
                    </div>
                    <div className="text-sm text-alpine-text-secondary">
                      {new Date(signal.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Latest Signals */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-alpine-text-primary ">Latest Signals</h2>
            <div className="flex items-center gap-2">
              {isPolling && (
                <div className="flex items-center gap-2 text-sm text-alpine-text-secondary">
                  <div className="w-2 h-2 bg-alpine-neon-cyan rounded-full animate-pulse" />
                  Live
                </div>
              )}
              <button
                onClick={refresh}
                disabled={isLoading}
                className="p-2 rounded-lg bg-alpine-black-secondary border border-alpine-black-border hov-er:border-alpine-neon-cyan/50 transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 text-alpine-text-primary ${isLoading ? 'animate-spin' : ''}`} />
              </button>
              <Link
                href="/signals"
                className="flex items-center gap-1 text-sm text-alpine-neon-cyan hover:text-alpine-neon-pink transition-colors"
              >
                View All
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-4 bg-alpine-semantic-error/10 border border-alpine-semantic-error/30 rounded-lg flex items-center gap-2 text-alpine-semantic-error>
              <AlertCircle className="w-5 h-5" />
              <span>{error.message || 'Failed to load signals'}</span>
            </div>
          )}

          {isLoading && signals.length === 0 ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-alpine-neon-cyan animate-spin" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {signals.slice(0, 6).map((signal: any) => (
                <SignalCard key={signal.id} signal={signal} />
              ))}
            </div>
          )}
        </div>

        {/* Symbols Table */}
        {symbols.length > 0 && (
          <div>
            <h2 className="text-xl font-bold text-alpine-text-primary mb-4">Market Overview</h2>
            <SymbolTable
              symbols={symbols}
              onSymbolClick={(symbol: string) => router.push(`/signals?symbol=${symbol}`)}
            />
          </div>
        )}
      </main>
    </div>
  )
}

function StatCard({ 
  title, 
  value, 
  icon, 
  trend, 
  color 
}: { 
  title: string
  value: string | number
  icon: React.ReactNode
  trend?: 'up' | 'down'
  color: string
}) {
  return (
    <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-2">
        <div className={`p-2 rounded-lg bg-${color}/10 text-${color}`}>
          {icon}
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-sm ${
            trend === 'up' ? 'text-alpine-neon-cyan' : 'text-alpine-semantic-error
          }`}>
            {trend === 'up' ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
          </div>
        )}
      </div>
      <div className="text-2xl font-black text-alpine-text-primary mb-1">{value}</div>
      <div className="text-sm text-alpine-text-secondary">{title}</div>
    </div>
  )
}
