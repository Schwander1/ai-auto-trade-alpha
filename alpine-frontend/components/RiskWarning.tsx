'use client'

import { motion } from 'framer-motion'
import { AlertTriangle, Check, X } from 'lucide-react'

export default function RiskWarning() {
  return (
    <section className="bg-warning-red/10 border-y-4 border-warning-red/50 py-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-5xl mx-auto"
        >
          <div className="flex items-center space-x-4 mb-8">
            <AlertTriangle className="w-12 h-12 text-warning-red flex-shrink-0" />
            <h2 className="text-3xl sm:text-4xl font-bold text-warning-red">
              ⚠️ RISK WARNING - READ BEFORE SUBSCRIBING
            </h2>
          </div>

          <div className="space-y-6 text-ice-blue leading-relaxed">
            <div className="bg-warning-red/20 rounded-lg p-6 border border-warning-red/30">
              <p className="text-lg font-bold text-warning-red mb-4">
                Trading involves substantial risk of loss. You can lose your entire investment and more.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-bold text-ice-blue mb-4">Our Results:</h3>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-laser-green mr-3 mt-0.5 flex-shrink-0" />
                  <span>
                    <strong className="text-neon-pink">58.5% win rate:</strong> Verified across 20 years of backtested data
                  </span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-laser-green mr-3 mt-0.5 flex-shrink-0" />
                  <span>
                    <strong className="text-neon-pink">90.5 average confidence:</strong> Based on 4,391 historical signals
                  </span>
                </li>
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-laser-green mr-3 mt-0.5 flex-shrink-0" />
                  <span>
                    <strong className="text-neon-pink">4 adaptive regimes:</strong> Bull (66%), Bear (55%), Chop (56%), Crisis (57%)
                  </span>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-bold text-ice-blue mb-4">What This DOES NOT Mean:</h3>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <X className="w-5 h-5 text-warning-red mr-3 mt-0.5 flex-shrink-0" />
                  <span>You will achieve these same results in live trading</span>
                </li>
                <li className="flex items-start">
                  <X className="w-5 h-5 text-warning-red mr-3 mt-0.5 flex-shrink-0" />
                  <span>Past performance guarantees future results</span>
                </li>
                <li className="flex items-start">
                  <X className="w-5 h-5 text-warning-red mr-3 mt-0.5 flex-shrink-0" />
                  <span>Backtested data equals real-world execution</span>
                </li>
                <li className="flex items-start">
                  <X className="w-5 h-5 text-warning-red mr-3 mt-0.5 flex-shrink-0" />
                  <span>Our signals will always be profitable</span>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-bold text-ice-blue mb-4">Your Responsibilities:</h3>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <span className="text-warning-red mr-3 mt-1">•</span>
                  <span>You are solely responsible for trade execution</span>
                </li>
                <li className="flex items-start">
                  <span className="text-warning-red mr-3 mt-1">•</span>
                  <span>Position sizing decisions are YOUR responsibility</span>
                </li>
                <li className="flex items-start">
                  <span className="text-warning-red mr-3 mt-1">•</span>
                  <span>Risk management is YOUR responsibility</span>
                </li>
                <li className="flex items-start">
                  <span className="text-warning-red mr-3 mt-1">•</span>
                  <span>Consult a licensed advisor before trading</span>
                </li>
                <li className="flex items-start">
                  <span className="text-warning-red mr-3 mt-1">•</span>
                  <span>Only trade with capital you can afford to lose</span>
                </li>
              </ul>
            </div>

            <div className="bg-space-gray/50 rounded-lg p-6 border border-electric-cyan/20 mt-8">
              <p className="text-lg font-semibold text-ice-blue text-center">
                We provide signals and education. <span className="text-neon-pink">YOU make trading decisions.</span>
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

