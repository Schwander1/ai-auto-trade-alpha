'use client'

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import React from 'react'

const faqs: Array<{ question: string; answer: string | React.ReactNode }> = [
  {
    question: 'Is your 20-year track record real or backtested?',
    answer:
      "It's backtested. We ran our multi-regime strategy on historical data from 2006-2025 to validate the approach. Unlike many signal services who call backtests 'verified performance,' we're honest about what's simulation vs what's live. Launching November 12, 2025 at 9:00 AM ET, every signal will be cryptographically verified with SHA-256 signatures. You'll be able to download the complete live track record and verify every hash yourself. No backtest can be faked retroactively when it's signed in real-time.",
  },
  {
    question: 'What are confidence scores and how do you use them?',
    answer: (
      <>
        Every signal we generate includes a confidence score between 87-98%. This score represents how strongly our multi-regime system believes the trade setup meets our quality standards.
        <br />
        <br />
        <strong>How confidence scores work:</strong>
        <br />
        <br />
        Our system analyzes multiple factors simultaneously:
        <br />
        • Market regime identification (Bull/Bear/Chop/Crisis)
        <br />
        • Multi-indicator confluence (trend, momentum, volume)
        <br />
        • Risk-reward ratio calculations
        <br />
        • Historical pattern recognition
        <br />
        • Volatility conditions
        <br />
        <br />
        When all factors align strongly, confidence is high (95-98%). When factors align but with some uncertainty, confidence is lower (87-90%). We only generate signals when confidence reaches our minimum threshold of 87%.
        <br />
        <br />
        <strong>Our 20-year backtest shows:</strong>
        <br />
        • Minimum confidence: 87%
        <br />
        • Median confidence: 89%
        <br />
        • Maximum confidence: 98%
        <br />
        • Distribution: 57% of signals scored 87-90%, 43% scored 90%+
        <br />
        <br />
        <strong>Important:</strong> Confidence scores are NOT win rate predictions. A 95% confidence signal doesn't mean 95% chance of profit. It means our system is 95% confident the setup meets our criteria. Our actual win rate across all confidence levels is 45.2%.
        <br />
        <br />
        <strong>Why we show this:</strong> Most services hide their quality metrics or make up numbers. We show you the real distribution so you can analyze performance by confidence tier yourself in our downloadable dataset.
        <br />
        <br />
        Launching November 12, 2025 at 9:00 AM ET, every live signal will include its confidence score alongside SHA-256 cryptographic verification.
      </>
    ),
  },
  {
    question: 'How selective is your signal generation?',
    answer: (
      <>
        Extremely selective. Our system only generates signals when strict multi-regime criteria align, resulting in confidence scores of 87-98%.
        <br />
        <br />
        <strong>The numbers:</strong>
        <br />
        • 4,374 signals over 20 years = ~18 signals per month average
        <br />
        • Compare to competitors: Many send 50-200+ signals per month
        <br />
        • Our threshold: 87% minimum confidence (median 89%)
        <br />
        • Industry standard: Many services send everything their system generates, regardless of quality
        <br />
        <br />
        <strong>Why we're selective:</strong>
        <br />
        <br />
        1. <strong>Quality over quantity</strong> - We'd rather send you 20 high-quality signals than 200 low-quality ones. Each signal represents a genuine opportunity where multiple factors align.
        <br />
        <br />
        2. <strong>No spam</strong> - We don't flood your inbox hoping something hits. Every signal meets strict standards before being sent.
        <br />
        <br />
        3. <strong>You can verify</strong> - Download our complete 20-year backtest (4,374 signals). Every single signal is included. No cherry-picking. No gaps. Zero hidden data.
        <br />
        <br />
        4. <strong>Real standards</strong> - Unlike services that claim to be "selective" while secretly filtering out losers after the fact, we send ALL signals that meet our generation criteria. The 87-98% confidence threshold is applied BEFORE signal generation, not after.
        <br />
        <br />
        <strong>What this means for you:</strong>
        <br />
        • Fewer signals to act on (less stress, less time commitment)
        <br />
        • Higher average quality per signal
        <br />
        • Real 45.2% win rate (not inflated by hiding losers)
        <br />
        • Complete transparency (track performance yourself)
        <br />
        <br />
        Our selectivity is why our win rate is "only" 45% - we show you every trade, wins and losses, rather than cherry-picking winners to fake a 90%+ rate.
      </>
    ),
  },
  {
    question: 'Why is your win rate only 45%?',
    answer: (
      <>
        Two reasons, and both are about honesty:
        <br />
        <br />
        <strong>1. We show EVERY trade</strong>
        <br />
        <br />
        Most signal services claim 85-95% win rates. How do they achieve this?
        <br />
        <br />
        They don't.
        <br />
        <br />
        They show you their winners and hide their losers. Or they cherry-pick historical results. Or they retroactively filter out "low confidence" signals after they lose. There's no way to verify their claims because they don't provide complete data.
        <br />
        <br />
        We show you every single trade from our 20-year backtest: all 4,374 signals, including 2,390 losers. That's the real 45.2% win rate.
        <br />
        <br />
        <strong>2. We're highly selective</strong>
        <br />
        <br />
        Our system only generates signals when confidence reaches 87-98%. We don't spam low-quality trades hoping something sticks.
        <br />
        <br />
        Over 4,374 backtested signals, this selective approach produced:
        <br />
        • 45.2% win rate (real, not inflated)
        <br />
        • +565% total return (9.94% CAGR)
        <br />
        • Beat SPY by 165% over 20 years
        <br />
        • -36.1% max drawdown (we show the ugly truth too)
        <br />
        <br />
        <strong>The math that matters:</strong>
        <br />
        <br />
        A 45% win rate with proper risk management beats a fake 90% win rate every time.
        <br />
        <br />
        Example:
        <br />
        • Service A: Claims 90% win rate (cherry-picked, no verification)
        <br />
        • Service B (us): 45.2% win rate, but wins are 2.5x average loss size
        <br />
        • Over 100 trades: Service A (unknown real performance), Service B = profitable
        <br />
        <br />
        <strong>You can verify this yourself:</strong>
        <br />
        <br />
        Download our complete 20-year backtest. Import it into Excel, Python, or R. Calculate the win rate yourself. You'll get 45.2%.
        <br />
        <br />
        Then try this with ANY competitor. Most won't even provide downloadable data. Those who do often have suspicious gaps or cherry-picked date ranges.
        <br />
        <br />
        <strong>Launching November 12, 2025 at 9:00 AM ET:</strong>
        <br />
        <br />
        Every live signal will be SHA-256 cryptographically verified. You'll watch our real track record build from day one. If we start hiding losers or cherry-picking signals, you'll see it immediately in the verified logs.
        <br />
        <br />
        No more "trust us." Just math.
        <br />
        <br />
        <strong>Bottom line:</strong> We'd rather be honest with a 45% win rate than lie with a 90% win rate. Quality over quantity. Honesty over hype.
      </>
    ),
  },
  {
    question: 'How long did this take to build?',
    answer:
      '3+ years. 2019-2022: Research and data analysis. 2023-2024: Optimization and infrastructure. 2025: Public launch. We\'ve been trading these signals with our own capital since 2023.',
  },
  {
    question: 'Why is pricing lower than other services?',
    answer:
      "We're profitable from our own trading. Alpine is about sharing systems we already built and validated, not our primary revenue source. Lower prices = more traders = better market feedback to improve our edge.",
  },
  {
    question: 'Who is behind Alpine Analytics?',
    answer:
      "We're quantitative traders who prefer anonymity. Alpine Analytics LLC is our legal entity. We let our verified results speak for themselves.",
  },
  {
    question: 'Do you trade your own signals?',
    answer:
      'Yes. Every signal we send is based on the same system we trade with our own capital. We eat our own cooking.',
  },
  {
    question: 'Can you beat [famous hedge fund]?',
    answer:
      "We don't make comparisons to other firms. Our 58.5% backtested win rate is verifiable and speaks for itself. We're swing traders, not high-frequency quants. Different strategies, different goals.",
  },
  {
    question: 'Why reveal your system publicly?',
    answer:
      'We reveal the general approach (4 regime models, common indicators) but not the secret sauce (exact optimization methods, data preprocessing, proprietary combinations). Institutional tier gets more details, but core IP remains protected. More users = more data to improve the system.',
  },
  {
    question: 'What happens to my money?',
    answer:
      'Payments go to Alpine Analytics LLC. Revenue funds operations, continuous R&D, infrastructure costs, and our proprietary trading capital.',
  },
  {
    question: 'Will prices increase?',
    answer:
      'Yes, eventually. Current pricing is launch promotional. Annual plans lock in rates for the subscription term. We reserve the right to increase monthly pricing for new customers.',
  },
  {
    question: 'What if I want a refund?',
    answer:
      '7-day free trial (no credit card required). After paid subscription starts, 30-day money-back guarantee, no questions asked.',
  },
  {
    question: 'Any broker affiliations?',
    answer:
      'No. We have zero broker partnerships or affiliate relationships. We don\'t profit from your trades, only your subscription.',
  },
  {
    question: 'Blue-green deployment?',
    answer:
      'Yes. We use blue-green deployment for zero-downtime system updates. Signals are never interrupted during infrastructure upgrades.',
  },
  {
    question: 'What is Kelly position sizing?',
    answer:
      'Kelly Criterion is a mathematical formula for optimal position sizing based on win rate and risk/reward ratio. Our Institutional tier provides detailed Kelly models based on our verified 58.5% win rate and historical performance data. This is advanced risk management for professional traders only. We do NOT recommend position sizing without understanding the risks.',
  },
  {
    question: 'Can I verify your results independently?',
    answer:
      'Yes, but differently for backtest vs live signals:\n\n**Backtest data (2006-2025):** Download the complete CSV and analyze it yourself. Use Python, R, or Excel to verify our calculations. The data uses real market prices—check against any data provider.\n\n**Live signals (Nov 12, 2025+):** Every signal will include a SHA-256 cryptographic hash generated at the moment of signal creation. We\'ll provide verification tools in December 2025 (after first month of live trading) so you can independently confirm that our published performance matches the signals we actually sent. No cherry-picking possible. No retroactive editing possible.\n\nThis is the difference between Alpine and other services: We\'re building a verifiable track record from scratch, not claiming backtests as "verified."',
  },
  {
    question: 'Terms of service?',
    answer:
      'Comprehensive Terms of Service available during signup. Covers usage rights, limitations, liability, data privacy, and dispute resolution.',
  },
  {
    question: 'Do you update your strategy?',
    answer:
      'Yes, continuously. Many signal services use static strategies that become stale. We iterate weekly—testing new indicators, refining entry logic, optimizing position sizing. Every change is deployed as a new strategy version (v1.0, v1.1, v2.0...) and tracked separately with SHA-256 verification. You can compare versions side-by-side to see improvements in real-time. More subscribers = more revenue = bigger R&D budget = better signals for everyone.',
  },
]

export default function FAQ() {
  return (
    <section id="faq" className="py-24 bg-alpine-black-primary">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-4xl md:text-6xl font-display font-black text-white text-center mb-16">
          Frequently Asked Questions
        </h2>

        <div className="max-w-3xl mx-auto">
          <Accordion type="single" collapsible className="w-full">
            {faqs.map((faq, index) => (
              <AccordionItem
                key={index}
                value={`item-${index}`}
                className="border-alpine-black-border"
              >
                <AccordionTrigger className="text-left text-alpine-text-primary font-semibold hover:no-underline hover:text-alpine-neon-cyan transition-colors">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-alpine-text-secondary leading-relaxed">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </div>
    </section>
  )
}
