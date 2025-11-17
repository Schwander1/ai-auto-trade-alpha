'use client'

import { motion } from 'framer-motion'
import { Download } from 'lucide-react'

export default function TheProof() {
  return (
    <section id="proof" className="bg-alpine-dark py-24 relative overflow-hidden">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-4xl md:text-6xl font-display font-black text-white text-center mb-16"
        >
          Others Sell Hope.{' '}
          <span className="text-alpine-accent">We Deliver Proof.</span>
        </motion.h2>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-12">
          {/* Column 1 */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="bg-alpine-card rounded-xl p-8 border border-alpine-border"
          >
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-2xl font-display font-bold text-alpine-text mb-4">20-Year Backtested Performance</h3>
            <p className="text-alpine-text-dim leading-relaxed mb-4">
              4,374 signals from 2006-2025 backtest. +565% return, 9.94% CAGR. Now launching live with SHA-256 verification. Download backtest data to analyze yourself.
            </p>
            <p className="text-alpine-text-dim text-sm">
              <strong className="text-alpine-accent">Live verification starts Wednesday, Nov 12 at 9:00 AM ET.</strong>
            </p>
          </motion.div>

          {/* Column 2 */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="bg-alpine-card rounded-xl p-8 border border-alpine-border"
          >
            <div className="text-4xl mb-4">📈</div>
            <h3 className="text-2xl font-display font-bold text-alpine-text mb-4">Beat SPY by 165%</h3>
            <div className="space-y-3 mb-4">
              <div className="flex justify-between items-center">
                <span className="text-alpine-text-dim">SPY:</span>
                <span className="text-alpine-text font-semibold">+400% (8.5% CAGR)</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-alpine-text-dim">Alpine:</span>
                <span className="text-alpine-accent font-bold text-lg">+565% (9.94% CAGR)</span>
              </div>
            </div>
            <p className="text-alpine-text-dim text-sm">
              SPY: +400% (8.5% CAGR) | Alpine: +565% (9.94% CAGR). Same 20-year period. Backtested with real market data. Live verification starts Wednesday, Nov 12 at 9:00 AM ET.
            </p>
          </motion.div>

          {/* Column 3 */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="bg-alpine-card rounded-xl p-8 border border-alpine-border"
          >
            <div className="text-4xl mb-4">🔍</div>
            <h3 className="text-2xl font-display font-bold text-alpine-text mb-4">Complete Transparency</h3>
            <p className="text-alpine-text-dim leading-relaxed mb-4">
              Our 20-year backtest: 45.2% win rate, +565% return. We show every trade - wins AND losses. Launching Nov 12 at 9:00 AM ET, every LIVE signal will be SHA-256 verified. All signals include confidence scores (87-98% range), proving our system only triggers when strong criteria align.
            </p>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <a
            href="/api/download-backtest"
            className="group relative inline-flex items-center justify-center gap-3 px-10 py-5 bg-gradient-to-r from-alpine-accent to-alpine-pink hover:from-alpine-pink hover:to-alpine-accent text-white font-black text-lg rounded-xl shadow-2xl shadow-alpine-accent/50 transform transition-all duration-300 hover:scale-105"
          >
            <span className="relative z-10 flex items-center gap-3">
              <Download className="w-6 h-6" />
              Download 20-Year Backtest Data (CSV)
            </span>
          </a>
        </motion.div>
      </div>
    </section>
  )
}

