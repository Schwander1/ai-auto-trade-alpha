'use client'

import { motion } from 'framer-motion'

export default function HonestDisclosure() {
  return (
    <section className="relative overflow-hidden border-y border-alpine-neon-pink/30 bg-gradient-to-r from-alpine-neon-pink/5 via-alpine-neon-cyan/5 to-alpine-neon-pink/5">
      <div className="relative container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="flex items-start gap-4 mb-6"
          >
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-alpine-neon-pink/20 flex items-center justify-center">
              <span className="text-2xl">⚠️</span>
            </div>
            <div>
              <h3 className="text-3xl font-black text-white mb-3">
                Honest Disclosure: This Is a Backtest
              </h3>
              <p className="text-xl text-alpine-text-secondary mb-4">
                Our 20-year performance data (565% return, 4,374 signals) is from
                <strong className="text-white"> historical simulation</strong>, not live trading.
                Many signal services hide this fact. <strong className="text-alpine-neon-cyan">We don't.</strong>
              </p>
              <div className="bg-alpine-black-primary border-2 border-alpine-neon-cyan/30 rounded-xl p-6">
                <p className="text-lg text-alpine-text-primary mb-2">
                  <strong className="text-alpine-neon-cyan">Launching November 12, 2025 at 9:00 AM ET</strong>,
                  we're proving it live:
                </p>
                <ul className="space-y-2 text-alpine-text-secondary">
                  <li className="flex items-center gap-3">
                    <span className="text-alpine-neon-cyan">✓</span>
                    Every signal SHA-256 cryptographically verified
                  </li>
                  <li className="flex items-center gap-3">
                    <span className="text-alpine-neon-cyan">✓</span>
                    No cherry-picking possible (math prevents it)
                  </li>
                  <li className="flex items-center gap-3">
                    <span className="text-alpine-neon-cyan">✓</span>
                    Watch real track record build from day one
                  </li>
                  <li className="flex items-center gap-3">
                    <span className="text-alpine-neon-cyan">✓</span>
                    Founding members lock in 50% off forever
                  </li>
                </ul>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

