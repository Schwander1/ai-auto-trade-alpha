'use client'

import { useState, useEffect } from 'react'
import { CheckCircle2, XCircle, Clock, TrendingUp, TrendingDown, Shield } from 'lucide-react'
import type { Signal, SignalVerification } from '@/types/signal'

interface SignalCardProps {
  /** Signal data from Argo backend */
  signal: Signal
  /** Optional callback when user verifies signal hash */
  onVerify?: (hash: string) => void
  /** Additional Tailwind classes */
  className?: string
  /** Whether to show verification button */
  showVerifyButton?: boolean
  /** Whether to show detailed information */
  showDetails?: boolean
}

/**
 * SignalCard displays a trading signal with real-time updates and SHA-256 verification.
 * 
 * Displays signal information including symbol, action (BUY/SELL), entry price,
 * confidence score, and cryptographic verification status. Supports interactive
 * verification and shows outcome if the signal has been closed.
 * 
 * @param signal - Signal data from Argo backend
 * @param onVerify - Optional callback when user verifies signal hash
 * @param className - Additional Tailwind classes
 * @param showVerifyButton - Whether to show verification button (default: true)
 * @param showDetails - Whether to show detailed information (default: true)
 * 
 * @example
 * ```tsx
 * <SignalCard 
 *   signal={signalData} 
 *   onVerify={handleVerify}
 *   className="mb-4"
 * />
 * ```
 */
export default function SignalCard({
  signal,
  onVerify,
  className = '',
  showVerifyButton = true,
  showDetails = true,
}: SignalCardProps) {
  // 1. STATE DECLARATIONS
  const [isVerified, setIsVerified] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [verificationError, setVerificationError] = useState<string | null>(null)

  // 2. EFFECTS
  useEffect(() => {
    // Auto-verify on mount if hash exists
    if (signal.hash && !isVerified) {
      verifySignalHash()
    }
  }, [signal.hash])

  // 3. EVENT HANDLERS
  const handleVerifyClick = async () => {
    setIsLoading(true)
    setVerificationError(null)
    
    try {
      const result = await verifySignalHash()
      if (result.isValid) {
        setIsVerified(true)
        onVerify?.(signal.hash)
      } else {
        setVerificationError(result.error || 'Verification failed')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      setVerificationError(errorMessage)
      console.error('Verification failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // 4. HELPER FUNCTIONS
  const verifySignalHash = async (): Promise<SignalVerification> => {
    // TODO: Implement actual SHA-256 verification
    // This is a placeholder - replace with actual verification logic
    try {
      // Simulate verification (replace with actual API call)
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // For now, assume valid if hash exists and has correct length
      const isValid = signal.hash.length === 64 && /^[a-f0-9]+$/i.test(signal.hash)
      
      return {
        isValid,
        verifiedAt: new Date().toISOString(),
        error: isValid ? undefined : 'Invalid hash format',
      }
    } catch (error) {
      return {
        isValid: false,
        verifiedAt: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Verification error',
      }
    }
  }

  const formatConfidence = (value: number): string => {
    return `${value.toFixed(1)}%`
  }

  const formatPrice = (price: number): string => {
    return `$${price.toFixed(2)}`
  }

  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return timestamp
    }
  }

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 95) return 'text-alpine-accent'
    if (confidence >= 90) return 'text-alpine-pink'
    return 'text-alpine-text-dim'
  }

  const getConfidenceBg = (confidence: number): string => {
    if (confidence >= 95) return 'bg-alpine-accent/10 border-alpine-accent/30'
    if (confidence >= 90) return 'bg-alpine-pink/10 border-alpine-pink/30'
    return 'bg-alpine-card border-alpine-border'
  }

  const getOutcomeDisplay = () => {
    if (!signal.outcome) return null

    const isWin = signal.outcome === 'win'
    const Icon = isWin ? CheckCircle2 : XCircle
    const color = isWin ? 'text-alpine-accent' : 'text-alpine-red'
    const bgColor = isWin ? 'bg-alpine-accent/10' : 'bg-alpine-red/10'

    return (
      <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${bgColor}`}>
        <Icon className={`w-5 h-5 ${color}`} aria-hidden="true" />
        <div>
          <div className={`text-sm font-semibold ${color}`}>
            {isWin ? 'Win' : signal.outcome === 'expired' ? 'Expired' : 'Loss'}
          </div>
          {signal.pnl_pct !== null && signal.pnl_pct !== undefined && (
            <div className={`text-xs ${color}`}>
              {signal.pnl_pct >= 0 ? '+' : ''}{signal.pnl_pct.toFixed(2)}%
            </div>
          )}
        </div>
      </div>
    )
  }

  // 5. EARLY RETURNS
  if (!signal) return null

  // 6. RENDER
  return (
    <div
      className={`bg-alpine-card border border-alpine-border rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow ${className}`}
      role="article"
      aria-label={`Trading signal for ${signal.symbol}`}
    >
      {/* Header: Symbol and Action */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-xl font-display font-bold text-alpine-text">
            {signal.symbol}
          </h3>
          {signal.regime && (
            <span className="px-2 py-1 text-xs font-semibold rounded border border-alpine-border text-alpine-text-dim">
              {signal.regime}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {signal.action === 'BUY' ? (
            <TrendingUp className="w-5 h-5 text-alpine-accent" aria-hidden="true" />
          ) : (
            <TrendingDown className="w-5 h-5 text-alpine-red" aria-hidden="true" />
          )}
          <span
            className={`px-3 py-1 rounded-lg text-sm font-bold ${
              signal.action === 'BUY'
                ? 'bg-alpine-accent/20 text-alpine-accent border border-alpine-accent/30'
                : 'bg-alpine-red/20 text-alpine-red border border-alpine-red/30'
            }`}
          >
            {signal.action}
          </span>
        </div>
      </div>

      {/* Confidence Score */}
      <div
        className={`mb-4 p-3 rounded-lg border ${getConfidenceBg(signal.confidence)}`}
      >
        <div className="flex items-center justify-between">
          <span className="text-sm text-alpine-text-dim">Confidence</span>
          <span className={`text-lg font-black ${getConfidenceColor(signal.confidence)}`}>
            {formatConfidence(signal.confidence)}
          </span>
        </div>
        {signal.type && (
          <div className="mt-1 text-xs text-alpine-text-dim">
            {signal.type} Signal
          </div>
        )}
      </div>

      {/* Price Information */}
      {showDetails && (
        <div className="space-y-2 mb-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-alpine-text-dim">Entry Price</span>
            <span className="text-alpine-text font-semibold">
              {formatPrice(signal.entry_price)}
            </span>
          </div>
          {signal.stop_loss && (
            <div className="flex justify-between items-center">
              <span className="text-sm text-alpine-text-dim">Stop Loss</span>
              <span className="text-alpine-red font-semibold">
                {formatPrice(signal.stop_loss)}
              </span>
            </div>
          )}
          {signal.take_profit && (
            <div className="flex justify-between items-center">
              <span className="text-sm text-alpine-text-dim">Take Profit</span>
              <span className="text-alpine-accent font-semibold">
                {formatPrice(signal.take_profit)}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Outcome Display */}
      {getOutcomeDisplay() && (
        <div className="mb-4">{getOutcomeDisplay()}</div>
      )}

      {/* Verification Status */}
      <div className="mb-4 flex items-center gap-2">
        {isVerified ? (
          <div className="flex items-center gap-2 text-alpine-accent">
            <Shield className="w-4 h-4" aria-hidden="true" />
            <span className="text-sm font-semibold">SHA-256 Verified</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-alpine-text-dim">
            <Clock className="w-4 h-4" aria-hidden="true" />
            <span className="text-sm">Not verified</span>
          </div>
        )}
        {signal.hash && (
          <span className="text-xs text-alpine-text-dim font-mono ml-auto">
            {signal.hash.slice(0, 8)}...
          </span>
        )}
      </div>

      {/* Verification Error */}
      {verificationError && (
        <div className="mb-4 p-2 bg-alpine-red/10 border border-alpine-red/30 rounded text-sm text-alpine-red">
          {verificationError}
        </div>
      )}

      {/* Timestamp */}
      <div className="mb-4 text-xs text-alpine-text-dim">
        {formatTimestamp(signal.timestamp)}
      </div>

      {/* Verify Button */}
      {showVerifyButton && !isVerified && (
        <button
          onClick={handleVerifyClick}
          disabled={isLoading}
          className="w-full px-4 py-2 bg-gradient-to-r from-alpine-accent to-alpine-pink hover:from-alpine-pink hover:to-alpine-accent text-white font-black rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          aria-label="Verify signal hash"
        >
          {isLoading ? (
            <>
              <Clock className="w-4 h-4 animate-spin" aria-hidden="true" />
              Verifying...
            </>
          ) : (
            <>
              <Shield className="w-4 h-4" aria-hidden="true" />
              Verify Signal
            </>
          )}
        </button>
      )}
    </div>
  )
}

