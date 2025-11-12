/**
 * Integration tests for subscriptions API routes
 */

describe('Subscriptions API Routes', () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'

  describe('GET /api/subscriptions/plan', () => {
    it('requires authentication', async () => {
      const response = await fetch(`${API_URL}/api/subscriptions/plan`)

      expect([401, 403]).toContain(response.status)
    })
  })

  describe('POST /api/subscriptions/upgrade', () => {
    it('requires authentication', async () => {
      const response = await fetch(`${API_URL}/api/subscriptions/upgrade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tier: 'PROFESSIONAL' }),
      })

      expect([401, 403]).toContain(response.status)
    })

    it('requires tier parameter', async () => {
      const response = await fetch(`${API_URL}/api/subscriptions/upgrade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      })

      expect(response.status).toBeGreaterThanOrEqual(400)
    })
  })

  describe('GET /api/subscriptions/invoices', () => {
    it('requires authentication', async () => {
      const response = await fetch(`${API_URL}/api/subscriptions/invoices`)

      expect([401, 403]).toContain(response.status)
    })
  })
})

