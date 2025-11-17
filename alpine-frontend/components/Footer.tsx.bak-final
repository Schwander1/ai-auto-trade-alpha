'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { Mail, Copy, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'

const footerLinks = {
  product: [
    { label: 'Download Trade Data', href: '/#proof', isExternal: false },
    { label: 'Methodology', href: '/methodology', isExternal: false },
    { label: 'Pricing', href: '/#pricing', isExternal: false },
  ],
  legal: [
    { label: 'Terms', href: '/terms', isExternal: false },
    { label: 'Privacy', href: '/privacy', isExternal: false },
    { label: 'Refunds', href: '/refunds', isExternal: false },
  ],
  company: [
    { label: 'Contact', href: '/contact', isExternal: false },
  ],
}

export default function Footer() {
  const [emailCopied, setEmailCopied] = useState(false)

  const copyEmail = () => {
    navigator.clipboard.writeText('alpine.signals@proton.me')
    setEmailCopied(true)
    setTimeout(() => setEmailCopied(false), 2000)
  }

  const handleLinkClick = (href: string, isExternal: boolean) => {
    if (isExternal) {
      return
    }
    if (href.startsWith('/#')) {
      // Smooth scroll to section on home page
      const sectionId = href.replace('/#', '#')
      const element = document.querySelector(sectionId)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' })
      }
    }
  }

  return (
    <footer className="bg-alpine-darker border-t border-alpine-border">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Get in Touch Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-12"
        >
          <h3 className="text-2xl font-display font-bold text-alpine-text mb-6">Get in Touch</h3>
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl">
            {/* Contact Email */}
            <div className="bg-alpine-card border border-alpine-border rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-4">
                <Mail className="w-6 h-6 text-alpine-accent" />
                <div>
                  <div className="text-alpine-text-dim text-sm mb-1">Email</div>
                  <div className="flex items-center space-x-2">
                    <a
                      href="mailto:alpine.signals@proton.me"
                      className="text-alpine-accent hover:text-alpine-accent-dark transition-colors font-semibold"
                    >
                      alpine.signals@proton.me
                    </a>
                    <button
                      onClick={copyEmail}
                      className="text-alpine-text-dim hover:text-alpine-accent transition-colors"
                      aria-label="Copy email"
                    >
                      {emailCopied ? (
                        <Check className="w-4 h-4 text-alpine-accent" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Support Hours */}
            <div className="bg-alpine-card border border-alpine-border rounded-lg p-6">
              <div className="text-alpine-text-dim text-sm mb-1">Support Hours</div>
              <div className="text-alpine-text font-semibold">Mon-Fri 9AM-6PM ET</div>
            </div>
          </div>

          {/* Response Times */}
          <div className="bg-alpine-card border border-alpine-border rounded-lg p-6 mt-6 max-w-2xl">
            <h4 className="text-alpine-text font-semibold mb-4">Response Times</h4>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="text-alpine-text-dim text-sm mb-1">Starter</div>
                <div className="text-alpine-text font-semibold">48-72 hours</div>
              </div>
              <div>
                <div className="text-alpine-text-dim text-sm mb-1">Professional</div>
                <div className="text-alpine-accent font-semibold">24-48 hours</div>
              </div>
              <div>
                <div className="text-alpine-text-dim text-sm mb-1">Institutional</div>
                <div className="text-alpine-blue font-semibold">&lt; 1 hour</div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Links Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-8 mb-8">
          <div>
            <h3 className="text-alpine-text font-semibold mb-4">Product</h3>
            <ul className="space-y-2">
              {footerLinks.product.map((link) => (
                <li key={link.href}>
                  {link.href.startsWith('/#') ? (
                    <a
                      href={link.href}
                      onClick={(e) => {
                        e.preventDefault()
                        handleLinkClick(link.href, link.isExternal)
                      }}
                      className="text-alpine-text-dim hover:text-alpine-accent transition-colors text-sm"
                    >
                      {link.label}
                    </a>
                  ) : (
                    <Link
                      href={link.href}
                      className="text-alpine-text-dim hover:text-alpine-accent transition-colors text-sm"
                    >
                      {link.label}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-alpine-text font-semibold mb-4">Legal</h3>
            <ul className="space-y-2">
              {footerLinks.legal.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-alpine-text-dim hover:text-alpine-green transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-alpine-text font-semibold mb-4">Company</h3>
            <ul className="space-y-2">
              {footerLinks.company.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-alpine-text-dim hover:text-alpine-green transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-alpine-border pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-6">
            <p className="text-alpine-text-dim text-sm">
              © 2025 Alpine Analytics LLC. All rights reserved.
            </p>
          </div>
          <div className="bg-alpine-card rounded-lg p-6 border border-alpine-border mb-4">
            <p className="text-alpine-text-dim text-xs leading-relaxed mb-2">
              Alpine Analytics®, our SHA-256 cryptographic verification system for trading signals, and our adaptive regime detection methodology are protected under pending U.S. patent application. Any unauthorized use or replication of this system is prohibited. <strong>Patent Pending - SHA-256 Cryptographic Verification System</strong>. All rights reserved.
            </p>
          </div>
          <p className="text-alpine-text-dim text-xs text-center mb-2">
            Not financial advice. For educational purposes only. See Terms of Service for full disclaimers.
          </p>
          <p className="text-alpine-text-dim text-xs text-center max-w-4xl mx-auto">
            Historical performance data (2006-2025) represents backtested results. Live cryptographically verified trading begins Wednesday, November 12, 2025 at 9:00 AM ET.
          </p>
        </div>
      </div>
    </footer>
  )
}
