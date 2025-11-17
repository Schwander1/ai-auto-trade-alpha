'use client'

import { motion } from 'framer-motion'
import { AlertTriangle, Check, X } from 'lucide-react'

export default function RiskDisclosure() {
  return (
    <section className="bg-alpine-orange/10 border-y-4 border-alpine-orange/50 py-16">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-5xl mx-auto"
        >
          <div className="flex items-center space-x-4 mb-8">
            <AlertTriangle className="w-12 h-12 text-alpine-orange flex-shrink-0" />
            <h2 className="text-3xl sm:text-4xl font-bold text-alpine-orange">
              ⚠️ TRADING INVOLVES SUBSTANTIAL RISK
            </h2>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* What Our Data Shows */}
            <div>
              <h3 className="text-xl font-bold text-alpine-text-primary mb-4">What Our Data Shows:</h3>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-alpine-neon-cyan mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">
                    <strong className="text-alpine-neon-cyan">45.2% win rate</strong> in 20-year backtest (4,374 signals)
                  </span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-alpine-neon-cyan mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">
                    <strong className="text-alpine-neon-purple">+565%</strong> backtested return (9.94% CAGR)
                  </span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-alpine-neon-cyan mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">
                    <strong className="text-alpine-semantic-error">-36.1%</strong> maximum drawdown (significant)
                  </span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-alpine-neon-cyan mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">
                    Beat SPY by <strong className="text-alpine-neon-cyan">165%</strong> (backtested, same period)
                  </span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-alpine-neon-cyan mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">
                    Signal confidence range: <strong className="text-alpine-neon-cyan">87-98%</strong> (median 89%)
                  </span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-alpine-neon-cyan mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">
                    High selectivity: Only generate when strict criteria met
                  </span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-alpine-neon-cyan mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">
                    <strong className="text-alpine-neon-cyan">Live verified track record begins Wednesday, November 12, 2025 at 9:00 AM ET</strong>
                  </span>
                </li>
              </ul>
            </div>

            {/* What This DOES NOT Mean */}
            <div>
              <h3 className="text-xl font-bold text-alpine-text-primary mb-4">What This DOES NOT Mean:</h3>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <X className="w-5 h-5 text-alpine-semantic-error mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">You will achieve these same results</span>
                </li>
                <li className="flex items-start">
                  <X className="w-5 h-5 text-alpine-semantic-error mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">Past performance guarantees future results</span>
                </li>
                <li className="flex items-start">
                  <X className="w-5 h-5 text-alpine-semantic-error mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">Our signals will always be profitable</span>
                </li>
                <li className="flex items-start">
                  <X className="w-5 h-5 text-alpine-semantic-error mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">You can't lose money</span>
                </li>
                <li className="flex items-start">
                  <X className="w-5 h-5 text-alpine-semantic-error mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">Backtested results equal future live performance</span>
                </li>
                <li className="flex items-start">
                  <X className="w-5 h-5 text-alpine-semantic-error mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">Historical simulation represents actual trading</span>
                </li>
                <li className="flex items-start">
                  <X className="w-5 h-5 text-alpine-semantic-error mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">Confidence scores guarantee signal success</span>
                </li>
                <li className="flex items-start">
                  <X className="w-5 h-5 text-alpine-semantic-error mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-alpine-text-primary ">Higher confidence always means higher win probability</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Your Responsibilities */}
          <div className="mt-8">
            <h3 className="text-xl font-bold text-alpine-text-primary mb-4">Your Responsibilities:</h3>
            <ul className="space-y-2">
              <li className="flex items-start">
                <span className="text-alpine-orange mr-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">Position sizing is YOUR decision</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-orange mr-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">Risk management is YOUR responsibility</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-orange mr-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">You can lose your entire investment</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-orange mr-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">Consult a licensed advisor before trading</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-orange mr-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">Only trade with capital you can afford to lose</span>
              </li>
            </ul>
          </div>

          {/* Final Statement */}
          <div className="bg-alpine-black-secondary rounded-lg p-6 border border-alpine-black-border m-t-8">
            <p className="text-lg font-semibold text-alpine-text-primary text-center">
              We provide signals for educational purposes.
            </p>
            <p className="text-lg font-semibold text-alpine-neon-cyan text-center-mt-2">
              YOU make trading decisions. YOU accept the risks.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

