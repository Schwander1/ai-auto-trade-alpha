'use client'

import { motion } from 'framer-motion'
import { Target, FileText, TrendingUp, Clock, Eye } from 'lucide-react'

const signalFeatures = [
  {
    icon: Target,
    title: 'Confidence Score (0-100)',
    description: 'Our signals average 90.5 confidence',
    color: 'alpine-neon-pink',
  },
  {
    icon: TrendingUp,
    title: 'Win Rate by Regime',
    description: '66% Bulls, 55-57% Bears/Chop/Crisis',
    color: 'alpine-neon-cyan',
  },
  {
    icon: Target,
    title: 'Entry, Target, Stop',
    description: 'Complete trade plan',
    color: 'alpine-semantic-success',
  },
  {
    icon: FileText,
    title: 'Detailed Reasoning',
    description: "Know exactly why we're entering",
    color: 'alpine-neon-purple',
  },
  {
    icon: Clock,
    title: 'Hold Time Estimate',
    description: 'Plan your commitment',
    color: 'alpine-semantic-error',
  },
  {
    icon: Eye,
    title: 'Market Regime',
    description: 'Context matters',
    color: 'alpine-neon-cyan',
  },
]

const iconColors = {
  'alpine-neon-pink': 'text-alpine-neon-pink',
  'alpine-neon-cyan': 'text-alpine-neon-cyan',
  'alpine-semantic-success': 'text-alpine-semantic-success',
  'alpine-neon-purple': 'text-alpine-neon-purple',
  'alpine-semantic-error': 'text-alpine-semantic-error',
}

export default function HighConfidenceSignals() {
  return (
    <section className="bg-alpine-black-primary py-24 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(254,28,128,0.05),transparent_70%)]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl sm:text-5xl font-bold text-alpine-text-primary mb-4 font-heading">
            High-Confidence Signals Only
          </h2>
          <p className="text-xl text-alpine-text-secondary max-w-3xl mx-auto mb-4">
            We don't spam. We're selective.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto mb-12">
          {signalFeatures.map((feature, index) => {
            const Icon = feature.icon
            const iconColor = iconColors[feature.color as keyof typeof iconColors]
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="card-neon rounded-xl p-6 border border-alpine-neon-cyan/20 hover:border-alpine-neonpin-k/50 transition-all text-center"
              >
                <Icon className={`w-8 h-8 ${iconColor} mx-auto mb-4`} />
                <h3 className="text-lg font-bold text-alpine-text-primary mb-2 font-heading">{feature.title}</h3>
                <p className="text-alpine-text-secondary text-sm">{feature.description}</p>
              </motion.div>
            )
          })}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="space-y-4 max-w-4xl mx-auto"
        >
          <div className="card-neon rounded-xl p-6 border-2 border-alpine-neonpin-k/30 text-center">
            <p className="text-lg text-alpine-text-primary font-semibold mb-2">
              You decide position sizing based on{' '}
              <span className="text-alpine-neon-pink">YOUR risk tolerance</span>.
            </p>
          </div>
          <div className="card-neon rounded-xl p-6 border border-alpine-neon-cyan/20">
            <p className="text-alpine-text-primary leading-relaxed mb-2">
              Our <span className="text-alpine-neon-pink font-semibold">58.5% average</span> includes ALL signals.
            </p>
            <p className="text-alpine-text-primary leading-relaxed">
              <span className="text-alpine-neon-pink font-semibold">High-confidence signals (85%+)</span> have historically performed better.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

