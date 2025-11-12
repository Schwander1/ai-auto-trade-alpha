export default function TermsPage() {
  return (
    <div className="min-h-screen bg-alpine-darker text-alpine-text">
      <div className="container mx-auto px-6 py-20 max-w-4xl">
        <h1 className="text-4xl font-display font-bold mb-8 text-alpine-green">Terms of Service</h1>
        <p className="text-alpine-text-dim mb-6">Last updated: November 10, 2025</p>

        <div className="space-y-8 text-alpine-text-dim">
          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">1. Acceptance of Terms</h2>
            <p>By accessing and using Alpine Analytics ("Service"), you accept and agree to be bound by these Terms of Service.</p>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">2. Service Description</h2>
            <p>Alpine Analytics provides trading signal recommendations for educational purposes. We do not provide financial advice, investment advice, or trading advice.</p>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">3. Risk Disclosure</h2>
            <p className="font-bold text-alpine-red mb-2">TRADING INVOLVES SUBSTANTIAL RISK OF LOSS.</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>You can lose your entire investment</li>
              <li>Past performance does not guarantee future results</li>
              <li>Our signals are for educational purposes only</li>
              <li>You are solely responsible for your trading decisions</li>
              <li>You should only trade with capital you can afford to lose</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">4. Backtest Disclosure</h2>
            <p>Historical performance data prior to November 12, 2025 represents backtested results, not actual trading signals. Backtested performance is hypothetical and has inherent limitations:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Backtested results do not represent actual trading</li>
              <li>Results may not reflect impact of material economic and market factors</li>
              <li>Backtesting can be designed with benefit of hindsight</li>
            </ul>
            <p className="mt-4">Live cryptographically verified signals begin Wednesday, November 12, 2025 at 9:00 AM ET.</p>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">5. Subscription & Payment</h2>
            <p>Subscriptions are billed annually. Founder pricing locks in your rate for life. Prices may increase for new customers but will not increase for existing Founder tier members.</p>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">6. Refund Policy</h2>
            <p>7-day free trial allows you to evaluate the service. After the trial period, all payments are final and non-refundable. See our Refund Policy for details.</p>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">7. Intellectual Property</h2>
            <p>Alpine Analytics®, our SHA-256 cryptographic verification system, and adaptive regime detection methodology are protected under pending U.S. patent application. Unauthorized use is prohibited.</p>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">8. Limitation of Liability</h2>
            <p className="font-bold">TO THE MAXIMUM EXTENT PERMITTED BY LAW, ALPINE ANALYTICS SHALL NOT BE LIABLE FOR ANY TRADING LOSSES, INVESTMENT LOSSES, OR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES.</p>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">9. Contact</h2>
            <p>For questions about these Terms, contact: <a href="mailto:alpine.signals@proton.me" className="text-alpine-green hover:underline">alpine.signals@proton.me</a></p>
          </section>
        </div>

        <div className="mt-12">
          <a href="/" className="text-alpine-green hover:underline">← Back to Home</a>
        </div>
      </div>
    </div>
  )
}

