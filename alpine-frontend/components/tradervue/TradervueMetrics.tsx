'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, DollarSign, Target, Loader2, AlertCircle } from 'lucide-react'

interface TradervueMetricsProps {
  days?: number
  className?: string
}

interface Metrics {
  win_rate?: number
  total_profit?: number
  total_trades?: number
  profit_factor?: number
  sharpe_ratio?: number
  max_drawdown?: number
}

/**
 * Tradervue Metrics Component
 * Displays performance metrics from Tradervue
 */
export default function TradervueMetrics({ days = 30, className = '' }: TradervueMetricsProps) {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true)
        setError(null)

        const response = await fetch(`/api/v1/tradervue/metrics?days=${days}`)

        if (!response.ok) {
          if (response.status === 503) {
            setError('Tradervue integration not configured')
          } else if (response.status === 404) {
            setError('Metrics not available')
          } else {
            setError('Failed to load metrics')
          }
          return
        }

        const data = await response.json()
        setMetrics(data.metrics || {})
      } catch (err) {
        setError('Error fetching metrics')
        console.error('Tradervue metrics error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
  }, [days])

  if (loading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <Loader2 className="w-8 h-8 animate-spin text-alpine-blue" />
      </div>
    )
  }

  if (error) {
    return (
      <div className={`flex flex-col items-center justify-center p-4 bg-alpine-black-secondary rounded-lg ${className}`}>
        <AlertCircle className="w-8 h-8 text-yellow-500 mb-2" />
        <p className="text-sm text-gray-400">{error}</p>
      </div>
    )
  }

  if (!metrics) {
    return null
  }

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 ${className}`}>
      {metrics.win_rate !== undefined && (
        <MetricCard
          label="Win Rate"
          value={`${metrics.win_rate.toFixed(1)}%`}
          icon={<Target className="w-5 h-5" />}
          trend={metrics.win_rate >= 50 ? 'up' : 'down'}
        />
      )}

      {metrics.total_profit !== undefined && (
        <MetricCard
          label="Total Profit"
          value={`$${metrics.total_profit.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          icon={<DollarSign className="w-5 h-5" />}
          trend={metrics.total_profit >= 0 ? 'up' : 'down'}
        />
      )}

      {metrics.total_trades !== undefined && (
        <MetricCard
          label="Total Trades"
          value={metrics.total_trades.toString()}
          icon={<TrendingUp className="w-5 h-5" />}
        />
      )}

      {metrics.profit_factor !== undefined && (
        <MetricCard
          label="Profit Factor"
          value={metrics.profit_factor.toFixed(2)}
          icon={<TrendingUp className="w-5 h-5" />}
          trend={metrics.profit_factor >= 1 ? 'up' : 'down'}
        />
      )}

      {metrics.sharpe_ratio !== undefined && (
        <MetricCard
          label="Sharpe Ratio"
          value={metrics.sharpe_ratio.toFixed(2)}
          icon={<TrendingUp className="w-5 h-5" />}
          trend={metrics.sharpe_ratio >= 1 ? 'up' : 'down'}
        />
      )}

      {metrics.max_drawdown !== undefined && (
        <MetricCard
          label="Max Drawdown"
          value={`${Math.abs(metrics.max_drawdown).toFixed(2)}%`}
          icon={<TrendingDown className="w-5 h-5" />}
          trend="down"
        />
      )}
    </div>
  )
}

function MetricCard({
  label,
  value,
  icon,
  trend
}: {
  label: string
  value: string
  icon: React.ReactNode
  trend?: 'up' | 'down'
}) {
  const trendColor = trend === 'up' ? 'text-green-500' : trend === 'down' ? 'text-red-500' : 'text-gray-400'

  return (
    <div className="bg-alpine-black-secondary rounded-lg p-4 border border-alpine-black-tertiary">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">{label}</span>
        <div className={trendColor}>{icon}</div>
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
    </div>
  )
}

