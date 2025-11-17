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
    <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-8 max-w-2xl mx-auto">
      <h3 className="text-2xl font-display font-bold text-alpine-text-primary mb-4">Send Us Feedback</h3>
      <p className="text-alpine-text-secondary mb-6">
        Questions? Suggestions? Issues? Let us know. We read every message.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-alpine-text-primary text-smfont-semiboldmb-2">
            Your Email (optional)
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            className="w-full px-4 py-3 bg-alpine-black-primary border-border-alpine-black-border rounded-lg text-alpine-text-primaryplaceholder-alpine-textsecondaryfocu-s:outline-none focus:border-alpine-neon-cyantransitioncolor-s"
          />
        </div>

        <div>
          <label htmlFor="message" className="block text-alpine-text-primary text-smfont-semiboldmb-2">
            Message *
          </label>
          <textarea
            id="message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            required
            rows={6}
            placeholder="Tell us what's on your mind..."
            className="w-full px-4 py-3 bg-alpine-black-primary border-border-alpine-black-border rounded-lg text-alpine-text-primaryplaceholder-alpine-textsecondaryfocu-s:outline-none focus:border-alpine-neon-cyantransition-colors-resizenon-e"
          />
        </div>

        <button
          type="submit"
          disabled={!message || status === 'sending'}
          className="w-full px-6 py-3 bg-gradient-to-r from-alpine-neon-cyan to-alpine-neon-pinkhove-r:from-alpine-neon-pinkhove-r:to-alpine-neoncyandisable-d:bg-alpine-textsecondarydisable-d:cursor-not-allowed text-white font-black rounded-lg transition-all shadow-lg shadow-alpine-neoncya-n/50 flex items-center justify-center gap-2"
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
          <div className="p-4 bg-alpine-neon-cyan/10 border border-alpine-neon-cyan/30 rounded-lg text-alpine-neon-cyan text-sm">
            ✓ Message sent! We'll respond within 24-48 hours.
          </div>
        )}

        {status === 'error' && (
          <div className="p-4 bg-alpine-semantic-error10 border border-alpine-semantic-error30 rounded-lg text-alpine-semantic-errortext-sm">
            ✗ Failed to send. Please email directly: <a href="mailto:alpine.signals@proton.me" className="underline">alpine.signals@proton.me</a>
          </div>
        )}
      </form>
    </div>
  )
}

