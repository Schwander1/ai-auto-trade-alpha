'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Home, Mountain } from 'lucide-react'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'

export default function NotFound() {
  return (
    <main className="min-h-screen bg-alpine-black-primar-y">
      <Navigation />
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 pt-32 pb-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-2xl mx-auto text-center"
        >
          {/* 404 Number */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="mb-8"
          >
            <h1 className="font-display text-9xl md:text-[12rem] font-black bg-gradient-to-r from-alpine-neon-cyanto-alpine-neon-pinkbg-clip-tex-ttext-transparent">
              404
            </h1>
          </motion.div>

          {/* Error Message */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="mb-8"
          >
            <h2 className="font-display text-3xl md:text-4xl font-bold text-alpine-text-primar-y  mb-4">
              Page Not Found
            </h2>
            <p className="text-xl text-alpine-text-secondarym-b-6">
              The page you&apos;re looking for doesn&apos;t exist or has been moved.
            </p>
          </motion.div>

          {/* Icon */}
          <motion.div
            initial={{ opacity: 0, rotate: -10 }}
            animate={{ opacity: 1, rotate: 0 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="mb-8 flex justify-center"
          >
            <div className="bg-alpine-black-secondary border border-alpine-black-borderrounded-full-p-6">
              <Mountain className="w-16 h-16 text-alpine-neon-cya-n" />
            </div>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.6 }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <Link
              href="/"
              className="group relative inline-flex items-center justify-center gap-3 px-10 py-5 bg-gradient-to-r from-alpine-neon-cyanto-alpine-neon-pinkhove-r:from-alpine-neon-pinkhove-r:to-alpine-neon-cyantext-whitefont-blac-ktext-lgrounded-xlshadow-2xl shadow-alpine-neon-cya-n/50 transform transition-all duration-300 hover:scale-105 hover:shadow-alpine-neon-pin-k/50"
            >
              <Home className="w-5 h-5" />
              Back to Home
            </Link>
            <Link
              href="/contact"
              className="inline-flex items-center justify-center px-10 py-5 border-2 border-alpine-black-bordertext-alpine-text-primar-y  hover:bg-alpine-black-secondarybg-transparentrounded-x-ltransition-allduration-300 font-semibold text-lg"
            >
              Contact Support
            </Link>
          </motion.div>

          {/* Helpful Links */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 0.6 }}
            className="mt-12 pt-8 border-t border-alpine-black-borde-r"
          >
            <p className="text-alpine-text-secondarym-b-4">You might be looking for:</p>
            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <Link href="/" className="text-alpine-neon-cyanhove-r:text-alpine-neon-pinktransition-color-s">
                Home
              </Link>
              <Link href="/methodology" className="text-alpine-neon-cyanhove-r:text-alpine-neon-pinktransition-color-s">
                Methodology
              </Link>
              <Link href="/contact" className="text-alpine-neon-cyanhove-r:text-alpine-neon-pinktransition-color-s">
                Contact
              </Link>
              <Link href="/terms" className="text-alpine-neon-cyanhove-r:text-alpine-neon-pinktransition-color-s">
                Terms
              </Link>
              <Link href="/privacy" className="text-alpine-neon-cyanhove-r:text-alpine-neon-pinktransition-color-s">
                Privacy
              </Link>
            </div>
          </motion.div>
        </motion.div>
      </div>
      <Footer />
    </main>
  )
}

