'use client'

import { motion } from 'framer-motion'

export default function SignalSelectivity() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="bg-alpine-black-secondary border border-alpine-neon-cyan/30 rounded-lg p-8 mb-12"
    >
      <div className="flex items-start gap-4 mb-4">
        <div className="w-12 h-12 bg-alpine-neon-cyan/10 rounded-lg flex items-center justify-center flex-shrink-0">
          <span className="text-2xl">📊</span>
        </div>
        <div className="flex-1">
          <h3 className="text-2xl font-black text-alpine-text-primary mb-2">
            High Signal Selectivity
          </h3>
          <p className="text-sm text-alpine-text-secondary mb-4">
            <strong className="text-alpine-neon-cyan">Updated: November 12, 2025</strong> - Backtest confidence analysis
          </p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-lg font-bold text-alpine-text-primary mb-3">Confidence Distribution</h4>
          <div className="space-y-2 text-alpine-text-secondary mb-4">
            <div className="flex justify-between items-center">
              <span>Minimum confidence:</span>
              <strong className="text-alpine-neon-cyan">87%</strong>
            </div>
            <div className="flex justify-between items-center">
              <span>Median confidence:</span>
              <strong className="text-alpine-neon-cyan">89%</strong>
            </div>
            <div className="flex justify-between items-center">
              <span>Maximum confidence:</span>
              <strong className="text-alpine-neon-cyan">98%</strong>
            </div>
          </div>

          <div className="mt-4 space-y-2">
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-alpine-black-primaryroundedful-l-h-2">
                <div className="bg-alpine-neon-cyanroundedful-l-h-2" style={{ width: '57%' }}></div>
              </div>
              <span className="text-sm text-alpine-text-secondary">57% (87-90%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-alpine-black-primaryroundedful-l-h-2">
                <div className="bg-alpine-neon-pink-roundedful-lh-2" style={{ width: '43%' }}></div>
              </div>
              <span className="text-sm text-alpine-text-secondary">43% (90%+)</span>
            </div>
          </div>
        </div>

        <div>
          <h4 className="text-lg font-bold text-alpine-text-primary mb-3">What This Means</h4>
          <ul className="space-y-3 text-alpine-text-secondary">
            <li className="flex items-start gap-2">
              <span className="text-alpine-neon-cyanfontbo-ld">✓</span>
              <span>
                Our system is <strong className="text-alpine-text-primary ">highly selective</strong> - only generates signals when strong multi-regime criteria align
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-alpine-neon-cyanfontbo-ld">✓</span>
              <span>
                We don't spam low-quality trades - <strong className="text-alpine-text-primary ">every signal meets strict standards</strong>
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-alpine-neon-cyanfontbo-ld">✓</span>
              <span>
                All qualifying signals are sent - <strong className="text-alpine-text-primary ">no cherry-picking</strong> or hidden filtering
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-alpine-neon-cyanfontbo-ld">✓</span>
              <span>
                Track performance by confidence tier yourself in the <strong className="text-alpine-text-primary ">downloadable dataset</strong>
              </span>
            </li>
          </ul>
        </div>
      </div>

      <div className="mt-6 pt-6 border-t border-alpine-black-border">
        <p className="text-alpine-text-secondary text-sm">
          <strong className="text-alpine-neon-cyan">Transparency note:</strong> Unlike services that claim to "only send high-confidence signals"
          while hiding low performers, we send ALL signals that meet our multi-regime criteria. Every signal is cryptographically verified
          starting November 12, 2025 at 9:00 AM ET. No retroactive editing. No cherry-picking. Just math.
        </p>
      </div>
    </motion.div>
  )
}

