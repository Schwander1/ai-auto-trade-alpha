'use client'

import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import PricingTable from '@/components/dashboard/PricingTable'
import PaymentModal from '@/components/dashboard/PaymentModal'
import UserMenu from '@/components/dashboard/UserMenu'
import { CheckCircle2, Zap, Crown, Rocket, ArrowRight } from 'lucide-react'

/**
 * Pricing Page - Pricing tiers with upgrade CTA
 */
export default function PricingPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [currentTier, setCurrentTier] = useState<string>('')
  const [selectedTier, setSelectedTier] = useState<{ name: string; price: number; priceId: string } | null>(null)
  const [subscription, setSubscription] = useState<any>(null)

  useEffect(() => {
    if (session) {
      fetch('/api/subscriptions/plan')
        .then((res) => res.json())
        .then((data) => {
          setSubscription(data)
          setCurrentTier(data.tier || '')
        })
        .catch(console.error)
    }
  }, [session])

  const handleUpgrade = (tier: string) => {
    if (!session) {
      router.push('/login')
      return
    }

    const prices: Record<string, { price: number; priceId: string }> = {
      starter: { price: 49, priceId: 'price_1SSNCpLoDEAt72V24jylX5T0' },
      pro: { price: 99, priceId: 'price_1SSNRdLoDEAt72V2LIS5cbRI' },
      elite: { price: 249, priceId: 'price_1SSNXhLoDEAt72V2Y2uQarct' },
    }

    const tierData = prices[tier]
    if (tierData) {
      setSelectedTier({ name: tier, ...tierData })
    }
  }

  const features = [
    '95%+ win rate signals',
    'Real-time market analysis',
    'SHA-256 verified signals',
    '24/7 market monitoring',
    'Advanced backtesting',
    'API access (Elite)',
  ]

  return (
    <div className="min-h-screen bg-alpine-bg">
      {/* Header */}
      <header className="bg-alpine-card border-b border-alpine-border sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-alpine-text">Pricing</h1>
            {session && <UserMenu />}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-black text-alpine-text mb-4">
            Choose Your Plan
          </h2>
          <p className="text-xl text-alpine-text-dim max-w-2xl mx-auto">
            Start with our Founder plan and upgrade anytime. All plans include our proven trading signals.
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-12 max-w-4xl mx-auto">
          {features.map((feature, index) => (
            <div key={index} className="flex items-center gap-2 text-alpine-text">
              <CheckCircle2 className="w-5 h-5 text-alpine-accent flex-shrink-0" />
              <span className="text-sm">{feature}</span>
            </div>
          ))}
        </div>

        {/* Pricing Table */}
        <PricingTable currentTier={currentTier} onUpgrade={handleUpgrade} />

        {/* FAQ Section */}
        <div className="mt-16 max-w-3xl mx-auto">
          <h3 className="text-2xl font-bold text-alpine-text mb-6 text-center">Frequently Asked Questions</h3>
          <div className="space-y-4">
            <FAQItem
              question="Can I upgrade or downgrade my plan?"
              answer="Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately."
            />
            <FAQItem
              question="What payment methods do you accept?"
              answer="We accept all major credit cards through Stripe. All payments are secure and encrypted."
            />
            <FAQItem
              question="Is there a free trial?"
              answer="We offer a 7-day free trial for new users. No credit card required to start."
            />
            <FAQItem
              question="Can I cancel anytime?"
              answer="Yes, you can cancel your subscription at any time. You'll continue to have access until the end of your billing period."
            />
          </div>
        </div>

        {/* CTA Section */}
        {!session && (
          <div className="mt-16 text-center">
            <div className="bg-alpine-card border border-alpine-border rounded-lg p-8 max-w-2xl mx-auto">
              <h3 className="text-2xl font-bold text-alpine-text mb-4">
                Ready to get started?
              </h3>
              <p className="text-alpine-text-dim mb-6">
                Join thousands of traders using Alpine Analytics signals
              </p>
              <button
                onClick={() => router.push('/signup')}
                className="bg-gradient-to-r from-alpine-accent to-alpine-pink hover:from-alpine-pink hover:to-alpine-accent text-white font-bold px-8 py-3 rounded-lg transition-all inline-flex items-center gap-2"
              >
                Get Started
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Payment Modal */}
      {selectedTier && (
        <PaymentModal
          isOpen={!!selectedTier}
          onClose={() => setSelectedTier(null)}
          tier={selectedTier.name}
          price={selectedTier.price}
          priceId={selectedTier.priceId}
        />
      )}
    </div>
  )
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
  return (
    <div className="bg-alpine-card border border-alpine-border rounded-lg p-4">
      <h4 className="font-semibold text-alpine-text mb-2">{question}</h4>
      <p className="text-sm text-alpine-text-dim">{answer}</p>
    </div>
  )
}
