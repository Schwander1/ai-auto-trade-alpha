import { render, screen, fireEvent } from '@testing-library/react'
import PricingTable from '@/components/dashboard/PricingTable'

describe('PricingTable', () => {
  const mockOnUpgrade = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders all three tiers', () => {
    render(<PricingTable onUpgrade={mockOnUpgrade} />)
    
    expect(screen.getByText(/founder/i)).toBeInTheDocument()
    expect(screen.getByText(/professional/i)).toBeInTheDocument()
    expect(screen.getByText(/institutional/i)).toBeInTheDocument()
  })

  it('displays pricing for each tier', () => {
    render(<PricingTable onUpgrade={mockOnUpgrade} />)
    
    expect(screen.getByText(/\$49/)).toBeInTheDocument()
    expect(screen.getByText(/\$99/)).toBeInTheDocument()
    expect(screen.getByText(/\$249/)).toBeInTheDocument()
  })

  it('highlights popular tier', () => {
    render(<PricingTable onUpgrade={mockOnUpgrade} />)
    
    expect(screen.getByText(/most popular/i)).toBeInTheDocument()
  })

  it('shows current tier', () => {
    render(<PricingTable currentTier="starter" onUpgrade={mockOnUpgrade} />)
    
    expect(screen.getByText(/current plan/i)).toBeInTheDocument()
  })

  it('calls onUpgrade when upgrade button clicked', () => {
    render(<PricingTable onUpgrade={mockOnUpgrade} />)
    
    const upgradeButtons = screen.getAllByText(/upgrade/i)
    fireEvent.click(upgradeButtons[0])
    
    expect(mockOnUpgrade).toHaveBeenCalled()
  })

  it('disables upgrade button for current tier', () => {
    render(<PricingTable currentTier="starter" onUpgrade={mockOnUpgrade} />)
    
    const currentPlanButton = screen.getByText(/current plan/i)
    expect(currentPlanButton.closest('button')).toBeDisabled()
  })

  it('displays features for each tier', () => {
    render(<PricingTable onUpgrade={mockOnUpgrade} />)
    
    expect(screen.getByText(/basic signals/i)).toBeInTheDocument()
    expect(screen.getByText(/premium signals/i)).toBeInTheDocument()
    expect(screen.getByText(/all signals/i)).toBeInTheDocument()
  })
})

