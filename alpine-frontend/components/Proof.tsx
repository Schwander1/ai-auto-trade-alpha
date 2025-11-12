'use client'

import { motion } from 'framer-motion'
import { Download, Lock, AlertCircle } from 'lucide-react'

const stats = [
  { label: 'Years Tested', value: '20', subtext: '2006-2025' },
  { label: 'Average Win Rate', value: '58.5%', subtext: 'All conditions' },
  { label: 'High-Confidence Signals', value: '70%+', subtext: '85%+ confidence win rate', highlight: true },
  { label: 'Symbols Traded', value: '12', subtext: 'NVDA, TSLA, AAPL, MSFT, META, AMD, AMZN, NFLX, SPY, QQQ, COIN, MSTR' },
]

const events = [
  { year: 2008, event: 'Financial Crisis', color: 'warning-red' },
  { year: 2020, event: 'COVID Crash', color: 'warning-red' },
  { year: 2022, event: 'Bear Market', color: 'warning-red' },
]

export default function Proof() {
  return (
    <section id="proof" className="bg-space-gray py-24 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,0,110,0.05),transparent_70%)]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl sm:text-5xl font-bold text-ice-blue mb-4">
            Independently Verifiable Results
          </h2>
          <p className="text-xl text-ice-blue/70 max-w-3xl mx-auto mb-4">
            Every signal is timestamped and hashed. We can't fake the data even if we wanted to.
          </p>
          <p className="text-lg text-neon-pink font-semibold max-w-3xl mx-auto">
            Tested on 12,000+ trades. SHA-256 verified. No BS.
          </p>
        </motion.div>

        {/* Independently Verifiable Data */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="glassmorphism rounded-2xl p-8 mb-12 border-electric-cyan/30"
        >
          <h3 className="text-2xl font-bold text-ice-blue mb-6 text-center">
            Independently Verifiable Data
          </h3>
          <p className="text-ice-blue/70 text-center mb-6">
            Download Our Complete Signal History:
          </p>
          <ul className="space-y-3 mb-8 text-ice-blue/90">
            <li className="flex items-start">
              <span className="text-neon-pink mr-3 mt-1">•</span>
              <span><strong className="text-neon-pink">4,391 signals</strong> with SHA-256 hashes</span>
            </li>
            <li className="flex items-start">
              <span className="text-neon-pink mr-3 mt-1">•</span>
              <span>Confidence scores (average: <strong className="text-neon-pink">90.5</strong>)</span>
            </li>
            <li className="flex items-start">
              <span className="text-neon-pink mr-3 mt-1">•</span>
              <span>Entry, target, stop levels</span>
            </li>
            <li className="flex items-start">
              <span className="text-neon-pink mr-3 mt-1">•</span>
              <span>Regime classification</span>
            </li>
            <li className="flex items-start">
              <span className="text-neon-pink mr-3 mt-1">•</span>
              <span>Timestamps (cryptographically signed)</span>
            </li>
          </ul>
          <p className="text-ice-blue/90 text-center mb-6 font-semibold">
            Verify independently that our <span className="text-neon-pink">58.5% win rate</span> is accurate.
          </p>
          <p className="text-ice-blue/70 text-center mb-6 italic">
            We can't fake the data even if we wanted to.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="flex items-center justify-center space-x-2 bg-gradient-cta text-black px-6 py-3 rounded-lg font-semibold hover:scale-105 transition-transform shadow-glow-pink">
              <Download className="w-5 h-5" />
              <span>Download Signal Log (CSV)</span>
            </button>
            <button className="flex items-center justify-center space-x-2 border-2 border-electric-cyan text-electric-cyan px-6 py-3 rounded-lg font-semibold hover:bg-electric-cyan/10 transition-colors">
              <Lock className="w-5 h-5" />
              <span>Verify SHA-256 Hashes</span>
            </button>
          </div>
        </motion.div>

        {/* What We Don't Do */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="glassmorphism rounded-2xl p-8 mb-12 border-warning-red/30"
        >
          <div className="flex items-start space-x-4">
            <AlertCircle className="w-8 h-8 text-warning-red flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-ice-blue font-bold text-xl mb-4">What We Don't Do</h3>
              <ul className="space-y-3 text-ice-blue/70">
                <li className="flex items-start">
                  <span className="text-warning-red mr-3">✗</span>
                  <span>Don't hide losses - we show complete 20-year history</span>
                </li>
                <li className="flex items-start">
                  <span className="text-warning-red mr-3">✗</span>
                  <span>Don't cherry-pick - all periods included</span>
                </li>
                <li className="flex items-start">
                  <span className="text-warning-red mr-3">✗</span>
                  <span>Don't fake timestamps - SHA-256 verified</span>
                </li>
                <li className="flex items-start">
                  <span className="text-warning-red mr-3">✗</span>
                  <span>Don't make unverifiable claims - everything is auditable</span>
                </li>
              </ul>
            </div>
          </div>
        </motion.div>

        {/* Performance Chart Placeholder */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="glassmorphism rounded-2xl p-8 mb-12 border-electric-cyan/30"
        >
          <div className="h-64 flex items-end justify-between gap-2 mb-8">
            {Array.from({ length: 20 }).map((_, i) => {
              const height = 30 + Math.random() * 70
              const isEvent = events.some((e) => e.year === 2006 + i)
              return (
                <motion.div
                  key={i}
                  initial={{ height: 0 }}
                  whileInView={{ height: `${height}%` }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.05 }}
                  className={`flex-1 rounded-t ${
                    isEvent
                      ? 'bg-warning-red/50'
                      : i % 3 === 0
                        ? 'bg-laser-green/50'
                        : 'bg-neon-pink/50'
                  }`}
                />
              )
            })}
          </div>
          <div className="flex flex-wrap justify-center gap-6 text-sm">
            {events.map((event) => (
              <div key={event.year} className="flex items-center space-x-2 text-ice-blue/70">
                <div className={`w-3 h-3 rounded-full bg-${event.color}`} />
                <span className="font-semibold">{event.year}:</span>
                <span>{event.event}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className={`glassmorphism rounded-xl p-6 text-center ${
                stat.highlight
                  ? 'border-2 border-neon-pink/50 shadow-glow-pink'
                  : 'border-neon-pink/20'
              } ${index === 3 ? 'md:col-span-2 lg:col-span-1' : ''}`}
            >
              <div className="text-ice-blue/70 text-sm mb-2">{stat.label}</div>
              <div
                className={`text-4xl font-bold mb-1 ${
                  stat.highlight ? 'text-neon-pink' : 'text-neon-pink'
                }`}
              >
                {stat.value}
              </div>
              <div className="text-ice-blue/50 text-xs leading-relaxed">{stat.subtext}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
