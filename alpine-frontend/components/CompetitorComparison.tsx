'use client'

import { motion } from 'framer-motion'
import { Check, X, Download } from 'lucide-react'
import { Button } from '@/components/ui/button'

const comparisonData = [
  {
    feature: 'Historical Track Record',
    alpine: '20-year backtest (honest disclosure)',
    competitors: 'Claim "verified" without proof',
    alpineDetail: '4,374 signals, 45.2% win rate. Labeled as backtest, not fake verification.',
    competitorDetail: 'Backtest results presented as "verified track record" with no distinction.',
  },
  {
    feature: 'Signal Quality Standards',
    alpine: 'High selectivity (87-98% confidence)',
    competitors: 'Send everything, hide quality metrics',
    alpineDetail: 'High selectivity (87-98% confidence threshold). System only generates signals when strict multi-regime criteria met. All signals 87-98% confidence. Complete transparency.',
    competitorDetail: 'Many services spam signals regardless of quality. No published standards. Cherry-pick winners for marketing.',
  },
  {
    feature: 'Signal Delivery',
    alpine: 'Send ALL qualifying signals (no cherry-picking)',
    competitors: 'Hide poor signals, only show winners',
    alpineDetail: 'We send every signal that meets our strict criteria (87-98% confidence). No filtering after generation. SHA-256 verification.',
    competitorDetail: 'Claim "we only send high-confidence signals" while retroactively hiding losses. No way to verify.',
  },
  {
    feature: 'Complete Trade History',
    alpine: true,
    alpineDetail: '4,374 trades. Every single one. 2006-2025.',
    competitorDetail: 'Cherry-picked wins. Losses hidden.',
  },
  {
    feature: 'Cryptographic Verification',
    alpine: true,
    alpineDetail: 'SHA-256 signatures. Mathematically impossible to fake.',
    competitorDetail: 'Unverifiable claims. "Trust us."',
  },
  {
    feature: 'Verification Method',
    alpine: 'SHA-256 Cryptographic Proof',
    competitors: 'Screenshots / Self-Reported',
    alpineDetail: 'Open-source tools. Verify yourself in 60 seconds. Mathematically impossible to fake.',
    competitorDetail: 'PDF screenshots. No way to verify claims. Just "trust us."',
  },
  {
    feature: 'Show Losing Trades',
    alpine: true,
    alpineDetail: '45.2% win rate. We show every loss.',
    competitorDetail: 'Only promote winners. 90%+ win rates (often unverifiable or selective).',
  },
  {
    feature: 'Real Drawdowns',
    alpine: true,
    alpineDetail: 'Max drawdown: -36.1%. Disclosed upfront.',
    competitorDetail: 'Hide or minimize risk. Unrealistic claims.',
  },
  {
    feature: 'Downloadable Data',
    alpine: true,
    alpineDetail: 'Full CSV. Analyze yourself. Python/R/Excel ready.',
    competitorDetail: 'PDF screenshots. No raw data. Can\'t verify.',
  },
  {
    feature: 'Independent Verification',
    alpine: true,
    alpineDetail: 'Verify SHA-256 hashes yourself. Open methodology.',
    competitorDetail: 'No verification possible. Black box.',
  },
  {
    feature: 'Win Rate Honesty',
    alpine: '45.2%',
    competitors: '85-95% (claimed)',
    alpineDetail: 'Real, verified across 4,374 trades.',
    competitorDetail: 'Inflated, selective, unverifiable.',
  },
  {
    feature: 'Adaptive Strategy',
    alpine: true,
    alpineDetail: '4 regimes. Switches based on market conditions.',
    competitorDetail: 'One strategy. Fails in different market environments.',
  },
]

export default function CompetitorComparison() {
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
            Why Alpine Is Different: <span className="bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pink-bg-cliptex-ttext-transparent">Cryptographic Proof vs Marketing Claims</span>
          </h2>
          <p className="text-xl text-alpine-text-secondary">
            Many signal services hide their failures. We prove our performance.
          </p>
        </motion.div>

        <div className="max-w-6xl mx-auto">
          {/* Table Header */}
          <div className="grid grid-cols-3 gap-4 mb-4 pb-4 border-b border-alpine-black-border">
            <div className="font-semibold text-alpine-text-primary ">Feature</div>
            <div className="font-semibold text-alpine-neon-cyan text-center">Alpine</div>
            <div className="font-semibold text-alpine-semantic-error text-center">Other Services</div>
          </div>

          {/* Comparison Rows */}
          <div className="space-y-4">
            {comparisonData.map((row, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="grid grid-cols-3 gap-4 p-4 rounded-lg bg-alpine-black-secondary border border-alpine-black-border hove-r:border-alpine-neon-cyan/50 transition-colors"
              >
                <div className="font-medium text-alpine-text-primary ">{row.feature}</div>
                <div className="text-center">
                  {typeof row.alpine === 'boolean' ? (
                    row.alpine ? (
                      <Check className="w-6 h-6 text-alpine-neon-cyanmxau-to" />
                    ) : (
                      <X className="w-6 h-6 text-alpine-semantic-errormxau-to" />
                    )
                  ) : (
                    <span className="text-alpine-neon-cyanfontbo-ld">{row.alpine}</span>
                  )}
                  <p className="text-sm text-alpine-text-secondary mt-1">{row.alpineDetail}</p>
                </div>
                <div className="text-center">
                  {typeof row.competitors === 'string' ? (
                    <span className="text-alpine-semantic-errorfontbo-ld">{row.competitors}</span>
                  ) : (
                    <X className="w-6 h-6 text-alpine-semantic-errormxau-to" />
                  )}
                  <p className="text-sm text-alpine-text-secondary mt-1">{row.competitorDetail}</p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Emphasis Callout */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mt-8 p-6 bg-gradient-to-r from-alpine-neon-cyan/10 via-alpine-neon-pink/10 to-alpine-neon-purple/10 border border-alpine-neon-cyan/30 rounded-lg text-center"
          >
            <p className="text-lg text-alpine-text-primary ">
              <strong className="text-alpine-neon-cyan">
                Many signal services show you PDFs and screenshots.
              </strong>
              <br />
              We give you cryptographic proof. There's a difference.
            </p>
          </motion.div>

          {/* CTA */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mt-12 text-center"
          >
            <p className="text-alpine-text-primary font-semibold-textl-gmb-4">
              Don't trust promises. Download the proof.
            </p>
            <a
              href="/api/download-backtest"
              className="group relative inline-flex items-center justify-center gap-3 px-10 py-5 bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pinkhove-r:from-alpine-neon-pinkhove-r:to-alpine-neon-cyantext-white-fontblac-ktext-lgrounded-xlshadow-2xl shadow-alpine-neoncya-n/50 transform transition-all duration-300 hover:scale-105"
            >
              <span className="relative z-10 flex items-center gap-3">
                <Download className="w-6 h-6" />
                Download 20-Year Backtest Data
              </span>
            </a>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

