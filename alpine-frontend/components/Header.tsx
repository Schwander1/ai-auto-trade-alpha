'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Menu, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function Header() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navItems = [
    { label: 'Home', href: '#home' },
    { label: 'Pricing', href: '#pricing' },
    { label: 'Proof', href: '#proof' },
    { label: 'FAQ', href: '#faq' },
  ]

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-alpine-black-primary/95 backdrop-blur-md border-b border-alpine-neon-cyan/20 shadow-glow-cyan'
          : 'bg-transparent'
      }`}
    >
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <a href="#home" className="flex items-center space-x-2" aria-label="Alpine Analytics Home">
            <div className="w-10 h-10 bg-gradient-cta rounded-lg flex items-center justify-center shadow-glow-cyan">
              <span className="text-black font-bold text-xl">A</span>
            </div>
            <span className="text-alpine-text-primary font-bold text-xl">Alpine Analytics</span>
          </a>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="text-alpine-text-primary hover:text-alpine-neon-cyan transition-colors font-medium"
              >
                {item.label}
              </a>
            ))}
          </div>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center space-x-4">
            <Button
              onClick={() => {
                const pricing = document.getElementById('pricing')
                pricing?.scrollIntoView({ behavior: 'smooth' })
              }}
              className="bg-gradient-cta text-black font-bold shadow-glow-cyan hover:scale-105 transition-transform"
            >
              Start Trial
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-alpine-text-primary"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden py-4 space-y-4 border-t border-alpine-neon-cyan/20"
            >
              {navItems.map((item) => (
                <a
                  key={item.href}
                  href={item.href}
                  className="block text-ice-blue/90 hover:text-electric-cyan transition-colors font-medium"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item.label}
                </a>
              ))}
              <div className="pt-4">
                <Button
                  className="w-full bg-gradient-cta text-black font-bold"
                  onClick={() => {
                    setIsMobileMenuOpen(false)
                    const pricing = document.getElementById('pricing')
                    pricing?.scrollIntoView({ behavior: 'smooth' })
                  }}
                >
                  Start Trial
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>
    </motion.header>
  )
}
