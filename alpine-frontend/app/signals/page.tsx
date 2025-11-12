'use client'

import { useSignals } from '@/hooks/useSignals'
import SignalCard from '@/components/signal-card'
import { RefreshCw, AlertCircle, Loader2 } from 'lucide-react'

/**
 * Signals page displaying all trading signals.
 * Protected route - requires authentication.
 */
export default function SignalsPage() {
  const { signals, isLoading, error, refresh, isPolling } = useSignals({
    limit: 50,
    premiumOnly: false,
    pollInterval: 30000, // 30 seconds
    autoPoll: true,
    cache: true,
  })

  return (
    <div className="min-h-screen bg-alpine-bg">
      {/* Header */}
      <div className="border-b border-alpine-border bg-alpine-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-display font-black text-alpine-text mb-2">
                All Trading Signals
              </h1>
              <p className="text-alpine-text-dim">
                Complete signal history from Argo Trading Engine
                {isPolling && (
                  <span className="ml-2 inline-flex items-center gap-1 text-xs">
                    <span className="w-2 h-2 bg-alpine-accent rounded-full animate-pulse" />
                    Live
                  </span>
                )}
              </p>
            </div>
            <button
              onClick={refresh}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-alpine-card border border-alpine-border rounded-lg hover:bg-alpine-border/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Refresh signals"
            >
              <RefreshCw
                className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`}
                aria-hidden="true"
              />
              <span className="text-sm font-semibold text-alpine-text">Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Loading State */}
        {isLoading && signals.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-12 h-12 text-alpine-accent animate-spin mb-4" aria-hidden="true" />
            <p className="text-alpine-text-dim text-lg">Loading signals...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="mb-6 p-4 bg-alpine-red/10 border border-alpine-red/30 rounded-xl">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-alpine-red flex-shrink-0 mt-0.5" aria-hidden="true" />
              <div className="flex-1">
                <h3 className="text-alpine-red font-semibold mb-1">Error Loading Signals</h3>
                <p className="text-alpine-text-dim text-sm mb-3">{error.message}</p>
                <button
                  onClick={refresh}
                  className="px-4 py-2 bg-alpine-red/20 hover:bg-alpine-red/30 text-alpine-red rounded-lg text-sm font-semibold transition-colors"
                >
                  Retry
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && signals.length === 0 && (
          <div className="text-center py-20">
            <p className="text-alpine-text-dim text-lg mb-4">No signals available</p>
            <button
              onClick={refresh}
              className="px-6 py-3 bg-gradient-to-r from-alpine-accent to-alpine-pink hover:from-alpine-pink hover:to-alpine-accent text-white font-black rounded-lg transition-all duration-300"
            >
              Refresh
            </button>
          </div>
        )}

        {/* Signals Grid */}
        {signals.length > 0 && (
          <>
            <div className="mb-6 flex items-center justify-between">
              <p className="text-alpine-text-dim">
                Showing <span className="font-semibold text-alpine-text">{signals.length}</span> signal{signals.length !== 1 ? 's' : ''}
              </p>
              {isLoading && signals.length > 0 && (
                <div className="flex items-center gap-2 text-sm text-alpine-text-dim">
                  <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                  <span>Updating...</span>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {signals.map((signal) => (
                <SignalCard
                  key={signal.id}
                  signal={signal}
                  showVerifyButton={true}
                  showDetails={true}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

