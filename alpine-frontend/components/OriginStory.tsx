'use client'

import { motion } from 'framer-motion'
import { Calendar, TrendingDown, Code, Rocket } from 'lucide-react'

const timeline = [
  {
    period: '2019-2022',
    phase: 'Research Phase',
    icon: Code,
    items: [
      'Analyzed 50+ years of market data across regimes',
      'Identified 4 distinct market states',
      'Built regime detection algorithms',
      'Developed adaptive parameter systems',
    ],
  },
  {
    period: '2022',
    phase: 'The Test',
    icon: TrendingDown,
    items: [
      'When the 2022 bear market hit, traditional systems collapsed',
      'Our adaptive system? Profitable in the volatility',
    ],
  },
  {
    period: '2023-2024',
    phase: 'Refinement',
    icon: Code,
    items: [
      '10,000+ hours of optimization',
      'Multi-symbol validation',
      'Cryptographic verification system',
      'Production infrastructure buildout',
    ],
  },
  {
    period: '2025',
    phase: 'Public Launch',
    icon: Rocket,
    items: [
      'After proving it with our own capital for years',
      "we're offering it to serious traders",
    ],
  },
]

export default function OriginStory() {
  return (
    <section id="origin" className="bg-alpine-black-primary py-24 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(254,28,128,0.05),transparent_70%)]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto"
        >
          <h2 className="text-4xl sm:text-5xl font-bold text-alpine-text-primary mb-4 text-center">
            Built Over 3+ Years by Quantitative Traders
          </h2>

          <div className="space-y-6 text-lg text-alpine-text-primary leading-relaxed mb-12">
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              We're proprietary traders who spent years frustrated by static signal services.
            </motion.p>
          </div>

          {/* Timeline */}
          <div className="space-y-8">
            {timeline.map((item, index) => {
              const Icon = item.icon
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -30 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.2 }}
                  className="glassmorphism rounded-xl p-6 border-l-4 border-alpine-neon-pink"
                >
                  <div className="flex items-start space-x-4 mb-4">
                    <div className="w-12 h-12 rounded-lg bg-alpine-neon-pink/20 border border-alpine-neon-pink/30 flex items-center justify-center flex-shrink-0">
                      <Icon className="w-6 h-6 text-alpine-neon-pink" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="text-alpine-neon-pink font-bold text-lg">{item.period}</span>
                        <span className="text-alpine-neon-cyan font-semibold">{item.phase}</span>
                      </div>
                      <ul className="space-y-2 mt-3">
                        {item.items.map((bullet, i) => (
                          <li key={i} className="flex items-start">
                            <span className="text-alpine-neon-pink mr-3 mt-1">•</span>
                            <span className="text-alpine-text-secondary">{bullet}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.8 }}
            className="mt-12 pt-8 border-t border-alpine-neon-cyan/20 text-center"
          >
            <p className="text-2xl font-bold text-alpine-text-primary mb-2">This isn't a side project.</p>
            <p className="text-xl text-alpine-neon-pink font-semibold">It's our livelihood.</p>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
