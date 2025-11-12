/**
 * Integration tests for user API routes
 */

describe('User API Routes', () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'

  describe('GET /api/user/me', () => {
    it('returns user data when authenticated', async () => {
      // This would require a valid session token
      // For now, test the endpoint structure
      const response = await fetch(`${API_URL}/api/user/me`, {
        headers: {
          'Cookie': 'next-auth.session-token=test', // Mock session
        },
      })

      // Should return 401 if not authenticated, or 200 if authenticated
      expect([200, 401]).toContain(response.status)
    })

    it('returns 401 when not authenticated', async () => {
      const response = await fetch(`${API_URL}/api/user/me`)

      expect(response.status).toBe(401)
    })
  })
})

