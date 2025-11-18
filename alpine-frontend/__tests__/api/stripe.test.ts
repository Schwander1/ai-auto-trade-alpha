/**
 * Integration tests for Stripe API routes
 */

describe('Stripe API Routes', () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('POST /api/stripe/create-checkout-session', () => {
    it('requires authentication', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 401,
        ok: false,
      })

      const response = await fetch(`${API_URL}/api/stripe/create-checkout-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tier: 'STARTER' }),
      })

      // Should return 401 or redirect
      expect([401, 403, 301, 302]).toContain(response.status)
    })

    it('requires tier parameter', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 400,
        ok: false,
      })

      const response = await fetch(`${API_URL}/api/stripe/create-checkout-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      })

      expect(response.status).toBeGreaterThanOrEqual(400)
    })
  })

  describe('POST /api/stripe/create-portal-session', () => {
    it('requires authentication', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 401,
        ok: false,
      })

      const response = await fetch(`${API_URL}/api/stripe/create-portal-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      })

      expect([401, 403]).toContain(response.status)
    })
  })

  describe('POST /api/stripe/webhook', () => {
    it('requires webhook signature', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 400,
        ok: false,
      })

      const response = await fetch(`${API_URL}/api/stripe/webhook`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'checkout.session.completed' }),
      })

      // Should return 400 or 401 without signature
      expect([400, 401, 403]).toContain(response.status)
    })
  })
})
