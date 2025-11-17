'use client'

import { useTradingEnvironment } from '@/hooks/useTradingEnvironment'
import { Loader2, Building2, Code, Factory, AlertCircle, RefreshCw } from 'lucide-react'

/**
 * Trading Environment Badge Component
 * Displays current trading environment (Dev/Production/Prop Firm) with visual indicators
 */
export default function TradingEnvironmentBadge() {
  const { status, loading, error, refresh } = useTradingEnvironment()

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-alpine-black-secondary border border-alpine-black-border rounded-lg">
        <Loader2 className="w-4 h-4 animate-spin text-alpine-text-secondary" />
        <span className="text-sm text-alpine-text-secondary">Loading...</span>
      </div>
    )
  }

  if (error || !status) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-alpine-semantic-error/10 border border-alpine-semantic-error/30 rounded-lg">
        <AlertCircle className="w-4 h-4 text-alpine-semantic-error" />
        <span className="text-sm text-alpine-semantic-error">Status unavailable</span>
        <button
          onClick={refresh}
          className="ml-1 p-1 hover:bg-alpine-semantic-error/20 rounded transition-colors"
          title="Retry"
        >
          <RefreshCw className="w-3 h-3 text-alpine-semantic-error" />
        </button>
      </div>
    )
  }

  const getModeConfig = () => {
    if (status.trading_mode === 'prop_firm') {
      return {
        label: 'Prop Firm',
        icon: Building2,
        color: 'text-alpine-neon-purple',
        bg: 'bg-alpine-neon-purple/10',
        border: 'border-alpine-neon-purple/30',
        glow: 'shadow-[0_0_8px_rgba(168,85,247,0.3)]'
      }
    } else if (status.trading_mode === 'production') {
      return {
        label: 'Production',
        icon: Factory,
        color: 'text-alpine-neon-cyan',
        bg: 'bg-alpine-neon-cyan/10',
        border: 'border-alpine-neon-cyan/30',
        glow: 'shadow-[0_0_8px_rgba(34,211,238,0.3)]'
      }
    } else if (status.trading_mode === 'dev') {
      return {
        label: 'Dev',
        icon: Code,
        color: 'text-alpine-neon-pink',
        bg: 'bg-alpine-neon-pink/10',
        border: 'border-alpine-neon-pink/30',
        glow: 'shadow-[0_0_8px_rgba(236,72,153,0.3)]'
      }
    } else {
      return {
        label: 'Simulation',
        icon: AlertCircle,
        color: 'text-alpine-text-secondary',
        bg: 'bg-alpine-black-secondary',
        border: 'border-alpine-black-border',
        glow: ''
      }
    }
  }

  const config = getModeConfig()
  const Icon = config.icon

  return (
    <div 
      className={`flex items-center gap-2 px-3 py-1.5 ${config.bg} border ${config.border} rounded-lg ${config.glow} transition-all hover:opacity-80`}
      title={`Trading Mode: ${config.label}${status.account_name ? ` - ${status.account_name}` : ''}${!status.alpaca_connected ? ' (Not Connected)' : ''}`}
    >
      <Icon className={`w-4 h-4 ${config.color}`} />
      <span className={`text-sm font-semibold ${config.color}`}>
        {config.label}
      </span>
      {status.account_name && (
        <span className="text-xs text-alpine-text-secondary truncate max-w-[120px]">
          {status.account_name}
        </span>
      )}
      {!status.alpaca_connected && (
        <span className="text-xs text-alpine-text-secondary">
          (Offline)
        </span>
      )}
    </div>
  )
}

