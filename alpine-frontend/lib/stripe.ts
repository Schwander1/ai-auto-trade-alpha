/**
 * Stripe client initialization
 * Server-side and client-side utilities
 */

import Stripe from 'stripe'
import { loadStripe, Stripe as StripeJS } from '@stripe/stripe-js'

// Server-side Stripe client
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
apiVersion: '2023-10-16',
  typescript: true,
})

// Client-side Stripe.js (returns null if key is missing)
let stripePromise: Promise<StripeJS | null> | null = null

export const getStripe = (): Promise<StripeJS | null> => {
  if (!stripePromise) {
    const publishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
    if (!publishableKey) {
      console.warn('NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY is not set')
      return Promise.resolve(null)
    }
    stripePromise = loadStripe(publishableKey)
  }
  return stripePromise
}

/**
 * Price ID mapping for subscription tiers
 */
export const STRIPE_PRICE_IDS = {
  STARTER: process.env.STRIPE_PRICE_ID_STARTER!,
  PROFESSIONAL: process.env.STRIPE_PRICE_ID_PROFESSIONAL!,
  INSTITUTIONAL: process.env.STRIPE_PRICE_ID_INSTITUTIONAL!,
} as const

/**
 * Tier pricing information
 */
export const TIER_PRICING = {
  STARTER: {
    name: 'Starter',
    price: 485,
    priceId: STRIPE_PRICE_IDS.STARTER,
    trialDays: 7,
  },
  PROFESSIONAL: {
    name: 'Professional',
    price: 985,
    priceId: STRIPE_PRICE_IDS.PROFESSIONAL,
    trialDays: 7,
  },
  INSTITUTIONAL: {
    name: 'Institutional',
    price: 3985,
    priceId: STRIPE_PRICE_IDS.INSTITUTIONAL,
    trialDays: 7,
  },
} as const

/**
 * Validate that all required Stripe environment variables are set
 */
export function validateStripeConfig(): void {
  const required = [
    'STRIPE_SECRET_KEY',
    'NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY',
    'STRIPE_PRICE_ID_STARTER',
    'STRIPE_PRICE_ID_PROFESSIONAL',
    'STRIPE_PRICE_ID_INSTITUTIONAL',
  ]

  const missing = required.filter((key) => !process.env[key])

  if (missing.length > 0) {
    throw new Error(
      `Missing required Stripe environment variables: ${missing.join(', ')}`
    )
  }
}

