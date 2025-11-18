import { renderHook, waitFor, act } from '@testing-library/react'
import { useTradingEnvironment } from '@/hooks/useTradingEnvironment'

// Mock fetch
global.fetch = jest.fn()

describe('useTradingEnvironment', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
  })

  it('fetches trading status on mount', async () => {
    const mockStatus = {
      environment: 'production',
      trading_mode: 'production',
      account_name: 'Test Account',
      alpaca_connected: true
    }

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockStatus
    })

    const { result } = renderHook(() => useTradingEnvironment())

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.status).toEqual(mockStatus)
    expect(result.current.error).toBeNull()
  })

  it('handles fetch errors', async () => {
    ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useTradingEnvironment())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.status).toBeNull()
    expect(result.current.error).toBeInstanceOf(Error)
  })

  it('handles non-ok responses', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error'
    })

    const { result } = renderHook(() => useTradingEnvironment())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.status).toBeNull()
    expect(result.current.error).toBeInstanceOf(Error)
  })

  it('refreshes status when refresh is called', async () => {
    const mockStatus = {
      environment: 'production',
      trading_mode: 'production',
      alpaca_connected: true
    }

    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockStatus
    })

    const { result } = renderHook(() => useTradingEnvironment())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Call refresh
    await act(async () => {
      await result.current.refresh()
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(global.fetch).toHaveBeenCalledTimes(2)
  })

  it('auto-refreshes every 30 seconds', async () => {
    const mockStatus = {
      environment: 'production',
      trading_mode: 'production',
      alpaca_connected: true
    }

    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockStatus
    })

    const { result } = renderHook(() => useTradingEnvironment())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Fast-forward 30 seconds
    jest.advanceTimersByTime(30000)

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2)
    })
  })

  it('includes authorization header when token is available', async () => {
    // Mock localStorage
    const mockToken = 'test-token'
    Storage.prototype.getItem = jest.fn(() => mockToken)

    const mockStatus = {
      environment: 'production',
      trading_mode: 'production',
      alpaca_connected: true
    }

    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockStatus
    })

    renderHook(() => useTradingEnvironment())

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled()
    })

    const fetchCall = (global.fetch as jest.Mock).mock.calls[0]
    expect(fetchCall[1]?.headers?.['Authorization']).toBe(`Bearer ${mockToken}`)
  })
})

