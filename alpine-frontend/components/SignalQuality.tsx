'use client'

import { motion } from 'framer-motion'
import { Check } from 'lucide-react'

const symbolData = [
  { symbol: 'QQQ', trades: 417, winRate: '52.0%', performance: '+$110,063', highlight: true },
  { symbol: 'SPY', trades: 405, winRate: '54.6%', performance: '+$66,202', highlight: true },
  { symbol: 'GOOGL', trades: 329, winRate: '48.9%', performance: '+$95,064', highlight: false },
  { symbol: 'AAPL', trades: 324, winRate: '45.7%', performance: '+$83,712', highlight: false },
  { symbol: 'AMZN', trades: 362, winRate: '48.1%', performance: '+$67,724', highlight: false },
  { symbol: 'MSFT', trades: 358, winRate: '46.9%', performance: '+$20,117', highlight: false },
]

export default function SignalQuality() {
  return (
    <section className="bg-alpine-black-primary py-24 relative overflow-hidden">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-bold text-alpine-text-primary text-center mb-4 font-heading"
        >
          Not All Signals Are Equal
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-xl text-alpine-text-secondary text-center-mb-12"
        >
          We tested 4,374 signals. Here's what we learned:
        </motion.p>

        {/* Data Table */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="card-neon rounded-xl p-8 border border-alpine-neon-cyan/20 max-w-4xl mx-auto mb-8 overflow-x-auto"
        >
          <table className="w-full">
            <thead>
              <tr className="border-b border-alpine-neon-cyan/20">
                <th className="text-left py-4 px-4 text-alpine-text-primary font-semibold">Symbol</th>
                <th className="text-right py-4 px-4 text-alpine-text-primary font-semibold">Trades</th>
                <th className="text-right py-4 px-4 text-alpine-text-primary font-semibold">Win Rate</th>
                <th className="text-right py-4 px-4 text-alpine-text-primary font-semibold">Performance</th>
              </tr>
            </thead>
            <tbody>
              {symbolData.map((row, index) => (
                <tr
                  key={index}
                  className={`border-b border-alpine-neon-cyan/10 ${
                    row.highlight ? 'bg-alpine-neon-pink/5' : ''
                  }`}
                >
                  <td className="py-4 px-4">
                    <span className="text-alpine-text-primary font-bold font-mono">{row.symbol}</span>
                  </td>
                  <td className="py-4 px-4 text-right">
                    <span className="text-alpine-text-primary font-mono">{row.trades}</span>
                  </td>
                  <td className="py-4 px-4 text-right">
                    <span className="text-alpine-text-primary font-mono">{row.winRate}</span>
                  </td>
                  <td className="py-4 px-4 text-right">
                    <span className="text-alpine-semantic-success font-bold font-mono">{row.performance}</span>
                    {row.highlight && (
                      <Check className="w-4 h-4 text-alpine-semantic-success inline-block ml-2" />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </motion.div>

        {/* Callout Box */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="card-neon rounded-xl p-6 border-2 border-alpine-neon-pink/30 max-w-3xl mx-auto text-center"
        >
          <div className="text-3xl mb-3">💡</div>
          <p className="text-lg text-alpine-text-primary font-semibold">
            Our Starter tier focuses on the{' '}
            <span className="text-alpine-neon-pink">TOP 6 PERFORMING SYMBOLS</span>.
          </p>
          <p className="text-alpine-text-secondary mt-2">
            Not random picks. Mathematically optimized.
          </p>
        </motion.div>
      </div>
    </section>
  )
}

