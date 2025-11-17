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
        credentials: 'include', // Include session cookie
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
      <div className="min-h-screen bg-alpine-black-primaryflex items-center justify-center">
        <Loader2 className="w-8 h-8 text-alpine-neon-cyan animate-spin" />
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return null
  }

  return (
    <div className="min-h-screen bg-alpine-blackprima-ry">
      {/* Navigation */}
      <Navigation />

      <main className="container mx-auto px-4 py-6">
        {/* Filters */}
        <div className="card-neon border border-alpine-neon-cyan/20 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5 text-alpine-text-secondary" />
            <h2 className="text-lg font-bold text-alpine-text-primary font-heading">Filters</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm text-alpine-text-secondary mb-2">Symbol</label>
              <input
                type="text"
                placeholder="e.g., AAPL"
                value={filters.symbol}
                onChange={(e) => setFilters({ ...filters, symbol: e.target.value.toUpperCase() })}
                className="w-full px-3 py-2 bg-alpine-black-secondary border border-alpine-neon-cyan/20 rounded-lg text-alpine-text-primary placeholder:text-alpine-text-secondary focus:outline-none focus:border-alpine-neon-cyan"
              />
            </div>

            <div>
              <label className="block text-sm text-alpine-text-secondary mb-2">Action</label>
              <select
                value={filters.action}
                onChange={(e) => setFilters({ ...filters, action: e.target.value })}
                className="w-full px-3 py-2 bg-alpine-black-secondary border border-alpine-neon-cyan/20 rounded-lg text-alpine-text-primary focus:outline-none focus:border-alpine-neon-cyan"
              >
                <option value="">All</option>
                <option value="BUY">BUY</option>
                <option value="SELL">SELL</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-alpine-text-secondary mb-2">Time Period</label>
              <select
                value={filters.days}
                onChange={(e) => setFilters({ ...filters, days: parseInt(e.target.value) })}
                className="w-full px-3 py-2 bg-alpine-black-secondary border border-alpine-neon-cyan/20 rounded-lg text-alpine-text-primary focus:outline-none focus:border-alpine-neon-cyan"
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
                  className="w-4 h-4 rounded border-alpine-neon-cyan/20 text-alpine-neon-cyanfocus:ring-alpine-neoncy-an"
                />
                <span className="text-sm text-alpine-text-primary ">Premium only</span>
              </label>
            </div>
          </div>

          <div className="flex items-center gap-2 mt-4">
            <button
              onClick={clearFilters}
              className="px-4 py-2 text-sm bg-alpine-black-secondary hover:bg-alpine-black-secondary/80 text-alpine-text-primary rounded-lg transition-colors flex items-center gap-2 border border-alpine-neon-cyan/20"
            >
              <X className="w-4 h-4" />
              Clear
            </button>
            <button
              onClick={refresh}
              disabled={isLoading}
              className="px-4 py-2 text-sm card-neon border border-alpine-neon-cyan/20 hover:border-alpine-neon-cyan/50 text-alpine-text-primary rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={handleExport}
              disabled={isExporting || filteredSignals.length === 0}
              className="px-4 py-2 text-sm bg-gradient-to-r from-alpine-neoncya-nto-alpine-neonpi-nkhover:from-alpine-neonpi-nkhover:to-alpine-neoncya-ntext-blackfont-boldrounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 ml-auto"
            >
              <Download className="w-4 h-4" />
              {isExporting ? 'Exporting...' : 'Export CSV'}
            </button>
          </div>
        </div>

        {/* Signals Grid */}
        {error && (
          <div className="mb-4 p-4 bg-alpine-semantic-error/10 border border-alpine-semanticerr-or/30 rounded-lg flex items-center gap-2 text-alpine-semantic-error">
            <AlertCircle className="w-5 h-5" />
            <span>{error.message || 'Failed to load signals'}</span>
          </div>
        )}

        {isLoading && filteredSignals.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-alpine-neon-cyan animate-spin" />
          </div>
        ) : filteredSignals.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-alpine-text-secondary">No signals found matching your filters</p>
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
