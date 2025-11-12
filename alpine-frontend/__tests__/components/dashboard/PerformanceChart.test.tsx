import { render, screen, waitFor } from '@testing-library/react'
import PerformanceChart from '@/components/dashboard/PerformanceChart'

const mockData = [
  { date: '2024-01-01', equity: 10000, drawdown: 0 },
  { date: '2024-01-02', equity: 10100, drawdown: 0 },
  { date: '2024-01-03', equity: 10200, drawdown: 0 },
]

describe('PerformanceChart', () => {
  it('renders chart container', async () => {
    render(<PerformanceChart data={mockData} type="equity" />)
    
    await waitFor(() => {
      expect(screen.getByText('Equity Curve')).toBeInTheDocument()
    })
  })

  it('displays correct title for equity chart', () => {
    render(<PerformanceChart data={mockData} type="equity" />)
    
    expect(screen.getByText('Equity Curve')).toBeInTheDocument()
  })

  it('displays correct title for winrate chart', () => {
    render(<PerformanceChart data={mockData} type="winrate" />)
    
    expect(screen.getByText('Win Rate')).toBeInTheDocument()
  })

  it('displays correct title for ROI chart', () => {
    render(<PerformanceChart data={mockData} type="roi" />)
    
    expect(screen.getByText('ROI')).toBeInTheDocument()
  })

  it('handles empty data', () => {
    render(<PerformanceChart data={[]} type="equity" />)
    
    // Component should render without crashing
    expect(screen.getByText('Equity Curve')).toBeInTheDocument()
  })
})

