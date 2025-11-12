'use client'

import { useState } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion'
import { Button } from '@/components/ui/button'
import { Check, Zap, ArrowRight, Clock, Sparkles } from 'lucide-react'

// Hardcoded price IDs as specified
const PRICE_IDS = {
  STARTER: 'price_1SSNCpLoDEAt72V24jylX5T0',
  PROFESSIONAL: 'price_1SSNRdLoDEAt72V2LIS5cbRI',
  INSTITUTIONAL: 'price_1SSNXhLoDEAt72V2Y2uQarct',
} as const

const pricingTiers = [
  {
    id: 'starter',
    name: 'Starter',
    description: 'Best for beginners',
    priceAnnual: 485,
    priceId: PRICE_IDS.STARTER,
    trialDays: 7,
    mainFeatures: [
      'Top 6 Stock Signals (QQQ, SPY, GOOGL, AAPL, AMZN, MSFT)',
      '~100 signals per month',
      'Email delivery (9 AM ET daily)',
      '87-98% confidence scores',
      'Est. 49% win rate',
      'SHA-256 verified trade log',
    ],
    additionalFeatures: [
      'Est. 8-9% CAGR',
      'Educational content',
      '7-day free trial',
      'Cancel anytime',
    ],
    popular: false,
  },
  {
    id: 'professional',
    name: 'Professional',
    description: 'Most Popular',
    priceAnnual: 985,
    priceId: PRICE_IDS.PROFESSIONAL,
    trialDays: 7,
    mainFeatures: [
      'Everything in Starter, plus:',
      'BTC signals (best-performing crypto)',
      '~150 signals per month',
      'Email + SMS delivery',
      'Est. 47% win rate',
      'Priority support (< 24hr)',
    ],
    additionalFeatures: [
      'Est. 9-10% CAGR',
      'Weekly market analysis',
      '7-day free trial',
      'Cancel anytime',
    ],
    popular: true,
  },
  {
    id: 'institutional',
    name: 'Institutional',
    description: 'Best for professionals & firms',
    priceAnnual: 3985,
    priceId: PRICE_IDS.INSTITUTIONAL,
    trialDays: 7,
    mainFeatures: [
      'Everything in Professional, plus:',
      'REST API access',
      'Kelly sizing calculator',
      'Real-time performance dashboard',
      'Custom webhooks (Slack, etc.)',
      'Priority support (< 1hr)',
    ],
    additionalFeatures: [
      'NDA + Full methodology disclosure',
      'Confidence score API access',
      '7-day free trial',
      'Cancel anytime',
    ],
    popular: false,
  },
]

export default function PricingPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [billingPeriod, setBillingPeriod] = useState<'annual' | 'monthly'>('annual')
  const [activeTab, setActiveTab] = useState('professional')

  const handleCheckout = (priceId: string) => {
    if (status === 'unauthenticated') {
      router.push(`/signup?redirect=${encodeURIComponent('/pricing')}`)
      return
    }

    // Redirect to checkout API
    window.location.href = `/api/checkout?priceId=${priceId}`
  }

  const activeTier = pricingTiers.find((tier) => tier.id === activeTab) || pricingTiers[1]
  const displayPrice = billingPeriod === 'annual' 
    ? activeTier.priceAnnual 
    : Math.round(activeTier.priceAnnual / 12)
  const priceLabel = billingPeriod === 'annual' ? '/year' : '/month'

  return (
    <div className="min-h-screen bg-alpine-bg">
      {/* Header */}
      <div className="border-b border-alpine-border bg-alpine-card">
        <div className="container mx-auto px-4 py-12 text-center">
          <h1 className="text-4xl md:text-5xl font-display font-black text-alpine-text mb-4">
            Choose Your Plan
          </h1>
          <p className="text-lg text-alpine-text-dim max-w-2xl mx-auto mb-6">
            Start with a 7-day free trial. No credit card required until trial ends.
            Cancel anytime.
          </p>
          
          {/* Conversion CTA */}
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-alpine-accent/20 to-alpine-pink/20 border-2 border-alpine-accent/50 rounded-xl mb-4">
            <Clock className="w-5 h-5 text-alpine-accent" aria-hidden="true" />
            <span className="text-alpine-text font-bold text-lg">
              Founder Pricing Ends Soon: Lock in Now
            </span>
            <Sparkles className="w-5 h-5 text-alpine-pink" aria-hidden="true" />
          </div>
        </div>
      </div>

      {/* Pricing Tabs */}
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          {/* Tier Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-8">
              {pricingTiers.map((tier) => (
                <TabsTrigger
                  key={tier.id}
                  value={tier.id}
                  className="data-[state=active]:bg-alpine-accent/20 data-[state=active]:text-alpine-accent"
                >
                  {tier.name}
                  {tier.popular && (
                    <span className="ml-2 px-2 py-0.5 bg-alpine-pink/20 text-alpine-pink text-xs rounded-full">
                      Popular
                    </span>
                  )}
                </TabsTrigger>
              ))}
            </TabsList>

            {/* Tab Content */}
            {pricingTiers.map((tier) => (
              <TabsContent key={tier.id} value={tier.id} className="mt-0">
                <div className="bg-alpine-card border border-alpine-border rounded-xl p-8 md:p-12">
                  {/* Tier Header */}
                  <div className="text-center mb-8">
                    <h2 className="text-3xl md:text-4xl font-display font-black text-alpine-text mb-2">
                      {tier.name}
                    </h2>
                    <p className="text-alpine-text-dim mb-6">{tier.description}</p>

                    {/* Billing Period Toggle */}
                    <div className="flex items-center justify-center gap-4 mb-6">
                      <button
                        onClick={() => setBillingPeriod('monthly')}
                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                          billingPeriod === 'monthly'
                            ? 'bg-alpine-accent/20 text-alpine-accent border border-alpine-accent/30'
                            : 'text-alpine-text-dim hover:text-alpine-text'
                        }`}
                      >
                        Monthly
                      </button>
                      <button
                        onClick={() => setBillingPeriod('annual')}
                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                          billingPeriod === 'annual'
                            ? 'bg-alpine-accent/20 text-alpine-accent border border-alpine-accent/30'
                            : 'text-alpine-text-dim hover:text-alpine-text'
                        }`}
                      >
                        Annual
                        <span className="ml-2 px-2 py-0.5 bg-alpine-pink/20 text-alpine-pink text-xs rounded">
                          Save 17%
                        </span>
                      </button>
                    </div>

                    {/* Price Display */}
                    <div className="mb-6">
                      <div className="flex items-baseline justify-center gap-2">
                        <span className="text-5xl md:text-6xl font-black text-alpine-text">
                          ${displayPrice.toLocaleString()}
                        </span>
                        <span className="text-xl text-alpine-text-dim">{priceLabel}</span>
                      </div>
                      <p className="text-sm text-alpine-text-dim mt-2">
                        {tier.trialDays}-day free trial • Cancel anytime
                      </p>
                    </div>
                  </div>

                  {/* Main Features */}
                  <ul className="space-y-4 mb-6">
                    {tier.mainFeatures.map((feature, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <Check className="w-5 h-5 text-alpine-accent flex-shrink-0 mt-0.5" aria-hidden="true" />
                        <span className="text-alpine-text">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* Additional Features (Collapsible) */}
                  {tier.additionalFeatures.length > 0 && (
                    <Accordion type="single" collapsible className="mb-8">
                      <AccordionItem value="more-features" className="border-alpine-border">
                        <AccordionTrigger className="text-alpine-text-dim hover:text-alpine-text">
                          View more features
                        </AccordionTrigger>
                        <AccordionContent>
                          <ul className="space-y-3 pt-2">
                            {tier.additionalFeatures.map((feature, index) => (
                              <li key={index} className="flex items-start gap-3">
                                <Check className="w-4 h-4 text-alpine-accent flex-shrink-0 mt-0.5" aria-hidden="true" />
                                <span className="text-sm text-alpine-text-dim">{feature}</span>
                              </li>
                            ))}
                          </ul>
                        </AccordionContent>
                      </AccordionItem>
                    </Accordion>
                  )}

                  {/* CTA Button */}
                  <Button
                    onClick={() => handleCheckout(tier.priceId)}
                    className="w-full bg-gradient-to-r from-alpine-accent to-alpine-pink hover:from-alpine-pink hover:to-alpine-accent text-white font-black text-lg py-6 rounded-lg transition-all duration-300 hover:scale-105 shadow-lg"
                    size="lg"
                  >
                    Start {tier.trialDays}-Day Free Trial
                    <ArrowRight className="w-5 h-5 ml-2" aria-hidden="true" />
                  </Button>

                  {/* Trust Indicators */}
                  <div className="mt-6 text-center">
                    <p className="text-xs text-alpine-text-dim">
                      ✓ No credit card required for trial • ✓ Cancel anytime • ✓ Secure checkout via Stripe
                    </p>
                  </div>
                </div>
              </TabsContent>
            ))}
          </Tabs>

          {/* FAQ Section */}
          <div className="mt-16 bg-alpine-card border border-alpine-border rounded-xl p-8 max-w-3xl mx-auto">
            <h3 className="text-2xl font-display font-bold text-alpine-text mb-6 text-center">
              Frequently Asked Questions
            </h3>
            <Accordion type="single" collapsible className="space-y-4">
              <AccordionItem value="trial" className="border-alpine-border">
                <AccordionTrigger className="text-alpine-text hover:text-alpine-accent">
                  What happens after the trial?
                </AccordionTrigger>
                <AccordionContent className="text-alpine-text-dim">
                  After your 7-day free trial, your subscription will automatically renew at the
                  selected billing period. You can cancel anytime from your account dashboard.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="change-plans" className="border-alpine-border">
                <AccordionTrigger className="text-alpine-text hover:text-alpine-accent">
                  Can I change plans later?
                </AccordionTrigger>
                <AccordionContent className="text-alpine-text-dim">
                  Yes! You can upgrade or downgrade your plan at any time. Changes are prorated
                  automatically.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="payment" className="border-alpine-border">
                <AccordionTrigger className="text-alpine-text hover:text-alpine-accent">
                  What payment methods do you accept?
                </AccordionTrigger>
                <AccordionContent className="text-alpine-text-dim">
                  We accept all major credit cards through Stripe. Your payment information is
                  securely processed and never stored on our servers.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        </div>
      </div>
    </div>
  )
}
