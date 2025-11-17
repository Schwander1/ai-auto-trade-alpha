export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-alpine-black-primary text-alpine-text-primary ">
      <div className="container mx-auto px-6 py-20 max-w-4xl">
        <h1 className="text-4xl font-display font-bold mb-8 text-alpine-semantic-success">Privacy Policy</h1>
        <p className="text-alpine-text-secondary mb-6">Last updated: November 10, 2025</p>

        <div className="space-y-8 text-alpine-text-secondary">
          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text-primary mb-4">1. Information We Collect</h2>
            <p className="mb-4">We collect information you provide directly:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Email address (for account creation and signal delivery)</li>
              <li>Phone number (optional, for SMS signal delivery - Professional tier only)</li>
              <li>Payment information (processed securely via Stripe)</li>
              <li>Usage data (which signals you view, when you log in)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text-primary mb-4">2. How We Use Your Information</h2>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Deliver trading signals via email and SMS</li>
              <li>Process payments and manage subscriptions</li>
              <li>Send service updates and important notices</li>
              <li>Improve our service and develop new features</li>
              <li>Respond to customer support requests</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text-primary mb-4">3. Data Sharing</h2>
            <p className="mb-4">We do NOT sell your personal data. We share data only with:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li><strong>Payment processors</strong> (Stripe) to process transactions</li>
              <li><strong>Email service</strong> (SendGrid) to deliver signals</li>
              <li><strong>SMS service</strong> (Twilio) to deliver SMS signals (if opted in)</li>
              <li><strong>Analytics tools</strong> to understand service usage</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text-primary mb-4">4. Data Security</h2>
            <p>We use industry-standard security measures including SSL/TLS encryption, secure password hashing, and encrypted database storage.</p>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text-primary mb-4">5. Your Rights</h2>
            <p className="mb-4">You have the right to:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Access your personal data</li>
              <li>Correct inaccurate data</li>
              <li>Request deletion of your data</li>
              <li>Opt out of marketing emails</li>
              <li>Export your data</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text-primary mb-4">6. Cookies</h2>
            <p>We use essential cookies for authentication and session management. We do not use tracking or advertising cookies.</p>
          </section>

          <section>
            <h2 className="text-2xl font-display font-bold text-alpine-text-primary mb-4">7. Contact</h2>
            <p>For privacy questions or to exercise your rights, contact: <a href="mailto:alpine.signals@proton.me" className="text-alpine-semanticsuccesshove-r:underline">alpine.signals@proton.me</a></p>
          </section>
        </div>

        <div className="mt-12">
          <a href="/" className="text-alpine-semanticsuccesshove-r:underline">← Back to Home</a>
        </div>
      </div>
    </div>
  )
}

