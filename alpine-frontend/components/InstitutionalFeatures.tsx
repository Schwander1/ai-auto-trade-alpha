'use client'

import { motion } from 'framer-motion'
import { Calculator, Shield, BarChart3, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function InstitutionalFeatures() {
  return (
    <section className="bg-alpine-black-primary py-24 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(150,0,255,0.05),transparent_70%)]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-bold text-alpine-text-primary text-center mb-4"
        >
          Advanced Position Sizing{' '}
          <span className="text-alpine-neon-pink">(Institutional Tier)</span>
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-xl text-alpine-text-secondary text-center mb-12"
        >
          For Professional Traders
        </motion.p>

        <div className="max-w-4xl mx-auto space-y-8 mb-12">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="glassmorphism rounded-xl p-8 border-2 border-alpine-neon-pink/30"
          >
            <div className="flex items-center space-x-3 mb-6">
              <Calculator className="w-8 h-8 text-alpine-neon-pink" />
              <h3 className="text-2xl font-bold text-alpine-text-primary">Kelly Criterion Position Sizing Models</h3>
            </div>
            <ul className="space-y-3 text-alpine-text-primary">
              <li className="flex items-start">
                <span className="text-alpine-neon-pink mr-3 mt-1">•</span>
                <span>Optimal position sizing based on win rate and reward/risk</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-neon-pink mr-3 mt-1">•</span>
                <span>Half-Kelly conservative approach (recommended)</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-neon-pink mr-3 mt-1">•</span>
                <span>Full methodology and assumptions</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-neon-pink mr-3 mt-1">•</span>
                <span>Backtested portfolio simulations</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-neon-pink mr-3 mt-1">•</span>
                <span>Expected value calculations</span>
              </li>
            </ul>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="glassmorphism rounded-xl p-8 border-2 border-alpine-neon-cyan/30"
          >
            <div className="flex items-center space-x-3 mb-6">
              <Shield className="w-8 h-8 text-alpine-neon-cyan" />
              <h3 className="text-2xl font-bold text-alpine-text-primary">Advanced Risk Management Tools</h3>
            </div>
            <ul className="space-y-3 text-alpine-text-primary">
              <li className="flex items-start">
                <span className="text-alpine-neon-cyan mr-3 mt-1">•</span>
                <span>Drawdown analysis</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-neon-cyan mr-3 mt-1">•</span>
                <span>Portfolio heat mapping</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-neon-cyan mr-3 mt-1">•</span>
                <span>Correlation-based position limits</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-neon-cyan mr-3 mt-1">•</span>
                <span>Monthly compounding models</span>
              </li>
            </ul>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="glassmorphism rounded-xl p-8 border-2 border-alpine-semantic-success/30"
          >
            <div className="flex items-center space-x-3 mb-6">
              <BarChart3 className="w-8 h-8 text-alpine-semantic-success" />
              <h3 className="text-2xl font-bold text-alpine-text-primary">Historical Performance Simulations</h3>
            </div>
            <ul className="space-y-3 text-alpine-text-primary">
              <li className="flex items-start">
                <span className="text-alpine-semantic-success mr-3 mt-1">•</span>
                <span>20-year backtested scenarios</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-semantic-success mr-3 mt-1">•</span>
                <span>Multiple position sizing strategies</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-semantic-success mr-3 mt-1">•</span>
                <span>Risk-adjusted return metrics</span>
              </li>
              <li className="flex items-start">
                <span className="text-alpine-semantic-success mr-3 mt-1">•</span>
                <span>Detailed performance attribution</span>
              </li>
            </ul>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="glassmorphism rounded-xl p-8 border-2 border-alpine-semantic-error/30 max-w-4xl mx-auto mb-8"
        >
          <div className="flex items-start space-x-4">
            <AlertTriangle className="w-8 h-8 text-alpine-semantic-error flex-shrink-0 mt-1" />
            <div>
              <p className="text-alpine-text-primary leading-relaxed mb-2">
                <strong className="text-alpine-semantic-error">⚠️ All simulations are based on historical backtests</strong> and do not guarantee future performance.
              </p>
              <p className="text-alpine-text-primary leading-relaxed">
                Institutional tier is for professional traders who understand advanced risk management concepts.
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <Button
            size="lg"
            className="bg-gradient-cta text-black font-bold text-lg px-8 py-6 shadow-glow-pink hover:scale-105 transition-transform"
            onClick={() => {
              const pricing = document.getElementById('pricing')
              pricing?.scrollIntoView({ behavior: 'smooth' })
            }}
          >
            Request Institutional Access
          </Button>
        </motion.div>
      </div>
    </section>
  )
}

