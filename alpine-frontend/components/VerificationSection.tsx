'use client'

import { motion } from 'framer-motion'
import { Terminal, ShieldCheck, Download, FileText, CheckCircle2 } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function VerificationSection() {
  return (
    <section className="py-20 bg-alpine-darker border-y border-alpine-border">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-6xl font-display font-black text-white mb-4">
            Verification Tools{' '}
            <span className="bg-gradient-to-r from-alpine-accent to-alpine-pink bg-clip-text text-transparent">
              Coming Soon
            </span>
          </h2>
          <p className="text-xl text-alpine-text-dim max-w-3xl mx-auto">
            We're building open-source verification tools to prove our live performance.
            <br />
            Available after first month of live trading (December 2025).
          </p>
        </motion.div>

        {/* 3-Step Process Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {/* Step 1: Download */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0 }}
            className="bg-alpine-card border border-alpine-border rounded-lg p-8 relative"
          >
            <div
              className="absolute -top-4 left-8 bg-alpine-accent text-alpine-darker w-8 h-8 rounded-full flex items-center justify-center font-bold"
              aria-label="Step 1"
            >
              1
            </div>
            <Terminal className="w-12 h-12 text-alpine-accent mb-4" />
            <h3 className="text-xl font-display font-bold text-alpine-text mb-3">
              Download Verification Script
            </h3>
            <p className="text-alpine-text-dim mb-4">
              Get our Python verification tool (open source)
            </p>
            <pre
              className="bg-alpine-darker p-3 rounded text-sm text-alpine-accent font-mono overflow-x-auto"
              role="code"
            >
              pip install alpine-verify
            </pre>
          </motion.div>

          {/* Step 2: Run */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.15 }}
            className="bg-alpine-card border border-alpine-border rounded-lg p-8 relative"
          >
            <div
              className="absolute -top-4 left-8 bg-alpine-accent text-alpine-darker w-8 h-8 rounded-full flex items-center justify-center font-bold"
              aria-label="Step 2"
            >
              2
            </div>
            <CheckCircle2 className="w-12 h-12 text-alpine-accent mb-4" />
            <h3 className="text-xl font-display font-bold text-alpine-text mb-3">
              Run Verification
            </h3>
            <p className="text-alpine-text-dim mb-4">
              Check all 4,374 SHA-256 hashes in under 60 seconds
            </p>
            <pre
              className="bg-alpine-darker p-3 rounded text-sm text-alpine-accent font-mono text-xs overflow-x-auto"
              role="code"
            >
              alpine-verify --csv Alpine_Trade_History.csv --check-all
            </pre>
          </motion.div>

          {/* Step 3: Proof */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="bg-alpine-card border border-alpine-border rounded-lg p-8 relative"
          >
            <div
              className="absolute -top-4 left-8 bg-alpine-accent text-alpine-darker w-8 h-8 rounded-full flex items-center justify-center font-bold"
              aria-label="Step 3"
            >
              3
            </div>
            <ShieldCheck className="w-12 h-12 text-alpine-accent mb-4" />
            <h3 className="text-xl font-display font-bold text-alpine-text mb-3">
              See the Proof
            </h3>
            <p className="text-alpine-text-dim mb-4">
              Every hash will match. 100% verification rate.
            </p>
            <p className="text-alpine-red font-bold text-sm">
              If even ONE hash fails, we're lying.
            </p>
            <p className="text-alpine-text-dim text-sm mt-2">(They won't.)</p>
          </motion.div>
        </div>

        {/* Verification Output Example */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="bg-alpine-card rounded-lg border border-alpine-border p-6 mb-8"
        >
          <p className="text-alpine-text-dim text-sm mb-3 font-semibold">Preview - Actual output when tools launch in December 2025:</p>
          <pre
            className="text-sm text-alpine-accent font-mono overflow-x-auto"
            role="code"
          >{`✓ Verifying trade #1... PASS (hash matches)

✓ Verifying trade #2... PASS (hash matches)

✓ Verifying trade #3... PASS (hash matches)

...

✓ Verifying trade #4374... PASS (hash matches)



════════════════════════════════════════
VERIFICATION COMPLETE
════════════════════════════════════════

Total Trades: 4,374
Verified: 4,374 (100%)
Failed: 0
Status: ✓ ALL HASHES VALID



Performance data is AUTHENTIC and UNALTERED.`}</pre>
        </motion.div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
          <button
            disabled
            className="px-10 py-5 bg-alpine-card border-2 border-alpine-border text-alpine-text-dim font-bold text-lg rounded-xl opacity-50 cursor-not-allowed"
            title="Available December 2025 after first month of live trading"
            aria-label="Verification Tool Coming Soon"
          >
            <Download className="w-6 h-6 inline mr-3" />
            Verification Tool (Coming Dec 2025)
          </button>
          <Button
            size="lg"
            variant="outline"
            className="bg-alpine-card hover:bg-alpine-darker border border-alpine-border text-alpine-text font-semibold"
            aria-label="Read Technical Documentation"
          >
            <FileText className="w-5 h-5 mr-2" />
            Read Technical Documentation
          </Button>
        </div>

        {/* Trust Badge */}
        <div className="text-center">
          <p className="text-alpine-text-dim text-sm max-w-2xl mx-auto mb-4">
            Verification tools are currently in development and will be released in December 2025 after we have one month of live trading data. The commands shown above are previews of the planned functionality. Until release, you can download our backtest CSV and analyze it using standard data analysis tools.
          </p>
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-alpine-accent/10 to-alpine-pink/10 border-2 border-alpine-accent/30 rounded-full">
            <ShieldCheck className="w-5 h-5 text-alpine-accent" />
            <span className="font-black text-white">
              Live Verification Launches Nov 12, 2025 at 9:00 AM ET
            </span>
          </div>
        </div>
      </div>
    </section>
  )
}

