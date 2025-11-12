'use client'

import { motion } from 'framer-motion'
import { Clock, Mail, Smartphone, TrendingUp, User } from 'lucide-react'

const expectations = [
  {
    icon: TrendingUp,
    title: '4-8 signals per month average',
    description: 'Quality over quantity. We wait for high-probability setups.',
    color: 'neon-pink',
  },
  {
    icon: Clock,
    title: 'Hold time: 2-10 days per trade',
    description: 'Swing trading timeframe. Not day trading, not long-term investing.',
    color: 'electric-cyan',
  },
  {
    icon: Mail,
    title: 'Email + SMS notifications',
    description: 'Real-time alerts for Pro/Institutional. Email only for Starter.',
    color: 'laser-green',
  },
  {
    icon: User,
    title: 'Manual execution required',
    description: 'You place trades with your broker. We provide signals, you execute.',
    color: 'neon-purple',
  },
  {
    icon: Clock,
    title: '~15 minutes per signal',
    description: 'Time commitment: Review signal, check reasoning, place trade.',
    color: 'warning-red',
  },
]

const iconColors = {
  'neon-pink': 'text-neon-pink',
  'electric-cyan': 'text-electric-cyan',
  'laser-green': 'text-laser-green',
  'neon-purple': 'text-neon-purple',
  'warning-red': 'text-warning-red',
}

export default function WhatToExpect() {
  return (
    <section id="features" className="bg-black py-24 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,0,110,0.05),transparent_70%)]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-bold text-ice-blue text-center mb-16"
        >
          What to Expect
        </motion.h2>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {expectations.map((item, index) => {
            const Icon = item.icon
            const iconColor = iconColors[item.color as keyof typeof iconColors]
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="glassmorphism rounded-xl p-6 border border-electric-cyan/20 hover:border-neon-pink/50 transition-all"
              >
                <Icon className={`w-8 h-8 ${iconColor} mb-4`} />
                <h3 className="text-xl font-bold text-ice-blue mb-2">{item.title}</h3>
                <p className="text-ice-blue/70 text-sm leading-relaxed">{item.description}</p>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

