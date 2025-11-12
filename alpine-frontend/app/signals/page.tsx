'use client'

import { useSession } from 'next-auth/react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { useSignals } from '@/hooks/useSignals'
import SignalCard from '@/components/dashboard/SignalCard'
import Navigation from '@/components/dashboard/Navigation'
import { 
  Filter, Download, RefreshCw, Search, X,
  AlertCircle, Loader2, Calendar, TrendingUp, TrendingDown
} from 'lucide-react'

/**
 * Signals Page - Signal history with filters and CSV export
 */
export default function SignalsPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const searchParams = useSearchParams()
  const [filters, setFilters] = useState({
    symbol: searchParams.get('symbol') || '',
    action: searchParams.get('action') || '',
    premiumOnly: searchParams.get('premium') === 'true',
    days: parseInt(searchParams.get('days') || '30'),
  })
  const [isExporting, setIsExporting] = useState(false)

  const { signals, isLoading, error, refresh } = useSignals({
    limit: 100,
    premiumOnly: filters.premiumOnly,
    pollInterval: 60000,
    autoPoll: true,
    cache: true,
  })

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login')
    }
  }, [status, router])

  const filteredSignals = signals.filter((signal: any) => {
    if (filters.symbol && signal.symbol !== filters.symbol) return false
    if (filters.action && signal.action !== filters.action) return false
    return true
  })

  const handleExport = async () => {
    setIsExporting(true)
    try {
      const response = await fetch(`/api/signals/export?format=csv&days=${filters.days}`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `signals_${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        throw new Error('Export failed')
      }
    } catch (err) {
      console.error('Export error:', err)
      alert('Failed to export signals. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  const clearFilters = () => {
    setFilters({
      symbol: '',
      action: '',
      premiumOnly: false,
      days: 30,
    })
    router.push('/signals')
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-alpine-bg flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-alpine-accent animate-spin" />
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return null
  }

  return (
    <div className="min-h-screen bg-alpine-bg">
      {/* Navigation */}
      <Navigation />

      <main className="container mx-auto px-4 py-6">
        {/* Filters */}
        <div className="bg-alpine-card border border-alpine-border rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5 text-alpine-text-dim" />
            <h2 className="text-lg font-bold text-alpine-text">Filters</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm text-alpine-text-dim mb-2">Symbol</label>
              <input
                type="text"
                placeholder="e.g., AAPL"
                value={filters.symbol}
                onChange={(e) => setFilters({ ...filters, symbol: e.target.value.toUpperCase() })}
                className="w-full px-3 py-2 bg-alpine-bg border border-alpine-border rounded-lg text-alpine-text placeholder-alpine-text-dim focus:outline-none focus:border-alpine-accent"
              />
            </div>

            <div>
              <label className="block text-sm text-alpine-text-dim mb-2">Action</label>
              <select
                value={filters.action}
                onChange={(e) => setFilters({ ...filters, action: e.target.value })}
                className="w-full px-3 py-2 bg-alpine-bg border border-alpine-border rounded-lg text-alpine-text focus:outline-none focus:border-alpine-accent"
              >
                <option value="">All</option>
                <option value="BUY">BUY</option>
                <option value="SELL">SELL</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-alpine-text-dim mb-2">Time Period</label>
              <select
                value={filters.days}
                onChange={(e) => setFilters({ ...filters, days: parseInt(e.target.value) })}
                className="w-full px-3 py-2 bg-alpine-bg border border-alpine-border rounded-lg text-alpine-text focus:outline-none focus:border-alpine-accent"
              >
                <option value="7">Last 7 days</option>
                <option value="30">Last 30 days</option>
                <option value="90">Last 90 days</option>
                <option value="365">Last year</option>
              </select>
            </div>

            <div className="flex items-end gap-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.premiumOnly}
                  onChange={(e) => setFilters({ ...filters, premiumOnly: e.target.checked })}
                  className="w-4 h-4 rounded border-alpine-border text-alpine-accent focus:ring-alpine-accent"
                />
                <span className="text-sm text-alpine-text">Premium only</span>
              </label>
            </div>
          </div>

          <div className="flex items-center gap-2 mt-4">
            <button
              onClick={clearFilters}
              className="px-4 py-2 text-sm bg-alpine-border hover:bg-alpine-border/80 text-alpine-text rounded-lg transition-colors flex items-center gap-2"
            >
              <X className="w-4 h-4" />
              Clear
            </button>
            <button
              onClick={refresh}
              disabled={isLoading}
              className="px-4 py-2 text-sm bg-alpine-card border border-alpine-border hover:border-alpine-accent/50 text-alpine-text rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={handleExport}
              disabled={isExporting || filteredSignals.length === 0}
              className="px-4 py-2 text-sm bg-gradient-to-r from-alpine-accent to-alpine-pink hover:from-alpine-pink hover:to-alpine-accent text-white font-bold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 ml-auto"
            >
              <Download className="w-4 h-4" />
              {isExporting ? 'Exporting...' : 'Export CSV'}
            </button>
          </div>
        </div>

        {/* Signals Grid */}
        {error && (
          <div className="mb-4 p-4 bg-alpine-red/10 border border-alpine-red/30 rounded-lg flex items-center gap-2 text-alpine-red">
            <AlertCircle className="w-5 h-5" />
            <span>{error.message || 'Failed to load signals'}</span>
          </div>
        )}

        {isLoading && filteredSignals.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-alpine-accent animate-spin" />
          </div>
        ) : filteredSignals.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-alpine-text-dim">No signals found matching your filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredSignals.map((signal: any) => (
              <SignalCard key={signal.id} signal={signal} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
