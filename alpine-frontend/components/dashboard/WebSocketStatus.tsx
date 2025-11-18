'use client'

import { Wifi, WifiOff, Loader2 } from 'lucide-react'

interface WebSocketStatusProps {
  isConnected: boolean
  isConnecting?: boolean
  className?: string
}

/**
 * WebSocket connection status indicator
 * Shows real-time connection status for signal streaming
 */
export default function WebSocketStatus({ 
  isConnected, 
  isConnecting = false,
  className = '' 
}: WebSocketStatusProps) {
  if (isConnecting) {
    return (
      <div className={`flex items-center gap-2 text-alpine-text-secondary ${className}`}>
        <Loader2 className="w-4 h-4 animate-spin" />
        <span className="text-sm">Connecting...</span>
      </div>
    )
  }

  if (isConnected) {
    return (
      <div className={`flex items-center gap-2 text-alpine-neon-cyan ${className}`}>
        <Wifi className="w-4 h-4" />
        <span className="text-sm font-medium">Live</span>
      </div>
    )
  }

  return (
    <div className={`flex items-center gap-2 text-alpine-text-secondary ${className}`}>
      <WifiOff className="w-4 h-4" />
      <span className="text-sm">Offline</span>
    </div>
  )
}

