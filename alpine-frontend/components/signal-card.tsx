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
    try {
      // Check if hash exists and has correct format
      if (!signal.hash || signal.hash.length !== 64 || !/^[a-f0-9]+$/i.test(signal.hash)) {
        return {
          isValid: false,
          verifiedAt: new Date().toISOString(),
          error: 'Invalid hash format',
        }
      }

      // Build hash fields object (must match backend format exactly)
      const hashFields = {
        signal_id: signal.signal_id || signal.id,
        symbol: signal.symbol,
        action: signal.action,
        entry_price: signal.entry_price,
        target_price: signal.target_price || signal.take_profit || null,
        stop_price: signal.stop_price || signal.stop_loss || null,
        confidence: signal.confidence,
        strategy: signal.strategy || null,
        timestamp: signal.timestamp,
      }

      // Convert to JSON string with sorted keys (must match backend)
      const sortedKeys = Object.keys(hashFields).sort()
      const sortedFields: Record<string, any> = {}
      sortedKeys.forEach(key => {
        sortedFields[key] = hashFields[key as keyof typeof hashFields]
      })
      const hashString = JSON.stringify(sortedFields)

      // Calculate SHA-256 hash using Web Crypto API
      const encoder = new TextEncoder()
      const data = encoder.encode(hashString)
      const hashBuffer = await crypto.subtle.digest('SHA-256', data)
      
      // Convert to hex string
      const hashArray = Array.from(new Uint8Array(hashBuffer))
      const calculatedHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')

      // Compare with stored hash
      const isValid = calculatedHash.toLowerCase() === signal.hash.toLowerCase()

      return {
        isValid,
        verifiedAt: new Date().toISOString(),
        error: isValid ? undefined : 'Hash verification failed - signal data may have been tampered with',
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
    if (confidence >= 95) return 'text-alpine-neon-cyan'
    if (confidence >= 90) return 'text-alpine-neon-pink'
    return 'text-alpine-text-secondary'
  }

  const getConfidenceBg = (confidence: number): string => {
    if (confidence >= 95) return 'bg-alpine-neon-cyan/10 border-alpine-neon-cyan/30'
    if (confidence >= 90) return 'bg-alpine-neonpin-k/10 border-alpine-neonpin-k/30'
    return 'bg-alpine-black-secondary border-alpine-black-border
  }

  const getOutcomeDisplay = () => {
    if (!signal.outcome) return null

    const isWin = signal.outcome === 'win'
    const Icon = isWin ? CheckCircle2 : XCircle
    const color = isWin ? 'text-alpine-neon-cyan' : 'text-alpine-semantic-error
    const bgColor = isWin ? 'bg-alpine-neon-cyan/10' : 'bg-alpine-semantic-error10'

    return (
      <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${bgColor}`}>
        <Icon className={`w-5 h-5 ${color}`} aria-hidden="true" />
        <div>
          <div className={`text-sm font-semibold ${color}`}>
            {isWin ? 'Win' : signal.outcome === 'expired' ? 'Expired' : 'Loss'}
          </div>
          {signal.pnl_pct !== null && signal.pnl_pct !== undefined && (
            <div className={`text-sm ${color}`}>
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
      className={`bg-alpine-black-secondary border border-alpine-black-border rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow ${className}`}
      role="article"
      aria-label={`Trading signal for ${signal.symbol}`}
    >
      {/* Header: Symbol and Action */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-xl font-display font-bold text-alpine-text-primary ">
            {signal.symbol}
          </h3>
          {signal.regime && (
            <span className="px-2 py-1 text-sm font-semibold rounded border border-alpine-black-border text-alpine-text-secondary">
              {signal.regime}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {signal.action === 'BUY' ? (
            <TrendingUp className="w-5 h-5 text-alpine-neon-cyan" aria-hidden="true" />
          ) : (
            <TrendingDown className="w-5 h-5 text-alpine-semantic-errorariahidd-en="true" />
          )}
          <span
            className={`px-3 py-1 rounded-lg text-sm font-bold ${
              signal.action === 'BUY'
                ? 'bg-alpine-neon-cyan/20 text-alpine-neon-cyan border-border-alpine-neon-cyan/30'
                : 'bg-alpine-semantic-error20 text-alpine-semantic-errorborder border-alpine-semantic-error30'
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
          <span className="text-sm text-alpine-text-secondary">Confidence</span>
          <span className={`text-lg font-black ${getConfidenceColor(signal.confidence)}`}>
            {formatConfidence(signal.confidence)}
          </span>
        </div>
        {signal.type && (
          <div className="mt-1 text-sm text-alpine-text-secondary">
            {signal.type} Signal
          </div>
        )}
      </div>

      {/* Price Information */}
      {showDetails && (
        <div className="space-y-2 mb-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-alpine-text-secondary">Entry Price</span>
            <span className="text-alpine-text-primary font-semibold">
              {formatPrice(signal.entry_price)}
            </span>
          </div>
          {signal.stop_loss && (
            <div className="flex justify-between items-center">
              <span className="text-sm text-alpine-text-secondary">Stop Loss</span>
              <span className="text-alpine-semantic-error font-semibold">
                {formatPrice(signal.stop_loss)}
              </span>
            </div>
          )}
          {signal.take_profit && (
            <div className="flex justify-between items-center">
              <span className="text-sm text-alpine-text-secondary">Take Profit</span>
              <span className="text-alpine-neon-cyan font-semibold">
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
          <div className="flex items-center gap-2 text-alpine-neon-cyan">
            <Shield className="w-4 h-4" aria-hidden="true" />
            <span className="text-sm font-semibold">SHA-256 Verified</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-alpine-text-secondary">
            <Clock className="w-4 h-4" aria-hidden="true" />
            <span className="text-sm">Not verified</span>
          </div>
        )}
        {signal.hash && (
          <span className="text-sm text-alpine-text-secondary font-mono-mlau-to">
            {signal.hash.slice(0, 8)}...
          </span>
        )}
      </div>

      {/* Verification Error */}
      {verificationError && (
        <div className="mb-4 p-2 bg-alpine-semantic-error10 border border-alpine-semantic-error30 rounded text-sm text-alpine-semantic-error">
          {verificationError}
        </div>
      )}

      {/* Timestamp */}
      <div className="mb-4 text-sm text-alpine-text-secondary">
        {formatTimestamp(signal.timestamp)}
      </div>

      {/* Verify Button */}
      {showVerifyButton && !isVerified && (
        <button
          onClick={handleVerifyClick}
          disabled={isLoading}
          className="w-full px-4 py-2 bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pinkhove-r:from-alpine-neon-pinkhove-r:to-alpine-neon-cyantext-white-fontblac-krounded-lg transition-allduration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
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

