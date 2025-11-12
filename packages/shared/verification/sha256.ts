/**
 * SHA-256 verification utilities for trading signals
 * Ensures signal integrity and authenticity
 */

import type { Signal } from '../types/signal'

/**
 * Generate SHA-256 hash of signal data
 * @param signal - Signal object to hash
 * @returns Promise resolving to hex-encoded SHA-256 hash
 */
export async function generateSignalHash(signal: Omit<Signal, 'hash'>): Promise<string> {
  // Create a deterministic string representation of the signal
  const signalData = JSON.stringify({
    id: signal.id,
    symbol: signal.symbol,
    action: signal.action,
    entry_price: signal.entry_price,
    stop_loss: signal.stop_loss,
    take_profit: signal.take_profit,
    confidence: signal.confidence,
    timestamp: signal.timestamp,
  })

  // Generate SHA-256 hash
  const encoder = new TextEncoder()
  const data = encoder.encode(signalData)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  
  // Convert to hex string
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

/**
 * Verify signal hash
 * @param signal - Signal object with hash to verify
 * @returns Promise resolving to verification result
 */
export async function verifySignalHash(signal: Signal): Promise<boolean> {
  try {
    const { hash, ...signalWithoutHash } = signal
    const computedHash = await generateSignalHash(signalWithoutHash)
    return computedHash === hash
  } catch (error) {
    console.error('Error verifying signal hash:', error)
    return false
  }
}

/**
 * Verify multiple signals
 * @param signals - Array of signals to verify
 * @returns Promise resolving to array of verification results
 */
export async function verifySignals(signals: Signal[]): Promise<boolean[]> {
  return Promise.all(signals.map(signal => verifySignalHash(signal)))
}

