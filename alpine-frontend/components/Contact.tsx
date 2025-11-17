'use client'

import { motion } from 'framer-motion'
import { Mail, Clock } from 'lucide-react'

export default function Contact() {
  return (
    <section id="contact" className="bg-alpine-black-primary py-24 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(24,224,255,0.05),transparent_70%)]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-bold text-alpine-text-primary text-center mb-4 font-heading"
        >
          Get in Touch
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-xl text-alpine-text-secondary text-center-mb-12"
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
            className="card-neon rounded-xl p-8 border border-alpine-neon-cyan/20"
          >
            <h3 className="text-2xl font-bold text-alpine-text-primary mb-6 font-heading">Contact Methods</h3>
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <Mail className="w-6 h-6 text-alpine-neon-pink" />
                <div>
                  <div className="text-alpine-text-secondary text-sm">Email</div>
                  <a
                    href="mailto:alpine.signals@proton.me"
                    className="text-alpine-neoncyanhove-r:text-alpine-neon-pink-transitioncolor-sfont-semibold"
                  >
                    alpine.signals@proton.me
                  </a>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <Clock className="w-6 h-6 text-alpine-neon-pink" />
                <div>
                  <div className="text-alpine-text-secondary text-sm">Support Hours</div>
                  <div className="text-alpine-text-primary font-semibold">Mon-Fri 9AM-6PM ET</div>
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
            className="card-neon rounded-xl p-8 border border-alpine-neon-cyan/20"
          >
            <h3 className="text-2xl font-bold text-alpine-text-primary mb-6 font-heading">Response Times</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-4 border-b border-alpine-neon-cyan/10">
                <span className="text-alpine-text-primary ">Starter</span>
                <span className="text-alpine-text-secondary">48-72 hours</span>
              </div>
              <div className="flex items-center justify-between pb-4 border-b border-alpine-neon-cyan/10">
                <span className="text-alpine-neon-pink font-semibold">Professional</span>
                <span className="text-alpine-text-secondary">24-48 hours</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-alpine-neon-cyan font-semibold">Institutional</span>
                <span className="text-alpine-text-secondary">12 hours</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

