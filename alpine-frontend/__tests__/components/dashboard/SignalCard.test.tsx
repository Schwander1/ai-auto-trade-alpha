import { render, screen, fireEvent } from '@testing-library/react'
import SignalCard from '@/components/dashboard/SignalCard'
import type { Signal } from '@/types/signal'

const mockSignal: Signal = {
  id: '1',
  symbol: 'AAPL',
  action: 'BUY',
  entry_price: 150.25,
  confidence: 95.5,
  timestamp: new Date().toISOString(),
  hash: 'abc123def456',
  type: 'PREMIUM',
  regime: 'Bull',
  stop_loss: 145.00,
  take_profit: 160.00,
  exit_price: null,
  outcome: null,
  pnl_pct: null,
}

describe('SignalCard', () => {
  it('renders signal data correctly', () => {
    render(<SignalCard signal={mockSignal} />)

    expect(screen.getByText('AAPL')).toBeInTheDocument()
    expect(screen.getByText('BUY')).toBeInTheDocument()
    expect(screen.getByText(/\$150\.25/)).toBeInTheDocument()
    expect(screen.getByText(/95\.5%/)).toBeInTheDocument()
  })

  it('displays stop loss and take profit when provided', () => {
    render(<SignalCard signal={mockSignal} />)

    expect(screen.getByText(/\$145\.00/)).toBeInTheDocument()
    expect(screen.getByText(/\$160\.00/)).toBeInTheDocument()
  })

  it('displays outcome when signal is closed', () => {
    const closedSignal: Signal = {
      ...mockSignal,
      outcome: 'win' as const,
      exit_price: 155.00,
      pnl_pct: 3.16,
    }

    render(<SignalCard signal={closedSignal} />)

    expect(screen.getByText(/win/i)).toBeInTheDocument()
    expect(screen.getByText(/\+3\.16%/)).toBeInTheDocument()
  })

  it('renders in compact mode', () => {
    render(<SignalCard signal={mockSignal} compact />)

    expect(screen.getByText('AAPL')).toBeInTheDocument()
    // In compact mode, detailed info should not be visible
    expect(screen.queryByText(/Stop Loss/)).not.toBeInTheDocument()
  })

  it('displays regime badge when provided', () => {
    render(<SignalCard signal={mockSignal} />)

    // Regime badge might be displayed as "Bull" (capitalized) or "bull" (lowercase)
    const regimeText = screen.queryByText(/bull/i)
    expect(regimeText).toBeInTheDocument()
  })

  it('formats confidence score correctly', () => {
    render(<SignalCard signal={mockSignal} />)

    const confidenceElement = screen.getByText(/95\.5%/)
    expect(confidenceElement).toBeInTheDocument()
  })
})
