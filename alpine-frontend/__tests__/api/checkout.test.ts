/**
 * Integration tests for checkout API routes
 */

describe('Checkout API Routes', () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'

  describe('GET /api/checkout', () => {
    it('requires priceId parameter', async () => {
      const response = await fetch(`${API_URL}/api/checkout`)

      expect(response.status).toBeGreaterThanOrEqual(400)
    })

    it('validates priceId format', async () => {
      const response = await fetch(`${API_URL}/api/checkout?priceId=invalid`)

      expect(response.status).toBeGreaterThanOrEqual(400)
    })

    it('redirects to login when not authenticated', async () => {
      const response = await fetch(
        `${API_URL}/api/checkout?priceId=price_1SSNCpLoDEAt72V24jylX5T0`
      )

      // Should redirect or return 401
      expect([301, 302, 401, 403]).toContain(response.status)
    })
  })
})

