'use client'

import { motion } from 'framer-motion'
import { AlertTriangle, Check, X } from 'lucide-react'

export default function RiskWarning() {
  return (
    <section className="bg-alpine-semantic-error/10 border-y-4 border-alpine-semantic-error/50 py-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-5xl mx-auto"
        >
          <div className="flex items-center space-x-4 mb-8">
            <AlertTriangle className="w-12 h-12 text-alpine-semantic-errorflexshri-nk-0" />
            <h2 className="text-3xl sm:text-4xl font-bold text-alpine-semantic-error">
              ⚠️ RISK WARNING - READ BEFORE SUBSCRIBING
            </h2>
          </div>

          <div className="space-y-6 text-alpine-text-primary leading-relaxed">
            <div className="bg-alpine-semantic-error/20 rounded-lg p-6 border border-alpine-semantic-error/30">
              <p className="text-lg font-bold text-alpine-semantic-error mb-4">
                Trading involves substantial risk of loss. You can lose your entire investment and more.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-bold text-alpine-text-primary mb-4">Our Results:</h3>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-alpine-semantic-successm-r-3 mt-0.5 flex-shrink-0" />
                  <span>
                    <strong className="text-alpine-neon-pink">58.5% win rate:</strong> Verified across 20 years of backtested data
                  </span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-alpine-semantic-successm-r-3 mt-0.5 flex-shrink-0" />
                  <span>
                    <strong className="text-alpine-neon-pink">90.5 average confidence:</strong> Based on 4,391 historical signals
                  </span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-alpine-semantic-successm-r-3 mt-0.5 flex-shrink-0" />
                  <span>
                    <strong className="text-alpine-neon-pink">4 adaptive regimes:</strong> Bull (66%), Bear (55%), Chop (56%), Crisis (57%)
                  </span>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-bold text-alpine-text-primary mb-4">What This DOES NOT Mean:</h3>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <X className="w-5 h-5 text-alpine-semantic-error mr-3 mt-0.5 flex-shrink-0" />
                  <span>You will achieve these same results in live trading</span>
                </li>
                <li className="flex items-start">
                  <X className="w-5 h-5 text-alpine-semantic-error mr-3 mt-0.5 flex-shrink-0" />
                  <span>Past performance guarantees future results</span>
                </li>
                <li className="flex items-start">
                  <X className="w-5 h-5 text-alpine-semantic-error mr-3 mt-0.5 flex-shrink-0" />
                  <span>Backtested data equals real-world execution</span>
                </li>
                <li className="flex items-start">
                  <X className="w-5 h-5 text-alpine-semantic-error mr-3 mt-0.5 flex-shrink-0" />
                  <span>Our signals will always be profitable</span>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-bold text-alpine-text-primary mb-4">Your Responsibilities:</h3>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <span className="text-alpine-semantic-error mr-3 mt-1">•</span>
                  <span>You are solely responsible for trade execution</span>
                </li>
                <li className="flex items-start">
                  <span className="text-alpine-semantic-error mr-3 mt-1">•</span>
                  <span>Position sizing decisions are YOUR responsibility</span>
                </li>
                <li className="flex items-start">
                  <span className="text-alpine-semantic-error mr-3 mt-1">•</span>
                  <span>Risk management is YOUR responsibility</span>
                </li>
                <li className="flex items-start">
                  <span className="text-alpine-semantic-error mr-3 mt-1">•</span>
                  <span>Consult a licensed advisor before trading</span>
                </li>
                <li className="flex items-start">
                  <span className="text-alpine-semantic-error mr-3 mt-1">•</span>
                  <span>Only trade with capital you can afford to lose</span>
                </li>
              </ul>
            </div>

            <div className="bg-alpine-black-primary/50 rounded-lg p-6 border border-alpine-neon-cyan/20 mt-8">
              <p className="text-lg font-semibold text-alpine-text-primary text-center">
                We provide signals and education. <span className="text-alpine-neon-pink">YOU make trading decisions.</span>
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

