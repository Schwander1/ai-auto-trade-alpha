'use client'

import { motion } from 'framer-motion'
import { Check, X } from 'lucide-react'

const comparisons = [
  {
    feature: 'Win Rate',
    alpine: '58.5% (verified)',
    industry: '35-45% (claimed)',
    alpineCheck: true,
  },
  {
    feature: 'Strategy',
    alpine: 'Adaptive (4 regimes)',
    industry: 'Static',
    alpineCheck: true,
  },
  {
    feature: 'Data',
    alpine: '20 years shown',
    industry: 'Cherry-picked periods',
    alpineCheck: true,
  },
  {
    feature: 'Proof',
    alpine: 'Cryptographic',
    industry: 'Self-reported',
    alpineCheck: true,
  },
  {
    feature: 'Infrastructure',
    alpine: 'Enterprise-grade',
    industry: 'Basic',
    alpineCheck: true,
  },
  {
    feature: 'Development',
    alpine: '3+ years R&D',
    industry: 'Quick launch',
    alpineCheck: true,
  },
  {
    feature: 'Pricing',
    alpine: '$97-797/mo',
    industry: '$500-3,000/mo',
    alpineCheck: true,
  },
]

export default function Comparison() {
  return (
    <section className="bg-alpine-black-primary py-24">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-bold text-alpine-text-primary text-center mb-16 font-heading"
        >
          Alpine vs Industry
        </motion.h2>

        <div className="card-neon rounded-2xl overflow-hidden border-alpine-neon-cyan/30 max-w-4xl mx-auto">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-alpine-black-secondary border-b-border-alpine-neon-cyan/20">
                <tr>
                  <th className="px-6 py-4 text-left font-semibold text-alpine-text-primary ">Feature</th>
                  <th className="px-6 py-4 text-left font-semibold text-alpine-neon-pink">Alpine Analytics</th>
                  <th className="px-6 py-4 text-left font-semibold text-alpine-text-secondary">
                    Industry Average
                  </th>
                </tr>
              </thead>
              <tbody>
                {comparisons.map((comp, index) => (
                  <motion.tr
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.4, delay: index * 0.05 }}
                    className="border-b border-alpine-neon-cyan/10 last:border-0 hover:bg-alpine-black-secondary/50 transition-colors"
                  >
                    <td className="px-6 py-4 font-semibold text-alpine-text-primary ">{comp.feature}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <Check className="w-5 h-5 text-alpine-semantic-success" />
                        <span className="text-alpine-neon-pink font-medium">{comp.alpine}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <X className="w-5 h-5 text-alpine-semantic-error" />
                        <span className="text-alpine-text-secondary">{comp.industry}</span>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  )
}
