'use client'

import { useState } from 'react'
import { CheckCircle2, XCircle, Clock, TrendingUp, TrendingDown, Shield, ExternalLink } from 'lucide-react'
import type { Signal } from '@/types/signal'

interface SignalCardProps {
  signal: Signal
  className?: string
  compact?: boolean
}

/**
 * Enhanced SignalCard component for dashboard display
 * Shows entry/exit prices, P&L, and verification status
 */
export default function SignalCard({ signal, className = '', compact = false }: SignalCardProps) {
  const [isVerified, setIsVerified] = useState(false)

  const formatPrice = (price: number) => `$${price.toFixed(2)}`
  const formatPercent = (value: number) => `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  }

  const getActionColor = (action: string) => {
    return action === 'BUY' 
      ? 'bg-alpine-accent/20 text-alpine-accent border-alpine-accent/30'
      : 'bg-alpine-red/20 text-alpine-red border-alpine-red/30'
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 95) return 'text-alpine-accent'
    if (confidence >= 90) return 'text-alpine-pink'
    return 'text-alpine-text-dim'
  }

  return (
    <div className={`bg-alpine-card border border-alpine-border rounded-lg p-4 hover:border-alpine-accent/50 transition-all ${className}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-lg font-bold text-alpine-text">{signal.symbol}</h3>
            <span className={`px-2 py-0.5 text-xs font-semibold rounded border ${getActionColor(signal.action)}`}>
              {signal.action}
            </span>
          </div>
          <div className="flex items-center gap-4 text-sm text-alpine-text-dim">
            <span>{formatTime(signal.timestamp)}</span>
            {signal.regime && (
              <span className="px-2 py-0.5 bg-alpine-border rounded text-xs">
                {signal.regime}
              </span>
            )}
          </div>
        </div>
        <div className={`text-right ${getConfidenceColor(signal.confidence)}`}>
          <div className="text-2xl font-black">{signal.confidence.toFixed(1)}%</div>
          <div className="text-xs text-alpine-text-dim">{signal.type}</div>
        </div>
      </div>

      {!compact && (
        <>
          <div className="grid grid-cols-2 gap-3 mb-3 pt-3 border-t border-alpine-border">
            <div>
              <div className="text-xs text-alpine-text-dim mb-1">Entry</div>
              <div className="text-sm font-semibold text-alpine-text">{formatPrice(signal.entry_price)}</div>
            </div>
            {signal.stop_loss && (
              <div>
                <div className="text-xs text-alpine-text-dim mb-1">Stop Loss</div>
                <div className="text-sm font-semibold text-alpine-red">{formatPrice(signal.stop_loss)}</div>
              </div>
            )}
            {signal.take_profit && (
              <div>
                <div className="text-xs text-alpine-text-dim mb-1">Take Profit</div>
                <div className="text-sm font-semibold text-alpine-accent">{formatPrice(signal.take_profit)}</div>
              </div>
            )}
            {signal.exit_price !== null && signal.exit_price !== undefined && (
              <div>
                <div className="text-xs text-alpine-text-dim mb-1">Exit</div>
                <div className="text-sm font-semibold text-alpine-text">{formatPrice(signal.exit_price)}</div>
              </div>
            )}
          </div>

          {signal.outcome && (
            <div className={`flex items-center gap-2 p-2 rounded ${
              signal.outcome === 'win' 
                ? 'bg-alpine-accent/10 text-alpine-accent' 
                : 'bg-alpine-red/10 text-alpine-red'
            }`}>
              {signal.outcome === 'win' ? (
                <CheckCircle2 className="w-4 h-4" />
              ) : (
                <XCircle className="w-4 h-4" />
              )}
              <span className="text-sm font-semibold capitalize">{signal.outcome}</span>
              {signal.pnl_pct !== null && signal.pnl_pct !== undefined && (
                <span className="ml-auto text-sm font-bold">
                  {formatPercent(signal.pnl_pct)}
                </span>
              )}
            </div>
          )}

          <div className="flex items-center justify-between mt-3 pt-3 border-t border-alpine-border">
            <div className="flex items-center gap-2 text-xs text-alpine-text-dim">
              {isVerified ? (
                <>
                  <Shield className="w-3 h-3 text-alpine-accent" />
                  <span>Verified</span>
                </>
              ) : (
                <>
                  <Clock className="w-3 h-3" />
                  <span>Pending</span>
                </>
              )}
            </div>
            {signal.hash && (
              <span className="text-xs font-mono text-alpine-text-dim">
                {signal.hash.slice(0, 8)}...
              </span>
            )}
          </div>
        </>
      )}
    </div>
  )
}

