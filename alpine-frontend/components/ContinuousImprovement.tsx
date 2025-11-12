'use client'

import { motion } from 'framer-motion'
import SignalSelectivity from './SignalSelectivity'

export default function ContinuousImprovement() {
  return (
    <section className="py-20 bg-alpine-darker">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-6xl font-display font-black text-white mb-4">
            Always Improving. <span className="bg-gradient-to-r from-alpine-accent to-alpine-pink bg-clip-text text-transparent">Cryptographically Proven.</span>
          </h2>
          <p className="text-xl text-alpine-text-dim max-w-3xl mx-auto">
            Many signal services are static. We iterate weekly. And every change is verifiable.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {/* Card 1: Rapid Iteration */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0 }}
            className="bg-alpine-card border border-alpine-border rounded-lg p-8"
          >
            <div className="w-12 h-12 bg-alpine-accent/10 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">⚡</span>
            </div>
            <h3 className="text-xl font-display font-bold text-alpine-text mb-3">
              Weekly Updates
            </h3>
            <p className="text-alpine-text-dim mb-4">
              Traditional hedge funds update strategies quarterly or annually.
            </p>
            <p className="text-alpine-text">
              We iterate <strong className="text-alpine-accent">weekly</strong>. Test new indicators.
              Refine entry logic. Optimize position sizing. Ship improvements fast.
            </p>
          </motion.div>

          {/* Card 2: Transparent Testing */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.15 }}
            className="bg-alpine-card border border-alpine-border rounded-lg p-8"
          >
            <div className="w-12 h-12 bg-alpine-accent/10 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">🔬</span>
            </div>
            <h3 className="text-xl font-display font-bold text-alpine-text mb-3">
              Live Testing
            </h3>
            <p className="text-alpine-text-dim mb-4">
              Every strategy improvement is deployed live and tracked separately.
            </p>
            <p className="text-alpine-text">
              We label each signal with its <strong className="text-alpine-accent">strategy version</strong> (v1.0, v1.1, v2.0...).
              Compare versions side-by-side. See what's working. All verified.
            </p>
          </motion.div>

          {/* Card 3: Better Over Time */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="bg-alpine-card border border-alpine-border rounded-lg p-8"
          >
            <div className="w-12 h-12 bg-alpine-accent/10 rounded-lg flex items-center justify-center mb-4">
              <span className="text-2xl">📈</span>
            </div>
            <h3 className="text-xl font-display font-bold text-alpine-text mb-3">
              Performance Compounds
            </h3>
            <p className="text-alpine-text-dim mb-4">
              More subscribers = more revenue = more R&D budget = better signals.
            </p>
            <p className="text-alpine-text">
              Your subscription <strong className="text-alpine-accent">funds improvements</strong> that benefit everyone.
              Better infrastructure. More compute. Smarter algorithms. Continuous evolution.
            </p>
          </motion.div>
        </div>

        {/* How It Works Timeline */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="bg-gradient-to-r from-alpine-accent/10 via-alpine-pink/10 to-alpine-blue/10 border border-alpine-accent/30 rounded-xl p-8"
        >
          <h3 className="text-2xl font-display font-bold text-alpine-text mb-6 text-center">
            How Rapid Iteration Works
          </h3>

          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-alpine-accent text-alpine-darker rounded-full flex items-center justify-center font-bold">
                1
              </div>
              <div>
                <p className="text-alpine-text font-semibold">Deploy Strategy v1.0</p>
                <p className="text-alpine-text-dim text-sm">November 12, 2025 at 9:00 AM ET: Launch with multi-regime system</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-alpine-accent text-alpine-darker rounded-full flex items-center justify-center font-bold">
                2
              </div>
              <div>
                <p className="text-alpine-text font-semibold">Collect Live Data</p>
                <p className="text-alpine-text-dim text-sm">Track every signal. Analyze what works. Identify improvements.</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-alpine-accent text-alpine-darker rounded-full flex items-center justify-center font-bold">
                3
              </div>
              <div>
                <p className="text-alpine-text font-semibold">Test Enhancement</p>
                <p className="text-alpine-text-dim text-sm">Develop Strategy v1.1. Backtest on recent data. Validate improvement.</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-alpine-accent text-alpine-darker rounded-full flex items-center justify-center font-bold">
                4
              </div>
              <div>
                <p className="text-alpine-text font-semibold">Deploy & Verify</p>
                <p className="text-alpine-text-dim text-sm">Ship v1.1 to production. All signals SHA-256 signed. Compare v1.0 vs v1.1 live.</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-alpine-accent text-alpine-darker rounded-full flex items-center justify-center font-bold">
                5
              </div>
              <div>
                <p className="text-alpine-text font-semibold">Repeat Weekly</p>
                <p className="text-alpine-text-dim text-sm">v1.2, v1.3, v2.0... Continuous improvement. Never stop optimizing.</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Signal Selectivity Card */}
        <SignalSelectivity />

        {/* The Difference */}
        <div className="mt-12 text-center">
          <p className="text-lg text-alpine-text-dim mb-2">
            In 1 year, we'll have deployed <strong className="text-alpine-accent">50+ strategy versions</strong>.
          </p>
          <p className="text-lg text-alpine-text-dim">
            Traditional funds? Maybe 2-4 updates per year.
          </p>
          <p className="text-xl text-alpine-text mt-4">
            <strong className="text-alpine-accent">Speed + Verification = Unfair Advantage</strong>
          </p>
        </div>
      </div>
    </section>
  )
}

