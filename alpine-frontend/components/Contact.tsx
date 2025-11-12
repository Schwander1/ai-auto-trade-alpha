'use client'

import { motion } from 'framer-motion'
import { Mail, Clock } from 'lucide-react'

export default function Contact() {
  return (
    <section id="contact" className="py-24 relative overflow-hidden" style={{ backgroundColor: '#0a0a0a' }}>
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
          Get in Touch
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-xl text-ice-blue/70 text-center mb-12"
        >
          Questions? We're here to help.
        </motion.p>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Contact Methods */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="glassmorphism rounded-xl p-8 border border-electric-cyan/20"
          >
            <h3 className="text-2xl font-bold text-ice-blue mb-6">Contact Methods</h3>
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <Mail className="w-6 h-6 text-neon-pink" />
                <div>
                  <div className="text-ice-blue/70 text-sm">Email</div>
                  <a
                    href="mailto:alpine.signals@proton.me"
                    className="text-electric-cyan hover:text-neon-pink transition-colors font-semibold"
                  >
                    alpine.signals@proton.me
                  </a>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <Clock className="w-6 h-6 text-neon-pink" />
                <div>
                  <div className="text-ice-blue/70 text-sm">Support Hours</div>
                  <div className="text-ice-blue font-semibold">Mon-Fri 9AM-6PM ET</div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Response Times */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="glassmorphism rounded-xl p-8 border border-electric-cyan/20"
          >
            <h3 className="text-2xl font-bold text-ice-blue mb-6">Response Times</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-4 border-b border-electric-cyan/10">
                <span className="text-ice-blue">Starter</span>
                <span className="text-ice-blue/70">48-72 hours</span>
              </div>
              <div className="flex items-center justify-between pb-4 border-b border-electric-cyan/10">
                <span className="text-neon-pink font-semibold">Professional</span>
                <span className="text-ice-blue/70">24-48 hours</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-electric-cyan font-semibold">Institutional</span>
                <span className="text-ice-blue/70">12 hours</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

