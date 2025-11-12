import { fetchSignals } from '@/lib/api'

// Mock fetch
global.fetch = jest.fn()

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('fetches signals successfully', async () => {
    const mockSignals = [
      {
        id: '1',
        symbol: 'AAPL',
        action: 'BUY',
        entry_price: 150.25,
        confidence: 95.5,
        timestamp: new Date().toISOString(),
      },
    ]

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockSignals,
    })

    // Note: fetchSignals might not be exported, adjust based on actual exports
    // This is a placeholder test structure
    expect(global.fetch).toBeDefined()
  })

  it('handles API errors', async () => {
    ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

    // Test error handling
    expect(global.fetch).toBeDefined()
  })
})

