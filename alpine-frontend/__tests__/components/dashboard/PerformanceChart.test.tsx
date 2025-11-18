import { render, screen, waitFor } from '@testing-library/react'
import PerformanceChart from '@/components/dashboard/PerformanceChart'

// Mock lightweight-charts (only if module exists)
try {
  require.resolve('lightweight-charts')
  jest.mock('lightweight-charts', () => ({
    createChart: jest.fn(() => ({
      addLineSeries: jest.fn(() => ({
        setData: jest.fn(),
      })),
      timeScale: jest.fn(() => ({
        fitContent: jest.fn(),
      })),
      applyOptions: jest.fn(),
      remove: jest.fn(),
    })),
  }))
} catch (e) {
  // Module doesn't exist, create a manual mock
  jest.mock('lightweight-charts', () => ({
    createChart: jest.fn(() => ({
      addLineSeries: jest.fn(() => ({
        setData: jest.fn(),
      })),
      timeScale: jest.fn(() => ({
        fitContent: jest.fn(),
      })),
      applyOptions: jest.fn(),
      remove: jest.fn(),
    })),
  }), { virtual: true })
}

const mockData = [
  { date: '2024-01-01', equity: 10000, drawdown: 0 },
  { date: '2024-01-02', equity: 10100, drawdown: 0 },
  { date: '2024-01-03', equity: 10200, drawdown: 0 },
]

describe('PerformanceChart', () => {
  beforeEach(() => {
    // Mock getBoundingClientRect for chart container
    Element.prototype.getBoundingClientRect = jest.fn(() => ({
      width: 800,
      height: 300,
      top: 0,
      left: 0,
      bottom: 300,
      right: 800,
      x: 0,
      y: 0,
      toJSON: jest.fn(),
    }))
  })

  it('renders chart container', async () => {
    render(<PerformanceChart data={mockData} type="equity" />)
    
    // Title should be visible immediately
    expect(screen.getByText('Equity Curve')).toBeInTheDocument()
    
    // Wait for chart to load
    await waitFor(() => {
      expect(screen.getByText('Equity Curve')).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('displays correct title for equity chart', async () => {
    render(<PerformanceChart data={mockData} type="equity" />)
    
    await waitFor(() => {
      expect(screen.getByText('Equity Curve')).toBeInTheDocument()
    })
  })

  it('displays correct title for winrate chart', async () => {
    render(<PerformanceChart data={mockData} type="winrate" />)
    
    await waitFor(() => {
      expect(screen.getByText('Win Rate')).toBeInTheDocument()
    })
  })

  it('displays correct title for ROI chart', async () => {
    render(<PerformanceChart data={mockData} type="roi" />)
    
    await waitFor(() => {
      expect(screen.getByText('ROI')).toBeInTheDocument()
    })
  })

  it('handles empty data', () => {
    render(<PerformanceChart data={[]} type="equity" />)
    
    // Component should render without crashing - title should still show
    expect(screen.getByText('Equity Curve')).toBeInTheDocument()
  })
})

