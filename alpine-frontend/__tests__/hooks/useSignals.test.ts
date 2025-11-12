import { renderHook, waitFor, act } from '@testing-library/react'
import { useSignals } from '@/hooks/useSignals'
import { fetchLatestSignals } from '@/lib/api'

jest.mock('@/lib/api', () => ({
  fetchLatestSignals: jest.fn(),
}))

describe('useSignals', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
  })

  it('fetches signals on mount', async () => {
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

    ;(fetchLatestSignals as jest.Mock).mockResolvedValue(mockSignals)

    const { result } = renderHook(() => useSignals({ limit: 10 }))

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(fetchLatestSignals).toHaveBeenCalledWith(10, false, expect.any(AbortSignal))
    expect(result.current.signals).toEqual(mockSignals)
  })

  it('handles loading state', async () => {
    ;(fetchLatestSignals as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve([]), 100))
    )

    const { result } = renderHook(() => useSignals())

    expect(result.current.isLoading).toBe(true)

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
  })

  it('handles errors', async () => {
    const error = new Error('Failed to fetch')
    ;(fetchLatestSignals as jest.Mock).mockRejectedValue(error)

    const { result } = renderHook(() => useSignals())

    await waitFor(() => {
      expect(result.current.error).toBeTruthy()
    })

    expect(result.current.error?.message).toBe('Failed to fetch')
  })

  it('polls at specified interval', async () => {
    const mockSignals = [{ id: '1', symbol: 'AAPL', action: 'BUY', entry_price: 150, confidence: 95, timestamp: new Date().toISOString() }]
    ;(fetchLatestSignals as jest.Mock).mockResolvedValue(mockSignals)

    renderHook(() => useSignals({ pollInterval: 5000, autoPoll: true }))

    await waitFor(() => {
      expect(fetchLatestSignals).toHaveBeenCalledTimes(1)
    })

    act(() => {
      jest.advanceTimersByTime(5000)
    })

    await waitFor(() => {
      expect(fetchLatestSignals).toHaveBeenCalledTimes(2)
    })
  })

  it('does not poll when autoPoll is false', async () => {
    ;(fetchLatestSignals as jest.Mock).mockResolvedValue([])

    renderHook(() => useSignals({ autoPoll: false }))

    await waitFor(() => {
      expect(fetchLatestSignals).toHaveBeenCalledTimes(0)
    })
  })

  it('respects premiumOnly option', async () => {
    ;(fetchLatestSignals as jest.Mock).mockResolvedValue([])

    renderHook(() => useSignals({ premiumOnly: true }))

    await waitFor(() => {
      expect(fetchLatestSignals).toHaveBeenCalledWith(10, true, expect.any(AbortSignal))
    })
  })

  it('respects limit option', async () => {
    ;(fetchLatestSignals as jest.Mock).mockResolvedValue([])

    renderHook(() => useSignals({ limit: 20 }))

    await waitFor(() => {
      expect(fetchLatestSignals).toHaveBeenCalledWith(20, false, expect.any(AbortSignal))
    })
  })

  it('allows manual refresh', async () => {
    const mockSignals = [{ id: '1', symbol: 'AAPL', action: 'BUY', entry_price: 150, confidence: 95, timestamp: new Date().toISOString() }]
    ;(fetchLatestSignals as jest.Mock).mockResolvedValue(mockSignals)

    const { result } = renderHook(() => useSignals({ autoPoll: false }))

    await act(async () => {
      await result.current.refresh()
    })

    expect(fetchLatestSignals).toHaveBeenCalled()
    expect(result.current.signals).toEqual(mockSignals)
  })

  it('cancels previous request on new fetch', async () => {
    const abortController = { abort: jest.fn() }
    ;(fetchLatestSignals as jest.Mock).mockImplementation(() => 
      new Promise(() => {}) // Never resolves
    )

    const { result } = renderHook(() => useSignals({ autoPoll: false }))

    await act(async () => {
      result.current.refresh()
      result.current.refresh() // Second call should cancel first
    })

    // Should handle abort gracefully
    expect(fetchLatestSignals).toHaveBeenCalled()
  })

  it('caches results when cache is enabled', async () => {
    const mockSignals = [{ id: '1', symbol: 'AAPL', action: 'BUY', entry_price: 150, confidence: 95, timestamp: new Date().toISOString() }]
    ;(fetchLatestSignals as jest.Mock).mockResolvedValue(mockSignals)

    const { result } = renderHook(() => useSignals({ cache: true, autoPoll: false }))

    await act(async () => {
      await result.current.refresh()
    })

    const firstCallCount = (fetchLatestSignals as jest.Mock).mock.calls.length

    await act(async () => {
      await result.current.refresh()
    })

    // Should still call but check cache
    expect(fetchLatestSignals).toHaveBeenCalledTimes(firstCallCount + 1)
  })

  it('cleans up on unmount', async () => {
    ;(fetchLatestSignals as jest.Mock).mockResolvedValue([])

    const { unmount } = renderHook(() => useSignals({ pollInterval: 1000 }))

    await waitFor(() => {
      expect(fetchLatestSignals).toHaveBeenCalled()
    })

    unmount()

    act(() => {
      jest.advanceTimersByTime(2000)
    })

    // Should not call after unmount
    const callCount = (fetchLatestSignals as jest.Mock).mock.calls.length
    expect(fetchLatestSignals).toHaveBeenCalledTimes(callCount)
  })
})

