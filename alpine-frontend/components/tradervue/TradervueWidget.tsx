'use client'

import { useEffect, useState } from 'react'
import { ExternalLink, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react'

interface TradervueWidgetProps {
  widgetType?: 'equity' | 'trades' | 'performance'
  width?: number
  height?: number
  className?: string
}

/**
 * Tradervue Widget Component
 * Embeds Tradervue performance widgets in the dashboard
 */
export default function TradervueWidget({
  widgetType = 'equity',
  width = 600,
  height = 400,
  className = ''
}: TradervueWidgetProps) {
  const [widgetUrl, setWidgetUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchWidgetUrl = async () => {
      try {
        setLoading(true)
        setError(null)

        const response = await fetch(
          `/api/v1/tradervue/widget-url?widget_type=${widgetType}&width=${width}&height=${height}`
        )

        if (!response.ok) {
          if (response.status === 503) {
            setError('Tradervue integration not configured')
          } else {
            setError('Failed to load widget URL')
          }
          return
        }

        const data = await response.json()
        setWidgetUrl(data.widget_url)
      } catch (err) {
        setError('Error fetching widget URL')
        console.error('Tradervue widget error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchWidgetUrl()
  }, [widgetType, width, height])

  if (loading) {
    return (
      <div className={`flex items-center justify-center ${className}`} style={{ width, height }}>
        <Loader2 className="w-8 h-8 animate-spin text-alpine-blue" />
      </div>
    )
  }

  if (error) {
    return (
      <div className={`flex flex-col items-center justify-center p-4 bg-alpine-black-secondary rounded-lg ${className}`} style={{ width, height }}>
        <AlertCircle className="w-8 h-8 text-yellow-500 mb-2" />
        <p className="text-sm text-gray-400">{error}</p>
      </div>
    )
  }

  if (!widgetUrl) {
    return null
  }

  return (
    <div className={className}>
      <iframe
        src={widgetUrl}
        width={width}
        height={height}
        frameBorder="0"
        className="rounded-lg"
        title={`Tradervue ${widgetType} widget`}
      />
    </div>
  )
}

/**
 * Tradervue Profile Link Component
 * Displays a link to the public Tradervue profile
 */
export function TradervueProfileLink({ className = '' }: { className?: string }) {
  const [profileUrl, setProfileUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchProfileUrl = async () => {
      try {
        const response = await fetch('/api/v1/tradervue/profile-url')
        if (response.ok) {
          const data = await response.json()
          setProfileUrl(data.profile_url)
        }
      } catch (err) {
        console.error('Tradervue profile URL error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchProfileUrl()
  }, [])

  if (loading || !profileUrl) {
    return null
  }

  return (
    <a
      href={profileUrl}
      target="_blank"
      rel="noopener noreferrer"
      className={`inline-flex items-center gap-2 text-alpine-blue hover:text-alpine-blue-light transition-colors ${className}`}
    >
      <CheckCircle2 className="w-4 h-4" />
      <span>Verified Performance on Tradervue</span>
      <ExternalLink className="w-3 h-3" />
    </a>
  )
}

/**
 * Tradervue Status Badge Component
 * Shows Tradervue integration status
 */
export function TradervueStatusBadge({ className = '' }: { className?: string }) {
  const [status, setStatus] = useState<{
    enabled: boolean
    username?: string
  } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/v1/tradervue/status')
        if (response.ok) {
          const data = await response.json()
          setStatus(data)
        }
      } catch (err) {
        console.error('Tradervue status error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()
  }, [])

  if (loading) {
    return null
  }

  if (!status?.enabled) {
    return null
  }

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1 bg-green-900/20 border border-green-700/50 rounded-full ${className}`}>
      <CheckCircle2 className="w-4 h-4 text-green-500" />
      <span className="text-sm text-green-400">Verified by Tradervue</span>
    </div>
  )
}

