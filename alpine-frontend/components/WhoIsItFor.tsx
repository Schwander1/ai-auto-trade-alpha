'use client'

import { motion } from 'framer-motion'
import { Check, X, TrendingUp } from 'lucide-react'

export default function WhoIsItFor() {
  return (
    <section className="bg-alpine-black-primary py-24 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(24,224,255,0.05),transparent_70%)]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-bold text-alpine-text-primary text-center mb-16 font-heading"
        >
          Who Alpine Is For{' '}
          <span className="text-alpine-neon-cyan">(And Who It's Not For)</span>
        </motion.h2>

        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto mb-16">
          {/* Perfect For */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="card-neon rounded-xl p-8 border-2 border-alpine-semanticsucces-s/30"
          >
            <div className="flex items-center space-x-3 mb-6">
              <Check className="w-8 h-8 text-alpine-semantic-success" />
              <h3 className="text-2xl font-bold text-alpine-text-primary font-heading">Perfect For</h3>
            </div>
            <ul className="space-y-4">
              <li className="flex items-start">
                <span className="text-alpine-semantic-successm-r-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">Swing traders holding positions 2-10 days</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-semantic-successm-r-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">
                  Traders who want consistent signals without constant screen time
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-semantic-successm-r-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">
                  Investors seeking higher win rates than traditional strategies
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-semantic-successm-r-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">
                  Traders comfortable with 4-8 signals per month (not day trading)
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-semantic-successm-r-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">
                  Those who value transparency over hype
                </span>
              </li>
            </ul>
          </motion.div>

          {/* Not Perfect For */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="card-neon rounded-xl p-8 border-2 border-alpine-semantic-error/30"
          >
            <div className="flex items-center space-x-3 mb-6">
              <X className="w-8 h-8 text-alpine-semantic-error" />
              <h3 className="text-2xl font-bold text-alpine-text-primary font-heading">Not Perfect For</h3>
            </div>
            <ul className="space-y-4">
              <li className="flex items-start">
                <span className="text-alpine-semantic-error mr-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">Day traders seeking 100+ trades per week</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-semantic-error mr-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">
                  Those expecting Renaissance-level returns (we're not them)
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-semantic-error mr-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">
                  Set-it-and-forget-it passive investors (you need to execute signals)
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-semantic-error mr-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">
                  Traders looking for 1000% annual gains
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-semantic-error mr-3 mt-1">•</span>
                <span className="text-alpine-text-primary ">
                  Those who can't handle occasional losing trades
                </span>
              </li>
            </ul>
          </motion.div>
        </div>

        {/* Renaissance Comparison */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="card-neon rounded-xl p-8 border-2 border-alpine-neonpin-k/30 max-w-4xl mx-auto"
        >
          <div className="flex items-center space-x-3 mb-6">
            <TrendingUp className="w-8 h-8 text-alpine-neon-pink" />
            <h3 className="text-2xl font-bold text-alpine-text-primary font-heading">
              We're Not Renaissance (And We Don't Pretend to Be)
            </h3>
          </div>
          <div className="space-y-4 text-alpine-text-primary /90 leading-relaxed">
            <p>
              Renaissance Medallion makes 66% annual returns with high-frequency statistical
              arbitrage, billions in capital, and hundreds of PhDs.
            </p>
            <p>
              We're swing traders who catch directional moves by adapting to market regimes.{' '}
              <span className="text-alpine-neon-cyan font-semibold">
                Different game, different edge.
              </span>
            </p>
            <div className="grid md:grid-cols-2 gap-6 mt-6 pt-6 border-t border-alpine-neon-cyan/20">
              <div>
                <div className="text-alpine-neon-pink font-semibold mb-2">Our edge:</div>
                <div className="text-alpine-text-primary/80">
                  Higher win rate through regime adaptation.
                </div>
              </div>
              <div>
                <div className="text-alpine-neon-cyan font-semibold-mb-2">Their edge:</div>
                <div className="text-alpine-text-primary/80">
                  Millions of tiny statistical edges compounded daily.
                </div>
              </div>
            </div>
            <p className="text-lg font-semibold text-alpine-neon-pinkm-t-6 pt-6 border-t border-alpine-neon-cyan/20">
              We're honest about what we do and don't do.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

