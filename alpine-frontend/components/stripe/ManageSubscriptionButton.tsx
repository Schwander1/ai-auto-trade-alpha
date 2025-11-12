'use client'

import { useState } from 'react'
import { useSession } from 'next-auth/react'
import { Button } from '@/components/ui/button'
import { Loader2, CreditCard, AlertCircle } from 'lucide-react'

interface ManageSubscriptionButtonProps {
  className?: string
  variant?: 'default' | 'outline' | 'ghost' | 'secondary'
}

/**
 * ManageSubscriptionButton - Opens Stripe Customer Portal
 */
export default function ManageSubscriptionButton({
  className,
  variant = 'outline',
}: ManageSubscriptionButtonProps) {
  const { data: session } = useSession()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleManageSubscription = async () => {
    if (!session?.user?.id) {
      setError('Please sign in to manage subscription')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/stripe/create-portal-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: session.user.id,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to create portal session')
      }

      // Redirect to Stripe Customer Portal
      if (data.url) {
        window.location.href = data.url
      } else {
        throw new Error('No portal URL returned')
      }
    } catch (err) {
      console.error('Portal session error:', err)
      setError(
        err instanceof Error ? err.message : 'Failed to open customer portal'
      )
      setIsLoading(false)
    }
  }

  return (
    <div className={className}>
      {error && (
        <div className="mb-4 p-3 bg-alpine-red/10 border border-alpine-red/30 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-alpine-red flex-shrink-0 mt-0.5" aria-hidden="true" />
          <p className="text-sm text-alpine-red">{error}</p>
        </div>
      )}
      <Button
        onClick={handleManageSubscription}
        disabled={isLoading}
        variant={variant}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
            Opening...
          </>
        ) : (
          <>
            <CreditCard className="w-4 h-4 mr-2" aria-hidden="true" />
            Manage Subscription
          </>
        )}
      </Button>
    </div>
  )
}

