import FeedbackForm from '@/components/FeedbackForm'

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-alpine-darker text-alpine-text">
      <div className="container mx-auto px-6 py-20 max-w-4xl">
        <h1 className="text-4xl font-display font-bold mb-8 text-alpine-green">Get in Touch</h1>

        <div className="space-y-8">
          <section className="bg-alpine-card border border-alpine-border rounded-lg p-8">
            <h2 className="text-2xl font-display font-bold mb-4">Contact Email</h2>
            <a
              href="mailto:alpine.signals@proton.me"
              className="text-2xl text-alpine-green hover:underline"
            >
              alpine.signals@proton.me
            </a>
          </section>

          <section className="bg-alpine-card border border-alpine-border rounded-lg p-8">
            <h2 className="text-2xl font-display font-bold mb-4">Support Hours</h2>
            <p className="text-alpine-text-dim">Monday - Friday, 9:00 AM - 6:00 PM ET</p>
          </section>

          <section className="bg-alpine-card border border-alpine-border rounded-lg p-8">
            <h2 className="text-2xl font-display font-bold mb-4">Response Times</h2>
            <div className="space-y-3 text-alpine-text-dim">
              <div className="flex justify-between">
                <span>Starter Tier:</span>
                <span className="font-semibold">48-72 hours</span>
              </div>
              <div className="flex justify-between">
                <span>Professional Tier:</span>
                <span className="font-semibold">24-48 hours</span>
              </div>
              <div className="flex justify-between">
                <span>Institutional Tier:</span>
                <span className="font-semibold text-alpine-green">&lt; 1 hour</span>
              </div>
            </div>
          </section>

          <section className="bg-alpine-card border border-alpine-border rounded-lg p-8">
            <h2 className="text-2xl font-display font-bold mb-4">Institutional Inquiries</h2>
            <p className="text-alpine-text-dim mb-4">
              For institutional subscriptions, API access, or NDA methodology disclosure, please email with "INSTITUTIONAL" in the subject line.
            </p>
            <a
              href="mailto:alpine.signals@proton.me?subject=INSTITUTIONAL%20Inquiry"
              className="inline-flex items-center gap-2 px-6 py-3 bg-alpine-green hover:bg-alpine-green-dark text-alpine-darker font-bold rounded-lg transition-colors"
            >
              Email for Institutional Access
            </a>
          </section>
        </div>

        {/* Feedback Form */}
        <div className="mt-12">
          <FeedbackForm />
        </div>

        <div className="mt-12">
          <a href="/" className="text-alpine-green hover:underline">← Back to Home</a>
        </div>
      </div>
    </div>
  )
}

