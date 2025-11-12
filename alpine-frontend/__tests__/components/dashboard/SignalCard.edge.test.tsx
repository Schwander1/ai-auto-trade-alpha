import { render, screen } from '@testing-library/react'
import SignalCard from '@/components/dashboard/SignalCard'
import type { Signal } from '@/types/signal'

describe('SignalCard Edge Cases', () => {
  it('handles missing optional fields', () => {
    const minimalSignal: Signal = {
      id: '1',
      symbol: 'AAPL',
      action: 'BUY',
      entry_price: 150.25,
      confidence: 95.5,
      timestamp: new Date().toISOString(),
      hash: '',
      type: 'premium',
    }

    render(<SignalCard signal={minimalSignal} />)
    
    expect(screen.getByText('AAPL')).toBeInTheDocument()
  })

  it('handles null exit price', () => {
    const signal: Signal = {
      id: '1',
      symbol: 'AAPL',
      action: 'BUY',
      entry_price: 150.25,
      confidence: 95.5,
      timestamp: new Date().toISOString(),
      exit_price: null,
      outcome: null,
      pnl_pct: null,
      hash: 'abc123',
      type: 'premium',
    }

    render(<SignalCard signal={signal} />)
    
    expect(screen.getByText('AAPL')).toBeInTheDocument()
  })

  it('handles loss outcome', () => {
    const signal: Signal = {
      id: '1',
      symbol: 'AAPL',
      action: 'BUY',
      entry_price: 150.25,
      confidence: 95.5,
      timestamp: new Date().toISOString(),
      exit_price: 145.00,
      outcome: 'loss',
      pnl_pct: -3.5,
      hash: 'abc123',
      type: 'premium',
    }

    render(<SignalCard signal={signal} />)
    
    expect(screen.getByText(/loss/i)).toBeInTheDocument()
    expect(screen.getByText(/-3\.5%/)).toBeInTheDocument()
  })

  it('handles expired outcome', () => {
    const signal: Signal = {
      id: '1',
      symbol: 'AAPL',
      action: 'BUY',
      entry_price: 150.25,
      confidence: 95.5,
      timestamp: new Date().toISOString(),
      exit_price: 150.25,
      outcome: 'expired',
      pnl_pct: 0,
      hash: 'abc123',
      type: 'premium',
    }

    render(<SignalCard signal={signal} />)
    
    expect(screen.getByText(/expired/i)).toBeInTheDocument()
  })

  it('handles very high confidence scores', () => {
    const signal: Signal = {
      id: '1',
      symbol: 'AAPL',
      action: 'BUY',
      entry_price: 150.25,
      confidence: 99.9,
      timestamp: new Date().toISOString(),
      hash: 'abc123',
      type: 'premium',
    }

    render(<SignalCard signal={signal} />)
    
    expect(screen.getByText(/99\.9%/)).toBeInTheDocument()
  })

  it('handles very low confidence scores', () => {
    const signal: Signal = {
      id: '1',
      symbol: 'AAPL',
      action: 'BUY',
      entry_price: 150.25,
      confidence: 50.0,
      timestamp: new Date().toISOString(),
      hash: 'abc123',
      type: 'premium',
    }

    render(<SignalCard signal={signal} />)
    
    expect(screen.getByText(/50\.0%/)).toBeInTheDocument()
  })
})

