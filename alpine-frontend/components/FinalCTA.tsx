'use client'

import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Shield, Lock, CheckCircle } from 'lucide-react'

export default function FinalCTA() {
  return (
    <section className="bg-black py-24 relative overflow-hidden">
      {/* Animated Starfield Background */}
      <div className="absolute inset-0">
        {Array.from({ length: 50 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-electric-cyan rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 2}s`,
            }}
          />
        ))}
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-3xl mx-auto"
        >
          <h2 className="text-4xl sm:text-5xl font-bold text-ice-blue mb-4">
            Ready to Trade Smarter?
          </h2>
          <p className="text-xl text-ice-blue/70 mb-8">
            Join the future of adaptive trading
          </p>

          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="mb-8"
          >
            <Button
              size="lg"
              className="bg-gradient-cta text-black font-bold text-lg px-12 py-6 shadow-glow-cyan animate-pulse-glow-cyan"
              onClick={() => {
                const pricing = document.getElementById('pricing')
                pricing?.scrollIntoView({ behavior: 'smooth' })
              }}
            >
              Start Your 7-Day Free Trial
            </Button>
          </motion.div>

          <p className="text-ice-blue/70 mb-8">
            No credit card • Cancel anytime • Money-back guarantee
          </p>

          <div className="flex flex-wrap justify-center gap-6">
            <div className="flex items-center space-x-2 text-ice-blue/70">
              <Lock className="w-5 h-5 text-electric-cyan" />
              <span className="text-sm">No credit card</span>
            </div>
            <div className="flex items-center space-x-2 text-ice-blue/70">
              <Shield className="w-5 h-5 text-laser-green" />
              <span className="text-sm">Money-back guarantee</span>
            </div>
            <div className="flex items-center space-x-2 text-ice-blue/70">
              <CheckCircle className="w-5 h-5 text-laser-green" />
              <span className="text-sm">7-Day Free Trial</span>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
