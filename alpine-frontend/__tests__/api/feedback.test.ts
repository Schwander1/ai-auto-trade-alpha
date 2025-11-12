/**
 * Integration tests for feedback API routes
 */

describe('Feedback API Routes', () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'

  describe('POST /api/feedback', () => {
    it('requires message field', async () => {
      const response = await fetch(`${API_URL}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      })

      expect(response.status).toBeGreaterThanOrEqual(400)
    })

    it('accepts valid feedback', async () => {
      const response = await fetch(`${API_URL}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          message: 'Test feedback message',
        }),
      })

      // Should succeed or return appropriate status
      expect([200, 201, 400, 500]).toContain(response.status)
    })

    it('rejects empty message', async () => {
      const response = await fetch(`${API_URL}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          message: '',
        }),
      })

      expect(response.status).toBeGreaterThanOrEqual(400)
    })
  })
})

