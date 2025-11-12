'use client'

import { motion } from 'framer-motion'
import { Quote } from 'lucide-react'

const testimonials = [
  {
    quote:
      'Finally, a service that shows their actual data. The SHA-256 verification is brilliant.',
    author: 'Mark T.',
    role: 'Professional Trader',
  },
  {
    quote:
      "I've tried 5 other signal services. Alpine is the only one that actually adapts to market conditions.",
    author: 'Sarah K.',
    role: 'Swing Trader',
  },
  {
    quote:
      "The transparency is refreshing. They don't hide their losing trades like everyone else.",
    author: 'James R.',
    role: 'Retail Trader',
  },
]

export default function SocialProof() {
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
          className="text-4xl sm:text-5xl font-bold text-ice-blue text-center mb-16"
        >
          What Traders Are Saying
        </motion.h2>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="glassmorphism rounded-xl p-8 border border-electric-cyan/20"
            >
              <Quote className="w-8 h-8 text-neon-pink mb-4" />
              <p className="text-ice-blue text-lg mb-6 leading-relaxed">
                "{testimonial.quote}"
              </p>
              <div>
                <div className="font-semibold text-ice-blue">{testimonial.author}</div>
                <div className="text-ice-blue/70 text-sm">{testimonial.role}</div>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center text-ice-blue/60 text-sm italic max-w-3xl mx-auto"
        >
          Note: Testimonials reflect individual experiences. Past performance does not guarantee
          future results.
        </motion.p>
      </div>
    </section>
  )
}
