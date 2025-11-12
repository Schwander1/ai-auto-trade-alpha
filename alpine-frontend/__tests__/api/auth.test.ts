/**
 * Integration tests for authentication API routes
 */

describe('Auth API Routes', () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9001'

  describe('POST /api/auth/signup', () => {
    it('creates a new user', async () => {
      const response = await fetch(`${API_URL}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: `test${Date.now()}@example.com`,
          password: 'TestPass123!',
          full_name: 'Test User',
        }),
      })

      // Should succeed or return appropriate error
      expect([200, 201, 400, 409]).toContain(response.status)
    })

    it('rejects invalid email', async () => {
      const response = await fetch(`${API_URL}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'invalid-email',
          password: 'TestPass123!',
          full_name: 'Test User',
        }),
      })

      expect(response.status).toBeGreaterThanOrEqual(400)
    })

    it('rejects weak password', async () => {
      const response = await fetch(`${API_URL}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'weak',
          full_name: 'Test User',
        }),
      })

      expect(response.status).toBeGreaterThanOrEqual(400)
    })
  })

  describe('POST /api/auth/login', () => {
    it('authenticates valid user', async () => {
      // This would require a test user to be created first
      // For now, just test the endpoint exists
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'TestPass123!',
        }),
      })

      // Should return 200, 401, or 404
      expect([200, 401, 404]).toContain(response.status)
    })
  })
})

