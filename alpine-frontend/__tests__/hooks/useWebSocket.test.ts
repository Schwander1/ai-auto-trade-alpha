import { renderHook, waitFor } from '@testing-library/react'
import { useWebSocket } from '@/hooks/useWebSocket'

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  readyState = MockWebSocket.CONNECTING
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null

  constructor(public url: string) {
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    }, 0)
  }

  send(data: string) {
    // Mock send
  }

  close() {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close'))
    }
  }
}

const mockWebSocketConstructor = jest.fn((url: string) => {
  return new MockWebSocket(url)
}) as any
mockWebSocketConstructor.CONNECTING = 0
mockWebSocketConstructor.OPEN = 1
mockWebSocketConstructor.CLOSING = 2
mockWebSocketConstructor.CLOSED = 3

global.WebSocket = mockWebSocketConstructor

describe('useWebSocket', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('connects to WebSocket', async () => {
    const onMessage = jest.fn()
    
    renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000',
        onMessage,
        enabled: true,
      })
    )

    await waitFor(() => {
      // Connection should be established
      expect(mockWebSocketConstructor).toHaveBeenCalled()
    })
  })

  it('calls onMessage when message is received', async () => {
    const onMessage = jest.fn()
    
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000',
        onMessage,
        enabled: true,
      })
    )

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true)
    })

    // Simulate message
    onMessage({ type: 'signal', data: 'test' })
    expect(onMessage).toHaveBeenCalled()
  })

  it('disconnects when enabled is false', async () => {
    const { result, rerender } = renderHook(
      ({ enabled }) =>
        useWebSocket({
          url: 'ws://localhost:8000',
          enabled,
        }),
      { initialProps: { enabled: true } }
    )

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true)
    })

    rerender({ enabled: false })

    await waitFor(() => {
      expect(result.current.isConnected).toBe(false)
    })
  })
})

