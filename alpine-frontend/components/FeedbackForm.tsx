'use client'

import { useState } from 'react'
import { Send } from 'lucide-react'

export default function FeedbackForm() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [status, setStatus] = useState<'idle' | 'sending' | 'success' | 'error'>('idle')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus('sending')

    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, message }),
      })

      if (response.ok) {
        setStatus('success')
        setEmail('')
        setMessage('')
        setTimeout(() => setStatus('idle'), 5000)
      } else {
        setStatus('error')
      }
    } catch (error) {
      setStatus('error')
    }
  }

  return (
    <div className="bg-alpine-card border border-alpine-border rounded-lg p-8 max-w-2xl mx-auto">
      <h3 className="text-2xl font-display font-bold text-alpine-text mb-4">Send Us Feedback</h3>
      <p className="text-alpine-text-dim mb-6">
        Questions? Suggestions? Issues? Let us know. We read every message.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-alpine-text text-sm font-semibold mb-2">
            Your Email (optional)
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            className="w-full px-4 py-3 bg-alpine-darker border border-alpine-border rounded-lg text-alpine-text placeholder-alpine-text-dim focus:outline-none focus:border-alpine-accent transition-colors"
          />
        </div>

        <div>
          <label htmlFor="message" className="block text-alpine-text text-sm font-semibold mb-2">
            Message *
          </label>
          <textarea
            id="message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            required
            rows={6}
            placeholder="Tell us what's on your mind..."
            className="w-full px-4 py-3 bg-alpine-darker border border-alpine-border rounded-lg text-alpine-text placeholder-alpine-text-dim focus:outline-none focus:border-alpine-accent transition-colors resize-none"
          />
        </div>

        <button
          type="submit"
          disabled={!message || status === 'sending'}
          className="w-full px-6 py-3 bg-gradient-to-r from-alpine-accent to-alpine-pink hover:from-alpine-pink hover:to-alpine-accent disabled:bg-alpine-text-dim disabled:cursor-not-allowed text-white font-black rounded-lg transition-all shadow-lg shadow-alpine-accent/50 flex items-center justify-center gap-2"
        >
          {status === 'sending' ? (
            'Sending...'
          ) : (
            <>
              <Send className="w-5 h-5" />
              Send Feedback
            </>
          )}
        </button>

        {status === 'success' && (
          <div className="p-4 bg-alpine-accent/10 border border-alpine-accent/30 rounded-lg text-alpine-accent text-sm">
            ✓ Message sent! We'll respond within 24-48 hours.
          </div>
        )}

        {status === 'error' && (
          <div className="p-4 bg-alpine-red/10 border border-alpine-red/30 rounded-lg text-alpine-red text-sm">
            ✗ Failed to send. Please email directly: <a href="mailto:alpine.signals@proton.me" className="underline">alpine.signals@proton.me</a>
          </div>
        )}
      </form>
    </div>
  )
}

