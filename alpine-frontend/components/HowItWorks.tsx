'use client'

import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Activity, Zap } from 'lucide-react'

const regimes = [
  {
    icon: TrendingUp,
    name: 'Bull Regime',
    strategy: 'Trend-following with momentum',
    winRate: '66% historical win rate*',
    detection: 'Price > 200 SMA, Low volatility',
    emoji: '📈',
  },
  {
    icon: TrendingDown,
    name: 'Bear Regime',
    strategy: 'Counter-trend reversions',
    winRate: '55% historical win rate*',
    detection: 'Price < 200 SMA, Declining markets',
    emoji: '📉',
  },
  {
    icon: Activity,
    name: 'Chop Regime',
    strategy: 'Range-bound mean reversion',
    winRate: '56% historical win rate*',
    detection: 'Sideways price action, Normal volatility',
    emoji: '🔀',
  },
  {
    icon: Zap,
    name: 'Crisis Regime',
    strategy: 'Volatility-based opportunities',
    winRate: '57% historical win rate*',
    detection: 'ATR > 5%, Extreme volatility',
    emoji: '⚡',
  },
]

const steps = [
  'Real-time regime detection (every 15 minutes)',
  'Multi-indicator confluence analysis',
  'Volume pattern confirmation',
  'Risk-adjusted position sizing (Kelly Criterion)',
  'SHA-256 cryptographic signature',
  'Delivery via email/SMS (<30 seconds)',
]

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="bg-alpine-black-primary py-24 relative overflow-hidden">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl sm:text-5xl font-bold text-alpine-text-primary mb-4 font-heading">
            4 Regimes. Not One Strategy.
          </h2>
          <p className="text-xl text-alpine-text-secondary max-w-3xl mx-auto mb-4">
            Many signal services have one strategy. It works in bull markets and fails in crashes.
          </p>
          <p className="text-lg text-alpine-neon-pink font-semibold">
            We adapt. In real-time.
          </p>
        </motion.div>

        {/* 4-Box Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {regimes.map((regime, index) => {
            const Icon = regime.icon
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card-neon rounded-xl p-6 border border-alpine-neon-cyan/20"
              >
                <div className="text-3xl mb-3">{regime.emoji}</div>
                <h3 className="text-xl font-bold text-alpine-text-primary mb-3 font-heading">{regime.name}</h3>
                <p className="text-alpine-text-primary mb-3">{regime.strategy}</p>
                <p className="text-alpine-neon-pink font-semibold text-sm mb-3">{regime.winRate}</p>
                <p className="text-alpine-text-secondary text-sm">Detected: {regime.detection}</p>
              </motion.div>
            )
          })}
        </div>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center text-alpine-text-secondary text-sm italic mb-12"
        >
          *Based on 20 years of backtested performance. Past results ≠ future results.
        </motion.p>

        {/* How Signals Are Generated */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="card-neon rounded-xl p-8 border-2 border-alpine-neon-pink/30 max-w-4xl mx-auto"
        >
          <h3 className="text-2xl font-bold text-alpine-text-primary mb-6 text-center font-heading">
            How Signals Are Generated
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            {steps.map((step, index) => (
              <div key={index} className="flex items-start space-x-3">
                <span className="text-alpine-neon-pink font-bold text-lg">{index + 1}.</span>
                <span className="text-alpine-text-primary ">{step}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
