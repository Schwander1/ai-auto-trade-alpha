// Mock stripe.ts before importing stripe-helpers
jest.mock('@/lib/stripe', () => ({
  TIER_PRICING: {
    STARTER: { name: 'Starter', price: 49 },
    PROFESSIONAL: { name: 'Professional', price: 99 },
    INSTITUTIONAL: { name: 'Institutional', price: 249 },
  },
  STRIPE_PRICE_IDS: {
    STARTER: 'price_starter',
    PROFESSIONAL: 'price_pro',
    INSTITUTIONAL: 'price_elite',
  },
  stripe: {},
  getStripe: jest.fn(),
}))

import {
  isSubscriptionActive,
  isOnTrial,
  getDaysUntilRenewal,
  getTrialDaysRemaining,
  canAccessPremiumSignals,
  requireActiveSubscription,
  getSubscriptionStatusText,
  getSubscriptionStatusColor,
  canUpgrade,
  getTierDisplayName,
  getTierPrice,
} from '@/lib/stripe-helpers'
import type { User } from '@prisma/client'

describe('Stripe Helpers', () => {
  describe('isSubscriptionActive', () => {
    it('returns false when subscriptionStatus is null', () => {
      const user = { subscriptionStatus: null } as User
      expect(isSubscriptionActive(user)).toBe(false)
    })

    it('returns true for active status', () => {
      const user = {
        subscriptionStatus: 'active',
        subscriptionEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      } as User
      expect(isSubscriptionActive(user)).toBe(true)
    })

    it('returns true for trialing status', () => {
      const user = {
        subscriptionStatus: 'trialing',
        subscriptionEnd: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      } as User
      expect(isSubscriptionActive(user)).toBe(true)
    })

    it('returns false when subscription has expired', () => {
      const user = {
        subscriptionStatus: 'active',
        subscriptionEnd: new Date(Date.now() - 1000),
      } as User
      expect(isSubscriptionActive(user)).toBe(false)
    })

    it('returns false for canceled status', () => {
      const user = { subscriptionStatus: 'canceled' } as User
      expect(isSubscriptionActive(user)).toBe(false)
    })
  })

  describe('isOnTrial', () => {
    it('returns true for trialing status', () => {
      const user = { subscriptionStatus: 'trialing' } as User
      expect(isOnTrial(user)).toBe(true)
    })

    it('returns false for active status', () => {
      const user = { subscriptionStatus: 'active' } as User
      expect(isOnTrial(user)).toBe(false)
    })
  })

  describe('getDaysUntilRenewal', () => {
    it('returns null when subscriptionEnd is null', () => {
      const user = { subscriptionEnd: null } as User
      expect(getDaysUntilRenewal(user)).toBeNull()
    })

    it('returns correct days until renewal', () => {
      const futureDate = new Date(Date.now() + 10 * 24 * 60 * 60 * 1000)
      const user = { subscriptionEnd: futureDate } as User
      const days = getDaysUntilRenewal(user)
      expect(days).toBeGreaterThanOrEqual(9)
      expect(days).toBeLessThanOrEqual(10)
    })

    it('returns 0 when subscription has expired', () => {
      const pastDate = new Date(Date.now() - 1000)
      const user = { subscriptionEnd: pastDate } as User
      expect(getDaysUntilRenewal(user)).toBe(0)
    })
  })

  describe('getTrialDaysRemaining', () => {
    it('returns null when not on trial', () => {
      const user = { subscriptionStatus: 'active' } as User
      expect(getTrialDaysRemaining(user)).toBeNull()
    })

    it('returns days when on trial', () => {
      const futureDate = new Date(Date.now() + 5 * 24 * 60 * 60 * 1000)
      const user = {
        subscriptionStatus: 'trialing',
        subscriptionEnd: futureDate,
      } as User
      const days = getTrialDaysRemaining(user)
      expect(days).toBeGreaterThanOrEqual(4)
      expect(days).toBeLessThanOrEqual(5)
    })
  })

  describe('canAccessPremiumSignals', () => {
    it('returns false when subscription is not active', () => {
      const user = {
        subscriptionStatus: 'canceled',
        tier: 'PROFESSIONAL',
      } as User
      expect(canAccessPremiumSignals(user)).toBe(false)
    })

    it('returns true for PROFESSIONAL tier with active subscription', () => {
      const user = {
        subscriptionStatus: 'active',
        tier: 'PROFESSIONAL',
        subscriptionEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      } as User
      expect(canAccessPremiumSignals(user)).toBe(true)
    })

    it('returns true for INSTITUTIONAL tier with active subscription', () => {
      const user = {
        subscriptionStatus: 'active',
        tier: 'INSTITUTIONAL',
        subscriptionEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      } as User
      expect(canAccessPremiumSignals(user)).toBe(true)
    })

    it('returns false for STARTER tier', () => {
      const user = {
        subscriptionStatus: 'active',
        tier: 'STARTER',
        subscriptionEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      } as User
      expect(canAccessPremiumSignals(user)).toBe(false)
    })
  })

  describe('requireActiveSubscription', () => {
    it('does not throw when subscription is active', () => {
      const user = {
        subscriptionStatus: 'active',
        subscriptionEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      } as User
      expect(() => requireActiveSubscription(user)).not.toThrow()
    })

    it('throws error when subscription is not active', () => {
      const user = { subscriptionStatus: 'canceled' } as User
      expect(() => requireActiveSubscription(user)).toThrow('Active subscription required')
    })
  })

  describe('getSubscriptionStatusText', () => {
    it('returns "No subscription" when status is null', () => {
      const user = { subscriptionStatus: null } as User
      expect(getSubscriptionStatusText(user)).toBe('No subscription')
    })

    it('returns correct text for active status', () => {
      const user = { subscriptionStatus: 'active' } as User
      expect(getSubscriptionStatusText(user)).toBe('Active')
    })

    it('returns correct text for trialing status', () => {
      const user = { subscriptionStatus: 'trialing' } as User
      expect(getSubscriptionStatusText(user)).toBe('Trial')
    })

    it('returns status as-is for unknown status', () => {
      const user = { subscriptionStatus: 'unknown_status' as any } as User
      expect(getSubscriptionStatusText(user)).toBe('unknown_status')
    })
  })

  describe('getSubscriptionStatusColor', () => {
    it('returns dim color when status is null', () => {
      const user = { subscriptionStatus: null } as User
      expect(getSubscriptionStatusColor(user)).toBe('text-alpine-text-dim')
    })

    it('returns accent color for active status', () => {
      const user = { subscriptionStatus: 'active' } as User
      expect(getSubscriptionStatusColor(user)).toBe('text-alpine-accent')
    })

    it('returns red color for past_due status', () => {
      const user = { subscriptionStatus: 'past_due' } as User
      expect(getSubscriptionStatusColor(user)).toBe('text-alpine-red')
    })
  })

  describe('canUpgrade', () => {
    it('returns true when upgrading from STARTER to PROFESSIONAL', () => {
      const user = { tier: 'STARTER' } as User
      expect(canUpgrade(user, 'PROFESSIONAL')).toBe(true)
    })

    it('returns true when upgrading from STARTER to INSTITUTIONAL', () => {
      const user = { tier: 'STARTER' } as User
      expect(canUpgrade(user, 'INSTITUTIONAL')).toBe(true)
    })

    it('returns true when upgrading from PROFESSIONAL to INSTITUTIONAL', () => {
      const user = { tier: 'PROFESSIONAL' } as User
      expect(canUpgrade(user, 'INSTITUTIONAL')).toBe(true)
    })

    it('returns false when already at target tier', () => {
      const user = { tier: 'PROFESSIONAL' } as User
      expect(canUpgrade(user, 'PROFESSIONAL')).toBe(false)
    })

    it('returns false when downgrading', () => {
      const user = { tier: 'PROFESSIONAL' } as User
      expect(canUpgrade(user, 'STARTER' as any)).toBe(false)
    })
  })

  describe('getTierDisplayName', () => {
    it('returns display name for known tier', () => {
      const name = getTierDisplayName('STARTER')
      expect(name).toBe('Starter')
    })

    it('returns display name for PROFESSIONAL tier', () => {
      const name = getTierDisplayName('PROFESSIONAL')
      expect(name).toBe('Professional')
    })

    it('returns tier as-is for unknown tier', () => {
      const name = getTierDisplayName('UNKNOWN_TIER')
      expect(name).toBe('UNKNOWN_TIER')
    })
  })

  describe('getTierPrice', () => {
    it('returns price for STARTER tier', () => {
      const price = getTierPrice('STARTER')
      expect(price).toBe(49)
    })

    it('returns price for PROFESSIONAL tier', () => {
      const price = getTierPrice('PROFESSIONAL')
      expect(price).toBe(99)
    })

    it('returns 0 for unknown tier', () => {
      const price = getTierPrice('UNKNOWN_TIER')
      expect(price).toBe(0)
    })
  })
})

