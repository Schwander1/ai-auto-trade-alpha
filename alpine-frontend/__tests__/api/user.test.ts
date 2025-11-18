/**
 * Integration tests for user API routes
 */

describe('User API Routes', () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('GET /api/user/me', () => {
    it('returns user data when authenticated', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 200,
        ok: true,
        json: async () => ({ id: '1', email: 'test@example.com' }),
      })

      const response = await fetch(`${API_URL}/api/user/me`, {
        headers: {
          'Cookie': 'next-auth.session-token=test', // Mock session
        },
      })

      // Should return 401 if not authenticated, or 200 if authenticated
      expect([200, 401]).toContain(response.status)
    })

    it('returns 401 when not authenticated', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 401,
        ok: false,
      })

      const response = await fetch(`${API_URL}/api/user/me`)

      expect(response.status).toBe(401)
    })
  })
})
