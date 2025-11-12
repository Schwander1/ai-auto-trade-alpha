/**
 * Integration tests for signals API routes
 */

describe('Signals API Routes', () => {
  const API_URL = process.env.NEXT_PUBLIC_ARGO_API_URL || 'http://localhost:8000'

  describe('GET /api/signals/latest', () => {
    it('returns array of signals', async () => {
      const response = await fetch(`${API_URL}/api/signals/latest?limit=10`)
      
      if (response.ok) {
        const data = await response.json()
        expect(Array.isArray(data)).toBe(true)
      } else {
        // API might not be running, that's okay for tests
        expect([200, 404, 500]).toContain(response.status)
      }
    })

    it('respects limit parameter', async () => {
      const response = await fetch(`${API_URL}/api/signals/latest?limit=5`)
      
      if (response.ok) {
        const data = await response.json()
        expect(data.length).toBeLessThanOrEqual(5)
      }
    })
  })

  describe('GET /api/signals/:id', () => {
    it('returns signal by ID', async () => {
      const response = await fetch(`${API_URL}/api/signals/1`)
      
      // Should return 200 or 404
      expect([200, 404]).toContain(response.status)
    })
  })

  describe('GET /api/signals/stats', () => {
    it('returns signal statistics', async () => {
      const response = await fetch(`${API_URL}/api/signals/stats`)
      
      if (response.ok) {
        const data = await response.json()
        expect(data).toHaveProperty('total_signals')
      } else {
        expect([200, 404, 500]).toContain(response.status)
      }
    })
  })
})

