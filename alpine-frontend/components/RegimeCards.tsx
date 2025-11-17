'use client'

import { motion } from 'framer-motion'

const regimes = [
  {
    emoji: '📈',
    name: 'Bull Regime',
    strategy: 'Trend-following with momentum',
    winRate: '66%',
    detection: 'Price > 200 SMA, Low volatility',
  },
  {
    emoji: '📉',
    name: 'Bear Regime',
    strategy: 'Counter-trend reversions',
    winRate: '55%',
    detection: 'Price < 200 SMA, Declining markets',
  },
  {
    emoji: '🔀',
    name: 'Chop Regime',
    strategy: 'Range-bound mean reversion',
    winRate: '56%',
    detection: 'Sideways price action, Normal volatility',
  },
  {
    emoji: '⚡',
    name: 'Crisis Regime',
    strategy: 'Volatility-based opportunities',
    winRate: '57%',
    detection: 'ATR > 5%, Extreme volatility',
  },
]

export default function RegimeCards() {
  return (
    <section className="py-24 bg-alpine-black-primary">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="font-display text-4xl tracking-[0.15em] tracking-[0.15em] md:text-6xl font-black text-white mb-4">
            4 Regimes. Not One Strategy.
          </h2>
          <p className="text-xl text-alpine-text-secondary">
            Many signal services have one strategy. It works in bull markets and fails in crashes.
          </p>
          <p className="text-lg text-alpine-neon-cyan font-semibold-mt-2">We adapt. In real-time.</p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {regimes.map((regime, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -8, scale: 1.02 }}
              className="p-6 rounded-lg bg-alpine-black-secondary border border-alpine-black-border hove-r:border-alpine-neon-cyan/50 transition-all"
            >
              <div className="text-4xl mb-4">{regime.emoji}</div>
              <h3 className="text-xl font-display font-bold text-alpine-text-primary mb-3">
                {regime.name}
              </h3>
              <p className="text-alpine-text-secondary mb-3">{regime.strategy}</p>
              <p className="text-alpine-neon-cyan font-bold-text-lgmb-3">{regime.winRate} win rate*</p>
              <p className="text-alpine-text-secondary text-sm">Detected: {regime.detection}</p>
            </motion.div>
          ))}
        </div>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center text-alpine-text-secondary text-smital-icmt-8"
        >
          *Based on 20 years of backtested performance. Past results ≠ future results.
        </motion.p>
      </div>
    </section>
  )
}

