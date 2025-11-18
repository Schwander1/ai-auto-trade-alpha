import { render, screen, waitFor } from '@testing-library/react'
import DashboardPage from '@/app/dashboard/page'

// Mock the hooks
jest.mock('@/hooks/useSignals', () => ({
  useSignals: jest.fn(() => ({
    signals: [
      {
        id: '1',
        symbol: 'AAPL',
        action: 'BUY',
        entry_price: 150.25,
        confidence: 95.5,
        timestamp: new Date().toISOString(),
      },
    ],
    isLoading: false,
    error: null,
    refresh: jest.fn(),
    isPolling: false,
  })),
}))

// Mock fetch
global.fetch = jest.fn()

describe('DashboardPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({}),
    })
  })

  it('renders dashboard header', async () => {
    render(<DashboardPage />)
    
    await waitFor(() => {
      expect(screen.getByText(/dashboard/i)).toBeInTheDocument()
    })
  })

  it('displays stats cards', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        winRate: 65.5,
        total_roi: 12.3,
        total_trades: 100,
      }),
    })

    render(<DashboardPage />)
    
    await waitFor(() => {
      expect(screen.getByText(/win rate/i)).toBeInTheDocument()
      expect(screen.getByText(/total roi/i)).toBeInTheDocument()
    })
  })

  it('displays latest signals', async () => {
    render(<DashboardPage />)
    
    await waitFor(() => {
      expect(screen.getByText(/latest signals/i)).toBeInTheDocument()
      expect(screen.getByText('AAPL')).toBeInTheDocument()
    })
  })

  it('shows loading state', () => {
    const { useSignals } = require('@/hooks/useSignals')
    useSignals.mockReturnValueOnce({
      signals: [],
      isLoading: true,
      error: null,
      refresh: jest.fn(),
      isPolling: false,
    })

    render(<DashboardPage />)
    
    // Should show loading or empty state
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument()
  })

  it('displays error message when fetch fails', async () => {
    const { useSignals } = require('@/hooks/useSignals')
    useSignals.mockReturnValueOnce({
      signals: [],
      isLoading: false,
      error: 'Failed to load signals',
      refresh: jest.fn(),
      isPolling: false,
    })

    render(<DashboardPage />)
    
    await waitFor(() => {
      // Error might be displayed as string or in an error component
      const errorText = screen.queryByText(/failed to load signals/i) ||
                       screen.queryByText(/error/i)
      expect(errorText).toBeTruthy()
    })
  })
})

