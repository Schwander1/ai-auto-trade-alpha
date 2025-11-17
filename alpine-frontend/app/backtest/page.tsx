'use client'

import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useState, useEffect, useCallback, useRef } from 'react'
import PerformanceChart from '@/components/dashboard/PerformanceChart'
import Navigation from '@/components/dashboard/Navigation'
import { 
  Play, Loader2, AlertCircle, BarChart3, TrendingUp,
  DollarSign, Target, Zap, Calendar
} from 'lucide-react'

/**
 * Backtest Page - Run backtests and view results
 */
export default function BacktestPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [isRunning, setIsRunning] = useState(false)
  const [backtestConfig, setBacktestConfig] = useState({
    symbol: 'AAPL',
    startDate: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
    initialCapital: 10000,
    strategy: 'default',
    riskPerTrade: 0.02,
  })
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [backtestHistory, setBacktestHistory] = useState<any[]>([])
  const abortControllerRef = useRef<AbortController | null>(null)

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login')
    }
  }, [status, router])

  useEffect(() => {
    // Load backtest history
    const loadHistory = async () => {
      try {
        const response = await fetch('/api/backtest/history')
        if (response.ok) {
          const data = await response.json()
          setBacktestHistory(data)
        }
      } catch (err) {
        console.error('Failed to load backtest history:', err)
      }
    }

    if (session) {
      loadHistory()
    }
  }, [session])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  const handleRunBacktest = useCallback(async () => {
    // Abort previous request if still running
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    setIsRunning(true)
    setError(null)
    setResults(null)

    // Create new abort controller for cleanup
    const abortController = new AbortController()
    abortControllerRef.current = abortController

    const pollTimeouts: NodeJS.Timeout[] = []

    try {
      const response = await fetch('/api/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(backtestConfig),
        signal: abortController.signal,
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Backtest failed')
      }

      const backtest = await response.json()
      
      // Optimized polling with AbortController and cleanup
      const maxAttempts = 30
      let attempts = 0

      const poll = async () => {
        // Check if aborted
        if (abortController.signal.aborted) {
          return
        }

        try {
          const res = await fetch(`/api/backtest/${backtest.backtest_id}`, {
            signal: abortController.signal,
          })
          
          if (abortController.signal.aborted) {
            return
          }

          if (res.ok) {
            const data = await res.json()
            if (data.status === 'completed') {
              setResults(data.results)
              setIsRunning(false)
              // Clear all timeouts
              pollTimeouts.forEach(clearTimeout)
              return
            } else if (data.status === 'failed') {
              throw new Error(data.error || 'Backtest failed')
            }
          }

          attempts++
          if (attempts < maxAttempts && !abortController.signal.aborted) {
            const timeout = setTimeout(poll, 2000)
            pollTimeouts.push(timeout)
          } else {
            throw new Error('Backtest timed out')
          }
        } catch (err) {
          // Don't set error if request was aborted
          if (err instanceof Error && err.name === 'AbortError') {
            return
          }
          setIsRunning(false)
          setError(err instanceof Error ? err.message : 'Failed to get results')
          // Clear all timeouts on error
          pollTimeouts.forEach(clearTimeout)
        }
      }

      poll()
    } catch (err) {
      // Don't set error if request was aborted
      if (err instanceof Error && err.name === 'AbortError') {
        return
      }
      setIsRunning(false)
      setError(err instanceof Error ? err.message : 'Backtest failed')
    }

    // Store cleanup function in ref for unmount
    return () => {
      pollTimeouts.forEach(clearTimeout)
      abortController.abort()
    }
  }, [backtestConfig])

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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Configuration Panel */}
          <div className="lg:col-span-1">
            <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6 sticky top-24">
              <h2 className="text-lg font-bold text-alpine-text-primary mb-4">Configuration</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-alpine-text-secondary mb-2">Symbol</label>
                  <input
                    type="text"
                    value={backtestConfig.symbol}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, symbol: e.target.value.toUpperCase() })}
                    className="w-full px-3 py-2 bg-alpine-black-primary border border-alpine-black-border rounded-lg text-alpine-text-primary focus:outline-none focus:border-alpine-neon-cyan"
                    placeholder="AAPL"
                  />
                </div>

                <div>
                  <label className="block text-sm text-alpine-text-secondary mb-2">Start Date</label>
                  <input
                    type="date"
                    value={backtestConfig.startDate}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, startDate: e.target.value })}
                    className="w-full px-3 py-2 bg-alpine-black-primary border border-alpine-black-border rounded-lg text-alpine-text-primary focus:outline-none focus:border-alpine-neon-cyan"
                  />
                </div>

                <div>
                  <label className="block text-sm text-alpine-text-secondary mb-2">End Date</label>
                  <input
                    type="date"
                    value={backtestConfig.endDate}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, endDate: e.target.value })}
                    className="w-full px-3 py-2 bg-alpine-black-primary border border-alpine-black-border rounded-lg text-alpine-text-primary focus:outline-none focus:border-alpine-neon-cyan"
                  />
                </div>

                <div>
                  <label className="block text-sm text-alpine-text-secondary mb-2">Initial Capital</label>
                  <input
                    type="number"
                    value={backtestConfig.initialCapital}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, initialCapital: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 bg-alpine-black-primary border border-alpine-black-border rounded-lg text-alpine-text-primary focus:outline-none focus:border-alpine-neon-cyan"
                    min="1000"
                    step="1000"
                  />
                </div>

                <div>
                  <label className="block text-sm text-alpine-text-secondary mb-2">Risk Per Trade</label>
                  <input
                    type="number"
                    value={backtestConfig.riskPerTrade}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, riskPerTrade: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 bg-alpine-black-primary border border-alpine-black-border rounded-lg text-alpine-text-primary focus:outline-none focus:border-alpine-neon-cyan"
                    min="0.01"
                    max="0.1"
                    step="0.01"
                  />
                  <p className="text-sm text-alpine-text-secondary mt-1">
                    {(backtestConfig.riskPerTrade * 100).toFixed(0)}% of capital per trade
                  </p>
                </div>

                <button
                  onClick={handleRunBacktest}
                  disabled={isRunning}
                  className="w-full bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pink hover:from-alpine-neon-pink hover:to-alpine-neon-cyan text-white font-boldpy-3 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isRunning ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Running...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      Run Backtest
                    </>
                  )}
                </button>

                {error && (
                  <div className="p-3 bg-alpine-semantic-error/10 border border-alpine-semantic-error/30 rounded-lg text-sm text-alpine-semantic-error flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    {error}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2 space-y-6">
            {results ? (
              <>
                {/* Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <MetricCard
                    title="Win Rate"
                    value={`${results.win_rate?.toFixed(1)}%`}
                    icon={<TrendingUp className="w-5 h-5" />}
                    color="alpine-neoncya-n"
                  />
                  <MetricCard
                    title="Total Return"
                    value={`${results.total_return?.toFixed(1)}%`}
                    icon={<DollarSign className="w-5 h-5" />}
                    color="alpine-neonpin-k"
                  />
                  <MetricCard
                    title="Sharpe Ratio"
                    value={results.sharpe_ratio?.toFixed(2)}
                    icon={<BarChart3 className="w-5 h-5" />}
                    color="alpine-neon-purple"
                  />
                  <MetricCard
                    title="Max Drawdown"
                    value={`${results.max_drawdown?.toFixed(1)}%`}
                    icon={<Target className="w-5 h-5" />}
                    color="alpine-semantic-error
                  />
                </div>

                {/* Equity Curve */}
                {results.equity_curve && results.equity_curve.length > 0 && (
                  <PerformanceChart data={results.equity_curve} type="equity" />
                )}

                {/* Detailed Stats */}
                <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6">
                  <h3 className="text-lg font-bold text-alpine-text-primary mb-4">Detailed Statistics</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <StatItem label="Total Trades" value={results.total_trades} />
                    <StatItem label="Winning Trades" value={results.winning_trades} />
                    <StatItem label="Losing Trades" value={results.losing_trades} />
                    <StatItem label="Avg Win" value={`${results.avg_win?.toFixed(2)}%`} />
                    <StatItem label="Avg Loss" value={`${results.avg_loss?.toFixed(2)}%`} />
                    <StatItem label="Profit Factor" value={results.profit_factor?.toFixed(2)} />
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-12 text-center">
                <BarChart3 className="w-16 h-16 text-alpine-text-secondarymx-automb-4" />
                <h3 className="text-lg font-bold text-alpine-text-primary mb-2">No Backtest Results</h3>
                <p className="text-alpine-text-secondary">
                  Configure your backtest parameters and click "Run Backtest" to get started
                </p>
              </div>
            )}

            {/* History */}
            {backtestHistory.length > 0 && (
              <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6">
                <h3 className="text-lg font-bold text-alpine-text-primary mb-4">Recent Backtests</h3>
                <div className="space-y-2">
                  {backtestHistory.slice(0, 5).map((backtest: any) => (
                    <div
                      key={backtest.id}
                      className="p-3 bg-alpine-black-primary rounded-lgflex items-center justify-between hover:bg-alpine-black-primary/80 transition-colors cursor-pointer"
                      onClick={() => {
                        setResults(backtest.results)
                        setBacktestConfig({
                          symbol: backtest.symbol,
                          startDate: backtest.start_date,
                          endDate: backtest.end_date,
                          initialCapital: backtest.initial_capital,
                          strategy: backtest.strategy,
                          riskPerTrade: backtest.risk_per_trade,
                        })
                      }}
                    >
                      <div>
                        <div className="font-semibold text-alpine-text-primary ">{backtest.symbol}</div>
                        <div className="text-sm text-alpine-text-secondary">
                          {new Date(backtest.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-semibold text-alpine-text-primary ">
                          {backtest.results?.total_return?.toFixed(1)}%
                        </div>
                        <div className="text-sm text-alpine-text-secondary">
                          {backtest.results?.win_rate?.toFixed(1)}% WR
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

function MetricCard({ title, value, icon, color }: any) {
  return (
    <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <div className={`p-2 rounded-lg bg-${color}/10 text-${color}`}>
          {icon}
        </div>
      </div>
      <div className="text-2xl font-black text-alpine-text-primary mb-1">{value}</div>
      <div className="text-sm text-alpine-text-secondary">{title}</div>
    </div>
  )
}

function StatItem({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <div className="text-sm text-alpine-text-secondary mb-1">{label}</div>
      <div className="text-sm font-semibold text-alpine-text-primary ">{value}</div>
    </div>
  )
}

