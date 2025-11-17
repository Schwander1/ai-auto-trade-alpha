'use client'

import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Activity, ShieldCheck } from 'lucide-react'

const regimes = [
  {
    name: 'BULL REGIME',
    icon: TrendingUp,
    color: 'alpine-neon-pink',
    winRate: '66.18%',
    strategy: 'Aggressive momentum',
    active: 'Strong uptrends',
    params: {
      rsi: '36-70',
      volume: '>1.4x',
      profit: '~5%',
      stop: '1-2%',
    },
  },
  {
    name: 'BEAR REGIME',
    icon: TrendingDown,
    color: 'alpine-semantic-error',
    winRate: '54.99%',
    strategy: 'Conservative shorts',
    active: 'Confirmed downtrends',
    params: {
      rsi: 'Adjusted lower',
      volume: '>1.4x',
      profit: '~3%',
      stop: 'Tight',
    },
  },
  {
    name: 'CHOP REGIME',
    icon: Activity,
    color: 'alpine-neon-cyan',
    winRate: '56.11%',
    strategy: 'Mean reversion',
    active: 'Range-bound markets',
    params: {
      rsi: 'Wider bands',
      volume: '>1.5x',
      profit: '~2.5%',
      stop: 'Tight',
    },
  },
  {
    name: 'CRISIS REGIME',
    icon: ShieldCheck,
    color: 'alpine-neon-purple',
    winRate: '56.67%',
    strategy: 'Capital preservation',
    active: 'High volatility',
    params: {
      rsi: 'Ultra-selective',
      volume: '>2.0x',
      profit: '~2%',
      stop: 'Very tight',
    },
  },
]

const glowClasses = {
  'alpine-neon-pink': 'shadow-glow-pink animate-pulse-glow-pink border-alpine-neon-pink/50',
  'alpine-semantic-error': 'shadow-glow-red animate-pulse-glow-red border-alpine-semantic-error/50',
  'alpine-neon-cyan': 'shadow-glow-cyan animate-pulse-glow-cyan border-alpine-neon-cyan/50',
  'alpine-neon-purple': 'shadow-glow-purple animate-pulse-glow-purple border-alpine-neon-purple/50',
}

const textColors = {
  'alpine-neon-pink': 'text-alpine-neon-pink',
  'alpine-semantic-error': 'text-alpine-semantic-error',
  'alpine-neon-cyan': 'text-alpine-neon-cyan',
  'alpine-neon-purple': 'text-alpine-neon-purple',
}

export default function Solution() {
  return (
    <section className="bg-alpine-black-primary py-24 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(24,224,255,0.05),transparent_70%)]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl sm:text-5xl font-bold text-alpine-text-primary mb-4">
            Four Specialized Strategies
          </h2>
          <p className="text-xl text-alpine-text-secondary max-w-3xl mx-auto mb-4">
            Our AI detects the current market regime and automatically uses the optimal strategy
          </p>
          <p className="text-sm text-alpine-text-tertiary italic">
            Full parameters available to Institutional tier
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {regimes.map((regime, index) => {
            const Icon = regime.icon
            const glowClass = glowClasses[regime.color as keyof typeof glowClasses]
            const textColor = textColors[regime.color as keyof typeof textColors]
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className={`glassmorphism rounded-xl p-6 border-2 ${glowClass} hover:border-opacity-100 transition-all`}
              >
                <div className="flex items-center justify-between mb-4">
                  <Icon className={`w-8 h-8 ${textColor}`} />
                  <span className={`text-xs font-bold uppercase ${textColor}`}>{regime.name}</span>
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="text-alpine-text-secondary text-sm mb-1">Win Rate</div>
                    <div className={`text-3xl font-bold font-mono ${textColor}`}>
                      {regime.winRate}
                    </div>
                  </div>
                  <div>
                    <div className="text-alpine-text-secondary text-sm mb-1">Strategy</div>
                    <div className="text-alpine-text-primary text-sm leading-relaxed">{regime.strategy}</div>
                  </div>
                  <div>
                    <div className="text-alpine-text-secondary text-sm mb-1">Activates</div>
                    <div className="text-alpine-text-primary text-sm font-semibold">{regime.active}</div>
                  </div>
                  <div className="pt-3 border-t border-alpine-neon-cyan/20">
                    <div className="text-alpine-text-secondary text-sm mb-2">Parameters (High-Level)</div>
                    <div className="space-y-1 text-sm font-mono text-alpine-text-secondary">
                      <div>RSI: {regime.params.rsi}</div>
                      <div>Vol: {regime.params.volume}</div>
                      <div>Target: {regime.params.profit}</div>
                      <div>Stop: {regime.params.stop}</div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
