'use client'

import { motion } from 'framer-motion'
import { Zap, Lock, Database, Server } from 'lucide-react'

const features = [
  {
    icon: Zap,
    title: 'Real-Time Processing',
    color: 'electric-cyan',
    items: [
      'Sub-100ms regime detection',
      'Distributed signal generation',
      'Blue-green deployment (zero downtime)',
      '99.9% uptime SLA',
    ],
  },
  {
    icon: Lock,
    title: 'Security & Verification',
    color: 'laser-green',
    items: [
      'SHA-256 cryptographic signing',
      'Immutable audit trails',
      'End-to-end encryption',
      'SOC 2 Type II compliant (in progress)',
    ],
  },
  {
    icon: Database,
    title: 'Data Infrastructure',
    color: 'neon-pink',
    items: [
      '20+ years historical data',
      'Real-time market feeds',
      'Multi-source validation',
      'Automated quality checks',
    ],
  },
  {
    icon: Server,
    title: 'Scalability',
    color: 'neon-purple',
    items: [
      'Microservices architecture',
      'Auto-scaling infrastructure',
      'Geographic redundancy',
      '<500ms global latency',
    ],
  },
]

const iconColors = {
  'electric-cyan': 'text-electric-cyan',
  'laser-green': 'text-laser-green',
  'neon-pink': 'text-neon-pink',
  'neon-purple': 'text-neon-purple',
}

const borderColors = {
  'electric-cyan': 'border-electric-cyan/30',
  'laser-green': 'border-laser-green/30',
  'neon-pink': 'border-neon-pink/30',
  'neon-purple': 'border-neon-purple/30',
}

export default function TechnicalInfrastructure() {
  return (
    <section className="bg-space-gray py-24 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,240,255,0.05),transparent_70%)]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-bold text-ice-blue text-center mb-4"
        >
          Enterprise-Grade Systems Built for Reliability
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center text-ice-blue/70 mb-12"
        >
          Technical details available to Institutional clients
        </motion.p>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            const iconColor = iconColors[feature.color as keyof typeof iconColors]
            const borderColor = borderColors[feature.color as keyof typeof borderColors]
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
                <div className="flex items-center space-x-3 mb-4">
                  <Icon className={`w-8 h-8 ${iconColor}`} />
                  <h3 className="text-xl font-bold text-ice-blue">{feature.title}</h3>
                </div>
                <ul className="space-y-2">
                  {feature.items.map((item, i) => (
                    <li key={i} className="flex items-start text-sm text-ice-blue/70">
                      <span className="text-electric-cyan mr-2 mt-1">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

