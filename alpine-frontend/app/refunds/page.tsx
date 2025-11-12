export default function RefundsPage() {
  return (
    <div className="min-h-screen bg-alpine-darker text-alpine-text">
      <div className="container mx-auto px-6 py-20 max-w-4xl">
        <h1 className="text-4xl font-display font-bold mb-8 text-alpine-green">Refund Policy</h1>
        <p className="text-alpine-text-dim mb-6">Last updated: November 10, 2025</p>

        <div className="space-y-8 text-alpine-text-dim">
          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">7-Day Free Trial</h2>
            <p>All subscription tiers include a 7-day free trial. You can cancel anytime during the trial period with no charge.</p>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">After Trial Period</h2>
            <p className="mb-4">Once the trial period ends and your subscription begins:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li><strong>All payments are final and non-refundable</strong></li>
              <li>You can cancel your subscription to prevent future charges</li>
              <li>No partial refunds for unused portion of subscription period</li>
              <li>Founder pricing is locked in for life (if you maintain active subscription)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">Cancellation</h2>
            <p>You may cancel your subscription at any time. Upon cancellation:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>You will continue to receive signals until the end of your billing period</li>
              <li>No refund will be issued for the current billing period</li>
              <li>You will not be charged for subsequent periods</li>
              <li>If you resubscribe later, Founder pricing may no longer be available</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">Exceptional Circumstances</h2>
            <p>Refunds may be considered in exceptional circumstances such as:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Technical issues preventing signal delivery for extended period</li>
              <li>Billing errors or duplicate charges</li>
            </ul>
            <p className="mt-4">Contact <a href="mailto:alpine.signals@proton.me" className="text-alpine-green hover:underline">alpine.signals@proton.me</a> to request review.</p>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text mb-4">Why No Refunds?</h2>
            <p>Trading signals are delivered immediately and cannot be "returned." The 7-day trial period allows you to fully evaluate the service before committing.</p>
          </section>
        </div>

        <div className="mt-12">
          <a href="/" className="text-alpine-green hover:underline">← Back to Home</a>
        </div>
      </div>
    </div>
  )
}

