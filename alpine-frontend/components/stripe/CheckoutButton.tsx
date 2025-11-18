'use client'

import { useState } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Loader2, AlertCircle } from 'lucide-react'
// UserTier type definition
type UserTier = 'STARTER' | 'PROFESSIONAL' | 'INSTITUTIONAL'

interface CheckoutButtonProps {
  tier: UserTier
  children?: React.ReactNode
  className?: string
}

/**
 * CheckoutButton component for Stripe subscription checkout
 */
export default function CheckoutButton({
  tier,
  children,
  className,
}: CheckoutButtonProps) {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCheckout = async () => {
    // Check authentication
    if (status === 'unauthenticated') {
      router.push('/signup?redirect=/pricing')
      return
    }

    if (!session?.user?.id) {
      setError('Please sign in to continue')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      // Create checkout session
      const response = await fetch('/api/stripe/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tier,
          userId: session.user.id,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to create checkout session')
      }

      // Redirect to Stripe Checkout
      if (data.url) {
        window.location.href = data.url
      } else {
        throw new Error('No checkout URL returned')
      }
    } catch (err) {
      console.error('Checkout error:', err)
      setError(
        err instanceof Error ? err.message : 'Failed to start checkout'
      )
      setIsLoading(false)
    }
  }

  return (
    <div className={className}>
      {error && (
        <div className="mb-4 p-3 bg-alpine-semantic-error10 border border-alpine-semantic-error30 rounded-lg flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-alpine-semantic-errorflexshri-nk-0 mt-0.5" aria-hidden="true" />
          <p className="text-sm text-alpine-semantic-error">{error}</p>
        </div>
      )}
      <Button
        onClick={handleCheckout}
        disabled={isLoading || status === 'loading'}
        className="w-full"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
            Processing...
          </>
        ) : (
          children || 'Start Free Trial'
        )}
      </Button>
    </div>
  )
}

