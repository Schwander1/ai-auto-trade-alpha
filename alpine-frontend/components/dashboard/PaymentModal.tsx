'use client'

import { useState, useEffect } from 'react'
import { X, Loader2, CreditCard, CheckCircle2 } from 'lucide-react'
import { loadStripe } from '@stripe/stripe-js'

interface PaymentModalProps {
  isOpen: boolean
  onClose: () => void
  tier: string
  price: number
  priceId: string
}

/**
 * PaymentModal component for Stripe checkout integration
 * Handles subscription upgrades with Stripe Checkout
 */
export default function PaymentModal({ isOpen, onClose, tier, price, priceId }: PaymentModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [stripe, setStripe] = useState<any>(null)

  useEffect(() => {
    if (isOpen) {
      loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '').then(setStripe)
    }
  }, [isOpen])

  const handleCheckout = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/subscriptions/upgrade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tier }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to create checkout session')
      }

      const { checkout_url } = await response.json()

      if (checkout_url) {
        window.location.href = checkout_url
      } else {
        throw new Error('No checkout URL returned')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-alpine-card border border-alpine-border rounded-lg max-w-md w-full p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-alpine-text-dim hover:text-alpine-text transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-lg bg-alpine-accent/10 flex items-center justify-center">
              <CreditCard className="w-6 h-6 text-alpine-accent" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-alpine-text">Upgrade to {tier}</h2>
              <p className="text-alpine-text-dim">Complete your subscription</p>
            </div>
          </div>

          <div className="bg-alpine-bg rounded-lg p-4 mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-alpine-text-dim">Plan</span>
              <span className="text-alpine-text font-semibold capitalize">{tier}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-alpine-text-dim">Price</span>
              <span className="text-2xl font-black text-alpine-text">${price}/month</span>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-alpine-red/10 border border-alpine-red/30 rounded-lg text-sm text-alpine-red">
              {error}
            </div>
          )}

          <div className="space-y-3">
            <button
              onClick={handleCheckout}
              disabled={isLoading || !stripe}
              className="w-full bg-gradient-to-r from-alpine-accent to-alpine-pink hover:from-alpine-pink hover:to-alpine-accent text-white font-bold py-3 rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <CreditCard className="w-5 h-5" />
                  Proceed to Checkout
                </>
              )}
            </button>

            <button
              onClick={onClose}
              className="w-full bg-alpine-border hover:bg-alpine-border/80 text-alpine-text font-semibold py-3 rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>

          <p className="mt-4 text-xs text-alpine-text-dim text-center">
            Secure payment powered by Stripe
          </p>
        </div>
      </div>
    </div>
  )
}

