'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Check } from 'lucide-react'

const symbolData = [
  { symbol: 'QQQ', trades: 417, winRate: 52.0, performance: 110063 },
  { symbol: 'SPY', trades: 405, winRate: 54.6, performance: 66202 },
  { symbol: 'GOOGL', trades: 329, winRate: 48.9, performance: 95064 },
  { symbol: 'AAPL', trades: 324, winRate: 45.7, performance: 83712 },
  { symbol: 'AMZN', trades: 362, winRate: 48.1, performance: 67724 },
  { symbol: 'MSFT', trades: 358, winRate: 46.9, performance: 20117 },
]

export default function SymbolTable() {
  const [animatedValues, setAnimatedValues] = useState(
    symbolData.map(() => ({ trades: 0, winRate: 0, performance: 0 }))
  )

  useEffect(() => {
    const intervals = symbolData.map((data, index) => {
      const duration = 2000
      const steps = 60
      const increment = {
        trades: data.trades / steps,
        winRate: data.winRate / steps,
        performance: data.performance / steps,
      }

      let currentStep = 0
      const interval = setInterval(() => {
        currentStep++
        setAnimatedValues((prev) => {
          const newValues = [...prev]
          newValues[index] = {
            trades: Math.min(data.trades, increment.trades * currentStep),
            winRate: Math.min(data.winRate, increment.winRate * currentStep),
            performance: Math.min(data.performance, increment.performance * currentStep),
          }
          return newValues
        })

        if (currentStep >= steps) {
          clearInterval(interval)
        }
      }, duration / steps)

      return interval
    })

    return () => intervals.forEach((interval) => clearInterval(interval))
  }, [])

  return (
    <section className="py-24 bg-alpine-dark">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="font-display text-4xl md:text-6xl font-black text-white mb-4">
            Not All Signals Are Equal
          </h2>
          <p className="text-xl text-alpine-text-dim">
            We tested 4,374 signals. Here's what we learned:
          </p>
        </motion.div>

        {/* Desktop Table */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="hidden md:block mb-8"
        >
          <div className="bg-alpine-card border border-alpine-border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-alpine-accent/10">
                <tr>
                  <th className="px-6 py-4 text-left text-alpine-text font-semibold">Symbol</th>
                  <th className="px-6 py-4 text-right text-alpine-text font-semibold">Trades</th>
                  <th className="px-6 py-4 text-right text-alpine-text font-semibold">Win Rate</th>
                  <th className="px-6 py-4 text-right text-alpine-text font-semibold">Performance</th>
                </tr>
              </thead>
              <tbody>
                {symbolData.map((row, index) => (
                  <motion.tr
                    key={row.symbol}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                    className={`border-t border-alpine-border ${
                      index < 2 ? 'bg-alpine-accent/5' : ''
                    }`}
                  >
                    <td className="px-6 py-4">
                      <span className="text-alpine-text font-bold font-mono text-lg">
                        {row.symbol}
                      </span>
                      {index < 2 && (
                        <Check className="w-5 h-5 text-alpine-accent inline-block ml-2" />
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-alpine-text-dim font-mono">
                        {Math.round(animatedValues[index].trades)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-alpine-text-dim font-mono">
                        {animatedValues[index].winRate.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-alpine-accent font-bold font-mono">
                        +${Math.round(animatedValues[index].performance).toLocaleString()}
                      </span>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Mobile Cards */}
        <div className="md:hidden space-y-4 mb-8">
          {symbolData.map((row, index) => (
            <motion.div
              key={row.symbol}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className={`bg-alpine-card border border-alpine-border rounded-lg p-4 ${
                index < 2 ? 'border-alpine-accent/50' : ''
              }`}
            >
              <div className="flex justify-between items-center mb-2">
                <span className="text-alpine-text font-bold font-mono text-lg">{row.symbol}</span>
                {index < 2 && <Check className="w-5 h-5 text-alpine-accent" />}
              </div>
              <div className="grid grid-cols-3 gap-2 text-sm">
                <div>
                  <div className="text-alpine-text-dim">Trades</div>
                  <div className="text-alpine-text font-semibold">
                    {Math.round(animatedValues[index].trades)}
                  </div>
                </div>
                <div>
                  <div className="text-alpine-text-dim">Win Rate</div>
                  <div className="text-alpine-text font-semibold">
                    {animatedValues[index].winRate.toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div className="text-alpine-text-dim">Performance</div>
                  <div className="text-alpine-accent font-bold">
                    +${Math.round(animatedValues[index].performance).toLocaleString()}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Callout */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-alpine-accent/10 border-2 border-alpine-accent rounded-lg p-6 text-center"
        >
          <div className="text-3xl mb-3">💡</div>
          <p className="text-lg text-alpine-text font-semibold">
            Our Starter tier focuses on the{' '}
            <span className="text-alpine-accent">TOP 6 PERFORMING SYMBOLS</span>.
          </p>
          <p className="text-alpine-text-dim mt-2">Not random picks. Mathematically optimized.</p>
        </motion.div>
      </div>
    </section>
  )
}

