import { fetchLatestSignals, fetchSignalById, checkApiHealth, ApiError, fetchWithRetry } from '@/lib/api'

global.fetch = jest.fn()

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('fetchLatestSignals', () => {
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

      const signals = await fetchLatestSignals(10, false)

      expect(signals).toEqual(mockSignals)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/signals/latest'),
        expect.any(Object)
      )
    })

    it('includes limit and premiumOnly in query params', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      })

      await fetchLatestSignals(20, true)

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('limit=20'),
        expect.any(Object)
      )
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('premium_only=true'),
        expect.any(Object)
      )
    })

    it('throws ApiError for invalid response format', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ invalid: 'format' }),
      })

      await expect(fetchLatestSignals()).rejects.toThrow(ApiError)
    })

    it('retries on 5xx errors', async () => {
      ;(global.fetch as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [],
        })

      jest.useFakeTimers()
      const promise = fetchLatestSignals()
      
      await act(async () => {
        jest.advanceTimersByTime(2000)
      })

      await expect(promise).resolves.toEqual([])
      jest.useRealTimers()
    })

    it('does not retry on 4xx errors', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({ error: 'Invalid request' }),
      })

      await expect(fetchLatestSignals()).rejects.toThrow(ApiError)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('handles abort signal', async () => {
      const abortController = new AbortController()
      abortController.abort()

      await expect(
        fetchLatestSignals(10, false, abortController.signal)
      ).rejects.toThrow()
    })
  })

  describe('fetchSignalById', () => {
    it('fetches signal by ID', async () => {
      const mockSignal = {
        id: '1',
        symbol: 'AAPL',
        action: 'BUY',
        entry_price: 150.25,
        confidence: 95.5,
        timestamp: new Date().toISOString(),
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSignal,
      })

      const signal = await fetchSignalById('1')

      expect(signal).toEqual(mockSignal)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/signals/1'),
        expect.any(Object)
      )
    })

    it('throws ApiError for 404', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
      })

      await expect(fetchSignalById('nonexistent')).rejects.toThrow(ApiError)
    })

    it('throws ApiError for invalid response format', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      })

      await expect(fetchSignalById('1')).rejects.toThrow(ApiError)
    })
  })

  describe('checkApiHealth', () => {
    it('returns health status', async () => {
      const mockHealth = { status: 'healthy', version: '1.0.0' }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockHealth,
      })

      const health = await checkApiHealth()

      expect(health).toEqual(mockHealth)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/health'),
        expect.any(Object)
      )
    })

    it('throws ApiError on failure', async () => {
      ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

      await expect(checkApiHealth()).rejects.toThrow(ApiError)
    })
  })

  describe('ApiError', () => {
    it('creates error with message and status code', () => {
      const error = new ApiError('Test error', 404)

      expect(error.message).toBe('Test error')
      expect(error.statusCode).toBe(404)
      expect(error.name).toBe('ApiError')
    })
  })
})

// Helper for fake timers
const act = async (callback: () => void) => {
  callback()
  await new Promise(resolve => setTimeout(resolve, 0))
}
