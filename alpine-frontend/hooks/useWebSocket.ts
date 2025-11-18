'use client'

import { useEffect, useRef, useState, useCallback } from 'react'

interface UseWebSocketOptions {
  url: string
  onMessage?: (data: any) => void
  onError?: (error: Event) => void
  onOpen?: () => void
  onClose?: () => void
  reconnect?: boolean
  reconnectInterval?: number
  maxReconnectInterval?: number
  enabled?: boolean
}

/**
 * Optimized WebSocket hook for real-time signal updates
 * 
 * Features:
 * - Exponential backoff reconnection
 * - Message queue for messages sent before connection
 * - Proper cleanup and memory leak prevention
 * - Callback refs to avoid unnecessary reconnections
 * - Connection state management
 */
export function useWebSocket({
  url,
  onMessage,
  onError,
  onOpen,
  onClose,
  reconnect = true,
  reconnectInterval = 3000,
  maxReconnectInterval = 30000,
  enabled = true,
}: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<any>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const shouldReconnectRef = useRef(reconnect)
  const currentReconnectDelayRef = useRef(reconnectInterval)
  const messageQueueRef = useRef<any[]>([])
  
  // Use refs for callbacks to avoid dependency issues and unnecessary reconnections
  const onMessageRef = useRef(onMessage)
  const onErrorRef = useRef(onError)
  const onOpenRef = useRef(onOpen)
  const onCloseRef = useRef(onClose)
  
  // Update refs when callbacks change
  useEffect(() => {
    onMessageRef.current = onMessage
    onErrorRef.current = onError
    onOpenRef.current = onOpen
    onCloseRef.current = onClose
  }, [onMessage, onError, onOpen, onClose])

  // Clear reconnect timeout helper
  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
  }, [])

  // Flush message queue when connected
  const flushMessageQueue = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN && messageQueueRef.current.length > 0) {
      const queue = [...messageQueueRef.current]
      messageQueueRef.current = []
      queue.forEach((message) => {
        try {
          wsRef.current?.send(JSON.stringify(message))
        } catch (err) {
          console.error('Failed to send queued message:', err)
        }
      })
    }
  }, [])

  const connect = useCallback(() => {
    // Don't connect if disabled, already connected, or already connecting
    if (!enabled) {
      return
    }
    
    const currentState = wsRef.current?.readyState
    if (currentState === WebSocket.OPEN || currentState === WebSocket.CONNECTING) {
      return
    }

    // Clean up existing connection if any
    if (wsRef.current) {
      try {
        wsRef.current.close()
      } catch (err) {
        // Ignore errors when closing
      }
      wsRef.current = null
    }

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        currentReconnectDelayRef.current = reconnectInterval // Reset delay on successful connection
        flushMessageQueue() // Send any queued messages
        onOpenRef.current?.()
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          const clientReceiveTime = performance.now()
          
          // Calculate delivery latency if server_timestamp is available
          if (data.server_timestamp) {
            const serverTime = data.server_timestamp * 1000 // Convert to milliseconds
            const latencyMs = clientReceiveTime - (performance.timeOrigin + serverTime - Date.now())
            
            // Log warning if latency exceeds patent requirement (<500ms)
            if (latencyMs > 500) {
              console.warn(
                `⚠️ Signal delivery latency ${latencyMs.toFixed(2)}ms exceeds patent requirement (<500ms)`,
                data
              )
            }
            
            // Store latency in signal data
            data.delivery_latency_ms = Math.round(latencyMs)
            
            // Mark performance for monitoring
            performance.mark(`signal-delivery-${data.id || 'unknown'}`)
          }
          
          setLastMessage(data)
          onMessageRef.current?.(data)
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        onErrorRef.current?.(error)
      }

      ws.onclose = (event) => {
        setIsConnected(false)
        onCloseRef.current?.()

        // Only reconnect if enabled and should reconnect
        if (shouldReconnectRef.current && enabled) {
          clearReconnectTimeout()
          
          // Exponential backoff: increase delay up to max
          const delay = Math.min(
            currentReconnectDelayRef.current,
            maxReconnectInterval
          )
          
          reconnectTimeoutRef.current = setTimeout(() => {
            // Double the delay for next attempt (exponential backoff)
            currentReconnectDelayRef.current = Math.min(
              currentReconnectDelayRef.current * 2,
              maxReconnectInterval
            )
            connect()
          }, delay)
        }
      }
    } catch (err) {
      console.error('Failed to create WebSocket:', err)
      onErrorRef.current?.(err as any)
    }
  }, [url, enabled, reconnectInterval, maxReconnectInterval, flushMessageQueue, clearReconnectTimeout])

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false
    clearReconnectTimeout()
    
    if (wsRef.current) {
      try {
        wsRef.current.close()
      } catch (err) {
        // Ignore errors when closing
      }
      wsRef.current = null
    }
    
    messageQueueRef.current = [] // Clear message queue
    setIsConnected(false)
  }, [clearReconnectTimeout])

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify(message))
      } catch (err) {
        console.error('Failed to send WebSocket message:', err)
        // Queue message if send fails
        messageQueueRef.current.push(message)
      }
    } else {
      // Queue message if not connected
      messageQueueRef.current.push(message)
      console.warn('WebSocket is not connected, message queued')
    }
  }, [])

  // Update reconnect preference
  useEffect(() => {
    shouldReconnectRef.current = reconnect
  }, [reconnect])

  // Main effect for connection management
  useEffect(() => {
    if (enabled) {
      connect()
    } else {
      disconnect()
    }

    return () => {
      disconnect()
    }
    // Only depend on url and enabled to avoid unnecessary reconnections
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, enabled])

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
  }
}

