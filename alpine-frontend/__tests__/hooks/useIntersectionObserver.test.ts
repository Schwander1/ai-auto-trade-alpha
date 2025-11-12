import { renderHook } from '@testing-library/react'
import { useIntersectionObserver } from '@/hooks/useIntersectionObserver'

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation((callback) => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
  root: null,
  rootMargin: '',
  thresholds: [],
}))

describe('useIntersectionObserver', () => {
  it('creates intersection observer', () => {
    const callback = jest.fn()
    const { result } = renderHook(() =>
      useIntersectionObserver(callback, { threshold: 0.5 })
    )

    expect(global.IntersectionObserver).toHaveBeenCalled()
    expect(result.current).toBeDefined()
  })

  it('observes element when ref is set', () => {
    const callback = jest.fn()
    const { result } = renderHook(() => useIntersectionObserver(callback))

    const mockElement = document.createElement('div')
    result.current.current = mockElement

    // Observer should be created and observe called
    expect(global.IntersectionObserver).toHaveBeenCalled()
  })

  it('cleans up on unmount', () => {
    const callback = jest.fn()
    const mockObserver = {
      observe: jest.fn(),
      unobserve: jest.fn(),
      disconnect: jest.fn(),
    }

    ;(global.IntersectionObserver as jest.Mock).mockReturnValueOnce(mockObserver)

    const { unmount } = renderHook(() => useIntersectionObserver(callback))

    unmount()

    expect(mockObserver.disconnect).toHaveBeenCalled()
  })
})

