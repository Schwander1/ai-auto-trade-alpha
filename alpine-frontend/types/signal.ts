/**
 * Type definitions for trading signals from external signal provider.
 */

export type SignalAction = 'BUY' | 'SELL'
export type SignalType = 'PREMIUM' | 'STANDARD'
export type SignalStatus = 'pending' | 'active' | 'closed' | 'expired'
export type SignalOutcome = 'win' | 'loss' | 'expired' | null
export type MarketRegime = 'Bull' | 'Bear' | 'Chop' | 'Crisis'

/**
 * Core trading signal interface matching Argo backend structure.
 */
export interface Signal {
  /** Unique signal identifier */
  id: string
  /** Trading symbol (e.g., 'AAPL', 'BTC/USD') */
  symbol: string
  /** Trading action: BUY or SELL */
  action: SignalAction
  /** Entry price for the signal */
  entry_price: number
  /** Stop loss price (null if not set) */
  stop_loss: number | null
  /** Take profit price (null if not set) */
  take_profit: number | null
  /** Confidence score (87-98% range) */
  confidence: number
  /** Signal type: PREMIUM (95%+) or STANDARD (87-94%) */
  type: SignalType
  /** ISO 8601 timestamp when signal was generated */
  timestamp: string
  /** SHA-256 cryptographic hash for verification */
  hash: string
  /** Market regime when signal was generated */
  regime?: MarketRegime
  /** Regime strength (0-100) */
  regime_strength?: number
  /** Signal status */
  status?: SignalStatus
  /** Trade outcome (null if pending) */
  outcome?: SignalOutcome
  /** Exit price (if closed) */
  exit_price?: number | null
  /** Profit/loss percentage (if closed) */
  pnl_pct?: number | null
  /** Exit timestamp (if closed) */
  exit_timestamp?: string | null
  /** Reasoning/explanation for the signal */
  reasoning?: string
}

/**
 * Signal verification result.
 */
export interface SignalVerification {
  /** Whether the signal hash is valid */
  isValid: boolean
  /** Verification timestamp */
  verifiedAt: string
  /** Error message if verification failed */
  error?: string
}

