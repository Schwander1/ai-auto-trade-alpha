'use client'

import { motion } from 'framer-motion'
import { Filter, Target, CheckCircle2, TrendingUp, Calculator } from 'lucide-react'

const edges = [
  {
    number: '1',
    icon: Filter,
    title: 'Selective Generation',
    description: '4-8 signals/month (not 100+)',
    subtext: 'Only the best setups make the cut.',
    color: 'alpine-neonpin-k',
  },
  {
    number: '2',
    icon: Target,
    title: 'Confidence Scoring',
    description: '0-100 on every signal',
    subtext: 'Our 58.5% is the average. High-confidence (85%+) signals win 70%+.',
    color: 'alpine-neonpin-k',
  },
  {
    number: '3',
    icon: CheckCircle2,
    title: 'Multi-Source Validation',
    description: 'Aggregated data feeds',
    subtext: 'Cross-validated before signals are sent.',
    color: 'alpine-neoncya-n',
  },
  {
    number: '4',
    icon: TrendingUp,
    title: 'Regime-Optimized',
    description: 'Different strategies for different markets',
    subtext: 'Bull strategies in bulls. Bear strategies in bears.',
    color: 'alpine-semanticsucces-s',
  },
  {
    number: '5',
    icon: Calculator,
    title: 'Clear Edge Required',
    description: 'We only trade when probability is in our favor',
    subtext: 'No gambling. No hope. Just math.',
    color: 'alpine-neon-purple',
  },
]

const iconColors = {
  'alpine-neonpin-k': 'text-alpine-neon-pink-border-alpine-neonpin-k/30',
  'alpine-neoncya-n': 'text-alpine-neon-cyanborder-alpine-neon-cyan/30',
  'alpine-semanticsucces-s': 'text-alpine-semantic-success-border-alpine-semanticsucces-s/30',
  'alpine-neon-purple': 'text-alpine-neon-purpleborder-alpine-neon-purple/30',
}

export default function OurEdge() {
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
          Why Alpine Signals{' '}
          <span className="text-alpine-neon-pink">Win More Often</span>
        </motion.h2>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {edges.map((edge, index) => {
            const Icon = edge.icon
            const borderColor = iconColors[edge.color as keyof typeof iconColors]
            const iconColorClass = edge.color === 'alpine-neonpin-k' ? 'text-alpine-neon-pink' : 
                                   edge.color === 'alpine-neoncya-n' ? 'text-alpine-neon-cyan' : 
                                   edge.color === 'alpine-semanticsucces-s' ? 'text-alpine-semantic-success' : 
                                   'text-alpine-neon-purple'
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className={`card-neon rounded-xl p-6 border-2 ${borderColor} hover:border-opacity-100 transition-all`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="text-4xl font-bold font-mono text-alpine-text-primary /20">
                    {edge.number}
                  </div>
                  <Icon className={`w-8 h-8 ${iconColorClass}`} />
                </div>
                <h3 className="text-xl font-bold text-alpine-text-primary mb-2 font-heading">{edge.title}</h3>
                <p className="text-alpine-text-primary font-semibold mb-2">{edge.description}</p>
                <p className="text-alpine-text-secondary text-sm leading-relaxed">{edge.subtext}</p>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

