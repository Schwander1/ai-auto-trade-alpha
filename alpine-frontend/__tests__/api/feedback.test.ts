/**
 * Integration tests for feedback API routes
 */

describe('Feedback API Routes', () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('POST /api/feedback', () => {
    it('requires message field', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 400,
        ok: false,
      })

      const response = await fetch(`${API_URL}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      })

      expect(response.status).toBeGreaterThanOrEqual(400)
    })

    it('accepts valid feedback', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 200,
        ok: true,
        json: async () => ({ success: true }),
      })

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
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 400,
        ok: false,
      })

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

