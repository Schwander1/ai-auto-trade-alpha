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
    color: 'neon-pink',
  },
  {
    number: '2',
    icon: Target,
    title: 'Confidence Scoring',
    description: '0-100 on every signal',
    subtext: 'Our 58.5% is the average. High-confidence (85%+) signals win 70%+.',
    color: 'neon-pink',
  },
  {
    number: '3',
    icon: CheckCircle2,
    title: 'Multi-Source Validation',
    description: 'Aggregated data feeds',
    subtext: 'Cross-validated before signals are sent.',
    color: 'electric-cyan',
  },
  {
    number: '4',
    icon: TrendingUp,
    title: 'Regime-Optimized',
    description: 'Different strategies for different markets',
    subtext: 'Bull strategies in bulls. Bear strategies in bears.',
    color: 'laser-green',
  },
  {
    number: '5',
    icon: Calculator,
    title: 'Clear Edge Required',
    description: 'We only trade when probability is in our favor',
    subtext: 'No gambling. No hope. Just math.',
    color: 'neon-purple',
  },
]

const iconColors = {
  'neon-pink': 'text-neon-pink border-neon-pink/30',
  'electric-cyan': 'text-electric-cyan border-electric-cyan/30',
  'laser-green': 'text-laser-green border-laser-green/30',
  'neon-purple': 'text-neon-purple border-neon-purple/30',
}

export default function OurEdge() {
  return (
    <section className="bg-black py-24 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,240,255,0.05),transparent_70%)]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-bold text-ice-blue text-center mb-16"
        >
          Why Alpine Signals{' '}
          <span className="text-neon-pink">Win More Often</span>
        </motion.h2>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {edges.map((edge, index) => {
            const Icon = edge.icon
            const borderColor = iconColors[edge.color as keyof typeof iconColors]
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className={`glassmorphism rounded-xl p-6 border-2 ${borderColor} hover:border-opacity-100 transition-all`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="text-4xl font-bold font-mono text-ice-blue/20">
                    {edge.number}
                  </div>
                  <Icon className={`w-8 h-8 ${edge.color === 'neon-pink' ? 'text-neon-pink' : edge.color === 'electric-cyan' ? 'text-electric-cyan' : edge.color === 'laser-green' ? 'text-laser-green' : 'text-neon-purple'}`} />
                </div>
                <h3 className="text-xl font-bold text-ice-blue mb-2">{edge.title}</h3>
                <p className="text-ice-blue/80 font-semibold mb-2">{edge.description}</p>
                <p className="text-ice-blue/70 text-sm leading-relaxed">{edge.subtext}</p>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

