'use client'

import { Check, X, Zap, Crown, Rocket } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface Tier {
  name: string
  displayName: string
  price: number
  priceId: string
  features: string[]
  limitations?: string[]
  icon: React.ReactNode
  popular?: boolean
}

interface PricingTableProps {
  currentTier?: string
  onUpgrade?: (tier: string) => void
  className?: string
}

/**
 * PricingTable component displaying 3 tiers with features
 * Shows current tier and upgrade CTAs
 */
export default function PricingTable({ currentTier, onUpgrade, className = '' }: PricingTableProps) {
  const tiers: Tier[] = [
    {
      name: 'starter',
      displayName: 'Founder',
      price: 49,
      priceId: 'price_1SSNCpLoDEAt72V24jylX5T0',
      icon: <Zap className="w-6 h-6" />,
      features: [
        'Basic signals (75%+ confidence)',
        '1 signal per day',
        'Email support',
        'Signal history (30 days)',
        'Basic analytics',
      ],
      limitations: [
        'No premium signals',
        'No backtesting',
        'No API access',
      ],
    },
    {
      name: 'pro',
      displayName: 'Professional',
      price: 99,
      priceId: 'price_1SSNRdLoDEAt72V2LIS5cbRI',
      icon: <Crown className="w-6 h-6" />,
      popular: true,
      features: [
        'Premium signals (85%+ confidence)',
        '10 signals per day',
        'Priority support',
        'Signal history (1 year)',
        'Advanced analytics',
        'Backtesting tools',
        'Export to CSV',
      ],
      limitations: [
        'No API access',
        'Limited custom strategies',
      ],
    },
    {
      name: 'elite',
      displayName: 'Institutional',
      price: 249,
      priceId: 'price_1SSNXhLoDEAt72V2Y2uQarct',
      icon: <Rocket className="w-6 h-6" />,
      features: [
        'All signals (95%+ confidence)',
        'Unlimited signals',
        '24/7 priority support',
        'Full signal history',
        'Advanced analytics & reporting',
        'Advanced backtesting',
        'API access',
        'Custom strategies',
        'White-label options',
      ],
    },
  ]

  const isCurrentTier = (tierName: string) => currentTier === tierName

  return (
    <div className={`grid grid-cols-1 md:grid-cols-3 gap-6 ${className}`}>
      {tiers.map((tier) => (
        <div
          key={tier.name}
          className={`relative bg-alpine-black-secondary border rounded-lg p-6 ${
            tier.popular
              ? 'border-alpine-neon-cyan shadow-glow-cyan'
              : 'border-alpine-black-border'
          } ${isCurrentTier(tier.name) ? 'ring-2 ring-alpine-neon-cyan' : ''}`}
        >
          {tier.popular && (
            <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
              <span className="bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pink text-white text-sm font-bold px-3 py-1 rounded-full">
                Most Popular
              </span>
            </div>
          )}

          {isCurrentTier(tier.name) && (
            <div className="absolute -top-3 right-4">
              <span className="bg-alpine-neon-cyan text-alpine-black-primarytext-sm-fontbol-dpx-3 py-1 rounded-full">
                Current Plan
              </span>
            </div>
          )}

          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-alpine-neoncya-n/10 text-alpine-neon-cyan mb-4">
              {tier.icon}
            </div>
            <h3 className="text-2xl font-bold text-alpine-text-primary mb-2">{tier.displayName}</h3>
            <div className="mb-4">
              <span className="text-4xl font-black text-alpine-text-primary ">${tier.price}</span>
              <span className="text-alpine-text-secondary">/month</span>
            </div>
          </div>

          <ul className="space-y-3 mb-6">
            {tier.features.map((feature, index) => (
              <li key={index} className="flex items-start gap-2">
                <Check className="w-5 h-5 text-alpine-neon-cyanflexshri-nk-0 mt-0.5" />
                <span className="text-sm text-alpine-text-primary ">{feature}</span>
              </li>
            ))}
            {tier.limitations?.map((limitation, index) => (
              <li key={`lim-${index}`} className="flex items-start gap-2 opacity-50">
                <X className="w-5 h-5 text-alpine-text-secondaryflexshri-nk-0 mt-0.5" />
                <span className="text-sm text-alpine-text-secondary">{limitation}</span>
              </li>
            ))}
          </ul>

          <Button
            onClick={() => onUpgrade?.(tier.name)}
            disabled={isCurrentTier(tier.name)}
            className={`w-full ${
              tier.popular
                ? 'bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pinkhove-r:from-alpine-neon-pinkhove-r:to-alpine-neoncya-n'
                : 'bg-alpine-black-border hover:bg-alpine-black-border/80'
            } text-white font-bold disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isCurrentTier(tier.name) ? 'Current Plan' : 'Upgrade'}
          </Button>
        </div>
      ))}
    </div>
  )
}

