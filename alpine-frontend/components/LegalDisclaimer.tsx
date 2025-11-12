'use client'

import { motion } from 'framer-motion'
import { AlertTriangle } from 'lucide-react'

export default function LegalDisclaimer() {
  return (
    <section className="bg-warning-red/10 border-y-2 border-warning-red/30 py-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto"
        >
          <div className="flex items-start space-x-4 mb-6">
            <AlertTriangle className="w-8 h-8 text-warning-red flex-shrink-0 mt-1" />
            <h2 className="text-2xl font-bold text-warning-red">
              ⚠️ IMPORTANT DISCLAIMERS - READ CAREFULLY
            </h2>
          </div>

          <div className="space-y-4 text-ice-blue/90 leading-relaxed">
            <p>
              <strong className="text-warning-red">Alpine Analytics LLC</strong> provides trading
              signals for educational and informational purposes only. We are{' '}
              <strong>NOT registered investment advisors</strong>.
            </p>

            <div>
              <strong className="text-ice-blue">Trading Risk:</strong> Trading involves substantial
              risk of loss. You can lose more than your initial investment. Past performance does
              not guarantee future results.
            </div>

            <div>
              <strong className="text-ice-blue">Backtest Limitations:</strong> Performance data is
              based on 20-year backtesting (2006-2025) on NVDA, AAPL, MSFT, QQQ. Backtested results
              are hypothetical and may not reflect actual live trading performance. Slippage, fees,
              and market conditions can significantly affect results.
            </div>

            <div>
              <strong className="text-ice-blue">No Guarantees:</strong> We make no guarantees of
              profit, win rate, or any specific outcome in live trading. Our 58.5% win rate is
              backtested and may not continue in future market conditions.
            </div>

            <div>
              <strong className="text-ice-blue">Your Responsibility:</strong> You are solely
              responsible for your trading decisions. Consult a licensed financial advisor before
              trading.
            </div>

            <div>
              <strong className="text-ice-blue">Company Disclosure:</strong> Alpine Analytics LLC is
              operated by professional traders who use these systems with their own capital.
              Subscription revenue funds operations and ongoing R&D.
            </div>

            <div>
              <strong className="text-ice-blue">Pricing:</strong> Current pricing is promotional
              and subject to change. Annual plans lock in rates for the subscription term.
            </div>

            <div>
              <strong className="text-ice-blue">Geographic Restrictions:</strong> Service may not
              be available in all jurisdictions. Check local regulations before subscribing.
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

