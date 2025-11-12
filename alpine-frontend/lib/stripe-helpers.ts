/**
 * Stripe subscription helper functions
 */

import type { User } from '@prisma/client'
import { TIER_PRICING } from './stripe'

/**
 * Check if user has an active subscription
 */
export function isSubscriptionActive(user: User): boolean {
  if (!user.subscriptionStatus) {
    return false
  }

  const activeStatuses = ['active', 'trialing']
  if (!activeStatuses.includes(user.subscriptionStatus)) {
    return false
  }

  // Also check subscription end date
  if (user.subscriptionEnd) {
    const now = new Date()
    return user.subscriptionEnd > now
  }

  return true
}

/**
 * Check if user is currently on trial
 */
export function isOnTrial(user: User): boolean {
  return user.subscriptionStatus === 'trialing'
}

/**
 * Get days until subscription renewal
 */
export function getDaysUntilRenewal(user: User): number | null {
  if (!user.subscriptionEnd) {
    return null
  }

  const now = new Date()
  const endDate = new Date(user.subscriptionEnd)
  const diffTime = endDate.getTime() - now.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  return diffDays > 0 ? diffDays : 0
}

/**
 * Get days remaining in trial
 */
export function getTrialDaysRemaining(user: User): number | null {
  if (!isOnTrial(user) || !user.subscriptionEnd) {
    return null
  }

  return getDaysUntilRenewal(user)
}

/**
 * Check if user can access premium signals
 * Premium signals require PROFESSIONAL or INSTITUTIONAL tier
 */
export function canAccessPremiumSignals(user: User): boolean {
  if (!isSubscriptionActive(user)) {
    return false
  }

  return user.tier === 'PROFESSIONAL' || user.tier === 'INSTITUTIONAL'
}

/**
 * Require active subscription - throws error if not active
 */
export function requireActiveSubscription(user: User): void {
  if (!isSubscriptionActive(user)) {
    throw new Error('Active subscription required')
  }
}

/**
 * Get subscription status display text
 */
export function getSubscriptionStatusText(user: User): string {
  if (!user.subscriptionStatus) {
    return 'No subscription'
  }

  const statusMap: Record<string, string> = {
    active: 'Active',
    trialing: 'Trial',
    past_due: 'Past Due',
    canceled: 'Canceled',
    unpaid: 'Unpaid',
  }

  return statusMap[user.subscriptionStatus] || user.subscriptionStatus
}

/**
 * Get subscription status color for UI
 */
export function getSubscriptionStatusColor(user: User): string {
  if (!user.subscriptionStatus) {
    return 'text-alpine-text-dim'
  }

  const colorMap: Record<string, string> = {
    active: 'text-alpine-accent',
    trialing: 'text-alpine-pink',
    past_due: 'text-alpine-red',
    canceled: 'text-alpine-text-dim',
    unpaid: 'text-alpine-red',
  }

  return colorMap[user.subscriptionStatus] || 'text-alpine-text-dim'
}

/**
 * Check if user can upgrade to a higher tier
 */
export function canUpgrade(user: User, targetTier: 'PROFESSIONAL' | 'INSTITUTIONAL'): boolean {
  const tierHierarchy: Record<string, number> = {
    STARTER: 1,
    PROFESSIONAL: 2,
    INSTITUTIONAL: 3,
  }

  const currentLevel = tierHierarchy[user.tier] || 0
  const targetLevel = tierHierarchy[targetTier] || 0

  return targetLevel > currentLevel
}

/**
 * Get tier display name
 */
export function getTierDisplayName(tier: string): string {
  return TIER_PRICING[tier as keyof typeof TIER_PRICING]?.name || tier
}

/**
 * Get tier price
 */
export function getTierPrice(tier: string): number {
  return TIER_PRICING[tier as keyof typeof TIER_PRICING]?.price || 0
}

