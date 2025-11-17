'use client'

import { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X, Mountain } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function Navigation() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navItems = useMemo(() => [
    { label: 'Home', href: '#home' },
    { label: 'Pricing', href: '#pricing' },
    { label: 'Proof', href: '#proof' },
    { label: 'FAQ', href: '#faq' },
  ], [])

  const scrollToSection = (href: string) => {
    const element = document.querySelector(href)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
      setIsMobileMenuOpen(false)
    }
  }

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'backdrop-blur-md bg-alpine-black-primary/80 border-b border-alpine-black-border'
          : 'bg-transparent'
      }`}
    >
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <a
            href="#home"
            onClick={(e) => {
              e.preventDefault()
              scrollToSection('#home')
            }}
            className="flex items-center space-x-2"
            aria-label="Alpine Analytics Home"
          >
            <Mountain className="w-8 h-8 text-alpine-neon-cyan" />
            <span className="font-display text-alpine-text-primary font-bold text-xl">Alpine Analytics</span>
          </a>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                onClick={(e) => {
                  e.preventDefault()
                  scrollToSection(item.href)
                }}
                className="text-alpine-text-secondary hover:text-alpine-text-primary transition-colors font-medium"
              >
                {item.label}
              </a>
            ))}
          </div>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center space-x-4">
            <Button
              onClick={() => scrollToSection('#pricing')}
              className="bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pink text-black font-black hover:from-alpine-neon-pink hover:to-alpine-neon-cyan transition-all shadow-lg shadow-alpine-neon-cyan/50"
            >
              Start Trial
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-alpine-text-primary"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
            aria-expanded={isMobileMenuOpen}
            aria-controls="mobile-menu"
          >
            {isMobileMenuOpen ? <X size={24} aria-hidden="true" /> : <Menu size={24} aria-hidden="true" />}
          </button>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              id="mobile-menu"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden py-4 space-y-4 border-t border-alpine-black-border"
              role="menu"
            >
              {navItems.map((item) => (
                <a
                  key={item.href}
                  href={item.href}
                  onClick={(e) => {
                    e.preventDefault()
                    scrollToSection(item.href)
                  }}
                  className="block text-alpine-text-secondary hover:text-alpine-text-primary transition-colors font-medium"
                >
                  {item.label}
                </a>
              ))}
              <div className="pt-4">
                <Button
                  className="w-full bg-alpine-neon-cyan text-black font-bold"
                  onClick={() => scrollToSection('#pricing')}
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

