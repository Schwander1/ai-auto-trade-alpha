'use client'

import { useSignals } from '@/hooks/useSignals'
import { useSession, signOut } from 'next-auth/react'
import SignalCard from '@/components/signal-card'
import { RefreshCw, AlertCircle, Loader2, LogOut, User, CreditCard, Calendar, TrendingUp } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import ManageSubscriptionButton from '@/components/stripe/ManageSubscriptionButton'
import CheckoutButton from '@/components/stripe/CheckoutButton'
import {
  isSubscriptionActive,
  isOnTrial,
  getTrialDaysRemaining,
  getDaysUntilRenewal,
  getSubscriptionStatusText,
  getSubscriptionStatusColor,
  canUpgrade,
  getTierDisplayName,
} from '@/lib/stripe-helpers'
import type { UserTier } from '@prisma/client'

/**
 * Dashboard page displaying real-time trading signals from Argo API.
 * 
 * Features:
 * - Automatic polling every 30 seconds
 * - Manual refresh capability
 * - Error handling and retry logic
 * - Loading states
 * - Responsive grid layout
 * - Authentication required (protected by middleware)
 */
export default function DashboardPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [userData, setUserData] = useState<any>(null)
  const { signals, isLoading, error, refresh, isPolling } = useSignals({
    limit: 20,
    premiumOnly: false,
    pollInterval: 30000, // 30 seconds
    autoPoll: true,
    cache: true,
  })

  // Fetch user data with subscription info
  useEffect(() => {
    if (session?.user?.id) {
      fetch('/api/user/me')
        .then((res) => res.json())
        .then((data) => setUserData(data))
        .catch((err) => console.error('Failed to fetch user data:', err))
    }
  }, [session])

  const handleSignOut = async () => {
    await signOut({ redirect: true, callbackUrl: '/' })
  }

  const subscriptionActive = userData ? isSubscriptionActive(userData) : false
  const onTrial = userData ? isOnTrial(userData) : false
  const trialDaysRemaining = userData ? getTrialDaysRemaining(userData) : null
  const daysUntilRenewal = userData ? getDaysUntilRenewal(userData) : null

  // Show loading state while checking session
  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-alpine-bg flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-alpine-accent animate-spin" aria-hidden="true" />
      </div>
    )
  }

  // If not authenticated, middleware will redirect, but show message just in case
  if (status === 'unauthenticated') {
    return (
      <div className="min-h-screen bg-alpine-bg flex items-center justify-center">
        <div className="text-center">
          <p className="text-alpine-text-dim mb-4">Please sign in to access the dashboard</p>
          <button
            onClick={() => router.push('/login')}
            className="px-6 py-3 bg-gradient-to-r from-alpine-accent to-alpine-pink hover:from-alpine-pink hover:to-alpine-accent text-white font-black rounded-lg transition-all duration-300"
          >
            Sign In
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-alpine-bg">
      {/* Header */}
      <div className="border-b border-alpine-border bg-alpine-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <h1 className="text-3xl font-display font-black text-alpine-text">
                  Trading Signals Dashboard
                </h1>
                {session?.user && (
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-alpine-card border border-alpine-border rounded-lg">
                      <User className="w-4 h-4 text-alpine-text-dim" aria-hidden="true" />
                      <span className="text-sm text-alpine-text">
                        {session.user.email}
                      </span>
                      <span className="text-xs px-2 py-0.5 bg-alpine-accent/20 text-alpine-accent rounded">
                        {session.user.tier}
                      </span>
                    </div>
                    <button
                      onClick={handleSignOut}
                      className="flex items-center gap-2 px-4 py-2 bg-alpine-card border border-alpine-border rounded-lg hover:bg-alpine-red/10 hover:border-alpine-red/30 transition-colors"
                      aria-label="Sign out"
                    >
                      <LogOut className="w-4 h-4 text-alpine-text-dim" aria-hidden="true" />
                      <span className="text-sm font-semibold text-alpine-text">Sign Out</span>
                    </button>
                  </div>
                )}
              </div>
              <p className="text-alpine-text-dim">
                Real-time signals from Argo Trading Engine
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
              className="ml-4 flex items-center gap-2 px-4 py-2 bg-alpine-card border border-alpine-border rounded-lg hover:bg-alpine-border/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
        {/* Subscription Status Section */}
        {session?.user && userData && (
          <div className="mb-8 bg-alpine-card border border-alpine-border rounded-xl p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-display font-bold text-alpine-text mb-2">
                  Subscription Status
                </h2>
                <div className="flex items-center gap-4 flex-wrap">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-alpine-text-dim">Tier:</span>
                    <span className="px-3 py-1 bg-alpine-accent/20 text-alpine-accent rounded-lg text-sm font-semibold">
                      {getTierDisplayName(userData.tier)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-alpine-text-dim">Status:</span>
                    <span className={`text-sm font-semibold ${getSubscriptionStatusColor(userData)}`}>
                      {getSubscriptionStatusText(userData)}
                    </span>
                  </div>
                  {onTrial && trialDaysRemaining !== null && (
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-alpine-pink" aria-hidden="true" />
                      <span className="text-sm text-alpine-text-dim">
                        {trialDaysRemaining} days left in trial
                      </span>
                    </div>
                  )}
                  {subscriptionActive && !onTrial && daysUntilRenewal !== null && (
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-alpine-accent" aria-hidden="true" />
                      <span className="text-sm text-alpine-text-dim">
                        Renews in {daysUntilRenewal} days
                      </span>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-3">
                {subscriptionActive && (
                  <ManageSubscriptionButton variant="outline" />
                )}
                {!subscriptionActive && (
                  <CheckoutButton tier={userData.tier || 'STARTER'}>
                    Subscribe Now
                  </CheckoutButton>
                )}
                {(userData.tier === 'STARTER' || userData.tier === 'PROFESSIONAL') && (
                  <>
                    {canUpgrade(userData, 'PROFESSIONAL') && (
                      <CheckoutButton tier="PROFESSIONAL">
                        <TrendingUp className="w-4 h-4 mr-2" />
                        Upgrade to Professional
                      </CheckoutButton>
                    )}
                    {canUpgrade(userData, 'INSTITUTIONAL') && (
                      <CheckoutButton tier="INSTITUTIONAL">
                        <TrendingUp className="w-4 h-4 mr-2" />
                        Upgrade to Institutional
                      </CheckoutButton>
                    )}
                  </>
                )}
              </div>
            </div>
            {!subscriptionActive && (
              <div className="mt-4 p-4 bg-alpine-red/10 border border-alpine-red/30 rounded-lg">
                <p className="text-sm text-alpine-red">
                  Your subscription is not active. Please subscribe to continue accessing signals.
                </p>
              </div>
            )}
          </div>
        )}

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

