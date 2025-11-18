import { render, screen, waitFor } from '@testing-library/react'
import TradingEnvironmentBadge from '@/components/dashboard/TradingEnvironmentBadge'
import { useTradingEnvironment } from '@/hooks/useTradingEnvironment'

// Mock the hook
jest.mock('@/hooks/useTradingEnvironment')

const mockUseTradingEnvironment = useTradingEnvironment as jest.MockedFunction<typeof useTradingEnvironment>

describe('TradingEnvironmentBadge', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('displays loading state', () => {
    mockUseTradingEnvironment.mockReturnValue({
      status: null,
      loading: true,
      error: null,
      refresh: jest.fn()
    })

    render(<TradingEnvironmentBadge />)
    
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('displays error state', () => {
    mockUseTradingEnvironment.mockReturnValue({
      status: null,
      loading: false,
      error: 'Failed to fetch',
      refresh: jest.fn()
    })

    render(<TradingEnvironmentBadge />)
    
    expect(screen.getByText('Status unavailable')).toBeInTheDocument()
  })

  it('displays production environment', () => {
    mockUseTradingEnvironment.mockReturnValue({
      status: {
        environment: 'production',
        trading_mode: 'production',
        account_name: 'Production Account',
        account_number: 'PA123',
        portfolio_value: 100000,
        buying_power: 200000,
        prop_firm_enabled: false,
        alpaca_connected: true,
        account_status: 'ACTIVE'
      },
      loading: false,
      error: null,
      refresh: jest.fn()
    })

    render(<TradingEnvironmentBadge />)
    
    expect(screen.getByText('Production')).toBeInTheDocument()
    expect(screen.getByText('Production Account')).toBeInTheDocument()
  })

  it('displays prop firm environment', () => {
    mockUseTradingEnvironment.mockReturnValue({
      status: {
        environment: 'production',
        trading_mode: 'prop_firm',
        account_name: 'Prop Firm Account',
        account_number: 'PF123',
        portfolio_value: 50000,
        buying_power: 50000,
        prop_firm_enabled: true,
        alpaca_connected: true,
        account_status: 'ACTIVE'
      },
      loading: false,
      error: null,
      refresh: jest.fn()
    })

    render(<TradingEnvironmentBadge />)
    
    expect(screen.getByText('Prop Firm')).toBeInTheDocument()
    expect(screen.getByText('Prop Firm Account')).toBeInTheDocument()
  })

  it('displays dev environment', () => {
    mockUseTradingEnvironment.mockReturnValue({
      status: {
        environment: 'development',
        trading_mode: 'dev',
        account_name: null,
        account_number: null,
        portfolio_value: null,
        buying_power: null,
        prop_firm_enabled: false,
        alpaca_connected: false,
        account_status: null
      },
      loading: false,
      error: null,
      refresh: jest.fn()
    })

    render(<TradingEnvironmentBadge />)
    
    expect(screen.getByText('Dev')).toBeInTheDocument()
  })

  it('displays offline status when not connected', () => {
    mockUseTradingEnvironment.mockReturnValue({
      status: {
        environment: 'production',
        trading_mode: 'production',
        account_name: 'Test Account',
        account_number: null,
        portfolio_value: null,
        buying_power: null,
        prop_firm_enabled: false,
        alpaca_connected: false,
        account_status: null
      },
      loading: false,
      error: null,
      refresh: jest.fn()
    })

    render(<TradingEnvironmentBadge />)
    
    expect(screen.getByText('(Offline)')).toBeInTheDocument()
  })

  it('calls refresh when retry button clicked', () => {
    const mockRefresh = jest.fn()
    mockUseTradingEnvironment.mockReturnValue({
      status: null,
      loading: false,
      error: 'Failed',
      refresh: mockRefresh
    })

    render(<TradingEnvironmentBadge />)
    
    const retryButton = screen.getByTitle('Retry')
    retryButton.click()
    
    expect(mockRefresh).toHaveBeenCalled()
  })

  it('displays tooltip with account information', () => {
    mockUseTradingEnvironment.mockReturnValue({
      status: {
        environment: 'production',
        trading_mode: 'production',
        account_name: 'Test Account',
        account_number: 'TA123',
        portfolio_value: 100000,
        buying_power: 200000,
        prop_firm_enabled: false,
        alpaca_connected: true,
        account_status: 'ACTIVE'
      },
      loading: false,
      error: null,
      refresh: jest.fn()
    })

    render(<TradingEnvironmentBadge />)
    
    const badge = screen.getByTitle(/Trading Mode: Production/)
    expect(badge).toBeInTheDocument()
  })
})

