'use client'

import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Check, Zap, Gift, Sparkles, ArrowRight, Lock } from 'lucide-react'

const founderPlans = [
  {
    name: 'FOUNDER TIER 1: STARTER',
    emoji: '🎁',
    founderPrice: 485,
    regularPrice: 970,
    savings: 50,
    limit: 50,
    remaining: 50,
    description: 'Best for beginners',
    features: [
      'Top 6 Stock Signals Only (QQQ, SPY, GOOGL, AAPL, AMZN, MSFT)',
      '~100 signals per month',
      'Email delivery (9 AM ET daily) - All signals include confidence scores (87-98%)',
      'Est. 49% win rate**',
      'All signals 87-98% confidence. High selectivity = better quality.',
      'Est. 8-9% CAGR**',
      'SHA-256 verified trade log',
      'Educational content',
      '7-day free trial',
      '"Founder" badge in community',
    ],
    lockedPrice: 485,
    popular: false,
    cta: 'Claim Founder Pricing',
    url: 'https://alpinewave.gumroad.com/l/gaizue',
  },
  {
    name: 'FOUNDER TIER 2: PROFESSIONAL',
    emoji: '⭐',
    founderPrice: 985,
    regularPrice: 1970,
    savings: 50,
    limit: 30,
    remaining: 30,
    description: 'MOST POPULAR',
    features: [
      'Everything in Starter, plus:',
      'BTC signals (best-performing crypto)',
      '~150 signals per month',
      'Email + SMS delivery - All signals include confidence scores (87-98%)',
      'Est. 47% win rate**',
      'All signals 87-98% confidence. High selectivity = better quality.',
      'Est. 9-10% CAGR**',
      'Weekly market analysis',
      'Priority support (< 24hr)',
      '"Founder Pro" badge',
      '7-day free trial',
    ],
    lockedPrice: 985,
    popular: true,
    cta: 'Claim Founder Pro',
    url: 'https://alpinewave.gumroad.com/l/alpine-founderpr-o',
  },
  {
    name: 'FOUNDING MEMBER: INSTITUTIONAL',
    emoji: '💎',
    founderPrice: 3985,
    regularPrice: 7970,
    savings: 50,
    limit: 10,
    remaining: 10,
    description: 'Best for professionals & firms',
    features: [
      'Everything in Professional, plus:',
      'REST API access',
      'Kelly sizing calculator',
      'Real-time performance dashboard',
      'Custom webhooks (Slack, etc.)',
      'Priority support (< 1hr)',
      'NDA + Full methodology disclosure',
      'Confidence score API access (87-98% threshold details included)',
      '"Founding Member" badge + special access',
      '7-day free trial',
    ],
    lockedPrice: 3985,
    popular: false,
    cta: 'Request Founding Member Access',
    url: 'https://alpinewave.gumroad.com/l/alpine-foundingmembe-r',
  },
]

const regularPricing = [
  { name: 'Starter', annual: 970, monthly: 97 },
  { name: 'Professional', annual: 1970, monthly: 197 },
  { name: 'Institutional', annual: 7970, monthly: 797 },
]

export default function Pricing() {
  return (
    <section
      id="pricing"
      className="py-24 relative overflow-hidden bg-alpine-black-primary"
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Founder Launch Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="inline-block bg-alpine-neon-cyan/20 border-2 border-alpine-neon-cyan/50 rounded-xl px-8 py-6 mb-4">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Gift className="w-6 h-6 text-alpine-neon-cyan" />
              <h2 className="text-2xl sm:text-3xl font-display font-bold text-alpine-neon-cyan">
                🎁 FOUNDER LAUNCH - LIMITED TIME ONLY
              </h2>
            </div>
            <p className="text-xl text-alpine-text-primary font-semiboldm-b-2">
              First 90 Customers Lock In <span className="text-alpine-neon-cyan">50% OFF FOR LIFE</span>
            </p>
            <p className="text-sm text-alpine-text-secondary">
              When founder spots sell out, prices double forever.
            </p>
          </div>
        </motion.div>

        {/* Founder Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-7xl mx-auto mb-12">
          {founderPlans.map((plan, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className={`relative rounded-2xl p-8 border-2 bg-alpine-black-secondary ${
                plan.popular
                  ? 'border-alpine-neon-cyan/50 shadow-glow-cyan scale-105'
                  : 'border-alpine-black-border'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-alpine-neon-cyan text-alpine-black-primary px-4 py-1 rounded-full text-sm font-bold flex items-center space-x-1">
                  <Zap className="w-4 h-4" />
                  <span>⭐ MOST POPULAR</span>
                </div>
              )}

              <div className="text-center mb-6">
                <div className="text-4xl mb-3">{plan.emoji}</div>
                <h3 className="text-xl font-display font-bold text-alpine-neon-cyan mb-4">{plan.name}</h3>

                <div className="mb-3">
                  <div className="text-5xl font-bold text-alpine-neon-cyan mb-1">
                    ${plan.founderPrice.toLocaleString()}
                  </div>
                  <div className="text-alpine-text-secondary text-sm-mb-2">/year FOR LIFE</div>
                  <div className="text-sm text-alpine-text-secondaryline-through-mb-1">
                    Regular: ${plan.regularPrice.toLocaleString()}/year
                  </div>
                  <div className="text-alpine-neon-cyan font-bold-text-sm">
                    YOU SAVE {plan.savings}% FOREVER
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="bg-alpine-orange/20 border border-alpine-orange/30 rounded-lg px-4 py-2">
                    <div className="text-sm text-alpine-orange font-semibold">
                      Limited to first {plan.limit} {plan.name.includes('FOUNDING MEMBER') ? 'members' : 'customers'}
                    </div>
                  </div>
                  <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg px-4 py-2">
                    <div className={`text-sm font-semibold ${
                      plan.description === 'MOST POPULAR' ? 'text-alpine-semantic-success' : 'text-alpine-text-secondary'
                    }`}>
                      {plan.description}
                    </div>
                  </div>
                </div>
              </div>

              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start space-x-3">
                    <Check className="w-5 h-5 text-alpine-neon-cyanflexshri-nk-0 mt-0.5" />
                    <span className={`text-alpine-text-primary text-sm ${
                      feature.includes('LOCKED AT')
                        ? 'font-bold text-alpine-neon-cyantextba-se'
                        : ''
                    }`}>
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              {/* LOCKED AT PRICE FOREVER */}
              <div className="bg-alpine-neon-cyan/20 border-2 border-alpine-neon-cyan/50 rounded-lg p-4 mb-6 text-center">
                <p className="text-alpine-neon-cyan font-bold-text-lg">
                  🔒 LOCKED AT ${plan.lockedPrice.toLocaleString()}/YEAR FOREVER
                </p>
              </div>

              <Button
                className={`w-full mb-3 ${
                  plan.popular
                    ? 'bg-alpine-neon-cyan text-alpine-black-primaryshadow-glow-cyanhove-r:bg-alpine-neon-cyandar-k'
                    : 'bg-alpine-neon-cyan text-alpine-blackprimaryhove-r:bg-alpine-neon-cyan-darkborde-r-2 border-alpine-neoncya-n'
                } font-bold text-lg py-6 hover:scale-105 transition-transform`}
                size="lg"
                onClick={() => {
                  window.open(plan.url, '_blank')
                }}
              >
                {plan.cta}
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>

              {/* Spots Remaining */}
              <div className="text-center">
                <div className="text-alpine-neon-cyan font-bold-text-sm">
                  {plan.remaining}/{plan.limit} spots remaining
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* What Happens When Founder Pricing Sells Out */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-alpine-black-secondary rounded-xl p-8 border-2 border-alpine-orange/50 max-w-4xl mx-auto mb-8"
        >
          <div className="flex items-center space-x-3 mb-6">
            <Zap className="w-8 h-8 text-alpine-orange" />
            <h3 className="text-2xl font-display font-bold text-alpine-text-primary ">
              ⚡ WHAT HAPPENS WHEN FOUNDER PRICING SELLS OUT?
            </h3>
          </div>
          <p className="text-3xl font-bold text-alpine-orange mb-6 text-center">
            Prices double. Forever.
          </p>
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            {regularPricing.map((price, index) => (
              <div key={index} className="text-center">
                <div className="text-alpine-text-secondary text-sm-mb-1">{price.name}:</div>
                <div className="text-alpine-text-primary font-bold-textl-g">
                  ${price.annual.toLocaleString()}/year
                </div>
                <div className="text-alpine-text-secondary text-sm">
                  (${price.monthly}/mo)
                </div>
              </div>
            ))}
          </div>
          <p className="text-lg text-alpine-text-primary font-semibold-textcente-r">
            Lock in 50% off now, or pay double later.
          </p>
        </motion.div>

        {/* Performance Disclaimer */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-16 max-w-5xl mx-auto bg-alpine-black-secondary border-2 border-alpine-black-border rounde-d-2xl p-8"
        >
          <h3 className="text-2xl font-black text-alpine-text-primary mb-4">
            About Our Signals & Confidence Scores
          </h3>
          <p className="text-lg text-alpine-text-secondary mb-4">
            All 4,374 backtest signals (2006-2025) scored between <strong className="text-alpine-neon-cyan">87-98% confidence</strong> (median 89%).
            This demonstrates our system is highly selective - we only generate signals when strong multi-regime criteria align.
          </p>
          <p className="text-lg text-alpine-text-secondary mb-4">
            <strong className="text-alpine-text-primary ">Launching November 12, 2025 at 9:00 AM ET:</strong> We will send ALL signals that meet our
            generation criteria (no cherry-picking). Every signal includes its confidence score and SHA-256 cryptographic
            verification. You can track performance by confidence tier in the complete downloadable dataset.
          </p>
          <p className="text-lg text-alpine-text-secondary">
            Win rates and returns shown are from backtested data. <strong className="text-alpine-text-primary ">Past performance
            does not guarantee future results.</strong> Live verified performance tracking begins Wednesday, November 12, 2025 at 9:00 AM ET.
          </p>
        </motion.div>
      </div>
    </section>
  )
}
