'use client'

import { motion } from 'framer-motion'
import { X, TrendingDown, FileX, AlertTriangle } from 'lucide-react'

const problems = [
  {
    icon: TrendingDown,
    title: 'One Strategy for All Markets',
    description:
      'Other services use the same RSI 40-70 in both bull runs and crashes. Would you drive the same speed in sunshine and blizzard?',
    color: 'alpine-semantic-error',
  },
  {
    icon: FileX,
    title: 'Cherry-Picked Results',
    description:
      'Show only their best 6 months. Hide the 2022 bear market. We show ALL 20 years of data.',
    color: 'alpine-semantic-error',
  },
  {
    icon: AlertTriangle,
    title: 'No Proof, Just Marketing',
    description:
      'Fake testimonials, no verification. Anyone can claim 80% win rate. We cryptographically verify every signal.',
    color: 'alpine-semantic-error',
  },
]

export default function Problem() {
  return (
    <section className="bg-alpine-black-primary py-24 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,45,85,0.05),transparent_70%)]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-bold text-alpine-text-primary text-center mb-16 font-heading"
        >
          Why Many Signal Services{' '}
          <span className="text-alpine-semantic-error">Fail You</span>
        </motion.h2>

        <div className="grid md:grid-cols-3 gap-8">
          {problems.map((problem, index) => {
            const Icon = problem.icon
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="card-neon rounded-xl p-8 border-alpine-semantic-error/30 hover:border-alpine-semantic-error/50 transition-all"
              >
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 rounded-lg bg-alpine-semantic-error/20 flex items-center justify-center border border-alpine-semantic-error/30">
                      <Icon className="w-6 h-6 text-alpine-semantic-error" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-alpine-text-primary mb-3 font-heading">{problem.title}</h3>
                    <p className="text-alpine-text-secondary leading-relaxed">{problem.description}</p>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
