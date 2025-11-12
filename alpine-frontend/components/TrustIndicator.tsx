'use client'

import { motion } from 'framer-motion'
import { AlertTriangle } from 'lucide-react'

export default function TrustIndicator() {
  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.6 }}
      className="py-12 bg-alpine-orange/10 border-y border-alpine-orange/30"
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-center space-x-4 max-w-4xl mx-auto">
          <AlertTriangle className="w-8 h-8 text-alpine-orange flex-shrink-0" />
          <div className="text-center">
            <p className="text-alpine-text font-semibold text-lg">
              ⚠️ <span className="text-alpine-orange">45.2% win rate on 87-98% confidence signals</span>. We're selective, not spammy. But we're profitable.
            </p>
            <p className="text-alpine-text-dim text-sm mt-2">
              And you can verify every single trade. All signals include confidence scores (87-98% range).
            </p>
          </div>
        </div>
      </div>
    </motion.section>
  )
}

