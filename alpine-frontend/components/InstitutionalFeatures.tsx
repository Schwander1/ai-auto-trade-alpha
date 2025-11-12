'use client'

import { motion } from 'framer-motion'
import { Calculator, Shield, BarChart3, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function InstitutionalFeatures() {
  return (
    <section className="bg-black py-24 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(176,38,255,0.05),transparent_70%)]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-bold text-ice-blue text-center mb-4"
        >
          Advanced Position Sizing{' '}
          <span className="text-neon-pink">(Institutional Tier)</span>
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-xl text-ice-blue/70 text-center mb-12"
        >
          For Professional Traders
        </motion.p>

        <div className="max-w-4xl mx-auto space-y-8 mb-12">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="glassmorphism rounded-xl p-8 border-2 border-neon-pink/30"
          >
            <div className="flex items-center space-x-3 mb-6">
              <Calculator className="w-8 h-8 text-neon-pink" />
              <h3 className="text-2xl font-bold text-ice-blue">Kelly Criterion Position Sizing Models</h3>
            </div>
            <ul className="space-y-3 text-ice-blue/90">
              <li className="flex items-start">
                <span className="text-neon-pink mr-3 mt-1">•</span>
                <span>Optimal position sizing based on win rate and reward/risk</span>
              </li>
              <li className="flex items-start">
                <span className="text-neon-pink mr-3 mt-1">•</span>
                <span>Half-Kelly conservative approach (recommended)</span>
              </li>
              <li className="flex items-start">
                <span className="text-neon-pink mr-3 mt-1">•</span>
                <span>Full methodology and assumptions</span>
              </li>
              <li className="flex items-start">
                <span className="text-neon-pink mr-3 mt-1">•</span>
                <span>Backtested portfolio simulations</span>
              </li>
              <li className="flex items-start">
                <span className="text-neon-pink mr-3 mt-1">•</span>
                <span>Expected value calculations</span>
              </li>
            </ul>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="glassmorphism rounded-xl p-8 border-2 border-electric-cyan/30"
          >
            <div className="flex items-center space-x-3 mb-6">
              <Shield className="w-8 h-8 text-electric-cyan" />
              <h3 className="text-2xl font-bold text-ice-blue">Advanced Risk Management Tools</h3>
            </div>
            <ul className="space-y-3 text-ice-blue/90">
              <li className="flex items-start">
                <span className="text-electric-cyan mr-3 mt-1">•</span>
                <span>Drawdown analysis</span>
              </li>
              <li className="flex items-start">
                <span className="text-electric-cyan mr-3 mt-1">•</span>
                <span>Portfolio heat mapping</span>
              </li>
              <li className="flex items-start">
                <span className="text-electric-cyan mr-3 mt-1">•</span>
                <span>Correlation-based position limits</span>
              </li>
              <li className="flex items-start">
                <span className="text-electric-cyan mr-3 mt-1">•</span>
                <span>Monthly compounding models</span>
              </li>
            </ul>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="glassmorphism rounded-xl p-8 border-2 border-laser-green/30"
          >
            <div className="flex items-center space-x-3 mb-6">
              <BarChart3 className="w-8 h-8 text-laser-green" />
              <h3 className="text-2xl font-bold text-ice-blue">Historical Performance Simulations</h3>
            </div>
            <ul className="space-y-3 text-ice-blue/90">
              <li className="flex items-start">
                <span className="text-laser-green mr-3 mt-1">•</span>
                <span>20-year backtested scenarios</span>
              </li>
              <li className="flex items-start">
                <span className="text-laser-green mr-3 mt-1">•</span>
                <span>Multiple position sizing strategies</span>
              </li>
              <li className="flex items-start">
                <span className="text-laser-green mr-3 mt-1">•</span>
                <span>Risk-adjusted return metrics</span>
              </li>
              <li className="flex items-start">
                <span className="text-laser-green mr-3 mt-1">•</span>
                <span>Detailed performance attribution</span>
              </li>
            </ul>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="glassmorphism rounded-xl p-8 border-2 border-warning-red/30 max-w-4xl mx-auto mb-8"
        >
          <div className="flex items-start space-x-4">
            <AlertTriangle className="w-8 h-8 text-warning-red flex-shrink-0 mt-1" />
            <div>
              <p className="text-ice-blue/90 leading-relaxed mb-2">
                <strong className="text-warning-red">⚠️ All simulations are based on historical backtests</strong> and do not guarantee future performance.
              </p>
              <p className="text-ice-blue/90 leading-relaxed">
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

