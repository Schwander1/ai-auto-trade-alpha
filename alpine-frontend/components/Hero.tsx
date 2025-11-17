'use client'

import { useState, useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Download, ArrowDown } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function Hero() {
  const [count, setCount] = useState(0)
  const [timeLeft, setTimeLeft] = useState({ hours: 0, minutes: 0, seconds: 0 })

  useEffect(() => {
    const target = 4374
    const increment = Math.ceil(target / 50)
    const interval = setInterval(() => {
      setCount((prev) => {
        if (prev >= target) {
          clearInterval(interval)
          return target
        }
        return Math.min(prev + increment, target)
      })
    }, 20)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const launchDate = new Date('2025-11-12T09:00:00-05:00').getTime()

    const updateCountdown = () => {
      const now = new Date().getTime()
      const distance = launchDate - now

      if (distance > 0) {
        const hours = Math.floor(distance / (1000 * 60 * 60))
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60))
        const seconds = Math.floor((distance % (1000 * 60)) / 1000)

        setTimeLeft({ hours, minutes, seconds })
      } else {
        setTimeLeft({ hours: 0, minutes: 0, seconds: 0 })
      }
    }

    updateCountdown()
    const interval = setInterval(updateCountdown, 1000)
    return () => clearInterval(interval)
  }, [])

  const stats = useMemo(() => [
    { label: 'Backtest Return', value: '+565.5%', sublabel: '2006-2025 simulation' },
    { label: 'CAGR', value: '9.94%', sublabel: 'Annualized' },
    { label: 'Backtested Signals', value: count.toLocaleString(), sublabel: '20-year dataset' },
    { label: 'Live Launch', value: 'Nov 12', sublabel: '9:00 AM ET' },
  ], [count])

  const container = useMemo(() => ({
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.3,
      },
    },
  }), [])

  const item = useMemo(() => ({
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
  }), [])

  return (
    <section
      id="home"
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
      style={{
        background: 'linear-gradient(180deg, var(--alpine-black-pure) 0%, var(--alpine-black-primary) 100%)',
      }}
    >
      {/* Floating Blob */}
      <motion.div
        className="absolute top-1/4 right-1/4 w-96 h-96 bg-alpine-neon-cyan/10 rounded-full blur-3xl pointer-events-none"
        animate={{
          x: [0, 100, 0],
          y: [0, -100, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10 py-20">
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="max-w-5xl mx-auto text-center"
        >
          {/* Heading */}
          <motion.h1
            variants={item}
            className="font-display text-5xl sm:text-6xl lg:text-7xl font-black tracking-[0.15em] mb-6"
          >
            <span className="text-white">Beat the Market.</span>
            <br />
            <span className="bg-gradient-to-r from-alpine-neon-cyanvia-alpine-neon-pink-to-alpine-neon-purplebg-cliptex-ttext-transparent">
              Provably.
            </span>
          </motion.h1>

          {/* Subheading */}
          <motion.p
            variants={item}
            className="text-2xl md:text-3xl text-alpine-text-secondary mb-8 max-w-4xl mx-auto leading-relaxed"
          >
            20-year backtest: <strong className="text-white">+565% return</strong>. Beat SPY by{' '}
            <strong className="text-alpine-neon-cyan">165%</strong>.
            <br />
            <span className="text-xl">Now launching live with cryptographic verification.</span>
            <br />
            <span className="text-lg text-alpine-neon-cyan font-semibold">Founding members lock in 50% off forever.</span>
          </motion.p>

          {/* Stats Grid */}
          <motion.div
            variants={item}
            className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
          >
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 + index * 0.1 }}
                className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-4"
              >
                <div className="text-alpine-neon-cyan font-black-text-lgmb-1">{stat.value}</div>
                <div className="text-alpine-text-primary font-semibold-texts-mmb-1">{stat.label}</div>
                {stat.sublabel && (
                  <div className="text-alpine-text-secondary text-sm">{stat.sublabel}</div>
                )}
              </motion.div>
            ))}
          </motion.div>

          {/* Launch Countdown */}
          <motion.div
            variants={item}
            className="mt-8 mb-8 text-center"
          >
            <div className="inline-block bg-gradient-to-r from-alpine-neon-cyan/10 via-alpine-neon-pink/10 to-alpine-neoncya-n/10 border-2 border-alpine-neon-cyan/30 rounded-xl p-6 shadow-lg">
              <p className="text-sm font-medium text-alpine-text-secondary mb-2">🚀 Live Launch Countdown</p>
              <div className="flex gap-4 justify-center mb-2">
                <div className="text-center">
                  <div className="text-3xl font-bold text-alpine-neon-cyan">
                    {String(timeLeft.hours).padStart(2, '0')}
                  </div>
                  <div className="text-sm text-alpine-text-secondary uppercase">Hours</div>
                </div>
                <div className="text-3xl font-bold text-alpine-neon-cyan">:</div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-alpine-neon-cyan">
                    {String(timeLeft.minutes).padStart(2, '0')}
                  </div>
                  <div className="text-sm text-alpine-text-secondary uppercase">Minutes</div>
                </div>
                <div className="text-3xl font-bold text-alpine-neon-cyan">:</div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-alpine-neon-cyan">
                    {String(timeLeft.seconds).padStart(2, '0')}
                  </div>
                  <div className="text-sm text-alpine-text-secondary uppercase">Seconds</div>
                </div>
              </div>
              <p className="text-sm font-semibold text-alpine-text-primary ">Wednesday, November 12, 2025 at 9:00 AM ET</p>
              <p className="text-sm text-alpine-text-secondary mt-1">Cryptographic verification goes live</p>
            </div>
          </motion.div>

          {/* CTAs */}
          <motion.div
            variants={item}
            className="flex flex-col sm:flex-row gap-4 justify-center mb-12"
          >
            <a
              href="/api/download-backtest"
              className="group relative inline-flex items-center justify-center gap-3 px-10 py-5 bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pinkhove-r:from-alpine-neon-pinkhove-r:to-alpine-neon-cyantext-white-fontblac-ktext-lgrounded-xlshadow-2xl shadow-alpine-neoncya-n/50 transform transition-all duration-300 hover:scale-105 hover:shadow-alpine-neonpin-k/50"
            >
              <span className="relative z-10 flex items-center gap-3">
                <Download className="w-6 h-6" />
                Download Backtest Data
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-alpine-neon-pink-to-alpine-neoncyanopacit-y-0 group-hover:opacity-100 rounded-xl blur transition-opacity duration-300"></div>
            </a>
            <button
              onClick={() => {
                const pricing = document.getElementById('pricing')
                pricing?.scrollIntoView({ behavior: 'smooth' })
              }}
              className="group relative px-10 py-5 bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pinkhove-r:from-alpine-neon-pinkhove-r:to-alpine-neon-cyantext-white-fontblac-ktext-lgrounded-xlshadow-2xl shadow-alpine-neoncya-n/50 transform transition-all duration-300 hover:scale-105 hover:shadow-alpine-neonpin-k/50"
            >
              <span className="relative z-10">Start 7-Day Trial →</span>
              <div className="absolute inset-0 bg-gradient-to-r from-alpine-neon-pink-to-alpine-neoncyanopacit-y-0 group-hover:opacity-100 rounded-xl blur transition-opacity duration-300"></div>
            </button>
          </motion.div>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="text-alpine-text-secondary"
          >
            <ArrowDown className="w-6 h-6" />
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
